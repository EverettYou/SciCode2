# Contents

* `REPORT.md` — the answer to all five tasks (effective theory, phase diagram, explanation of the data, ARPES prediction, Kramers–Kronig / Luttinger analysis).
* `parameters.json` — all extracted parameters and derived numbers in machine-readable form.
* `figures/`
  * `fig_sts_fits.png` — the four STS panels with the theory curves.
  * `fig_nmr_rho.png` — NMR 1/(T1 T) and resistivity, data vs theory, three fillings.
  * `fig_phase_diagram.png` — phase diagram in the (ν, T) plane.
  * `fig_arpes.png` — predicted low-T ARPES A(k,ω) along (0,0)→(1/2,0)→(1/2,1/2)→(0,0) for ν = 1/2, 0.3, 0.2.
  * `fig_luttinger.png` — Re G(k, 0) at ν = 1/2 from Kramers–Kronig, the zero energy ω₀(k), and the Luttinger count.
  * `supp_*.png` — supporting fits (candidate models for ν = 1/2, model-independent band weights, excluded Hatsugai–Kohmoto+pairing spectra, flexible fits of panel (b)).
* `code/` — `model.py` (the effective theory), `make_*.py` (figures), `fit_*.py` (fits to the STS data), `luttinger.py`, `hk_bcs.py` (exact per-pair solution of the HK+pairing model, used to exclude it).
* `work/` — scratch directory with intermediate fits and plots.

All scripts run with `python3` (numpy, scipy, matplotlib) from `/app/code`.
