"""Markdown tables for the report from data/summary.json.
Usage: python code/make_tables.py [L] [nu]  -> prints the cut table and the gap table."""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fmt(v, e=None, nd=3):
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    if e is None or not np.isfinite(e):
        return f"{v:.{nd}f}"
    # value(err) with err in units of the last digit
    if e <= 0:
        return f"{v:.{nd}f}"
    d = max(nd, int(np.ceil(-np.log10(e))) + 1)
    d = min(d, 6)
    scale = 10 ** d
    return f"{v:.{d}f}({int(round(e * scale))})"


def cut_tables(L, nu, tag=""):
    rows = [r for r in json.load(open(os.path.join(ROOT, "data", "summary.json")))
            if r["L"] == L and abs(r["nu"] - nu) < 1e-6 and r.get("tag", "") == tag]
    rows.sort(key=lambda r: r["J"])
    if not rows:
        return "(no data)"
    r0 = rows[0]
    out = []
    out.append(f"Energies and gaps, {L}x{L} bilayer, bc={r0['bc']}, nu={nu}. Free-band (J=0) references: "
               f"spin gap {r0['spin_gap_free']:.3f}, 2-particle gap {r0['charge_gap2_free']:.3f}, 1-particle gap {r0['charge_gap1_free']:.3f}.\n")
    out.append("| J | E/site | init (split) | Δ_s | Δ_c2 | Δ_c1 | E_pb(+) | E_pb(−) |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        split = r.get("init_split_site")
        init = f"{r['gs_init'][3:]} ({split:.4f})" if split is not None and np.isfinite(split) else r["gs_init"][3:]
        out.append(f"| {r['J']:g} | {fmt(r['E_site'], r['E_site_err'], 4)} | {init} | {fmt(r.get('spin_gap'), r.get('spin_gap_err'), 2)} | "
                   f"{fmt(r.get('charge_gap2'), r.get('charge_gap2_err'), 2)} | {fmt(r.get('charge_gap1'), r.get('charge_gap1_err'), 2)} | "
                   f"{fmt(r.get('pair_binding'), r.get('pair_binding_err'), 2)} | {fmt(r.get('pair_binding_h'), r.get('pair_binding_h_err'), 2)} |")
    out.append("")
    out.append("Correlation diagnostics (per site):\n")
    out.append("| J | ⟨S_i1·S_i2⟩ | double occ. | n(k) jump | n(k) in/out | S₋(π,π) | S₊(π,π) | N(π,π) | P_pair(r≥2) | P_pair(L/2,L/2) | P_pair(0) |")
    out.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        nq = r.get("Nq_pipi")
        out.append(f"| {r['J']:g} | {fmt(r['rung_SS'][0], r['rung_SS'][1])} | {fmt(r['docc'][0], r['docc'][1])} | "
                   f"{fmt(r.get('nk_jump'), r.get('nk_jump_err'), 2)} | {fmt(r.get('nk_in_shell'), None, 2)}/{fmt(r.get('nk_out_shell'), None, 2)} | "
                   f"{fmt(r.get('Sminus_pipi'), r.get('S_pipi_err'), 2)} | {fmt(r.get('Splus_pipi'), r.get('S_pipi_err'), 2)} | {fmt(nq, None, 2) if nq is not None else '—'} | "
                   f"{fmt(r['pair_far_avg'][0], r['pair_far_avg'][1], 3)} | {fmt(r['pair_max_dist'][0], r['pair_max_dist'][1], 3)} | {fmt(r['pair_onsite'][0], r['pair_onsite'][1], 3)} |")
    return "\n".join(out)


if __name__ == "__main__":
    L = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    nu = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    tag = sys.argv[3] if len(sys.argv) > 3 else ""
    print(cut_tables(L, nu, tag))
