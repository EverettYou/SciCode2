---
title: Symmetry-complete hot-spot renormalization group
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/lu2022cmaus/paper.pdf
- papers/you2022ksaic/paper.pdf
idea_ids: []
topics:
- Correlated Systems
---

# Symmetry-complete hot-spot renormalization group

**Summary**: Four-fermion interactions near Van Hove hot spots can be enumerated by symmetry and evolved as antisymmetric Majorana tensors, turning a large one-loop parquet calculation into auditable tensor contractions.

**Sources**: [Lu et al. (2022)](../../papers/lu2022cmaus/paper.pdf) [You and Vishwanath (2022)](../../papers/you2022ksaic/paper.pdf)

**Last updated**: 2026-08-23

---

## Workflow

1. Project the microscopic bands and interactions onto patches around Van Hove saddle points.
2. Enumerate momentum-conserving four-fermion vertices and quotient them by lattice, spin, and valley symmetries.
3. Remove linear dependencies by Gaussian elimination to obtain an interaction basis.
4. Convert complex fermions to Majorana components, where a coupling is a totally antisymmetric rank-4 tensor.
5. Contract the tensor with particle–particle and particle–hole susceptibilities, project each step back to the independent basis, and identify divergent susceptibility channels [Lu et al. (2022), §§II–IV](../../papers/lu2022cmaus/paper.pdf#page=2).

For six hot spots in each RTG valley, the construction reduces the symmetry-allowed set to 43 linearly independent vertices. The Majorana representation combines the usual one-loop diagrams into a single contraction form and reduces manual symmetry-factor bookkeeping [Lu et al. (2022), §§III.A and IV.A](../../papers/lu2022cmaus/paper.pdf#page=4).

An earlier reduced two-valley flow isolates density and Hund couplings and makes the VHS mechanism transparent: particle–particle ladders grow double-logarithmically, a small Hund anisotropy selects the spin sector, and sufficiently strong antiferromagnetic Hund coupling can redirect repulsive intervalley interaction toward singlet pairing [You and Vishwanath (2022), §Superconductivity](../../papers/you2022ksaic/paper.pdf#page=4). The later 43-vertex calculation resolves angular pairing channels that this two-patch model cannot distinguish.

## RTG result and scope

The displacement field changes nesting and thereby the leading channel. Under the paper's projected screened-Coulomb interaction, the flow favors spin-singlet d-wave pairing near \(u_d\approx26\) meV and i-wave pairing for the two larger-field nesting structures; the estimated acoustic-phonon attraction is about \(10^{-3}\) of the Coulomb scale [Lu et al. (2022), §§IV.B–V](../../papers/lu2022cmaus/paper.pdf#page=8).

These are one-loop weak-coupling instabilities at chemical potential tuned to the VHS. Patch truncation omits non-hot-spot states, RG divergence indicates an instability rather than solving the ordered phase, and microscopic screening and band parameters control the bare projection. Agreement with spin-singlet phenomenology does not uniquely identify d- versus i-wave order.

## Benchmark hooks

- Reproduce the symmetry-orbit enumeration and 43-dimensional independent basis.
- Verify tensor RG equations against explicit complex-fermion diagrams on a reduced model.
- Track basis, cutoff, and patch-resolution invariance of leading eigenchannels.
- Perturb away from exact VHS filling and test whether d/i-wave ordering survives.

## Related pages

- [[topics/unconventional-superconductivity|Unconventional superconductivity]]
- [[topics/fermi-and-non-fermi-liquids|Fermi and non-Fermi liquids]]
- [[papers/lu2022cmaus|Correlated metals and unconventional superconductivity in rhombohedral trilayer graphene]]
- [[concepts/intervalley-coherence|Intervalley coherence]]
- [[papers/you2022ksaic|Kohn-Luttinger superconductivity and intervalley coherence in rhombohedral trilayer graphene]]
