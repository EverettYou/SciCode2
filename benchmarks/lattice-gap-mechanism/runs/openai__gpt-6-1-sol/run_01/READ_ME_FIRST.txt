SINGLE-ORBITAL REANALYSIS

Read single_orbital_reanalysis.pdf first.

STATUS: The requested jointly validated microscopic solution was NOT obtained.
This package is a corrected research assessment, physical calculations, and
explicitly labeled conditional benchmarks. It must not be presented as a full
solution to the prompt. In particular, its reference ARPES and zero-area values
are not identified predictions for the supplied material.

The earlier auxiliary-pole construction and its ~8.13% Gamma-side zero-area
claim are withdrawn as solutions to the single-orbital microscopic task.
Empirical fits carried forward are explicitly labeled and retain their original
conditional uncertainties. All physical-electron calculations use one spinful
orbital (four local states) per site, with no auxiliary electron orbital.

Main outputs
  single_orbital_reanalysis.pdf           12-page corrected scientific report
  sts_empirical_observables.png/.pdf      original measurements and empirical fits
  sts_empirical_phase_map.png/.pdf        measured phase constraints, unknown regions
  figures/hubbard_ed_sts.png             exact-ground-state Hubbard STS benchmarks
  response_spin_dynamics.png             actual spin Lehmann response
  transport_kubo.png                     physical-current Kubo benchmark
  figures/hubbard_arpes_benchmark.png     conditional physical-electron ARPES maps
  figures/hubbard_zero_embedding.png      finite-cluster Green-zero interpolation
  sts_local_inverse_example.png/.pdf     exact single-orbital inverse example

Reproduce main computations from this folder
  Requirements: Python, NumPy >= 2, SciPy, Matplotlib, Pillow.
  Report authoring additionally uses ReportLab. The report script contains a
  local optional bundled-library path; remove/change it if your normal Python
  already provides ReportLab.
  Use OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 and a writable MPLCONFIGDIR.

  python code/electron_ed.py
  python code/hubbard_spectra.py
  python code/hubbard_kspace.py
  python response_constraints.py
  python response_spin_dynamics.py
  python transport_kubo.py
  python extended_proxy_search.py
  python audit_electron_spectra.py
  python audit_kspace_green.py
  python code/empirical_response_fits.py  # regenerates empirical covariance/bootstrap fits
  python sts_empirical_deliverables.py
  python code/build_report.py

Input records
  data/measurements.json and data/prompt.pdf are unchanged copies of the sources.
  data/sts_empirical_response_fits.json stores the verified prior empirical fits.
  data/sts_prior_* files are prior conditional spectral-fit inputs used only for
  audits or effective-hopping/gap calibration; they are not a validated model.

Methods and limitations
  Electron ED: 8- and 10-site tori, largest fixed-spin sector dimension 63,504.
  Spin response: all 1,024 states on 10 sites, strong-coupling spin projection.
  Optical response: 6-site open patch, all 924 states at six electrons.
  Continuous momentum plots: positive finite-window projection of ten allowed
  momenta, with C4 averaging. They are not thermodynamic-limit spectra.
  Statistical fit errors, finite-size effects, approximation error, and model
  non-identifiability are explicitly distinguished in the report.
