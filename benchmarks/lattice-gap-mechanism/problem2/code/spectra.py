"""Spectra of the gapped (rung-singlet) phase at half filling.

Approximation (stated in the report): strong-coupling quasiparticle theory.
The gapped state is the interlayer-singlet product dressed by hopping; its
elementary excitations are
  * trion  (3-electron rung)  : electron addition,  band eps_e(k), weight 1/2
  * holon  (1-electron rung)  : electron removal,   band eps_h(k), weight 1/2
  * triplon (rung triplet)    : spin excitation,    band  w_T(q),  weight 1
  * rung pairs (0- or 4-electron rung): charge-2e carriers, band E_b(k)
Effective amplitudes are extracted exactly from two-rung diagonalization
(strong_coupling.py) and combined by bond additivity.  The overall gap scale is
cross-checked against the VMC gaps.
  STM   : dI/dV(V) ~ A_loc(eV) = (1/2)[rho_e(w) + rho_h(-w)]  (plus the two-particle edge)
  NMR   : chi''_loc(w) = (1/4) rho_T(w) ; 1/T1 ~ int rho_T^2 n_B (1+n_B)
  rho(T): Boltzmann transport, constant relaxation time, intrinsic activation
          over the single-particle (Delta_1) and pair (Delta_2) channels.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strong_coupling import lattice_dispersions, pair_boson_parameters, two_rung_amplitudes, signed_amplitudes
from model import Lattice, hamiltonian_terms, spin_ops
from ed import Sector, build_operator, ground_state, lanczos_spectral, apply_term


def bands(J, t1=1.0, t2=0.2, L=96):
    d = lattice_dispersions(J, t1, t2, Lx=L, Ly=L)
    # rung-pair boson band: e_b(k) = 3J/4 + z1 d_se1 + z2 d_se2 - 2 t_b1 (cos kx + cos ky) - 2 t_b2 (cos(kx+ky)+cos(kx-ky))
    p1 = pair_boson_parameters(J, t1)
    p2 = pair_boson_parameters(J, t2)
    kx = d["trip"]["kx"]
    KX, KY = np.meshgrid(kx, kx, indexing="ij")
    for name in ("hole", "elec"):
        e0 = 0.75 * J + 4 * p1[name]["d_se"] + 4 * p2[name]["d_se"]
        # bosonic pair hops with a positive-definite kinetic energy (symmetric combination lowest)
        eb = e0 - 2 * p1[name]["t_b"] * (np.cos(KX) + np.cos(KY)) - 2 * p2[name]["t_b"] * (np.cos(KX + KY) + np.cos(KX - KY))
        d["pair_" + name] = dict(e0=e0, disp=eb, t_b1=p1[name]["t_b"], t_b2=p2[name]["t_b"], V1=p1[name]["V"], V2=p2[name]["V"])
    d["gaps"] = dict(
        spin=float(d["trip"]["disp"].min()),
        single=float(d["tri"]["disp"].min() + d["hol"]["disp"].min()),
        pair=float(0.5 * (d["pair_hole"]["disp"].min() + d["pair_elec"]["disp"].min())),
        trion_min=float(d["tri"]["disp"].min()), holon_min=float(d["hol"]["disp"].min()),
    )
    return d


def dos(disp, omegas, eta):
    e = disp.ravel()
    out = np.zeros(len(omegas))
    for x in e:
        out += eta / np.pi / ((omegas - x) ** 2 + eta ** 2)
    return out / len(e)


def stm_spectrum(d, omegas, eta=0.1):
    """A_loc(w) per (layer,spin) orbital with mu at mid-gap."""
    eps_e, eps_h = d["tri"]["disp"], d["hol"]["disp"]
    mu = 0.5 * (eps_e.min() - eps_h.min())
    A = 0.5 * dos(eps_e - mu, omegas, eta) + 0.5 * dos(-(eps_h - mu), omegas, eta)
    return A, mu


def spin_spectrum(d, omegas, eta=0.1):
    return 0.25 * dos(d["trip"]["disp"], omegas, eta)


def nmr_rate(d, temps):
    """1/T1 ~ sum_{q,q'} n_B(w_q)[1+n_B(w_q')] delta(w_q - w_q')  (intraband triplon scattering),
    evaluated with a small energy window; returned normalized to its value at the highest T."""
    w = d["trip"]["disp"].ravel()
    hist, edges = np.histogram(w, bins=200)
    centers = 0.5 * (edges[1:] + edges[:-1])
    rho = hist / len(w) / (edges[1] - edges[0])
    out = []
    for T in temps:
        nb = 1.0 / np.expm1(centers / T)
        out.append(np.sum(rho ** 2 * nb * (1 + nb)) * (edges[1] - edges[0]))
    out = np.array(out)
    return out


def fermi_deriv(x):
    # -df/dx for f = 1/(e^x+1)
    x = np.clip(x, -300, 300)
    return 0.25 / np.cosh(0.5 * x) ** 2


def resistivity(d, temps, t1=1.0, t2=0.2):
    """Boltzmann conductivity (constant tau, units e^2 tau / hbar per site) from
    (i) trion/holon quasiparticles (charge e) and (ii) rung-pair bosons (charge 2e,
    treated as a dilute Boltzmann gas).  The chemical potential sits at mid gap
    (intrinsic, particle-hole balanced within each channel)."""
    kx = d["trip"]["kx"]
    dk = kx[1] - kx[0]
    KX, KY = np.meshgrid(kx, kx, indexing="ij")
    out = {}
    for name in ("tri", "hol", "pair_elec", "pair_hole"):
        disp = d[name]["disp"]
        vx = np.gradient(disp, dk, axis=0)
        vy = np.gradient(disp, dk, axis=1)
        d[name]["v2"] = 0.5 * (vx ** 2 + vy ** 2)
    mu_qp = 0.5 * (d["tri"]["disp"].min() - d["hol"]["disp"].min())
    mu_pair = 0.5 * (d["pair_elec"]["disp"].min() - d["pair_hole"]["disp"].min())
    sig_qp, sig_pair = [], []
    for T in temps:
        s = 0.0
        for name, sign in (("tri", +1), ("hol", -1)):
            x = (d[name]["disp"] - sign * mu_qp) / T  # energies measured from mid-gap
            s += np.mean(d[name]["v2"] * fermi_deriv(x)) / T
        sig_qp.append(s)
        s = 0.0
        for name, sign in (("pair_elec", +1), ("pair_hole", -1)):
            x = (d[name]["disp"] - sign * mu_pair) / T
            s += 4.0 * np.mean(d[name]["v2"] * np.exp(-x)) / T  # charge 2e -> factor 4, Boltzmann gas
        sig_pair.append(s)
    sig_qp, sig_pair = np.array(sig_qp), np.array(sig_pair)
    return sig_qp, sig_pair, mu_qp, mu_pair


# ---------------------------------------------------------------------------
# Exact cluster cross-check (3x2 open bilayer): LDOS and local spin spectrum
# ---------------------------------------------------------------------------
def cluster_spectra(J, Lx=3, Ly=2, omegas=None, eta=0.15, t1=1.0, t2=0.2, n_lanczos=150, site=None):
    lat = Lattice(Lx, Ly, "oo")
    nc = lat.n_cell
    terms = hamiltonian_terms(lat, J, t1, t2)
    sec0 = Sector(lat, nc, nc, nc, nc)
    H0 = build_operator(sec0, sec0, terms)
    w0, v0 = ground_state(H0, k=1)
    E0, psi0 = w0[0], v0[:, 0]
    if site is None:
        site = 0
    if omegas is None:
        omegas = np.linspace(-1.5 * J, 1.5 * J, 600)
    res = dict(E0=E0, omegas=omegas, site=site)
    # electron addition (layer 0, up) : c+ psi0 lives in (nc+1, nc, nc+1, nc)
    secp = Sector(lat, nc + 1, nc, nc + 1, nc)
    Hp = build_operator(secp, secp, terms)
    cdag = build_operator(secp, sec0, [(1.0, ((lat.mode(0, site, 1), 1),))])
    phi = cdag @ psi0
    Ap = lanczos_spectral(Hp, E0, phi, omegas, eta, n_lanczos, sign=+1)
    secm = Sector(lat, nc - 1, nc, nc - 1, nc)  # removed an up electron from layer 0
    Hm = build_operator(secm, secm, terms)
    c = build_operator(secm, sec0, [(1.0, ((lat.mode(0, site, 1), 0),))])
    phi = c @ psi0
    Am = lanczos_spectral(Hm, E0, phi, omegas, eta, n_lanczos, sign=-1)
    # chemical potential at mid gap: find edges from the single-particle energies
    Ep = ground_state(Hp, k=1)[0][0]
    Em = ground_state(Hm, k=1)[0][0]
    res["gap1"] = Ep + Em - 2 * E0
    res["mu"] = 0.5 * ((Ep - E0) - (Em - E0))
    res["A_add"], res["A_rem"] = Ap, Am
    # local spin spectrum: S^z_{site,layer0} - S^z_{site,layer1}  (antisymmetric) and symmetric
    sz0, _, _ = spin_ops(lat, 0, site)
    sz1, _, _ = spin_ops(lat, 1, site)
    Sm = build_operator(sec0, sec0, sz0 + [(-c_, o) for (c_, o) in sz1])
    Sp = build_operator(sec0, sec0, sz0 + sz1)
    res["S_minus"] = lanczos_spectral(H0, E0, Sm @ psi0, omegas, eta, n_lanczos, sign=+1)
    res["S_plus"] = lanczos_spectral(H0, E0, Sp @ psi0, omegas, eta, n_lanczos, sign=+1)
    # spin gap and 2-particle gap on the cluster
    sec1 = Sector(lat, nc, nc, nc + 1, nc - 1)
    H1 = build_operator(sec1, sec1, terms)
    res["spin_gap"] = ground_state(H1, k=1)[0][0] - E0
    secp2 = Sector(lat, nc + 1, nc + 1, nc + 1, nc + 1)
    secm2 = Sector(lat, nc - 1, nc - 1, nc - 1, nc - 1)
    Ep2 = ground_state(build_operator(secp2, secp2, terms), k=1)[0][0]
    Em2 = ground_state(build_operator(secm2, secm2, terms), k=1)[0][0]
    res["gap2"] = 0.5 * (Ep2 + Em2 - 2 * E0)
    return res


def cluster_effective_levels(J, Lx=3, Ly=2, t1=1.0, t2=0.2):
    """Strong-coupling tight-binding levels of holon/trion/triplon and of the charge-2e rung pair
    on the same open cluster (bond additivity with the cluster's actual bonds)."""
    lat = Lattice(Lx, Ly, "oo")
    nc = lat.n_cell
    a1, a2 = two_rung_amplitudes(J, t1), two_rung_amplitudes(J, t2)
    p1, p2 = signed_amplitudes(J, t1), signed_amplitudes(J, t2)
    out = {}
    # rung-pair boson (hole pair = empty rung): e0 = 3J/4 + sum_bonds d_se, hopping -t_b
    b1, b2 = pair_boson_parameters(J, t1), pair_boson_parameters(J, t2)
    hb = np.zeros((nc, nc))
    for (bonds, b) in ((lat.nn_bonds, b1), (lat.nnn_bonds, b2)):
        for (i, j, ph) in bonds:
            hb[i, i] += b["hole"]["d_se"]
            hb[j, j] += b["hole"]["d_se"]
            hb[i, j] -= b["hole"]["t_b"]
            hb[j, i] -= b["hole"]["t_b"]
    hb += 0.75 * J * np.eye(nc)
    out["pair"] = np.linalg.eigvalsh(hb)
    for name, base in (("trip", J), ("hol", 0.75 * J), ("tri", 0.75 * J)):
        h = np.zeros((nc, nc))
        for (bonds, a, p) in ((lat.nn_bonds, a1, p1), (lat.nnn_bonds, a2, p2)):
            c, hop = a[name]
            s = -1.0 if p[name] > 0 else 1.0
            for (i, j, ph) in bonds:
                h[i, i] += c - base
                h[j, j] += c - base
                h[i, j] += s * hop
                h[j, i] += s * hop
        h += base * np.eye(nc)
        out[name] = np.linalg.eigvalsh(h)
    return out


if __name__ == "__main__":
    import json
    J = float(sys.argv[1]) if len(sys.argv) > 1 else 8.0
    d = bands(J)
    print(f"J={J}: strong-coupling gaps: spin={d['gaps']['spin']:.3f} single-particle={d['gaps']['single']:.3f} "
          f"pair={d['gaps']['pair']:.3f}  (trion min {d['gaps']['trion_min']:.3f}, holon min {d['gaps']['holon_min']:.3f})")
    print(f"   triplon: e0={d['trip']['e0']:.3f} hop1={d['trip']['hop1']:+.4f} hop2={d['trip']['hop2']:+.4f}; "
          f"trion: e0={d['tri']['e0']:.3f} hop1={d['tri']['hop1']:+.4f} hop2={d['tri']['hop2']:+.4f}; "
          f"holon: e0={d['hol']['e0']:.3f} hop1={d['hol']['hop1']:+.4f} hop2={d['hol']['hop2']:+.4f}")
    print(f"   pair boson: t_b1={d['pair_hole']['t_b1']:.4f} t_b2={d['pair_hole']['t_b2']:.4f} V1={d['pair_hole']['V1']:+.4f} e0={d['pair_hole']['e0']:.3f}")
    print(f"   E_gs/site (2nd order) = {d['e_gs_per_site']:.4f}")
    r = cluster_spectra(J)
    lv = cluster_effective_levels(J)
    print(f"3x2 open cluster ED at J={J}: gap1={r['gap1']:.3f} gap2={r['gap2']:.3f} spin_gap={r['spin_gap']:.3f}")
    print(f"   effective tight-binding levels: trion {np.round(lv['tri'],3)}")
    print(f"                                   holon {np.round(lv['hol'],3)}")
    print(f"                                   triplon {np.round(lv['trip'],3)}")
    print(f"   => effective gap1 = {lv['tri'].min()+lv['hol'].min():.3f}, spin gap = {lv['trip'].min():.3f}, pair gap (2-particle) = {lv['pair'].min():.3f}")
