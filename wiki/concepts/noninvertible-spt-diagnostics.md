---
title: Non-invertible SPT diagnostics
page_type: concept
status: provisional
updated: '2026-08-22'
source_refs:
- papers/lu2025scaso/paper.pdf
idea_ids: []
topics:
- Topological Phases
---

# Non-invertible SPT diagnostics

**Summary**: Strange correlators, decorated string operators, interface algebras, and entanglement-spectrum degeneracies provide tensor-network diagnostics for 1+1D phases protected by non-invertible symmetries.

**Sources**: [Lu et al. (2025)](../../papers/lu2025scaso/paper.pdf)

**Last updated**: 2026-08-22

---

## Current synthesis

For injective MPS fixed points, strange charged operators are local insertions constrained by the interface algebra between two non-invertible SPT phases. Their strange correlator remains long-ranged between distinct phases and decays otherwise [Lu et al. (2025), §Sec.3-and-Sec.5](../../papers/lu2025scaso/paper.pdf#Sec.3-and-Sec.5). String order is built by truncating a symmetry MPO and attaching charge-decoration tensors determined by the phase action tensors.

The Rep$(D_8)$ examples show how MPS/MPO contractions and ZX calculus expose categorical data. Entanglement-spectrum degeneracy is tied to irreducible representations of the interface algebra under the stated onsite realization assumptions [Lu et al. (2025), §Sec.5](../../papers/lu2025scaso/paper.pdf#Sec.5).

## Open boundary

The higher-dimensional generalization is not a direct copy: interfaces contain interacting operators of several codimensions. Numerical benchmarks should first verify the 1D tensor identities and finite-size convergence before extrapolating the diagnostic.

## Related pages

- [[methods/twisted-lattice-gauging|Twisted lattice gauging]]
- [[methods/quantum-process-code-constructions|Quantum processes for code constructions]]
- [[papers/lu2025scaso|Strange correlator and string order parameter for non-invertible SPT phases]]
