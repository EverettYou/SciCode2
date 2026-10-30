"""Flag unconverged / unstable runs and move their outputs aside so the batch reruns them.
Criteria: tau_corr > 5, R_hat > 1.05, error per site > 0.003, or final energy above the
mean of the last 20 optimization steps by more than 4 sigma (sampler drift)."""
import glob, json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pattern = sys.argv[1] if len(sys.argv) > 1 else "L*_nu*_J*"
bad = []
for f in sorted(glob.glob(os.path.join(ROOT, "data", pattern + ".json"))):
    if ".bad" in f:
        continue
    r = json.load(open(f))
    nc = r["Lx"] * r["Ly"]
    h = np.array(r["hist_E"]) / nc
    last = h[-20:].mean()
    reasons = []
    if not np.isfinite(r["energy_per_site"]) or not np.isfinite(last): reasons.append("nan")
    if r["tau_corr"] > 5: reasons.append(f"tau={r['tau_corr']:.1f}")
    if r["r_hat"] > (1.05 if nc <= 16 else 1.15): reasons.append(f"Rhat={r['r_hat']:.3f}")
    err_max = (0.003 + 0.0006 * r["J"]) * (nc / 16.0)  # variance grows ~J^2; larger lattices use fewer samples
    if r["energy_per_site_err"] > err_max: reasons.append(f"err={r['energy_per_site_err']:.4f}")
    if np.isfinite(last) and r["energy_per_site"] - last > 4 * max(r["energy_per_site_err"], 1e-4) + 0.002: reasons.append(f"final-last20={r['energy_per_site']-last:.4f}")
    if reasons:
        bad.append((f, reasons))
for f, reasons in bad:
    k = 1
    while os.path.exists(f.replace(".json", f".bad{k}.json")):
        k += 1
    os.rename(f, f.replace(".json", f".bad{k}.json"))
    mp = f.replace(".json", ".mpack")
    if os.path.exists(mp):
        os.rename(mp, mp.replace(".mpack", f".bad{k}.mpack"))
    print(f"BAD {os.path.basename(f)}: {' '.join(reasons)} -> rerun #{k}")
print(f"{len(bad)} bad runs flagged")
