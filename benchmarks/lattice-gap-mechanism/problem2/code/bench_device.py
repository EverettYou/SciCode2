"""Time one production SR iteration (sampling + energy + SR update) of the geminal-NQS on CPU vs GPU.

Usage:
  JAX_PLATFORMS=cpu  taskset -c 0-3 python code/bench_device.py --L 4 --n_iter 5
  JAX_PLATFORMS=cuda CUDA_VISIBLE_DEVICES=1 python code/bench_device.py --L 6 --n_iter 5
Mirrors run_point.py / batch.py production settings (4x4: 2048 samples, 6x6: 1024 samples, 64 chains,
n_hidden=16, SPRING momentum 0.8, diag_shift 0.01, FL / BCS init).  Prints JSON with timings.
"""
from __future__ import annotations
import argparse, json, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jax, optax, netket as nk
from model import Lattice
from vmc import (make_hilbert, make_hamiltonian, translation_tables, GeminalNQS, BilayerRule,
                 fl_pairing_matrix, bcs_pairing_matrix, pairing_matrix_to_params, build_observables)

p = argparse.ArgumentParser()
p.add_argument("--L", type=int, default=4)
p.add_argument("--J", type=float, default=4.0)
p.add_argument("--n_iter", type=int, default=5)
p.add_argument("--n_samples", type=int, default=None)
p.add_argument("--n_chains", type=int, default=64)
p.add_argument("--n_hidden", type=int, default=16)
p.add_argument("--no_ntk", action="store_true")
p.add_argument("--chunk", type=int, default=None, help="MCState chunk_size (needed on GPU for 6x6: unchunked local energies need ~75 GiB)")
p.add_argument("--measure", action="store_true", help="also time the observable measurement (spin,nk,pair,local)")
a = p.parse_args()
dev = jax.devices()[0]
L = a.L
n_samples = a.n_samples or (2048 if L == 4 else 1024)
lat = Lattice(L, L, "pa")
nc = lat.n_cell
N = nc  # nu = 1/2 : one electron per site per layer... N1=N2=nc/... (half filling: N1 = N2 = nc, Nup = Ndn = nc)
N1 = N2 = Nup = Ndn = nc
t0 = time.time()
hi = make_hilbert(lat, Nup, Ndn)
H = make_hamiltonian(hi, lat, a.J)
tabs = translation_tables(lat)
nfl = N1 // 2
Phi0 = fl_pairing_matrix(lat, nfl)[0] if L == 4 else bcs_pairing_matrix(lat, nfl, 0.5)
F0 = pairing_matrix_to_params(lat, Phi0, tabs)
F0 = F0 + 0.02 * np.random.default_rng(1).normal(size=F0.shape) * max(np.abs(F0).max(), 1e-3)
site_xy = np.array([lat.xy(o % nc) for o in range(lat.n_orb)], dtype=float)
model = GeminalNQS(n_modes=lat.n_modes, n_orb=lat.n_orb, n_cell=nc, Nup=Nup, Ndn=Ndn,
                   pair_idx=tuple(map(tuple, tabs["pair_idx"])), pair_sgn=tuple(map(tuple, tabs["pair_sgn"])),
                   jas_idx=tuple(map(tuple, tabs["jas_idx"])), perm=tuple(map(tuple, tabs["perm"])),
                   n_pair=tabs["n_pair"], n_jas=tabs["n_jas"], n_hidden=a.n_hidden,
                   use_rbm=True, use_jastrow2=True, pair_init=tuple(F0.tolist()), unpaired_init=(),
                   triplet=False, q_mod=(0.0, 0.0), site_xy=tuple(map(tuple, site_xy)), triplet_init=())
rule = BilayerRule(lat, N1, N2, Nup, Ndn, p_exchange=0.3)
sampler = nk.sampler.MetropolisSampler(hi, rule, n_chains=a.n_chains, sweep_size=lat.n_modes)
vstate = nk.vqs.MCState(sampler, model, n_samples=n_samples, n_discard_per_chain=16, seed=1, sampler_seed=101, chunk_size=a.chunk)
t_setup = time.time() - t0
# energy (compile + run)
t = time.time(); e = vstate.expect(H); float(e.mean.real); t_e_first = time.time() - t
vstate.reset()
t = time.time(); e = vstate.expect(H); float(e.mean.real); t_e = time.time() - t
opt = optax.sgd(learning_rate=0.03)
driver = nk.driver.VMC_SR(H, opt, variational_state=vstate, diag_shift=0.01, mode="real", momentum=0.8,
                          use_ntk=(False if a.no_ntk else None))
t = time.time(); driver.run(n_iter=1, show_progress=False); t_sr_first = time.time() - t
t = time.time(); driver.run(n_iter=a.n_iter, show_progress=False); t_sr = (time.time() - t) / a.n_iter
out = dict(device=str(dev), platform=dev.platform, L=L, n_params=int(vstate.n_parameters), n_samples=n_samples,
           n_chains=a.n_chains, chunk=a.chunk, setup_s=round(t_setup, 1), energy_first_s=round(t_e_first, 1), energy_s=round(t_e, 2),
           sr_first_s=round(t_sr_first, 1), sr_iter_s=round(t_sr, 2),
           threads=os.environ.get("OMP_NUM_THREADS"), xla=os.environ.get("XLA_FLAGS"))
if a.measure:
    obs = build_observables(hi, lat, ("spin", "nk", "pair", "local"))
    vstate.n_samples = 4096
    vstate.reset()
    t = time.time()
    for k, o in obs.items():
        float(np.real(vstate.expect(o).mean)) if not isinstance(o, (list, tuple)) else None
    out["measure_4096_first_s"] = round(time.time() - t, 1)
    vstate.reset()
    t = time.time()
    for k, o in obs.items():
        float(np.real(vstate.expect(o).mean)) if not isinstance(o, (list, tuple)) else None
    out["measure_4096_s"] = round(time.time() - t, 1)
print(json.dumps(out), flush=True)
