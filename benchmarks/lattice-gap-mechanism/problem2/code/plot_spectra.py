"""Spectra figure for the gapped phase at half filling at coupling J (argv[1]).
Panels: STM dI/dV, local spin spectrum (NMR/muSR), resistivity vs T.
Also writes data/spectra_J{J}.json with the curves and the gaps used."""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from spectra import bands, stm_spectrum, spin_spectrum, nmr_rate, resistivity, cluster_spectra, cluster_effective_levels, dos

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main(J, vmc_gaps=None):
    d = bands(J)
    om = np.linspace(-1.6 * J, 1.6 * J, 1200)
    eta = 0.12
    A, mu = stm_spectrum(d, om, eta)
    chi = spin_spectrum(d, om, eta)
    temps = np.linspace(0.05, 3.0, 120)
    sig_qp, sig_pair, mu_qp, mu_pair = resistivity(d, temps)
    rho = 1.0 / (sig_qp + sig_pair)
    t1 = nmr_rate(d, temps)
    # ED cluster cross-check
    cl = cluster_spectra(J, omegas=om, eta=eta)
    lv = cluster_effective_levels(J)

    fig, axs = plt.subplots(2, 2, figsize=(12, 8.5))
    ax = axs[0, 0]
    ax.plot(om, A, "k-", label="strong-coupling quasiparticle theory, 2D")
    Acl = cl["A_add"] + cl["A_rem"]
    # shift cluster spectrum so that its mid-gap sits at zero bias
    ax.plot(om - cl["mu"], Acl / max(Acl.max(), 1e-9) * A.max(), "r-", alpha=0.6, lw=1, label="exact 3x2 bilayer cluster (scaled)")
    g = d["gaps"]
    ax.axvspan(-g["single"] / 2, g["single"] / 2, color="gray", alpha=0.12)
    ax.axvline(-g["pair"], color="b", ls=":", lw=1); ax.axvline(g["pair"], color="b", ls=":", lw=1, label="two-particle (rung-pair) edge")
    ax.set_xlabel("bias  eV / t1"); ax.set_ylabel("dI/dV  ∝  A_loc(ω)   (arb.)"); ax.set_title(f"STM differential conductance, J={J}")
    ax.legend(fontsize=8)
    ax = axs[0, 1]
    ax.plot(om, chi, "k-", label="triplon band: χ''_loc(ω) = ¼ρ_T(ω), 2D")
    sm = cl["S_minus"]; ax.plot(om, sm / max(sm.max(), 1e-9) * chi.max(), "r-", alpha=0.6, lw=1, label="exact 3x2 cluster S₋(ω), scaled")
    ax.plot(om, cl["S_plus"] / max(sm.max(), 1e-9) * chi.max(), "g-", alpha=0.5, lw=1, label="exact 3x2 cluster S₊(ω) (layer-symmetric)")
    ax.set_xlim(0, 1.6 * J); ax.axvline(g["spin"], color="k", ls=":", lw=1)
    ax.set_xlabel("excitation energy ω / t1"); ax.set_ylabel("local spin spectral function (arb.)")
    ax.set_title("spin excitation spectrum entering 1/T1 and μSR"); ax.legend(fontsize=8)
    ax = axs[1, 0]
    ax.semilogy(temps, rho, "k-", label="ρ(T) = 1/(σ_qp + σ_pair)")
    ax.semilogy(temps, 1 / sig_qp, "b--", label="single-particle channel only")
    ax.semilogy(temps, 1 / sig_pair, "g--", label="rung-pair (2e boson) channel only")
    ax.set_xlabel("temperature T / t1"); ax.set_ylabel("resistivity  ρ  [ħ/(e²τ)]"); ax.set_title("resistivity, constant-τ Boltzmann")
    ax.legend(fontsize=8); ax.set_ylim(min(rho.min(), 1e-1) * 0.5, rho[temps > 0.2].max() * 2)
    ax = axs[1, 1]
    ax.semilogy(1 / temps[temps > 0.15], rho[temps > 0.15], "k-")
    ax.set_xlabel("1 / T"); ax.set_ylabel("ρ"); ax.set_title("Arrhenius plot")
    # fit slope at low T
    m = (temps > 0.2) & (temps < 0.6)
    p = np.polyfit(1 / temps[m], np.log(rho[m]), 1)
    ax.plot(1 / temps[m], np.exp(np.polyval(p, 1 / temps[m])), "r--", label=f"slope E_a = {p[0]:.2f} t1 (Δ2={g['pair']:.2f}, Δ1/2={g['single']/2:.2f})")
    ax.legend(fontsize=8)
    txt = (f"strong-coupling gaps (2D): Δ_spin={g['spin']:.2f}, Δ_1={g['single']:.2f}, Δ_2={g['pair']:.2f}\n"
           f"3x2 cluster ED: Δ_spin={cl['spin_gap']:.2f}, Δ_1={cl['gap1']:.2f}, Δ_2={cl['gap2']:.2f}; "
           f"effective-model on cluster: Δ_spin={lv['trip'].min():.2f}, Δ_1={lv['tri'].min()+lv['hol'].min():.2f}, Δ_2={lv['pair'].min():.2f}")
    if vmc_gaps:
        txt += "\nVMC 4x4: " + ", ".join(f"{k}={v[0]:.2f}±{v[1]:.2f}" for k, v in vmc_gaps.items())
    fig.suptitle(txt, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = os.path.join(ROOT, "figures", f"spectra_J{J:g}.png")
    fig.savefig(out, dpi=130)
    print("saved", out)
    with open(os.path.join(ROOT, "data", f"spectra_J{J:g}.json"), "w") as f:
        json.dump(dict(J=J, omegas=om.tolist(), A_stm=A.tolist(), chi_loc=chi.tolist(), temps=temps.tolist(),
                       rho=rho.tolist(), sigma_qp=sig_qp.tolist(), sigma_pair=sig_pair.tolist(), nmr_rate=t1.tolist(),
                       gaps_sc=g, cluster=dict(gap1=cl["gap1"], gap2=cl["gap2"], spin_gap=cl["spin_gap"], mu=cl["mu"]),
                       arrhenius_slope=float(p[0]), bands=dict(trip=dict(e0=d["trip"]["e0"], hop1=d["trip"]["hop1"], hop2=d["trip"]["hop2"]),
                                                                tri=dict(e0=d["tri"]["e0"], hop1=d["tri"]["hop1"], hop2=d["tri"]["hop2"]),
                                                                hol=dict(e0=d["hol"]["e0"], hop1=d["hol"]["hop1"], hop2=d["hol"]["hop2"]),
                                                                pair=dict(e0=d["pair_hole"]["e0"], t_b1=d["pair_hole"]["t_b1"], t_b2=d["pair_hole"]["t_b2"], V1=d["pair_hole"]["V1"]))), f)
    print(txt)


if __name__ == "__main__":
    J = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
    vmc = None
    try:
        rows = json.load(open(os.path.join(ROOT, "data", "summary.json")))
        r = [r for r in rows if r["L"] == 4 and abs(r["nu"] - 0.5) < 1e-6 and abs(r["J"] - J) < 1e-9 and not r.get("tag")]
        if r:
            r = r[0]
            vmc = {k: (r[v], r[v + "_err"]) for k, v in (("Δ_spin", "spin_gap"), ("Δ_1", "charge_gap1"), ("Δ_2", "charge_gap2")) if v in r}
    except Exception as e:
        print("no VMC gaps:", e)
    main(J, vmc)
