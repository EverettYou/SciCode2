"""Optimize the geminal-NQS at one (lattice, J, sector) point and measure diagnostics.

Example:
  python code/run_point.py --Lx 4 --Ly 4 --bc pa --J 2.0 --N1 16 --N2 16 --Nup 16 --Ndn 16 \
      --init fl --n_iter 400 --out data/L4_pa_J2.0_N32_Sz0_fl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jax
import jax.numpy as jnp
import optax
import netket as nk
from flax import serialization

from model import Lattice, free_energy_sector
from vmc import (make_hilbert, make_hamiltonian, translation_tables, GeminalNQS, BilayerRule,
                 fl_pairing_matrix, singlet_pairing_matrix, bcs_pairing_matrix,
                 pairing_matrix_to_params, unpaired_orbitals_init, build_observables)


def parse():
    p = argparse.ArgumentParser()
    p.add_argument("--Lx", type=int, default=4)
    p.add_argument("--Ly", type=int, default=4)
    p.add_argument("--bc", type=str, default="pa")
    p.add_argument("--J", type=float, required=True)
    p.add_argument("--t2", type=float, default=0.2)
    p.add_argument("--N1", type=int, required=True, help="electrons in layer 1")
    p.add_argument("--N2", type=int, required=True, help="electrons in layer 2")
    p.add_argument("--Nup", type=int, required=True)
    p.add_argument("--Ndn", type=int, required=True)
    p.add_argument("--init", type=str, default="fl", help="fl|singlet|bcs|mix|file:<path>")
    p.add_argument("--delta0", type=float, default=0.5, help="BCS init gap / mix weight")
    p.add_argument("--n_hidden", type=int, default=8)
    p.add_argument("--no_rbm", action="store_true")
    p.add_argument("--no_j2", action="store_true")
    p.add_argument("--n_iter", type=int, default=400)
    p.add_argument("--n_samples", type=int, default=2048)
    p.add_argument("--n_chains", type=int, default=64)
    p.add_argument("--n_discard", type=int, default=16)
    p.add_argument("--lr", type=float, default=0.03)
    p.add_argument("--lr_final", type=float, default=None)
    p.add_argument("--diag_shift", type=float, default=0.01)
    p.add_argument("--n_final", type=int, default=16384)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--measure", type=str, default="spin,nk,pair,local")
    p.add_argument("--p_exchange", type=float, default=0.3)
    p.add_argument("--triplet", action="store_true", help="Sz=1 sector: use up-up pairing block")
    p.add_argument("--qx", type=float, default=0.0, help="triplet modulation momentum / pi")
    p.add_argument("--qy", type=float, default=0.0)
    p.add_argument("--g0", type=float, default=0.3, help="initial amplitude of the on-site triplon pairing block")
    p.add_argument("--u_scale", type=float, default=1.0, help="scale of the Fermi-liquid-triplet orbital init")
    p.add_argument("--momentum", type=float, default=None, help="SPRING momentum (None = off)")
    p.add_argument("--no_ntk", action="store_true", help="force the explicit QGT (no kernel/NTK) SR solver")
    p.add_argument("--out", type=str, required=True)
    return p.parse_args()


def main():
    args = parse()
    t_start = time.time()
    lat = Lattice(args.Lx, args.Ly, args.bc)
    nc = lat.n_cell
    N1, N2, Nup, Ndn = args.N1, args.N2, args.Nup, args.Ndn
    assert N1 + N2 == Nup + Ndn
    hi = make_hilbert(lat, Nup, Ndn)
    H = make_hamiltonian(hi, lat, args.J, t2=args.t2)
    tabs = translation_tables(lat)

    # ---- initial pairing -------------------------------------------------
    n_small = min(Nup, Ndn)
    n_per_flavor = max(1, n_small // 2) if n_small > 0 else 0
    # intralayer projector needs n per (layer,spin); for the FL use N1//2 per flavor (Sz=0, N1=N2)
    nfl = int(round(N1 / 2))
    Phi_fl, band = fl_pairing_matrix(lat, nfl, t2=args.t2)
    Phi_sg = singlet_pairing_matrix(lat)
    init = args.init
    if init == "fl":
        Phi0 = Phi_fl
    elif init == "singlet":
        Phi0 = Phi_sg
    elif init == "bcs":
        Phi0 = bcs_pairing_matrix(lat, nfl, args.delta0, t2=args.t2)
    elif init == "mix":
        Phi0 = Phi_fl + args.delta0 * Phi_sg
    elif init.startswith("file:"):
        Phi0 = None
    elif init.startswith("auto:"):
        # auto:<prefix> -> load the lower-energy finished ground state <prefix>_gs_fl / _gs_sg (if any)
        import glob as _glob
        best, best_e = None, np.inf
        for cand in (init[5:] + "_gs_fl", init[5:] + "_gs_sg", init[5:] + "_gs_bcs"):
            if os.path.exists(cand + ".json") and os.path.exists(cand + ".mpack"):
                e = json.load(open(cand + ".json"))["energy"]
                if e < best_e:
                    best, best_e = cand, e
        if best is None:
            print("[init] auto: no finished ground state found, falling back to bcs", flush=True)
            init = "bcs"
            Phi0 = bcs_pairing_matrix(lat, nfl, args.delta0, t2=args.t2)
        else:
            init = "file:" + best + ".mpack"
            print(f"[init] auto: loading {best} (E={best_e:.4f})", flush=True)
            Phi0 = None
    else:
        raise ValueError(init)
    if Phi0 is not None:
        F0 = pairing_matrix_to_params(lat, Phi0, tabs)
        # reconstruction residual (nonzero if Phi0 lacks the (magnetic) translation symmetry)
        rec = F0[tabs["pair_idx"]] * tabs["pair_sgn"]
        resid = float(np.linalg.norm(rec - Phi0) / max(np.linalg.norm(Phi0), 1e-12))
        F0 = F0 + 0.02 * np.random.default_rng(args.seed).normal(size=F0.shape) * max(np.abs(F0).max(), 1e-3)
    else:
        F0 = None
        resid = 0.0
    m = abs(Nup - Ndn)
    U0 = args.u_scale * unpaired_orbitals_init(lat, nfl, m, t2=args.t2) if m > 0 else np.zeros((lat.n_orb, 0))
    use_trip = args.triplet and m == 2
    if use_trip:
        # init of the triplon part: on-site interlayer up-up pair, small, plus noise; the rank-2 part U0 is
        # the Fermi-liquid triplet (top occupied x lowest empty orbital) from unpaired_orbitals_init
        G0 = args.g0 * pairing_matrix_to_params(lat, Phi_sg, tabs)
        G0 = G0 + 0.02 * np.random.default_rng(args.seed + 7).normal(size=G0.shape)
    site_xy = np.array([lat.xy(o % nc) for o in range(lat.n_orb)], dtype=float)

    model = GeminalNQS(n_modes=lat.n_modes, n_orb=lat.n_orb, n_cell=nc, Nup=Nup, Ndn=Ndn,
                       pair_idx=tuple(map(tuple, tabs["pair_idx"])), pair_sgn=tuple(map(tuple, tabs["pair_sgn"])),
                       jas_idx=tuple(map(tuple, tabs["jas_idx"])), perm=tuple(map(tuple, tabs["perm"])),
                       n_pair=tabs["n_pair"], n_jas=tabs["n_jas"], n_hidden=args.n_hidden,
                       use_rbm=not args.no_rbm, use_jastrow2=not args.no_j2,
                       pair_init=tuple(F0.tolist()) if F0 is not None else (),
                       unpaired_init=tuple(map(tuple, U0)) if m > 0 else (),
                       triplet=use_trip, q_mod=(args.qx * np.pi, args.qy * np.pi),
                       site_xy=tuple(map(tuple, site_xy)),
                       triplet_init=tuple(G0.tolist()) if use_trip else ())

    rule = BilayerRule(lat, N1, N2, Nup, Ndn, p_exchange=args.p_exchange)
    sampler = nk.sampler.MetropolisSampler(hi, rule, n_chains=args.n_chains, sweep_size=lat.n_modes)
    vstate = nk.vqs.MCState(sampler, model, n_samples=args.n_samples, n_discard_per_chain=args.n_discard,
                            seed=args.seed, sampler_seed=args.seed + 100, chunk_size=None)
    if init.startswith("file:"):
        import msgpack
        from flax.core import freeze, unfreeze
        with open(init[5:], "rb") as f:
            raw = f.read()
        try:
            vstate.variables = serialization.from_bytes(vstate.variables, raw)
        except Exception:
            # partial load: copy matching parameter arrays only (e.g. gs -> sector with unpaired orbitals)
            loaded = serialization.msgpack_restore(raw)
            cur = {k: v for k, v in vstate.parameters.items()}
            n_copied = 0
            for k, v in loaded["params"].items():
                if k in cur and np.shape(v) == np.shape(cur[k]):
                    cur[k] = jnp.asarray(v)
                    n_copied += 1
            vstate.parameters = cur
            print(f"[init] partial load: {n_copied} parameter arrays copied", flush=True)
    n_params = vstate.n_parameters
    print(f"[setup] L={args.Lx}x{args.Ly} bc={args.bc} J={args.J} sector N1={N1} N2={N2} Nup={Nup} Ndn={Ndn} "
          f"n_params={n_params} init={init} resid={resid:.2e} ({time.time()-t_start:.1f}s)", flush=True)

    # sanity: initial energy
    e0 = vstate.expect(H)
    print(f"[init] E = {e0.mean.real:.5f} +- {e0.error_of_mean:.5f}  E/site = {e0.mean.real/nc:.5f}  "
          f"acc={float(vstate.sampler_state.acceptance):.3f} ({time.time()-t_start:.1f}s)", flush=True)

    # ---- optimization ----------------------------------------------------
    lr_final = args.lr_final if args.lr_final is not None else args.lr / 3
    schedule = optax.linear_schedule(args.lr, lr_final, args.n_iter)
    opt = optax.sgd(learning_rate=schedule)
    driver = nk.driver.VMC_SR(H, opt, variational_state=vstate, diag_shift=args.diag_shift, mode="real",
                              momentum=args.momentum, use_ntk=(False if args.no_ntk else None))
    log = nk.logging.RuntimeLog()
    t_opt = time.time()
    # chunked optimization with NaN guard: restore the last checkpoint and halve the learning rate on failure
    import copy
    chunk = 25
    done = 0
    n_restarts = 0
    lr_scale = 1.0
    ckpt = copy.deepcopy(vstate.parameters)
    hist_E, hist_err, hist_var = [], [], []
    while done < args.n_iter:
        n_this = min(chunk, args.n_iter - done)
        sub = nk.logging.RuntimeLog()
        driver.run(n_iter=n_this, out=sub, show_progress=False)
        e = np.real(np.asarray(sub.data["Energy"]["Mean"]))
        if not np.all(np.isfinite(e)) or not np.all(np.isfinite(np.asarray(sub.data["Energy"]["Variance"]))):
            n_restarts += 1
            lr_scale *= 0.5
            print(f"[opt] NaN at iteration ~{done + n_this}; restoring checkpoint, lr scale {lr_scale} (restart {n_restarts})", flush=True)
            vstate.parameters = copy.deepcopy(ckpt)
            # re-draw the Markov chains: the current chain states may have zero amplitude under the restored parameters
            vstate.sampler_state = vstate.sampler.init_state(vstate._model, vstate.variables,
                                                             jax.random.PRNGKey(args.seed + 1000 * n_restarts))
            vstate.reset()
            schedule = optax.linear_schedule(args.lr * lr_scale, lr_final * lr_scale, args.n_iter)
            driver = nk.driver.VMC_SR(H, optax.sgd(learning_rate=schedule), variational_state=vstate,
                                      diag_shift=args.diag_shift * (2 ** n_restarts), mode="real",
                                      momentum=None if n_restarts > 1 else args.momentum,
                                      use_ntk=(False if args.no_ntk else None))
            if n_restarts > 6:
                print("[opt] too many restarts, giving up", flush=True)
                break
            continue
        hist_E += e.tolist()
        hist_err += np.asarray(sub.data["Energy"]["Sigma"]).tolist()
        hist_var += np.asarray(sub.data["Energy"]["Variance"]).tolist()
        done += n_this
        ckpt = copy.deepcopy(vstate.parameters)
    hist_E, hist_err, hist_var = np.array(hist_E), np.array(hist_err), np.array(hist_var)
    print(f"[opt] done {args.n_iter} iters in {time.time()-t_opt:.1f}s; "
          f"last 20: E/site = {hist_E[-20:].mean()/nc:.5f}  var/site = {hist_var[-20:].mean()/nc:.4f}", flush=True)

    # ---- final measurement -------------------------------------------------
    vstate.n_samples = args.n_final
    vstate.chunk_size = 2048
    vstate.reset()
    t_m = time.time()
    E = vstate.expect(H)
    result = dict(
        Lx=args.Lx, Ly=args.Ly, bc=args.bc, J=args.J, t2=args.t2, N1=N1, N2=N2, Nup=Nup, Ndn=Ndn,
        init=init, n_params=int(n_params), n_iter=args.n_iter, n_samples=args.n_samples,
        triplet=bool(use_trip), qx=args.qx, qy=args.qy, n_hidden=args.n_hidden, momentum=args.momentum,
        n_final=args.n_final, diag_shift=args.diag_shift, lr=args.lr, seed=args.seed,
        energy=float(E.mean.real), energy_err=float(E.error_of_mean), energy_var=float(E.variance),
        tau_corr=float(E.tau_corr), r_hat=float(E.R_hat),
        energy_per_site=float(E.mean.real / nc), energy_per_site_err=float(E.error_of_mean / nc),
        acceptance=float(vstate.sampler_state.acceptance),
        hist_E=hist_E.tolist(), hist_err=hist_err.tolist(), hist_var=hist_var.tolist(), n_restarts=n_restarts,
        band=band.tolist(), init_resid=resid,
    )
    which = tuple(args.measure.split(",")) if args.measure else ()
    if which:
        obs = build_observables(hi, lat, which)
        vals = {}
        for name, op in obs.items():
            st = vstate.expect(op)
            vals[name] = [float(st.mean.real), float(st.error_of_mean)]
        result["obs"] = vals
    print(f"[final] E/site = {result['energy_per_site']:.6f} +- {result['energy_per_site_err']:.6f} "
          f"(var {E.variance:.3f}, tau {E.tau_corr:.2f}, Rhat {E.R_hat:.3f}) measured in {time.time()-t_m:.1f}s; "
          f"total {time.time()-t_start:.1f}s", flush=True)
    with open(args.out + ".json", "w") as f:
        json.dump(result, f)
    with open(args.out + ".mpack", "wb") as f:
        f.write(serialization.to_bytes(vstate.variables))


if __name__ == "__main__":
    main()
