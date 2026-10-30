"""Strong-coupling gaps of the rung-singlet phase vs J (2D, t2=0.2): where do they close?"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from spectra import bands
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
Js = np.arange(2.0, 12.01, 0.5)
rows = []
for J in Js:
    d = bands(J, L=48)
    g = d["gaps"]
    rows.append(dict(J=float(J), spin=g["spin"], single=g["single"], pair=g["pair"], e_gs=d["e_gs_per_site"],
                     trip_hop1=d["trip"]["hop1"], tri_hop1=d["tri"]["hop1"], tb1=d["pair_hole"]["t_b1"], V1=d["pair_hole"]["V1"]))
    print(f"J={J:5.2f}: spin gap={g['spin']:6.3f}  single-particle gap={g['single']:6.3f}  pair gap={g['pair']:6.3f}  E_gs/site={d['e_gs_per_site']:8.4f}  V1/tb1={d['pair_hole']['V1']/d['pair_hole']['t_b1']:.2f}")
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "..", "data", "sc_gaps_vs_J.json"), "w"))
fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(Js, [r["spin"] for r in rows], "o-", label="spin gap (triplon)")
ax.plot(Js, [r["single"] for r in rows], "s-", label="single-particle gap (trion+holon)")
ax.plot(Js, [r["pair"] for r in rows], "^-", label="two-particle gap (rung pair)")
ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("J/t1"); ax.set_ylabel("gap / t1"); ax.legend(fontsize=8)
ax.set_title("strong-coupling (2nd order) gaps of the rung-singlet insulator, 2D, t2=0.2")
fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "..", "figures", "sc_gaps_vs_J.png"), dpi=130)
