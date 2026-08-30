---
title: Current synthesis
page_type: thesis
status: provisional
updated: '2026-08-23'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
- labs/lab-001-local-controller-feasibility/REPORT.md
idea_ids:
- x-001
- c-001
- c-002
- k-001
- x-002
- c-004
---

# Current synthesis

**Summary**: Lab 001 establishes a reproducible low-qubit dense-QR reference and exact encoder/QR seam, but the size-transferable tensor-network question remains open because locality is nontrivial only when $N>R$.

**Sources**: [MQDM paper synthesis](../../../wiki/papers/liu2025mqdm.md); [benchmark task](../problem/TASK.md); [completed Lab 001](../labs/lab-001-local-controller-feasibility/REPORT.md)

**Last updated**: 2026-08-23

---

## Current synthesis

The paper separates trajectory-level reversal from ensemble recovery. Its companion implementation conditions on future measurement records and projects a full complex matrix to a unitary by QR [companion implementation analysis](../../../wiki/implementations/liu-quantum-diffusion-companion.md). The many-body extension must therefore redesign state representation, policy output, loss evaluation, and deployment together [benchmark algorithmic scope](../problem/TASK.md#Scope-and-approach-boundary).

The primary controller proposal composes generic unitaries supported on at most $R$ consecutive sites. Each fixed-size block can retain the companion's dense complex-matrix-plus-QR parameterization because its cost depends exponentially on $R$, not on the full chain length $N$. Locality lies in the block support, schedule, and spatial parameter sharing. At $N=1,2$ with $R\geq N$, a single allowed block covers the entire system, so a separately named local-gate head is not a distinct hypothesis class. Lab 001 therefore qualifies the companion baseline and encoder/QR seam; the first meaningful locality experiment requires $N>R$ and separate review.

Quimb is the reference backend rather than an incidental dependency. Its documented parametrized circuits and `TNOptimizer` support automatic differentiation, while `CircuitMPS`, MPS gate splitting, and TEBD supply the local tensor-network execution layer ([Quimb tensor optimization](https://quimb.readthedocs.io/en/main/tensor/tensor-optimization.html), [circuit documentation](https://quimb.readthedocs.io/en/latest/tensor/tensor-circuit.html), [1D algorithms](https://quimb.readthedocs.io/en/latest/tensor/tensor-1d.html)). This support does not remove the need for gradient validation: dynamic contraction simplifications and SVD truncation can change which autodiff path is valid.

## Strongest support

- Lab 001 freezes $N=1,2$ trajectory splits, reproduces the companion dense-QR behavior across three seeds per size, and validates an exact encoder/QR refactor. Mean held-out reversal fidelity is $0.652636\pm0.022455$ at $N=1$ and $0.420085\pm0.005803$ at $N=2$, with broad per-trajectory variation [Lab 001 findings](../labs/lab-001-local-controller-feasibility/REPORT.md#findings).
- The copied and refactored policies agree exactly on compared unitaries, losses, and gradients, providing a qualified implementation seam for a later bounded-block controller [QR-refactor evidence](../labs/lab-001-local-controller-feasibility/REPORT.md#findings).
- The existing dense one- and two-qubit code supplies a direct baseline and the generic QR parameterization reusable inside bounded-size block gates.
- Single-site weak Kraus updates admit local MPS application and sequential conditional sampling in the later execution phase.
- Composing QR-parameterized bounded-support gates removes the full-system dense unitary while retaining a robust parameterization within each block.
- A Hamiltonian/Trotter controller remains an optional comparator for continuous-time structure or interpretability once $N>R$; it is not a prerequisite low-qubit head.
- Exact state vectors and companion behavior provide parity tests before truncation.
- Oracle-feature and record-only variants separate ansatz capacity from inference difficulty.

## Tensions and alternatives

- The ideal inverse may require spatial range or temporal memory that grows with time or correlation length.
- Differentiating through long tensor-network rollouts may be unstable despite efficient forward contraction.
- The benchmark-local uv environment resolves the earlier ambient Quimb/Numba/NumPy incompatibility with Quimb 1.11.2, NumPy 2.2.6, and Numba 0.61.2. Zero-step exact-circuit, finite-difference, and no-truncation `CircuitMPS` checks validate execution only [Lab 001 limitations](../labs/lab-001-local-controller-feasibility/REPORT.md#analysis-and-limitations).
- The raw reverse loss is not calibrated across system sizes: Lab 001 observes a lower loss but lower fidelity at $N=2$, so loss alone cannot rank physical reversal quality across $N$ [Lab 001 limitations](../labs/lab-001-local-controller-feasibility/REPORT.md#analysis-and-limitations).
- Local-observable agreement can conceal wrong trajectory distributions or entanglement.
- TDVP tangent-space feedback is an alternative if TEBD passes capacity tests but suffers dominant Trotter/gauge error.

## Frontier

Lab 001 is complete and qualifies the dense QR behavioral reference and exact encoder/QR refactor at $N=1,2$. The deprecated low-qubit head comparison is preserved as negative design evidence: alternative full-system parameterizations do not test locality when $N\leq R$. The in-flight dense $N=3,R=2$ lab isolates bounded support. Separately, MPS must now be implemented as a small-system correctness backend: at $N=1,2,3$, an untruncated MPS path must reproduce the same dense-vector states, probabilities, reverse updates, losses, gradients, and fixed-budget training behavior before it is used at larger $N$. Passing that gate validates the algorithmic implementation—not a scaling claim—but is sufficient to begin controlled large-$N$ tests. See [the implementation reference](implementations/dense-qr-controller-reference.md), [open question](questions/scalable-trajectory-reversal.md), and [research frontier](ideas/research-frontier.md).

## Related pages

- [Weak-measurement quantum diffusion](../../../wiki/concepts/weak-measurement-quantum-diffusion.md)
- [Trajectory versus ensemble recovery](../../../wiki/comparisons/trajectory-vs-ensemble-recovery.md)
- [Companion implementation](../../../wiki/implementations/liu-quantum-diffusion-companion.md)
- [[implementations/dense-qr-controller-reference|Dense QR trajectory-controller reference]]
