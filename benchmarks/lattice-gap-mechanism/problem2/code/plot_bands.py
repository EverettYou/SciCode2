"""Strong-coupling quasiparticle bands at coupling J along the path (0,0)-(pi,0)-(pi,pi)-(0,0)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from spectra import bands
J = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
d = bands(J, L=96)
kx = d["trip"]["kx"]; n = len(kx)
# path indices
def path():
    idx, lab = [], []
    for i in range(n // 2 + 1): idx.append((i, 0))            # (0,0)->(pi,0)
    for j in range(1, n // 2 + 1): idx.append((n // 2, j))    # (pi,0)->(pi,pi)
    for i in range(1, n // 2 + 1): idx.append((n // 2 - i, n // 2 - i))  # (pi,pi)->(0,0)
    return idx
idx = path()
x = np.arange(len(idx))
fig, axs = plt.subplots(1, 2, figsize=(11, 4))
ax = axs[0]
for name, lab, c in (("tri", "trion (electron addition)", "tab:red"), ("hol", "holon (electron removal)", "tab:blue"), ("pair_hole", "rung pair, charge 2e (per pair)", "tab:green")):
    disp = d[name]["disp"]
    ax.plot(x, [disp[i, j] for (i, j) in idx], color=c, label=lab)
ax.axhline(0, color="k", lw=0.5)
ax.set_xticks([0, n // 2, n, 3 * n // 2]); ax.set_xticklabels(["(0,0)", "(π,0)", "(π,π)", "(0,0)"])
ax.set_ylabel("excitation energy above E_0 / t1"); ax.set_title(f"charge excitations of the rung-singlet state, J={J:g}"); ax.legend(fontsize=8)
ax = axs[1]
disp = d["trip"]["disp"]
ax.plot(x, [disp[i, j] for (i, j) in idx], color="tab:purple", label="triplon (S=1)")
ax.axhline(J, color="k", ls=":", lw=0.8, label="bare rung triplet energy J")
ax.set_xticks([0, n // 2, n, 3 * n // 2]); ax.set_xticklabels(["(0,0)", "(π,0)", "(π,π)", "(0,0)"])
ax.set_ylabel("ω(q) / t1"); ax.set_title("spin excitation (triplon) band"); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "..", "figures", f"bands_J{J:g}.png"), dpi=130)
print("saved", f"figures/bands_J{J:g}.png", "| gaps:", d["gaps"])
