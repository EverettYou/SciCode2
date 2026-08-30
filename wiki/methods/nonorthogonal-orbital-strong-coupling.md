---
title: Nonorthogonal-orbital strong-coupling expansion
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/huang2024qmiwm/paper.pdf
idea_ids: []
topics:
- Correlated Systems
- Topological Phases
---

# Nonorthogonal-orbital strong-coupling expansion

**Summary**: Wannier-obstructed bands can support a localized Mott description if orbital orthogonality is relaxed, producing generalized spin models with overlap-enabled exchange channels.

**Sources**: [Huang et al. (2024)](../../papers/huang2024qmiwm/paper.pdf)

**Last updated**: 2026-08-23

---

## Construction

For an isolated obstructed band set with \(W\ll U\ll\Delta\), exponentially localized, symmetry-compatible orbitals are optimized by Hartree energy but allowed to overlap, \(g_{IJ}\ne\delta_{IJ}\). Singly occupying these orbitals gives a nonorthogonal many-body Mott basis. Projecting the electron Hamiltonian becomes a generalized eigenproblem with metric \(G\), while diagrammatic expansions in orbital overlap and hopping systematically generate the effective spin Hamiltonian [Huang et al. (2024), §§II–IV](../../papers/huang2024qmiwm/paper.pdf#page=2).

Nonorthogonality opens direct two-spin and higher permutation channels that vanish in an orthogonal basis. Conventional superexchange is recovered through perturbative virtual double occupancy, but it now competes with overlap-enabled ferromagnetic, antiferromagnetic, and chiral interactions.

## Kagome demonstration

Applied to obstructed-trivial, Chern, and fragile-topological Kagome bands, the optimization yields exponentially localized orbitals with overlap \(g\). The leading Heisenberg coupling changes sign near \(U/t\sim1/g\), so flat-band ferromagnetism remains stable until bandwidth reaches order \(Ug\). Near the FM–AFM crossover, the leading Heisenberg term weakens and overlap-enabled chiral terms can dominate [Huang et al. (2024), §V](../../papers/huang2024qmiwm/paper.pdf#page=8).

## Validation boundary

The framework is controlled in the isolated-band strong-coupling hierarchy. The explicit phase diagram uses a toy Kagome model and classical candidate states; canted magnetism and possible spin liquids near the frustrated crossover require independent many-body calculations. Weak coupling at \(U/t\sim1\), intervalley structure, and quantitative material predictions are outside the demonstrated regime [Huang et al. (2024), §VI](../../papers/huang2024qmiwm/paper.pdf#page=11).

## Benchmark hooks

- Optimize localized nonorthogonal orbitals for a known obstructed band and verify exponential decay and band-span completeness.
- Reproduce the metric and projected Hamiltonian from independent symbolic and numerical overlap expansions.
- Track FM–AFM crossover scaling with \(g\), \(U\), and bandwidth.
- Solve the derived frustrated spin model beyond classical order and test proposed intermediate phases.

## Related pages

- [[topics/correlated-quantum-many-body-systems|Correlated quantum many-body systems]]
- [[topics/topological-phases|Topological phases]]
- [[papers/huang2024qmiwm|Quantum Magnetism in Wannier-Obstructed Mott Insulators]]
