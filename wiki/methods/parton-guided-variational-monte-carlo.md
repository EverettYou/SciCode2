---
title: Parton-guided variational Monte Carlo
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/hou2023vmcso/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Parton-guided variational Monte Carlo

**Summary**: A symmetry-breaking parton mean-field state can be dressed by a correlation projector so that the physical variational wavefunction restores the symmetry while retaining an interaction-generated fermion gap.

**Sources**: [Hou and You (2023)](../../papers/hou2023vmcso/paper.pdf)

**Last updated**: 2026-08-23

---

## Construction

For the bilayer honeycomb SMG model, the ansatz starts from a free-fermion ground state with a staggered interlayer hopping mass \(\lambda\), then applies an onsite Jastrow-like factor depending on the interlayer charge difference \(q_i^-\). Both \(\lambda\) and the local correlation potential are optimized by automatic-differentiation VMC [Hou and You (2023), §II](../../papers/hou2023vmcso/paper.pdf#page=2).

The two ingredients play distinct roles. The mean-field mass makes fermion correlations short-ranged but by itself breaks layer \(U(1)^-\). The Jastrow factor suppresses charged configurations and introduces phase fluctuations that restore the physical symmetry: the extrapolated interlayer coherence vanishes while symmetry-invariant spin correlations remain [Hou and You (2023), §III](../../papers/hou2023vmcso/paper.pdf#page=4).

## What the variational parameters reveal

The optimized \(\lambda\) is a gauge-charged parton diagnostic rather than a physical observable. Its onset can expose a candidate Higgs mechanism hidden behind a fully symmetric physical state, which is a useful interpretive capability of a parton-guided ansatz. It cannot by itself establish that the proposed emergent gauge theory is the exact infrared description [Hou and You (2023), §§IV–V](../../papers/hou2023vmcso/paper.pdf#page=4).

## Validation boundary

The ansatz is exact at the noninteracting and isolated-dimer limits. A one-unit-cell exact-diagonalization check reports fidelity at least 0.99 and relative energy excess at most \(10^{-4}\), but this small-system agreement does not remove variational bias at criticality [Hou and You (2023), §II](../../papers/hou2023vmcso/paper.pdf#page=2). The reported critical estimates use \(L=6\)–10 for energy scaling and up to \(L=16\) for fermion correlations; the authors state that the available sizes do not support a reliable infinite-size extrapolation of the fermion scaling dimension [Hou and You (2023), §III](../../papers/hou2023vmcso/paper.pdf#page=3).

## Benchmark hooks

- Reproduce the exact-limit and one-cell fidelity checks before fitting critical data.
- Compare alternative correlation factors and quantify ansatz-induced shifts in \(J_c\), \(\nu\), and \(\eta_\psi\).
- Separate physical observables from gauge-charged variational diagnostics in analysis and reporting.
- Cross-validate critical exponents against unbiased Monte Carlo on the same Hamiltonian and coupling convention.

## Related pages

- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]]
- [[papers/hou2023vmcso|Variational Monte Carlo study of symmetric mass generation in a bilayer honeycomb lattice model]]
