# Deliverables

* **`REPORT.md`** — the full answer to tasks 1–5: effective theory, coefficients with uncertainties, phase diagram, explanation of every data set, ARPES predictions, and the Green's‑function zeros / Luttinger count.
* **`figures/`**
  * `fig1_sts_fits.png` — STS panels (a)–(d) with model fits. Panel (a) also compares three spectral forms.
  * `fig2_nmr_rho.png` — NMR $1/T_1T$ and resistivity with activation fits and model curves.
  * `fig3_phase_diagram.png` — phase diagram vs filling ν and temperature, with the three crystals marked.
  * `fig4_arpes.png` — predicted ARPES intensity along Γ–X–M–Γ at ν = 1/2, ≈0.3, ≈0.2 (occupied side).
  * `fig4b_arpes_full_spectral_function.png` — the same with the full spectral function (both signs of ω).
  * `fig4c_arpes_edcs.png` — energy distribution curves at selected momenta.
  * `fig5_luttinger.png` — Re G(k, ω=0) from Kramers–Kronig, the zero contour, and its dependence on μ inside the gap.
* **`results/*.json`** — all fitted and computed numbers. `final_parameters.json` is the coefficient table.
* **`code/`** — the reproducible pipeline (Python 3, numpy/scipy/matplotlib). Run from `code/` in this order: `fit_sts.py`, `fit_nmr_rho.py`, `strong_coupling.py`, `phase_diagram.py`, `arpes.py`, `luttinger.py`, `final_parameters.py`. Total runtime is about 5 minutes.
* **`analysis/`** — exploratory scripts and intermediate plots from the model‑discrimination stage. The final pipeline does not need them.

**Answer in one line.** The perovskite blocks are bilayers. The two equivalent TM sites of a rung are coupled by an interlayer exchange $J_\perp\simeq8$, with in‑plane hoppings $t=1$ and $t'=0.194$, and no interlayer hopping and no $U$. At half filling the electrons form a featureless rung‑singlet ("symmetric‑mass‑generation") insulator. Its Green's‑function zeros enclose 0.315 of the Brillouin zone, not ν = 0.5, because the model lacks particle–hole symmetry. Doping turns it into an interlayer s‑wave superconductor: strong‑coupling with a pseudogap at ν ≈ 0.3, BCS‑like at ν ≈ 0.2.
