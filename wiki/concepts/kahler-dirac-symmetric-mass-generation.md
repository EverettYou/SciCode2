---
title: Kähler–Dirac symmetric mass generation
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/guo2023smgok/paper.pdf
idea_ids: []
topics:
- Correlated Systems
- Topological Phases
---

# Kähler–Dirac symmetric mass generation

**Summary**: Two copies of Kähler–Dirac fermions admit a dimension-independent interaction gapping mechanism because their bosonic boundary description carries a universal inversion-protected Z2 SPT obstruction.

**Sources**: [Guo and You (2023)](../../papers/guo2023smgok/paper.pdf)

**Last updated**: 2026-08-23

---

## Geometric lattice fermion

A Kähler–Dirac field packages antisymmetric tensor components as fermion modes on all-dimensional cells of a hypercubic lattice. Exterior and interior products define a lattice Kähler–Dirac operator whose square gives the discrete Laplacian, providing a dimension-uniform geometric representation [Guo and You (2023), §II](../../papers/guo2023smgok/paper.pdf#page=2).

## Bosonic SPT interpretation

Interaction-generated fermion bilinears form an \(O(D+2)\) nonlinear sigma model with a Wess–Zumino–Witten/topological term. The resulting boundary theory corresponds to a bosonic SPT protected by spatial inversion and classified by \(Z_2\) in every spacetime dimension. Two Kähler–Dirac copies cancel this obstruction and can be symmetrically trivialized [Guo and You (2023), §§III–IV](../../papers/guo2023smgok/paper.pdf#page=4).

An explicit inter-copy four-fermion interaction couples the bosonic channels. In the strong-coupling site problem it produces a unique symmetric ground state; a 256-dimensional exact diagonalization shows no many-body gap closing as the two coupling channels are interpolated [Guo and You (2023), §IV and Fig. 2](../../papers/guo2023smgok/paper.pdf#page=5).

## Classification link and boundary

Counting root inversion-protected fermionic SPT boundary modes recovers dimension-dependent reductions for ordinary Majorana/Dirac descriptions while retaining the simple “two Kähler–Dirac copies” rule. This is a constructive anomaly/gapping argument, but the displayed exact diagonalization is local and strong-coupling. Extended-lattice finite-size scaling, continuum restoration, intermediate coupling, and transition dynamics remain separate validation tasks [Guo and You (2023), §§V–VI](../../papers/guo2023smgok/paper.pdf#page=6).

## Benchmark hooks

- Implement lattice exterior/interior products and verify the Kähler–Dirac algebra in several dimensions.
- Reproduce the local spectrum and symmetry quantum numbers over the four-fermion coupling interpolation.
- Simulate extended lattices to test a unique symmetric gap, bilinear absence, and finite-size convergence.
- Match the bosonic topological term and fermionic inversion classification dimension by dimension.

## Related pages

- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]]
- [[concepts/fermi-surface-anomalies|Fermi-surface anomalies]]
- [[papers/guo2023smgok|Symmetric Mass Generation of Kähler-Dirac Fermions from the Perspective of Symmetry-Protected Topological Phases]]
