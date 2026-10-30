"""Phase diagram in the (nu, J) plane from data/summary.json, with the two line cuts marked.
Classification rules (also written to data/phase_labels.json):
  gap_excess_c = Δc2 - Δc2(J=0)      (two-particle gap above its finite-size free value)
  gap_excess_1 = Δc1 - Δc1(J=0)
  pair_far     = P(|r|>=2) (interlayer singlet pair correlation at long distance)
  nk_jump      = n(k) discontinuity across the J=0 Fermi surface
  Sminus_max   = max_q S-(q) per site
Labels:
  'SMG insulator'  : gap_excess_c > 0.5 and gap_excess_1 > 0.5 and pair_far < 0.03 and nk_jump < 0.35
  'SC (pairs)'     : pair_far >= 0.05 (free value 0.0005-0.01) and nk_jump < 0.9 and gap_excess_c < 0.5
  'FL'             : otherwise, if nk_jump > 0.9 and gap_excess_c < 0.3
  'crossover'      : remaining points
A magnetic label would require S-(Q)/N_c to grow with N (checked separately with L=6).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def classify(r):
    gx_c = r.get("charge_gap2", np.nan) - r.get("charge_gap2_free", 0)
    gx_1 = r.get("charge_gap1", np.nan) - r.get("charge_gap1_free", 0)
    pf = r.get("pair_far_avg", [np.nan])[0]
    nj = r.get("nk_jump", np.nan)
    pb = r.get("pair_binding", np.nan)
    feats = dict(gap_excess_c=gx_c, gap_excess_1=gx_1, pair_far=pf, nk_jump=nj, pair_binding=pb,
                 Sminus_max=r.get("Sminus_max", np.nan))
    if np.isfinite(gx_c) and gx_c > 0.5 and (not np.isfinite(gx_1) or gx_1 > 0.5) and pf < 0.03 and (not np.isfinite(nj) or nj < 0.35):
        lab = "SMG insulator"
    elif np.isfinite(pf) and pf >= 0.05 and (not np.isfinite(nj) or nj < 0.9) and (not np.isfinite(gx_c) or gx_c < 0.5):
        lab = "SC (interlayer pairs)"
    elif np.isfinite(nj) and nj > 0.9 and (not np.isfinite(gx_c) or gx_c < 0.3):
        lab = "FL"
    else:
        lab = "crossover"
    return lab, feats


def main(L=4):
    rows = [r for r in json.load(open(os.path.join(ROOT, "data", "summary.json"))) if r["L"] == L and not r.get("tag")]
    labels = []
    colors = {"FL": "tab:blue", "SC (interlayer pairs)": "tab:green", "SMG insulator": "tab:red", "crossover": "tab:gray",
              "band insulator (ν=1, exact)": "k"}
    fig, ax = plt.subplots(figsize=(8, 5.8))
    for r in rows:
        lab, feats = classify(r)
        labels.append(dict(L=r["L"], nu=r["nu"], J=r["J"], label=lab, **{k: (None if not np.isfinite(v) else float(v)) for k, v in feats.items()}))
        ax.scatter(r["nu"], r["J"], c=colors[lab], s=150, marker="s", edgecolor="k", zorder=3)
    for J in (1, 2, 4, 8):
        ax.scatter(1.0, J, c="k", s=150, marker="s", edgecolor="k", zorder=3)
    # cuts
    ax.axvline(0.5, color="k", ls="--", lw=1); ax.axvline(0.25, color="k", ls="--", lw=1)
    ax.text(0.5, 8.9, "half-filling cut", ha="center", fontsize=8); ax.text(0.25, 8.9, "quarter-filling cut", ha="center", fontsize=8)
    for lab, c in colors.items():
        ax.scatter([], [], c=c, s=100, marker="s", edgecolor="k", label=lab)
    ax.set_xlabel("filling ν  (electrons per layer per spin per site)"); ax.set_ylabel("J / t1"); ax.set_xlim(0.0, 1.06); ax.set_ylim(0, 9.4)
    ax.set_title(f"phase diagram of the bilayer t1-t2-J model, {L}x{L} bilayer (VMC labels; t2 = 0.2)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(ROOT, "figures", f"phase_diagram_L{L}.png"), dpi=140)
    with open(os.path.join(ROOT, "data", "phase_labels.json"), "w") as f:
        json.dump(labels, f, indent=1)
    for l in labels:
        print(f"nu={l['nu']:.3f} J={l['J']:4.1f}: {l['label']:22s} gapexc_c={l['gap_excess_c']} gapexc_1={l['gap_excess_1']} pair_far={l['pair_far']} nk_jump={l['nk_jump']} Epb={l['pair_binding']}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 4)
