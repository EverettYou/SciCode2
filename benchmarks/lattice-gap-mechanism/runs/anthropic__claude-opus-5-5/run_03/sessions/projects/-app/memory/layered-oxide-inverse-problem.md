---
name: layered-oxide-inverse-problem
description: "Findings for the /app \"layered oxide, low-T state at half filling\" inverse problem (STS/NMR/resistivity -> effective theory)"
metadata:
  node_type: memory
  type: project
  originSessionId: 40ca9e8b-bd23-4ae0-ad2d-7b74e214da18
  modified: 2026-10-29T18:00:07.435Z
---

Task (2026-10-29): infer effective theory from /app/measurements.json (STS a-d, NMR 1/T1, resistivity) for fillings nu=1/2, ~0.3, ~0.2; deliverables in /app.

Key findings (analysis scripts in /app/analysis):
- Panel (d) high-T nu=0.3 = bare band: t=1.00, t'=+0.195 (eps=-2t(cx+cy)-4t'cxcy), mu=-0.91, filling 0.30.
- Panel (a) nu=1/2 = two half-width TRANSLATED copies E=+-6.0+(eps-eps_c)/2 (slope exactly 0.500) -> first-order strong-coupling rung-singlet (SMG) insulator of a BILAYER with J_perp S1.S2.
- Panel (c) = isotropic BCS, Delta=1.966, mu fixed at normal-state value -> V=6.0=3J/4 (HFB decoupling) -> J_perp=8, U=0 (Phi=3J/4+U/2=6).
- NMR nu=1/2: 1/T1T ~ exp(-5.54/T); 2D 2nd-order triplon gap for J=8,U=0 is 5.43 (J=6,U=3 gives 4.32, excluded).
- Panel (b) fits anisotropic two-gap BCS (Delta~3 at kF, ~5 away), mu~-1.34.
- Zeros of G at nu=1/2 lie on band-center contour eps=-4t' -> BZ fraction ~0.31 (not 1/2): Luttinger fails (no PH symmetry).
- Status 2026-10-29: COMPLETE. Deliverables: /app/REPORT.md, /app/figures (fig1-5), /app/results/*.json, pipeline /app/code (run in order listed in README).
- Key judgment call: (J=8,U=0) chosen over (J=6,U=3) because only the 2D lattice triplon gap (not a 2-rung cluster) is physical; stated in report.
