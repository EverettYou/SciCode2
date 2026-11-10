# Deliverables

* `report.md` — the full answer to Tasks 1–5 (effective theory, phase diagram, explanation of the data, ARPES predictions, Luttinger surface), with the figures below embedded.
* `results.json` — every fitted parameter with its uncertainty.
* `figures/fig_sts_fits.png` — STS data (panels a–d) versus the effective theory.
* `figures/fig_nmr_rho_fits.png` — NMR and resistivity data versus the effective theory.
* `figures/fig_phase_diagram.png` — phase diagram (Task 2).
* `figures/fig_arpes.png` — predicted ARPES intensity at the three fillings (Task 4).
* `figures/fig_luttinger.png`, `figures/fig_luttinger_twopole.png`, `figures/fig_cpt_*.png` — Luttinger surface and cluster-perturbation-theory spectra at half filling (Task 5).
* `analysis/` — data-reduction scripts (fits to STS, NMR, resistivity).
* `theory/` — model, ARPES, phase diagram, exact diagonalisation / CPT, Kramers–Kronig scripts.

Run any script with `python3 -I <script>` from its own directory (no third-party packages beyond numpy, scipy, matplotlib).
