"""Collect run JSONs into per-point diagnostics.

For each (L, bc, nu, J):
  E_gs (min over inits, with metastability info), spin gap, 2-particle and
  1-particle charge gaps, pair binding, S(q) (layer-symmetric/antisymmetric),
  n(k), interlayer pair correlation, rung singlet correlation, double occupancy.
Writes data/summary.json and prints a table.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import Lattice, dispersion, free_energy_sector
from vmc import fourier_disp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r"L(\d+)_(\w\w)_nu([\d.]+)_J([\d.]+)(_x\w+)?_(gs_fl|gs_sg|gs_bcs|sz1_0|sz1_pp|sz1_p0|sz1_trip|p2|m2|p1|m1)\.json$")


def load_all():
    pts = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "L*_nu*_J*.json"))):
        m = PAT.search(os.path.basename(f))
        if not m:
            continue
        L, bc, nu, J, tag, sec = int(m[1]), m[2], float(m[3]), float(m[4]), (m[5] or ""), m[6]
        key = (L, bc, nu, J, tag)
        with open(f) as fh:
            pts.setdefault(key, {})[sec] = json.load(fh)
    return pts


def exact_free(L, bc, nu):
    """Exact J=0 energies of the sectors (per layer counts n, n+-1, Sz=1)."""
    lat = Lattice(L, L, bc)
    nc = lat.n_cell
    n = int(round(2 * nu * nc))
    ks = lat.kpoints()
    eps = np.sort(dispersion(ks[:, 0], ks[:, 1]))

    def E(nu_, nd_, n1, n2):
        # layers independent: fill lowest levels per (layer, spin); any split of Nup among layers;
        # minimum over the distribution (nonpolarized within each layer as far as possible)
        best = np.inf
        for n1u in range(0, nc + 1):
            n1d = n1 - n1u
            n2u = nu_ - n1u
            n2d = n2 - n2u
            if min(n1d, n2u, n2d) < 0 or max(n1u, n1d, n2u, n2d) > nc:
                continue
            e = sum(eps[:k].sum() for k in (n1u, n1d, n2u, n2d))
            best = min(best, e)
        return best

    out = dict(gs=E(n, n, n, n), sz1=E(n + 1, n - 1, n, n), p2=E(n + 1, n + 1, n + 1, n + 1),
               m2=E(n - 1, n - 1, n - 1, n - 1), p1=E(n + 1, n, n + 1, n), m1=E(n, n - 1, n, n - 1))
    out["spin_gap"] = out["sz1"] - out["gs"]
    out["charge_gap2"] = 0.5 * (out["p2"] + out["m2"] - 2 * out["gs"])
    out["charge_gap1"] = out["p1"] + out["m1"] - 2 * out["gs"]
    out["energy_per_site"] = out["gs"] / nc
    # n(k) of the free state (per layer per spin)
    occ = np.zeros(len(ks))
    order = np.argsort(dispersion(ks[:, 0], ks[:, 1]))
    occ[order[:n // 2]] = 1.0 if n % 2 == 0 else 1.0
    return out, ks, occ


def summarize(pts):
    rows = []
    for key in sorted(pts):
        L, bc, nu, J, tag = key
        d = pts[key]
        lat = Lattice(L, L, bc)
        nc = lat.n_cell
        ex, ks, occ0 = exact_free(L, bc, nu)
        row = dict(L=L, bc=bc, nu=nu, J=J, tag=tag, nc=nc)
        # ground state: min over inits
        gs_cands = {s: d[s] for s in ("gs_fl", "gs_sg", "gs_bcs") if s in d}
        if not gs_cands:
            continue
        best = min(gs_cands, key=lambda s: gs_cands[s]["energy"])
        g = gs_cands[best]
        row["gs_init"] = best
        row["E"] = g["energy"]
        row["E_err"] = g["energy_err"]
        row["E_site"] = g["energy_per_site"]
        row["E_site_err"] = g["energy_per_site_err"]
        row["E_var_site"] = g["energy_var"] / nc
        row["inits"] = {s: [v["energy_per_site"], v["energy_per_site_err"]] for s, v in gs_cands.items()}
        if len(gs_cands) > 1:
            es = sorted(v["energy_per_site"] for v in gs_cands.values())
            row["init_split_site"] = es[1] - es[0]

        def E_of(s):
            return (d[s]["energy"], d[s]["energy_err"]) if s in d else (None, None)

        # spin gap
        cands = [E_of(s) for s in ("sz1_0", "sz1_pp", "sz1_p0", "sz1_trip") if s in d]
        if cands:
            e1, er1 = min(cands, key=lambda x: x[0])
            row["spin_gap"] = e1 - row["E"]
            row["spin_gap_err"] = float(np.hypot(er1, row["E_err"]))
            row["sz1_q"] = {s: [d[s]["energy"] - row["E"], float(np.hypot(d[s]["energy_err"], row["E_err"]))]
                            for s in ("sz1_0", "sz1_pp", "sz1_p0", "sz1_trip") if s in d}
        row["spin_gap_free"] = ex["spin_gap"]
        # charge gaps
        if "p2" in d and "m2" in d:
            row["charge_gap2"] = 0.5 * (d["p2"]["energy"] + d["m2"]["energy"] - 2 * row["E"])
            row["charge_gap2_err"] = 0.5 * float(np.sqrt(d["p2"]["energy_err"] ** 2 + d["m2"]["energy_err"] ** 2 + 4 * row["E_err"] ** 2))
        row["charge_gap2_free"] = ex["charge_gap2"]
        if "p1" in d and "m1" in d:
            row["charge_gap1"] = d["p1"]["energy"] + d["m1"]["energy"] - 2 * row["E"]
            row["charge_gap1_err"] = float(np.sqrt(d["p1"]["energy_err"] ** 2 + d["m1"]["energy_err"] ** 2 + 4 * row["E_err"] ** 2))
        row["charge_gap1_free"] = ex["charge_gap1"]
        if "p2" in d and "p1" in d:
            # pair binding energy: E(N+2) + E(N) - 2 E(N+1)  (<0: bound pairs)
            row["pair_binding"] = d["p2"]["energy"] + row["E"] - 2 * d["p1"]["energy"]
            row["pair_binding_err"] = float(np.sqrt(d["p2"]["energy_err"] ** 2 + row["E_err"] ** 2 + 4 * d["p1"]["energy_err"] ** 2))
            row["pair_binding_free"] = ex["p2"] + ex["gs"] - 2 * ex["p1"]
        if "m2" in d and "m1" in d:
            row["pair_binding_h"] = d["m2"]["energy"] + row["E"] - 2 * d["m1"]["energy"]
            row["pair_binding_h_err"] = float(np.sqrt(d["m2"]["energy_err"] ** 2 + row["E_err"] ** 2 + 4 * d["m1"]["energy_err"] ** 2))
            row["pair_binding_h_free"] = ex["m2"] + ex["gs"] - 2 * ex["m1"]
        # observables
        obs = g.get("obs", {})
        vals = {k: (v[0], v[1]) for k, v in obs.items()}
        # two-body correlators (spin, density, pairs) are periodic: use the untwisted momenta q = 2 pi n / L
        qs = np.array([(2 * np.pi * nx / lat.Lx, 2 * np.pi * ny / lat.Ly) for nx in range(lat.Lx) for ny in range(lat.Ly)])
        iQ = int(np.argmin(np.abs(qs[:, 0] - np.pi) + np.abs(qs[:, 1] - np.pi)))
        iq0 = 0
        # layer / spin symmetry fill-in for the 'lite' measurement sets
        for k in list(vals):
            if k.startswith("s11_") and ("s22_" + k[4:]) not in vals:
                vals["s22_" + k[4:]] = vals[k]
            if k.startswith("g1u_") and ("g1d_" + k[4:]) not in vals:
                vals["g1d_" + k[4:]] = vals[k]
        if "s12_0_0" in vals:
            row["rung_SS"] = vals["s12_0_0"]
            row["docc"] = vals.get("docc1", (None, None))
            row["n1n2"] = vals.get("n1n2", (None, None))
            # structure factors: S_pm(q) = FT[C11 + C22 +- 2 C12]
            s11, e11 = fourier_disp(lat, vals, "s11", qs)
            s22, e22 = fourier_disp(lat, vals, "s22", qs)
            s12, e12 = fourier_disp(lat, vals, "s12", qs)
            Splus = (s11 + s22 + 2 * s12).real
            Sminus = (s11 + s22 - 2 * s12).real
            row["ks"] = ks.tolist()
            row["qs"] = qs.tolist()
            row["Sminus_pipi"] = float(Sminus[iQ])
            row["Splus_pipi"] = float(Splus[iQ])
            row["S11_pipi"] = float(s11.real[iQ])
            row["S_pipi_err"] = float(np.sqrt(e11[iQ] ** 2 + e22[iQ] ** 2 + 4 * e12[iQ] ** 2))
            row["S11"] = s11.real.tolist()
            row["S11_err"] = e11.tolist()
            row["Splus"] = Splus.tolist()
            row["Sminus"] = Sminus.tolist()
            row["S_err"] = np.sqrt(e11 ** 2 + e22 ** 2 + 4 * e12 ** 2).tolist()
            row["Sminus_max"] = float(np.max(Sminus))
            row["Sminus_max_q"] = qs[int(np.argmax(Sminus))].tolist()
            row["Splus_max"] = float(np.max(Splus))
            row["Splus_max_q"] = qs[int(np.argmax(Splus))].tolist()
            row["S11_max"] = float(np.max(s11.real))
            row["S11_max_q"] = qs[int(np.argmax(s11.real))].tolist()
        if "g1u_0_0" in vals:
            nk_u, enk = fourier_disp(lat, vals, "g1u", ks)
            nk_d, enkd = fourier_disp(lat, vals, "g1d", ks)
            nk = 0.5 * (nk_u + nk_d).real
            row["nk"] = nk.tolist()
            row["nk_err"] = (0.5 * np.sqrt(enk ** 2 + enkd ** 2)).tolist()
            row["nk_free"] = occ0.tolist()
            # Fermi-surface discontinuity: mean n(k) inside minus outside the J=0 Fermi sea
            inside = occ0 > 0.5
            if inside.any() and (~inside).any():
                # restrict to the shells adjacent to the Fermi level
                eps = dispersion(ks[:, 0], ks[:, 1])
                e_in = eps[inside].max()
                e_out = eps[~inside].min()
                sh_in = inside & (np.abs(eps - e_in) < 1e-6)
                sh_out = (~inside) & (np.abs(eps - e_out) < 1e-6)
                row["nk_jump"] = float(nk[sh_in].mean() - nk[sh_out].mean())
                row["nk_jump_err"] = float(np.hypot(np.sqrt(np.mean(np.array(row["nk_err"])[sh_in] ** 2)) / np.sqrt(sh_in.sum()),
                                                    np.sqrt(np.mean(np.array(row["nk_err"])[sh_out] ** 2)) / np.sqrt(sh_out.sum())))
                row["nk_in_shell"] = float(nk[sh_in].mean())
                row["nk_out_shell"] = float(nk[sh_out].mean())
        if "d11_0_0" in vals:
            # charge structure factor of the rung density n_i = n_i1 + n_i2:
            # N(q) = (1/Nc) sum_ij e^{iq(ri-rj)} (<n_i n_j> - <n_i><n_j>),  <n_i n_j> = d11 + d22 + 2 d12 (d22 = d11 by layer symmetry)
            nbar = 4 * nu  # electrons per rung
            d11, e11 = fourier_disp(lat, vals, "d11", qs)
            d12, e12 = fourier_disp(lat, vals, "d12", qs)
            Nq = (2 * d11 + 2 * d12).real
            Nq_conn = Nq.copy()
            Nq_conn[iq0] -= nc * nbar ** 2
            row["Nq"] = Nq_conn.tolist()
            row["Nq_err"] = np.sqrt(4 * e11 ** 2 + 4 * e12 ** 2).tolist()
            far = [i for i in range(len(qs)) if i != iq0]
            row["Nq_max"] = float(np.max(Nq_conn[far]))
            row["Nq_max_q"] = qs[far][int(np.argmax(Nq_conn[far]))].tolist()
            row["Nq_pipi"] = float(Nq_conn[iQ])
            # layer-antisymmetric density (interlayer charge imbalance) structure factor
            row["Nq_minus_max"] = float(np.max((2 * d11 - 2 * d12).real[far]))
            row["Nq_minus_pipi"] = float((2 * d11 - 2 * d12).real[iQ])
        if "pair_0_0" in vals:
            P = np.zeros((lat.Lx, lat.Ly))
            Pe = np.zeros((lat.Lx, lat.Ly))
            for dx in range(lat.Lx):
                for dy in range(lat.Ly):
                    P[dx, dy], Pe[dx, dy] = vals[f"pair_{dx}_{dy}"]
            row["pair_onsite"] = [float(P[0, 0]), float(Pe[0, 0])]
            row["pair_max_dist"] = [float(P[lat.Lx // 2, lat.Ly // 2]), float(Pe[lat.Lx // 2, lat.Ly // 2])]
            far = [(dx, dy) for dx in range(lat.Lx) for dy in range(lat.Ly)
                   if min(dx, lat.Lx - dx) ** 2 + min(dy, lat.Ly - dy) ** 2 >= 4]
            row["pair_far_avg"] = [float(np.mean([P[a] for a in far])), float(np.sqrt(np.mean([Pe[a] ** 2 for a in far]) / len(far)))]
            row["pair_q0"] = [float(P.sum()), float(np.sqrt((Pe ** 2).sum()))]
            row["pair_map"] = P.tolist()
        rows.append(row)
    return rows


def main():
    pts = load_all()
    rows = summarize(pts)
    with open(os.path.join(ROOT, "data", "summary.json"), "w") as f:
        json.dump(rows, f)
    hdr = f"{'L':>2} {'bc':>2} {'nu':>5} {'J':>5} | {'E/site':>9} {'err':>7} {'init':>6} {'split':>7} | {'Ds':>7} {'Dc2':>7} {'Dc1':>7} {'Epb':>7} | {'<S1S2>':>7} {'docc':>6} {'nkjump':>6} {'S-max':>6} {'S+max':>6} {'P(far)':>8} {'P(0)':>6}"
    print(hdr)
    for r in rows:
        def g(k, fmt="7.3f"):
            v = r.get(k)
            if v is None:
                return " " * int(fmt.split(".")[0])
            if isinstance(v, (list, tuple)):
                v = v[0]
            return format(v, fmt)
        print(f"{r['L']:>2} {r['bc']:>2} {r['nu']:5.3f} {r['J']:5.2f} | {r['E_site']:9.5f} {r['E_site_err']:7.5f} {r['gs_init']:>6} "
              f"{g('init_split_site','7.4f')} | {g('spin_gap')} {g('charge_gap2')} {g('charge_gap1')} {g('pair_binding')} | "
              f"{g('rung_SS')} {g('docc','6.3f')} {g('nk_jump','6.3f')} {g('Sminus_max','6.3f')} {g('Splus_max','6.3f')} {g('pair_far_avg','8.4f')} {g('pair_onsite','6.3f')}")
    print("free-band reference gaps (J=0): ")
    seen = set()
    for r in rows:
        k = (r["L"], r["bc"], r["nu"])
        if k in seen:
            continue
        seen.add(k)
        print(f"  L={r['L']} bc={r['bc']} nu={r['nu']}: spin_gap0={r['spin_gap_free']:.3f} charge_gap2_0={r['charge_gap2_free']:.3f} charge_gap1_0={r['charge_gap1_free']:.3f}")


if __name__ == "__main__":
    main()
