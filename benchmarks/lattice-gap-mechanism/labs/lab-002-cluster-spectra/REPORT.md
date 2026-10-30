---
document_type: lab_report
lab_id: lab-002
status: completed
idea_ids:
  - x-001
  - c-003
  - k-005
wiki_context:
  - benchmarks/lattice-gap-mechanism/wiki/thesis.md
  - benchmarks/lattice-gap-mechanism/problem/TASK.md
related_labs:
  - lab-001-phenomenon-card
---

# Lab 002: Cluster spectra and high-temperature band

## Motivation

Hand-drawn traces do not constrain a band, a bilayer, or the difference between a nesting-driven exciton and a local singlet. This lab computes those scales for one strong-coupling parameter set and exports the rounded values to the solver prompt.

## Design

The correlated calculation is exact diagonalization of a bilayer plaquette: two layers, each a 2×2 square, with each intralayer bond counted once. The hopping is $t=1$. The only interaction is an interlayer exchange $J=8t$ on the four rungs. Sectors keep $N_\uparrow$ and $N_\downarrow$ fixed. The script checks a two-site singlet at $-3J/4$ and a one-electron bond at $-t$ before the plaquette run.

The high-temperature momentum table is not this cluster. It is the infinite square lattice $\varepsilon(k)=-2t(\cos k_x+\cos k_y)$, with the chemical potential fixed by the density on a $241^2$ grid. That is the high-temperature limit in which the interaction no longer reconstructs the peak locus.

Resistivity is not a Kubo conductivity. It is $\exp[( \Delta_c/2)(1/T-1/T_0)]$ with $T_0=4t$ and $\Delta_c$ the half-filled charge gap.

## Methods and execution

Command: `/home/yzyou/SciCode2/.venv/bin/python scripts/spectra.py`. NumPy 2.4.6. Runtime about 19 seconds. Outputs: `results/summary.json`, `results/tunneling.json`, `results/neutron.json`, and `results/band_*.json`.

The saved tunneling file from the first run divided by a near-zero edge value. The script now divides by the maximum. The prompt uses that maximum-normalized shape. The peak positions did not change.

## Findings

Half filling, eight electrons. Ground-state energy $-24.718t$. The $N=7$ and $N=9$ ground states are equal, $-19.659t$, so the chemical-potential midpoint is zero. Charge gap $\Delta_c=10.119t$. The tunneling intensity, broadened with a Gaussian of width $0.2t$, is even in bias and is consistent with zero from $-4t$ to $4t$. The maxima lie near $\pm 5.5t$ and $\pm 6.5t$.

Spin. The lowest triplet is $6.752t$ above the singlet. The transverse spectral maximum at stacking momentum $\pi$ is at $8.32t$, $7.52t$, and $6.75t$ for in-plane momenta $(0,0)$, $(\pi,0)$, and $(\pi,\pi)$. At stacking momentum $0$ the in-plane center has no intensity, and the other two in-plane peaks are about one percent of the stacking-boundary maxima.

Removal costs from $N=8,7,6,5$ are $5.059t$, $0.101t$, $5.291t$, and $0.445t$. Two carriers removed together cost far less than twice one carrier. The same plaquette is still charge-gapped at six and at four electrons. That is a pair-breaking scale on eight sites, not a bulk metal and not a transition temperature.

Low-temperature occupied removal peaks, measured from the gap center: $-6.54t$ at $(0,0)$, $-5.72t$ at $(\pi,0)$, and $-5.06t$ at $(\pi,\pi)$. The infinite-lattice band at one electron per site is $-4t$, $0$, and $+4t$ at those three momenta. The occupied weight has been pushed away from the chemical potential at the Fermi-surface momentum and at the band bottom. A gap that only opened on the nested surface would leave the band bottom near $-4t$.

High-temperature chemical potentials: $0$ at density $1$, $-0.568t$ at $0.75$, and $-1.442t$ at $0.50$. Only the density-$1$ cut crosses zero at both $(1/2,0)$ and $(1/4,1/4)$.

## Limitations

The plaquette counts one bond in each direction, so its coordination is not the coordination of the infinite square lattice. Absolute cluster energies and the infinite-lattice band share the symbol $t$ but not the same kinetic Hamiltonian. $J/t=8$ is deep in the strong-coupling side of the regime discussed for this benchmark. Neutron intensities are broadened poles, not a dense momentum survey. Resistivity is the activated expression above. No thermodynamic superconducting temperature was computed.

## Search decision

Keep the rounded Lab 002 numbers as the solver-facing data. Do not put $t$, $J$, the plaquette, or a phase name in the prompt. The open prediction is the low-temperature momentum-resolved photoemission at $0.75$ electrons per site, which this lab did not compute. Prune any prompt curve that is not in `results/`.

## Wiki ingest handoff

Ingest the half-filled scales, the stacking-momentum contrast, the alternating removal costs, and the mismatch between the low-temperature removal peaks and the high-temperature band bottom. Do not ingest a bulk metal or a superconducting temperature. Those were not computed.
