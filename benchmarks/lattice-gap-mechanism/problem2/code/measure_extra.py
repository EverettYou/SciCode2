"""Re-measure additional observables for a finished run (loads its parameters).
Usage: python code/measure_extra.py data/<run> --measure dens --n_final 8192
"""
import argparse, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import netket as nk
from flax import serialization
from model import Lattice
from vmc import make_hilbert, translation_tables, GeminalNQS, BilayerRule, build_observables


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run")
    p.add_argument("--measure", type=str, default="dens")
    p.add_argument("--n_final", type=int, default=8192)
    a = p.parse_args()
    with open(a.run + ".json") as f:
        r = json.load(f)
    lat = Lattice(r["Lx"], r["Ly"], r["bc"])
    nc = lat.n_cell
    hi = make_hilbert(lat, r["Nup"], r["Ndn"])
    tabs = translation_tables(lat)
    m = abs(r["Nup"] - r["Ndn"])
    site_xy = np.array([lat.xy(o % nc) for o in range(lat.n_orb)], dtype=float)
    model = GeminalNQS(n_modes=lat.n_modes, n_orb=lat.n_orb, n_cell=nc, Nup=r["Nup"], Ndn=r["Ndn"],
                       pair_idx=tuple(map(tuple, tabs["pair_idx"])), pair_sgn=tuple(map(tuple, tabs["pair_sgn"])),
                       jas_idx=tuple(map(tuple, tabs["jas_idx"])), perm=tuple(map(tuple, tabs["perm"])),
                       n_pair=tabs["n_pair"], n_jas=tabs["n_jas"], n_hidden=r.get("n_hidden", 16),
                       triplet=bool(r.get("triplet", False)), q_mod=(r.get("qx", 0) * np.pi, r.get("qy", 0) * np.pi),
                       site_xy=tuple(map(tuple, site_xy)),
                       unpaired_init=tuple(map(tuple, np.zeros((lat.n_orb, m)))) if m > 0 else ())
    rule = BilayerRule(lat, r["N1"], r["N2"], r["Nup"], r["Ndn"], p_exchange=0.3)
    sampler = nk.sampler.MetropolisSampler(hi, rule, n_chains=64, sweep_size=lat.n_modes)
    vstate = nk.vqs.MCState(sampler, model, n_samples=a.n_final, n_discard_per_chain=32, seed=7, sampler_seed=11, chunk_size=2048)
    with open(a.run + ".mpack", "rb") as f:
        vstate.variables = serialization.from_bytes(vstate.variables, f.read())
    obs = build_observables(hi, lat, tuple(a.measure.split(",")))
    t0 = time.time()
    vals = r.get("obs", {})
    for name, op in obs.items():
        st = vstate.expect(op)
        vals[name] = [float(st.mean.real), float(st.error_of_mean)]
    r["obs"] = vals
    with open(a.run + ".json", "w") as f:
        json.dump(r, f)
    print(f"measured {len(obs)} observables in {time.time()-t0:.0f}s -> {a.run}.json")


if __name__ == "__main__":
    main()
