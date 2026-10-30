# Lab 004 execution plan

## Objective

Replace the sparse tunneling markers by the momentum sum of the strong-coupling spectral function, on a dispersion with nearest- and next-nearest-neighbor hopping.

## Stable interfaces

No function from `src/` is imported. The script is `scripts/stm_dos.py`. It uses NumPy from the repository virtualenv at `/home/yzyou/SciCode2/.venv`.

## Steps

1. Run `scripts/stm_dos.py`.
2. Read `results/summary.json`. The spectral-function sum rule must be within one percent of 1.
3. The script writes the tables under `problem/figures/data/`. The plotted PDFs live in `problem/figures/`.
4. Copy the high-temperature peaks and the occupied pole positions from the same file into the prompt tables, after rounding.

## Completion criteria

- The dispersion uses $t_1=1$ and $t_2=0.2t_1$.
- The Green's function is Eq. (19) of arXiv:2307.12223, with the frequency shifted by a positive imaginary part.
- The public curve is the Brillouin-zone average of $-\mathrm{Im}\,G/\pi$.

## Stop conditions

Stop if the sum rule fails, or if the saddle is still at the center of the band.
