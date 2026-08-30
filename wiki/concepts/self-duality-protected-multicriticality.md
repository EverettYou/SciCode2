---
title: Self-duality-protected multicriticality
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/lu2021spmid/paper.pdf
idea_ids: []
topics:
- Topological Phases
- Correlated Systems
---

# Self-duality-protected multicriticality

**Summary**: Promoting a self-duality to a symmetry pins a theory to the boundary between dual phases and can protect a multicritical junction separating continuous and first-order transitions.

**Sources**: [Lu et al. (2021)](../../papers/lu2021spmid/paper.pdf)

**Last updated**: 2026-08-23

---

## Constraint on phase diagrams

A self-duality exchanges two phases and forbids the perturbation that favors either side. With the duality imposed, the system cannot avoid their boundary; additional duality-even interactions can move it from a continuous critical line through a multicritical point to a first-order line [Lu et al. (2021), §I](../../papers/lu2021spmid/paper.pdf#page=1).

For easy-plane deconfined criticality, the relevant field theory is self-dual \(N_f=2\) QED\(_3\). Promoting mass fluctuations to Gross–Neveu scalar fields organizes O(4) DQCP, SO(5) criticality, symmetric-gapped/first-order regions, and their multicritical junctions in one phase diagram [Lu et al. (2021), §II](../../papers/lu2021spmid/paper.pdf#page=2).

## Stability calculation

A large-\(N_f\) expansion computes scaling and mixing of mass–mass and current–current quartic interactions in QED–Gross–Neveu–Chern–Simons theories. Certain Lorentz-breaking current interactions are relevant and can drive the self-dual critical theory toward a first-order transition. Their lattice image includes staggered diagonal dimer–dimer terms used in modified J–Q models [Lu et al. (2021), §§III–IV](../../papers/lu2021spmid/paper.pdf#page=5).

## Evidence boundary

The operator analysis is controlled at large flavor number and extrapolated to \(N_f=2\). Agreement with QMC phase-diagram trends supports the mapping but does not establish precise scaling dimensions or exclude intervening spin-liquid phases. Self-duality must be exact or emergent with sufficiently weak breaking; explicit duality-breaking perturbations can bypass the multicritical point.

## Benchmark hooks

- Reproduce quartic-operator mixing matrices and large-\(N_f\) eigenvalues.
- Match lattice staggered-dimer operators to continuum current interactions by symmetry.
- Simulate duality-preserving and weakly breaking paths to test whether the multicritical point can be bypassed.
- Compare extrapolation schemes at \(N_f=2\) against bootstrap or sign-free QMC data.

## Related pages

- [[topics/topological-phase-transitions|Topological phase transitions]]
- [[methods/twisted-lattice-gauging|Twisted lattice gauging]]
- [[concepts/intrinsically-gapless-topological-states|Intrinsically gapless topological states]]
- [[papers/lu2021spmid|Self-duality protected multicriticality in deconfined quantum phase transitions]]
