# Deliverables

- `REPORT.md` — the answer to tasks 1–5 (effective theory, phase diagram, explanation of the data, ARPES predictions, Green's-function zeros).
- `results_summary.json` — the key numbers in machine-readable form.
- Figures:
  - `fig1_sts_fits.png` — STS data with the fitted theory spectra (all four panels).
  - `fig2_nmr_resistivity.png` — NMR 1/(T1 T) and resistivity with model curves.
  - `fig3_ed_gaps.png` — exact diagonalization (8/10 sites) of the attractive t–t′–U model: pair-breaking gap vs filling, compared with the data.
  - `fig4_phase_diagram.png` — phase diagram vs filling 0–1, crystals marked.
  - `fig5_arpes.png` — predicted low-T ARPES maps along (0,0)–(½,0)–(½,½)–(0,0).
  - `fig6_zeros.png` — Re G(k,0) at ν = ½ (zero curve) and its sensitivity to the replica weights.
- `code/` — reproducible scripts:
  - `model.py`, `style.py` — shared helpers.
  - `fit_all.py` — fits; writes `params.json`.
  - `fig_fits.py` — draws Figs. 1 and 2.
  - `ed_hubbard.py`, `ed_study.py` — exact diagonalization.
  - `phase_diagram.py`, `arpes.py`, `zeros.py` — Figs. 4–6.
- `analysis/` — exploratory scripts used while discriminating between candidate models (not needed to reproduce the report).

Reproduce everything (a few minutes):

```
cd /app/code && python3 fit_all.py && python3 fig_fits.py && python3 ed_study.py && python3 phase_diagram.py && python3 arpes.py && python3 zeros.py
```
