---
title: Fermi-surface anomalies
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/lu2024dacof/paper.pdf
- papers/lu2023gfzif/paper.pdf
idea_ids: []
topics:
- Correlated Systems
- Topological Phases
---

# Fermi-surface anomalies

**Summary**: The stability and symmetric gappability of a Fermi surface can be encoded as an interacting fermionic SPT classification after treating momentum directions as negative synthetic dimensions.

**Sources**: [Lu et al. (2024)](../../papers/lu2024dacof/paper.pdf) [Lu et al. (2023)](../../papers/lu2023gfzif/paper.pdf)

**Last updated**: 2026-08-23

---

## Phase-space bulk and defect definition

A \(d\)-dimensional Fermi sea is represented as a Chern insulator in \(2d\)-dimensional noncommutative position–momentum space, with the Fermi surface as its chiral boundary. A phase-space Dirac regularization reproduces the Chern–Simons response and Luttinger-volume relation [Lu et al. (2024), §II](../../papers/lu2024dacof/paper.pdf#page=2).

Nonperturbatively, an interstitial translation defect can carry a projective representation of internal symmetry \(G\). Its phase defines an anomaly index \(\nu\), combining the symmetry/cobordism index of each Fermi surface with its normalized Fermi volume [Lu et al. (2024), §III and Eq. 50](../../papers/lu2024dacof/paper.pdf#page=6).

## Dimension reduction and classification

Because conjugate position and momentum coordinates do not commute, momentum directions count as negative synthetic dimensions in interacting-SPT classification. A codimension-one Fermi-surface anomaly in any physical dimension therefore reduces to a \((0+1)\)-dimensional fermionic SPT classification \(TP_1(\mathrm{Spin}\ltimes G)\). More generally, codimension-\(p\) surfaces reduce to \(p\)-dimensional spacetime [Lu et al. (2024), §§IV–V](../../papers/lu2024dacof/paper.pdf#page=8).

## Gappability and SMG

Vanishing \(\nu\) is the classification condition for deforming the Fermi surface to a symmetric product state. Some cases gap through pairing or band hybridization; Fermi-surface symmetric mass generation is the interacting case in which anomaly cancellation permits a gap but every symmetry-preserving fermion bilinear remains forbidden. Examples include finite cyclic flavor classes and charge-4e/quartet mechanisms [Lu et al. (2024), §IV.C and Table II](../../papers/lu2024dacof/paper.pdf#page=10).

Anomaly cancellation is not a constructive proof that a chosen local Hamiltonian reaches the gapped phase, nor does it determine its transition or energetics. The derivation mainly assumes translation invariance and develops codimension one in detail.

In the bilayer square-lattice SMG example, the anomaly-free Luttinger count survives the metal-to-insulator transition as a Green-function zero surface enclosing the parent Fermi volume. The exact square shape is fixed by additional particle–hole and reflection symmetries, not by anomaly cancellation alone [Lu et al. (2023), §§II.B–II.C](../../papers/lu2023gfzif/paper.pdf#page=3).

## Benchmark hooks

- Reproduce cobordism classes and anomaly-free copy numbers for selected symmetry groups.
- Numerically track defect projective phases under flux or interstitial insertion in finite lattices.
- Construct local interacting models for anomaly-free but bilinear-forbidden classes and test true symmetric gapping.
- Check codimension-\(p\) reduction against known Weyl-point, nodal-line, and ordinary Fermi-surface stability.

## Related pages

- [[topics/fermi-and-non-fermi-liquids|Fermi and non-Fermi liquids]]
- [[concepts/symmetric-mass-generation|Symmetric mass generation]]
- [[comparisons/smg-regimes-and-diagnostics|SMG regimes and diagnostics]]
- [[concepts/green-function-zero-surfaces|Green-function zero surfaces]]
- [[papers/lu2024dacof|Definition and Classification of Fermi Surface Anomalies]]
