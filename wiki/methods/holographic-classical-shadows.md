---
title: Holographic classical shadows
page_type: method
status: provisional
updated: 2026-08-23
source_refs:
- papers/zhang2025hcst/paper.pdf
idea_ids: []
topics:
- Quantum Information
---

# Holographic classical shadows

**Summary**: Hierarchical measurements distribute tomography across length scales, aiming for near-optimal shadow-norm scaling for contiguous Pauli operators without tuning circuit depth to each target.

**Sources**: [Zhang et al. (2025)](../../papers/zhang2025hcst/paper.pdf)

**Last updated**: 2026-08-23

---

## Scale-distributed measurement

In a binary tree, each layer measures half the remaining qudits, so depth \(t\) extracts boundary information at scale \(2^t\). In a holographic random tensor network, radial bulk position plays the same scale role with improved boundary connectivity. Snapshots are classically back-evolved through the corresponding tensor network, and Pauli learning rates determine inverse shadow norms [Zhang et al. (2025), §§I–II](../../papers/zhang2025hcst/paper.pdf#page=2).

The hierarchy removes the need to select a separate optimal circuit depth for each operator size or tune a measurement rate to a critical point. This is an architectural scale prior, distinct from observing an emergent critical measurement transition.

## Sample-complexity results

For a contiguous support of size \(k=2^m\) exactly matching a subtree, the tree protocol gives a shadow-norm bound scaling below the random-Pauli base \((d+1)^k\), approaching base \(d\) at large local dimension. For general contiguous intervals, a statistical-mechanics/minimal-cut analysis of hyperbolic random tensor networks gives \(\|P\|_{\rm sh}^2\simeq d^k f(k)\), where \(f(k)\) is polynomial and geometry-dependent [Zhang et al. (2025), §§III–IV and Eqs. 37–39](../../papers/zhang2025hcst/paper.pdf#page=10).

## Validation boundary

The tree loses translation symmetry and can be unfavorable for supports that do not align with a subtree. Exact holographic Pauli-learning-rate post-processing can scale exponentially, while the stated universal scaling uses a large-\(d\) statistical-mechanics approximation. Random-tensor implementations are also less direct than unitary trees; a general construction reviewed by the authors needs \(O(N)\) auxiliary qudits [Zhang et al. (2025), §§IV–V](../../papers/zhang2025hcst/paper.pdf#page=7).

## Benchmark hooks

- Implement the tree recursion and test aligned versus shifted contiguous supports.
- Compare minimal-cut predictions to exact small-network Pauli learning rates at finite \(d\).
- Measure total quantum and classical cost rather than shadow norm alone.
- Search for unitary/measurement realizations retaining the holographic scaling with fewer ancillas.

## Related pages

- [[concepts/classical-shadow-tomography|Classical shadow tomography]]
- [[comparisons/structured-classical-shadow-protocols|Structured classical-shadow protocols]]
- [[papers/zhang2025hcst|Holographic Classical Shadow Tomography]]
