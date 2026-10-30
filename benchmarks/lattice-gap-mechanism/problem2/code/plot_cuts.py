"""Figures for the line cuts: energy, gaps, correlators vs J; n(k) maps; S(q) maps.
Usage: python code/plot_cuts.py [L] [nu]"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strong_coupling import lattice_dispersions
from model import Lattice, dispersion
from pt2_fl import pt2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")


def load(L, nu, tag=""):
    rows = json.load(open(os.path.join(ROOT, "data", "summary.json")))
    rows = [r for r in rows if r["L"] == L and abs(r["nu"] - nu) < 1e-6 and r.get("tag", "") == tag]
    return sorted(rows, key=lambda r: r["J"])


def plot_cut(L, nu, tag=""):
    rows = load(L, nu, tag)
    if not rows:
        print("no rows")
        return
    J = np.array([r["J"] for r in rows])
    fig, axs = plt.subplots(2, 3, figsize=(14, 8))
    ax = axs[0, 0]
    E = np.array([r["E_site"] for r in rows]); Ee = np.array([r["E_site_err"] for r in rows])
    ax.errorbar(J, E, Ee, fmt="o-", label=f"VMC L={L}")
    for s, mk in (("gs_fl", "^"), ("gs_sg", "v")):
        es = [(r["J"], r["inits"][s][0]) for r in rows if s in r["inits"]]
        if es:
            ax.plot([e[0] for e in es], [e[1] for e in es], mk, ms=4, alpha=0.5, label=f"init {s}")
    e_free = exact_fl(L, rows[0]["bc"], nu)
    Jw = np.linspace(0, min(3.0, max(J)), 30)
    ax.plot(Jw, [e_free + pt2(L, rows[0]["bc"], nu, j) for j in Jw], "b--", lw=1, label="FL + exact 2nd-order PT (same cluster)")
    ax.axhline(e_free, color="k", ls=":", lw=0.8, label="free band (J=0)")
    if abs(nu - 0.5) < 1e-6:
        Jf = np.linspace(3, max(J), 50)
        ax.plot(Jf, [lattice_dispersions(j, 1.0, 0.2, 8, 8)["e_gs_per_site"] for j in Jf], "k--", label="rung-singlet + O(t²/J)")
    ax.set_xlabel("J/t1"); ax.set_ylabel("E / site"); ax.legend(fontsize=8); ax.set_title(f"nu={nu}: energy")

    ax = axs[0, 1]
    for key, lab in (("spin_gap", "spin gap Δs"), ("charge_gap2", "2-particle gap Δc2"), ("charge_gap1", "1-particle gap Δc1")):
        y = np.array([r.get(key, np.nan) for r in rows]); ye = np.array([r.get(key + "_err", 0) for r in rows])
        ax.errorbar(J, y, ye, fmt="o-", label=lab)
        ax.axhline(rows[0][key + "_free"], ls=":", color="gray")
    ax.plot(J, 0.75 * J, "k--", lw=0.8, label="3J/4")
    ax.set_xlabel("J/t1"); ax.set_ylabel("gap / t1"); ax.legend(fontsize=8); ax.set_title("gaps (dotted: J=0 finite-size values)")

    ax = axs[0, 2]
    y = np.array([r.get("pair_binding", np.nan) for r in rows]); ye = np.array([r.get("pair_binding_err", 0) for r in rows])
    ax.errorbar(J, y, ye, fmt="o-", label="E(N+2)+E(N)-2E(N+1)")
    y = np.array([r.get("pair_binding_h", np.nan) for r in rows]); ye = np.array([r.get("pair_binding_h_err", 0) for r in rows])
    ax.errorbar(J, y, ye, fmt="s-", label="E(N-2)+E(N)-2E(N-1)")
    ax.axhline(rows[0].get("pair_binding_free", 0), ls=":", color="gray"); ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("J/t1"); ax.set_ylabel("pair binding / t1"); ax.legend(fontsize=8); ax.set_title("pair binding (<0: bound pairs)")

    ax = axs[1, 0]
    y = np.array([r["rung_SS"][0] for r in rows]); ye = np.array([r["rung_SS"][1] for r in rows])
    ax.errorbar(J, y, ye, fmt="o-", label="<S_i1·S_i2>")
    y = np.array([r["docc"][0] for r in rows]); ax.plot(J, y, "s-", label="double occupancy")
    y = np.array([r.get("nk_jump", np.nan) for r in rows]); ye = np.array([r.get("nk_jump_err", 0) for r in rows])
    ax.errorbar(J, y, ye, fmt="^-", label="n(k) jump across FS")
    ax.axhline(-0.75, ls=":", color="gray"); ax.set_xlabel("J/t1"); ax.legend(fontsize=8); ax.set_title("local correlators / Fermi-surface jump")

    ax = axs[1, 1]
    for key, lab in (("Sminus_max", "max_q S₋(q) (layer-antisym.)"), ("Splus_max", "max_q S₊(q) (layer-sym.)"), ("S11_max", "max_q S₁₁(q)")):
        y = np.array([r.get(key, np.nan) for r in rows]); ax.plot(J, y, "o-", label=lab)
    ax.set_xlabel("J/t1"); ax.set_ylabel("S(q)"); ax.legend(fontsize=8); ax.set_title("spin structure factor maxima (per site)")

    ax = axs[1, 2]
    y = np.array([r["pair_far_avg"][0] for r in rows]); ye = np.array([r["pair_far_avg"][1] for r in rows])
    ax.errorbar(J, y, ye, fmt="o-", label="P(|r|≥2) interlayer singlet pair")
    y = np.array([r["pair_max_dist"][0] for r in rows]); ye = np.array([r["pair_max_dist"][1] for r in rows])
    ax.errorbar(J, y, ye, fmt="s-", label=f"P(L/2,L/2)")
    y = np.array([r["pair_onsite"][0] for r in rows]); ax.plot(J, y / 10, "^-", label="P(0)/10")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel("J/t1"); ax.set_ylabel("pair correlation"); ax.legend(fontsize=8); ax.set_title("interlayer pair correlations")
    fig.suptitle(f"Bilayer t1-t2-J, L={L}x{L} bc={rows[0]['bc']}, nu={nu}")
    fig.tight_layout()
    out = os.path.join(FIG, f"cut_L{L}_nu{nu:.3f}{tag}.png")
    fig.savefig(out, dpi=130)
    print("saved", out)

    # n(k) maps
    fig, axs = plt.subplots(1, len(rows), figsize=(2.6 * len(rows), 3))
    axs = np.atleast_1d(axs)
    for ax, r in zip(axs, rows):
        ks = np.array(r["ks"]); nk = np.array(r["nk"])
        sc = ax.scatter(ks[:, 0] / np.pi, ks[:, 1] / np.pi, c=nk, cmap="viridis", vmin=0, vmax=1, s=120, marker="s")
        for k, v in zip(ks, nk):
            ax.text(k[0] / np.pi, k[1] / np.pi, f"{v:.2f}", ha="center", va="center", fontsize=6, color="w")
        ax.set_title(f"J={r['J']}", fontsize=9); ax.set_xlabel("kx/π"); ax.set_aspect("equal")
    axs[0].set_ylabel("ky/π")
    fig.suptitle(f"momentum distribution n(k), L={L}, nu={nu}")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"nk_L{L}_nu{nu:.3f}{tag}.png"), dpi=130)

    # S(q) maps (layer antisymmetric)
    fig, axs = plt.subplots(2, len(rows), figsize=(2.6 * len(rows), 5.5))
    axs = np.atleast_2d(axs)
    for i, r in enumerate(rows):
        ks = np.array(r.get("qs", r["ks"]))
        for row, key in ((0, "Sminus"), (1, "Splus")):
            ax = axs[row, i]
            S = np.array(r[key])
            ax.scatter(ks[:, 0] / np.pi, ks[:, 1] / np.pi, c=S, cmap="magma", s=120, marker="s")
            for k, v in zip(ks, S):
                ax.text(k[0] / np.pi, k[1] / np.pi, f"{v:.2f}", ha="center", va="center", fontsize=6, color="c")
            ax.set_title(f"{key} J={r['J']}", fontsize=8); ax.set_aspect("equal")
    fig.suptitle(f"spin structure factors S₋(q) (top), S₊(q) (bottom), L={L}, nu={nu}")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"Sq_L{L}_nu{nu:.3f}{tag}.png"), dpi=130)


def exact_fl(L, bc, nu):
    lat = Lattice(L, L, bc)
    ks = lat.kpoints()
    eps = np.sort(dispersion(ks[:, 0], ks[:, 1]))
    n = int(round(nu * lat.n_cell))
    return 4 * eps[:n].sum() / lat.n_cell


if __name__ == "__main__":
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    nu = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    plot_cut(L, nu)
