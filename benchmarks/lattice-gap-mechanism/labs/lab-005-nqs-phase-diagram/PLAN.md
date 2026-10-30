# Lab 005 execution plan

## Objective

Compute the half-filling line cut, $\nu=1/2$, of the bilayer Hamiltonian in `problem2/prompt.tex` by neural quantum state variational Monte Carlo, before the quarter-filling cut or the $(\nu,J)$ plane is reported as a result.

## Stable interfaces

The environment is `labs/lab-005-nqs-phase-diagram/.venv`, not the repository `.venv`. The script is `scripts/linecut.py`. It uses NetKet and JAX.

## Steps

1. Confirm JAX sees one H200.
2. Build $H$ with $t_1=1$, $t_2=0.2$, on a periodic $L\times L$ bilayer. Start at $L=4$.
3. At half filling $\nu=1/2$, two electrons per lattice site, optimize a neural-network fermion state at $J\in\{0.5,2,4,8\}$.
4. For each $J$, record the energy per site, a charge gap from the neighboring particle-number sectors if the Hilbert space allows it, a spin structure factor, and an interlayer singlet pair correlation.
5. Write `results/linecut.json`. Do not draw a phase boundary from a run that has not converged.

## Completion criteria

- The $J=0$ energy matches the filled free band on the same finite lattice to the reported statistical error.
- Each finite $J$ has an energy with a statistical error bar.
- The report says which diagnostics were actually measured.

## Stop conditions

Stop if the sampler does not produce a finite energy, or if the $J=0$ check misses the free-band energy by more than the statistical error.
