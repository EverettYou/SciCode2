"""Compact (nu, J) table for the report from data/summary.json + the classifier in plot_phase_diagram.py."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_phase_diagram import classify
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [r for r in json.load(open(os.path.join(ROOT, "data", "summary.json"))) if r["L"] == 4 and not r.get("tag")]
rows.sort(key=lambda r: (r["nu"], r["J"]))
def f(v, nd=2):
    return "—" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"
print("| ν | bc | J | E/site | Δ_c2 − Δ_c2(J=0) | Δ_c1 − Δ_c1(J=0) | E_pb | ⟨S_i1·S_i2⟩ | n(k) jump | P_pair(r≥2) | S₋(π,π) | N(π,π) | label |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    lab, ft = classify(r)
    print(f"| {r['nu']:.3f} | {r['bc']} | {r['J']:g} | {r['E_site']:.4f} | {f(ft['gap_excess_c'])} | {f(ft['gap_excess_1'])} | {f(ft['pair_binding'])} | "
          f"{f(r['rung_SS'][0], 3)} | {f(ft['nk_jump'])} | {f(ft['pair_far'], 3)} | {f(r.get('Sminus_pipi'))} | {f(r.get('Nq_pipi'))} | {lab} |")
