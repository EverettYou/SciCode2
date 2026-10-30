---
document_type: lab_report
lab_id: lab-005
status: designed
idea_ids:
  - x-001
wiki_context:
  - benchmarks/lattice-gap-mechanism/problem2/TASK.md
related_labs:
  - lab-004-stm-greens-function
---

# Lab 005: Neural quantum state line cut

## Motivation

The forward problem asks for the phase diagram of the bilayer square lattice with $t_2=0.2t_1$. The $t_2=0$ transition does not locate it. This lab computes the half-filled line cut with variational Monte Carlo.

## Design

$H$ is the Hamiltonian in `problem2/prompt.tex`: intralayer $t_1$ and $t_2$, interlayer $J$, no interlayer hopping. The wavefunction is a neural-network state sampled by Monte Carlo. The first lattice is a $4\times 4$ bilayer with periodic boundaries, at half filling $\nu=1/2$ (two electrons per lattice site). The couplings on the first pass are $J\in\{0.5,2,4,8\}$ with $t_1=1$ and $t_2=0.2$.

The $J=0$ energy is compared with the exact filled tight-binding band on the same cluster. That comparison is the control. A phase label is not assigned until the diagnostics in the plan exist.

## Findings

Nothing has been computed. The NetKet environment was being installed when this report was written. No phase boundary is available.

## Wiki ingest handoff

Do not ingest a phase boundary from this report. Ingest only numbers that a later completed run writes into `results/linecut.json`.
