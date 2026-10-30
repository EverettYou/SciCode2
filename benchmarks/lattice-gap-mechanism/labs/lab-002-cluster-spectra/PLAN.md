# Lab 002 execution plan

## Objective

Compute the spectra that the solver prompt plots, and keep the approximation attached to every curve.

## Stable interfaces

No function from `src/` is imported. The script is `scripts/spectra.py`. It uses NumPy from the repository virtualenv at `/home/yzyou/SciCode2/.venv`.

## Steps

1. Run `scripts/spectra.py`.
2. Read `results/summary.json`, `results/tunneling.json`, and `results/neutron.json`.
3. Copy only rounded values that match those files into `problem/prompt.tex`.
4. Record the cluster, the activated resistivity, and the high-temperature band as separate approximations in `REPORT.md`.

## Completion criteria

- The dimer tests inside the script pass.
- Half-filling charge and spin scales, removal costs, neutron peak energies, and band chemical potentials are written to `results/summary.json`.
- The prompt tables match those outputs after rounding.

## Stop conditions

- Stop if the dimer singlet is not $-3J/4$ or the one-electron bond is not $-t$.
- Stop if the half-filled tunneling spectrum is not particle-hole symmetric.
- Do not describe the doped cluster gaps as a bulk metal, and do not report a thermodynamic transition temperature.
