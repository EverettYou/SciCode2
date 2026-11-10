# Analysis code (all Python 3, numpy/scipy/matplotlib)

Run from `/app/work` with `python3 -I <script>`; every script reads `/app/measurements.json`.

| script | purpose |
|---|---|
| `fitlib.py`, `n0lib.py`, `dos_tools.py` | k-grid, tight-binding band, DOS histogramming helpers |
| `fit_a.py`, `fit_a2.py`, `fit_a3.py` | fits of STS panel (a) (ν=1/2) with Hubbard-I-type two-pole spectra (several weight parametrisations) |
| `fit_c.py`, `fit_d.py` | BCS fit of panel (c) and bare-band fit of panel (d) |
| `fit_b.py`, `fit_b2.py`, `fit_b3.py` | candidate structures for panel (b) (BCS, two-pole, YRZ-like, Nambu+Mott, anisotropic BCS, flexible two-branch forms) |
| `models.py` | final spectral functions A(k,ω) for the three crystals |
| `sts_compare.py` | Figure `fig_sts_fits.png` (data vs theory) |
| `nmr_model.py` | NMR 1/(T1T) theory curves, `fig_nmr.png` |
| `rho_model.py` | resistivity theory curves, `fig_rho.png` |
| `phase_diagram.py` | BCS gap equation, calibrated T*, T_theta, Tc; `fig_phase_diagram.png` |
| `arpes.py` | predicted ARPES density plots, `fig_arpes.png`, `fig_arpes_weights.png` |
| `luttinger.py` | Kramers–Kronig Re G(k,0) at ν=1/2, zero curve, enclosed fraction; `fig_luttinger.png` |

Fit results are stored in `fit_*.npy`, model curves in `*_curves.npz`, `arpes_arrays.npz`, `luttinger_arrays.npz`.
