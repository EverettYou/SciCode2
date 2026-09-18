---
title: Corrected TDVP controller and transfer boundary
page_type: implementation
status: provisional
updated: '2026-09-07'
source_refs:
- labs/lab-007-paper-hamiltonian-score-matching/REPORT.md
idea_ids:
- c-003
- k-001
topics:
- Quantum Information
- Machine Learning
---

# Corrected TDVP controller and transfer boundary

**Summary**: The corrected local-generator TDVP backend reproduces dense
small-system evolution; a frozen shared controller executes through 32 qubits
but retains a substantial size-dependent global recovery error.

**Sources**: [Lab 007 report](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#findings)

**Last updated**: 2026-09-07

## Validated implementation boundary

The old routine projected a two-site gate onto one tensor. The replacement
uses a bond-5 MPO for the full frozen generator and alternates forward site
and backward bond-center evolution. Zero-diagonal QR phases preserve an
isometric basis instead of zeroing columns. Tests compare physical states,
nonzero gradients and finite differences against dense truth; separate
300-step AD checks pass at N=3,5
[TDVP audit](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#numerical-repair-paired-frozen-checkpoint).

One-site TDVP keeps the supplied bond spaces. It does not provide an SVD
truncation error bound. Coefficients and backaction remain fixed within a
macro step, including internal refinement; this is not feedback-timestep
convergence [refinement controls](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#refinement-and-ancilla-controls).

## Controller and observed boundary

Site heads see three-site Pauli windows; bond heads see the union of adjacent
windows, at most four sites. The 8,780 network parameters are shared across N.
Short-chain training uses dense evolution, with local MPS features and
updates independently checked. Larger evaluation uses only MPS contractions,
local coefficients and effective center exponentials
[methods](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#methods-and-execution).

The N=5-trained checkpoint gives F=0.9869 at N=5, 0.6667 at N=8, and 0.04674
at N=32. At N=32 the mean three-site trace distance is 0.2939 and the minimum
mean stabilizer is 0.6894. These metrics jointly show partial local recovery
and poor global recovery, rather than a successful full-state scalability
claim [size sweep](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#completed-size-sweep-through-32-qubits).

Ancilla-locked cluster states are tested under an explicit fixed endpoint
Hadamard conversion of the features and Hamiltonian, with physical on-site
noise unchanged. F=0.9861, 0.6722 and 0.4181 at N=5,8,12. This is unique-state
recovery, not a demonstrated teleportation protocol or an arbitrary logical
ensemble recovery [ancilla controls](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#refinement-and-ancilla-controls).

## Related pages

- [Current synthesis](../thesis.md)
- [Research frontier](../ideas/research-frontier.md)
- [Scalable trajectory reversal](../questions/scalable-trajectory-reversal.md)
