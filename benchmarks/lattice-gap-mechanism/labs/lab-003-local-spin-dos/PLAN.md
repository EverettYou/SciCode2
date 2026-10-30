# Lab 003 execution plan

## Objective

Replace the momentum-resolved magnetic peaks with the leading strong-coupling spin excitation, summed over momentum.

## Stable interfaces

No function from `src/` is imported. The script is `scripts/triplon_dos.py`. It uses NumPy from the repository virtualenv at `/home/yzyou/SciCode2/.venv`.

## Steps

1. Run `scripts/triplon_dos.py`.
2. Read `results/summary.json`. The small-hopping exact gaps must agree with the second-order gaps.
3. Keep the table in `results/`. The public magnetic figure is produced by Lab 004, from `problem/figures/data/`, into `problem/figures/local-magnetic.pdf`.

## Completion criteria

- The two-rung second-order gaps at $t=0.05$ match exact diagonalization of the same four sites.
- The infinite-lattice band edges and the per-bond amplitudes are in `results/summary.json`.
- The public curve is zero below the lower edge and is the density of states of $\omega(k)=\Delta+2t_{\mathrm{eff}}(\cos k_x+\cos k_y)$.

## Stop conditions

Stop if the one-triplon subspace at zero hopping is not two-dimensional in the $S_z=1$ sector, or if the small-hopping check disagrees beyond $10^{-4}t$.
