---
document_type: lab_report
lab_id: lab-003
status: completed
idea_ids:
  - x-001
  - k-004
wiki_context:
  - benchmarks/lattice-gap-mechanism/wiki/thesis.md
  - benchmarks/lattice-gap-mechanism/problem/TASK.md
related_labs:
  - lab-002-cluster-spectra
---

# Lab 003: Local magnetic density of states

## Motivation

A peak energy at one momentum does not show that the magnetic intensity turns on only above a threshold. Neutron scattering also keeps momentum in the public figure. This lab computes the leading spin excitation from the large-exchange limit and sums it over momentum, which is the spectrum a local magnetic probe couples to.

## Design

The unperturbed Hamiltonian is interlayer exchange $J$ on every rung. Its ground state is a product of rung singlets, energy $-3J/4$ per rung. The spin excitation kept at leading order is one rung triplet. Intralayer hopping $t$ is the perturbation.

The second-order amplitudes are computed on two rungs, four sites, at half filling. The singlet shift is the nondegenerate shift of the two-singlet state. The triplet amplitudes come from degenerate perturbation theory in the $S_z=1$ sector, where exactly two states sit at the unperturbed one-triplet energy. The effective matrix on that bond is a diagonal shift plus one hopping. On the infinite square lattice each rung has four neighbors, so

$$\omega(k)=J+4(\delta_L-\varepsilon_{ss})+2 t_{\mathrm{bond}}(\cos k_x+\cos k_y).$$

The local intensity is the density of states of this band. It is evaluated as $(1/\pi^2)K(\sqrt{1-u^2})$ and divided by the unsmeared edge value $1/(2\pi)$. A Gaussian of width $0.035t$ keeps the logarithmic peak finite. The public curve is this function of excitation energy, including the region below the lower edge where the intensity is zero.

Nuclear spin-lattice relaxation and longitudinal-field muon relaxation weight this momentum sum at the probe Larmor frequency. A laboratory field does not sweep that frequency across a band of several $t$. The figure is the function those probes couple to, not a fake field axis.

## Methods and execution

Command: `/home/yzyou/SciCode2/.venv/bin/python scripts/triplon_dos.py`. NumPy 2.4.6. Runtime under one second. Outputs: `results/summary.json`, `results/local_dos.json`, and `results/local-magnetic-dos.dat`. This script writes only the lab results. The public figure is the Lab 004 PDF in `problem/figures/`.

Parameters: $J=8t$, $t=1$. The small-hopping check uses $t=0.05$ on the same four sites.

## Findings

Per bond, in units of $t^2/J$: the two-singlet shift is $-4/3$, the one-triplet diagonal is $-4$, and the triplet hopping is $+4$. At $t=1$ and $J=8$ these are $-1/6$, $-1/2$, and $+1/2$.

The lattice dispersion is $\omega(k)=20/3+\cos k_x+\cos k_y$. The lower edge is $14/3\approx 4.667t$, the van Hove peak is at $20/3\approx 6.667t$, and the upper edge is $26/3\approx 8.667t$. The minimum is at $(\pi,\pi)$.

At $t=0.05$ the second-order gaps are $7.997917t$ and $8.000417t$. Exact diagonalization of the same four sites gives $7.997918t$ and $8.000417t$.

The plotted intensity is consistent with zero from zero energy up to the lower edge, steps up, rises to about $3.3$ times the step height at the band center, and returns to zero above the upper edge.

## Limitations

The expansion is second order in $t/J$. At $J/t=8$ the bandwidth is $4t$, not tiny compared with $J$, so the leading-order band is the spectrum that was computed here, not a controlled error bar. This run has no next-nearest hopping. The public magnetic curve is the Lab 004 recomputation at $t_2=0.2t_1$. The local sum does not resolve stacking momentum. No muon or nuclear relaxation rate versus temperature was computed.

## Search decision

Use this momentum sum as the public magnetic curve. Do not put neutron scattering, a momentum axis, $t$, $J$, or the words spin gap into the solver prompt. Keep the Lab 002 charge, removal, resistivity, and photoemission numbers.

## Wiki ingest handoff

Ingest the per-bond amplitudes, the band edges $14/3$ and $26/3$, and the small-hopping check against four-site diagonalization. Ingest that the public magnetic curve is this momentum sum, and that a laboratory field sweep does not traverse it. Do not ingest the Lab 002 neutron poles as the public magnetic spectrum.
