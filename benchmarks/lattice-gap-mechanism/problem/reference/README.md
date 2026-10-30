# Reference answer for `prompt.pdf` (lattice-gap-mechanism)

Everything here was produced from `../measurements.json` and the statement in `../prompt.pdf`.

* `report/report.pdf` (+ `report.tex`): the answer to the five tasks.
* `code/`: `fit_data.py` (fits of all curves -> `data/fit_results.json`), `strong_coupling.py` (two-rung second-order
  theory), `bcs.py` (inter-layer singlet mean field + exact two-body pair), `ed_gpu.py` (GPU Lanczos exact
  diagonalization of the bilayer t1-t2-J model, factorized up/down basis, memory-lean matvec),
  `run_4x2.py`, `run_3x3.py`, `run_3x3_path.py`, `dgap_dJ.py` (production ED), `analyze_ed.py` (calibration of the two-pole
  spectrum, triplon band, gaps), `arpes.py`, `luttinger.py`, `transport_nmr.py`, `phase_diagram.py` (figures),
  `test_ed.py`, `test_lean.py`, `check_k.py`, `bench_device.py` (validation and benchmarks).
* `data/`: JSON outputs of every step; `figures/`: all figures; `logs/`: ED run logs.

Reproduce: `cd code; python3 fit_data.py; python3 strong_coupling.py; python3 bcs.py; python3 run_4x2.py;
python3 run_3x3.py; python3 run_3x3_path.py; python3 analyze_ed.py; python3 transport_nmr.py; python3 arpes.py;
python3 luttinger.py; python3 phase_diagram.py; cd ../report; tectonic -X compile report.tex`.
The ED runs need an NVIDIA GPU with >= 100 GB (3x3 bilayer, 2.4e9 states); the 4x2 runs need ~20 GB.

## Main results (units of D)

* Model: bilayer square-lattice t1-t2-J model, t1 = 1.02(3), t2 = 0.20(1), J = 8.0(4); |t_perp| < 0.15, |U| < 0.5.
* nu = 1/2: symmetric rung-singlet (SMG / pair-Mott) insulator; charge gap 8.04 (ED 3x3: 8.66), spin gap 5.5 (ED: 5.43 / 5.66).
* nu ~ 0.3: inter-layer singlet superconductor, Tc = 0.36 (stiffness limited), gap 2.49 (ED 2.4-2.55), pseudogap up to T ~ 4.
* nu ~ 0.2: superconductor with sharp Bogoliubov quasiparticles, Tc = 0.59, gap 1.73 (mean field 1.73, ED 1.8-2.2), mu = -2.46.
* ARPES (figures/arpes.png): two parallel bands separated by 3J/2 at nu = 1/2 (coherent width 2.7-3.0, residues 0.3-0.55,
  satellites), Bogoliubov bands with a minimum-gap locus inside the normal-state Fermi surface at nu ~ 0.3 (0.23 of the zone,
  smeared) and nu ~ 0.2 (0.16 of the zone, sharp).
* Green's-function zeros at nu = 1/2 (figures/luttinger.png): zero surface at the gap midpoint encloses 0.74-0.81 of the zone
  around (0,0) (Re G > 0 there); first order 0.31; the fraction is set by the residues and is not nu = 0.5.
* GPU time: about five GPU-hours (H200) for the exact diagonalization.

Note: `../measurements.json` was regenerated on 2026-10-28 23:11 (after the first fits); all fits and figures were redone on
the current file (`data/fit_results_before_regeneration.json` keeps the earlier fit for reference).
