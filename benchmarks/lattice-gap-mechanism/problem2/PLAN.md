# Work plan (started 2026-10-26 20:40)

Goal: NQS-VMC phase diagram of the bilayer square lattice t1-t2-J model
(t1=1, t2=0.2, interlayer Heisenberg J, no interlayer hopping), line cuts at
nu=1/2 and nu=1/4, the (nu,J) plane, and three spectra in the gapped phase.

## Layout
- code/      python sources (ED reference, lattice, VMC engine, drivers, analysis)
- data/      raw results (json/npz), one file per run
- figures/   plots
- report/    research report (markdown + pdf)
- logs/      run logs
- .venv/     local python 3.11 environment (jax-cpu, netket, flax)

## Steps
1. ED reference on small clusters (2x2 bilayer plaquette, 16 modes) for validation.
2. VMC: neural-Jastrow x geminal (AGP) ansatz, custom Metropolis moves that
   conserve N_layer1, N_layer2, N_up, N_down; SR optimizer. Validate at J=0
   (free band) and vs ED on 2x2.
3. Half-filling cut on 4x4 bilayer (and 6x6 checks): E/site, charge gap (N+-2),
   spin gap (Sz=1), S(q), interlayer pair correlation, n(k).
4. Quarter-filling cut, same diagnostics.
5. (nu,J) grid on 4x4.
6. Spectra at a point in the gapped phase: STM dI/dV, spin spectrum, rho(T),
   via strong-coupling quasiparticle theory + SMA + small-cluster ED, tied to VMC gaps.
7. Report.
