---
title: Random-tensor-network entanglement transitions
page_type: concept
status: provisional
updated: 2026-08-23
source_refs:
- papers/vasseur2019etfhr/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Random-tensor-network entanglement transitions

**Summary**: Changing random-tensor bond weights or geometry can drive boundary states between area-, volume-, and subextensive entanglement regimes described by replica domain-wall statistical mechanics.

**Sources**: [Vasseur et al. (2019)](../../papers/vasseur2019etfhr/paper.pdf)

**Last updated**: 2026-08-23

---

## Boundary entanglement as bulk ordering

Averaging random tensors with a generalized replica trick maps boundary Rényi observables to fluctuating permutation-domain-wall free energies in a classical bulk spin model. Bond dimension controls the effective coupling: ordered bulk spins impose an extensive domain-wall cost and volume-law boundary entanglement, whereas disorder screens the cut and gives area-law entanglement [Vasseur et al. (2019), §§II–IV](../../papers/vasseur2019etfhr/paper.pdf#page=3).

Allowing the network graph itself to fluctuate couples the critical matter theory to two-dimensional quantum gravity. KPZ dressing changes scaling dimensions, while the fractal boundary geometry makes a large-bond minimal cut scale as (sqrt{L_A}), producing a subextensive, non-ETH entanglement phase between familiar area- and volume-law patterns [Vasseur et al. (2019), §V](../../papers/vasseur2019etfhr/paper.pdf#page=13).

## Interpretation boundary

The ensemble models entanglement statistics rather than eigenstates of a specified local Hamiltonian. Its continuous area-to-volume-law transition differs from a direct MBL–thermal transition, where thermodynamic entropy forces a discontinuity in the volume-law coefficient. Parent Hamiltonians, finite-bond critical numerics, symmetry effects, and the relation to monitored-circuit transitions remain open [Vasseur et al. (2019), §VI](../../papers/vasseur2019etfhr/paper.pdf#page=15).

## Benchmark hooks

- Derive replica spin weights for a small planar RTN and compare against direct tensor averages.
- Locate the finite-bond transition numerically and separate nonuniversal (D_c) from universal exponents.
- Reproduce KPZ-dressed dimensions on fixed versus fluctuating graph ensembles.
- Test minimal-cut scaling under tunable graph measures and boundary fractal dimensions.

## Related pages

- [[methods/replica-statistical-mechanics-of-monitored-circuits|Replica statistical mechanics of monitored circuits]]
- [[methods/learned-statistical-gravity|Learned statistical gravity from entanglement]]
- [[methods/holographic-classical-shadows|Holographic classical shadows]]
- [[topics/entanglement-structure-and-dynamics|Entanglement structure and dynamics]]
- [[papers/vasseur2019etfhr|Entanglement transitions from holographic random tensor networks]]
