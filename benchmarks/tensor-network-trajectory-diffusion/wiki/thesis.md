---
title: Current synthesis
page_type: thesis
status: provisional
updated: '2026-09-08'
source_refs:
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
- labs/lab-001-local-controller-feasibility/REPORT.md
- labs/lab-007-paper-hamiltonian-score-matching/REPORT.md
- labs/lab-009-encoded-recoverability/REPORT.md
idea_ids:
- x-001
- c-001
- c-002
- k-001
- x-002
- c-004
---

# Current synthesis

**Summary**: Corrected projector-splitting TDVP closes the tested dense/MPS gap. A shared local Hamiltonian trained at N=5 executes frozen reversal through N=32, but global recovery accuracy declines with size; state-feature access and dense short-chain training remain explicit limits.

**Sources**: [MQDM paper synthesis](../../../wiki/papers/liu2025mqdm.md); [benchmark task](../problem/TASK.md); [completed Lab 001](../labs/lab-001-local-controller-feasibility/REPORT.md)

**Last updated**: 2026-09-08

---

## Candidate physical-optimum question

The [recoverability candidate](../problem/recoverability/README.md) asks about
optimal recovery of unknown information. [Lab 009](../labs/lab-009-encoded-recoverability/REPORT.md#findings)
now supplies numerical primal/dual references for the complete N=2,4 grid, with
gaps below 1e-8 and resolved record advantages. At N=6,g=.5,eta=.75, the independently
verified interval is [0.9662998449,0.9663149318], width 1.51e-5. Explicit recovery
operations reproduce the achieved lower bounds. These extend Lab 008's analytic
anchors; they are not claims about the historical learned controller's optimality.

The old .02 gate is too loose: a standard transpose recovery with no training or
SDP meets it on every tested N=4,6 cell. Next calibrate N=8 with a proposed 1e-4
width before blind AI trials. No phase transition, low model success rate or
10–20 active-hour requirement has been demonstrated. The earlier trajectory task
remains a preserved research track.

## Current synthesis

The active Hamiltonian branch now has a validated numerical execution path.
On unchanged five-qubit weights and 64 paired trajectories, legacy F=0.2853
becomes F=0.8050 under corrected TDVP, matching dense evaluation. Full-bond
state/gradient tests and 300-step AD checks pass. The old projected-gate
routine is preserved as a historical control; its full-bond exactness claim
is withdrawn [Lab 007 numerical findings](../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#findings).

A frozen 8,780-parameter controller trained at N=5 reaches F=0.8896, 0.6667,
0.4157 and 0.04674 at N=6,8,12,32 with chi=4. Its N=32 reversal takes 90.45 s
for 16 trajectories. Three-qubit training fails much earlier. This is partial
recovery with measured cost, not uniformly accurate scalable recovery
[completed size sweep](../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#completed-size-sweep-through-32-qubits).

At N=8, chi=8 changes target F by about 0.002, but paired chi=4/8 state overlap
is 0.98365; target-F agreement alone does not establish wavefunction
convergence. All large-size runs use exact local state expectations, and
training remains dense at short N. Fixed unique targets do not establish
recovery of arbitrary logical ensembles
[limitations and controls](../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#analysis-and-limitations).

**Current frontier (inference):** Improve controller generalization and
Hamiltonian support under matched budgets, while testing residual chi error.
Keep record-decoder claims separate until the state-feature ceiling is
adequate. See the [implementation](implementations/corrected-tdvp-controller.md)
and [research frontier](ideas/research-frontier.md#2026-09-07--corrected-tdvp-and-frozen-transfer).

## Historical synthesis through 2026-08-23

The paper separates trajectory-level reversal from ensemble recovery. Its companion implementation conditions on future measurement records and projects a full complex matrix to a unitary by QR [companion implementation analysis](../../../wiki/implementations/liu-quantum-diffusion-companion.md). The many-body extension must therefore redesign state representation, policy output, loss evaluation, and deployment together [benchmark algorithmic scope](../problem/TASK.md#Scope-and-approach-boundary).

The primary controller proposal composes generic unitaries supported on at most $R$ consecutive sites. Each fixed-size block can retain the companion's dense complex-matrix-plus-QR parameterization because its cost depends exponentially on $R$, not on the full chain length $N$. Locality lies in the block support, schedule, and spatial parameter sharing. At $N=1,2$ with $R\geq N$, a single allowed block covers the entire system, so a separately named local-gate head is not a distinct hypothesis class. Lab 001 therefore qualifies the companion baseline and encoder/QR seam; the first meaningful locality experiment requires $N>R$ and separate review.

Quimb is the reference backend rather than an incidental dependency. Its documented parametrized circuits and `TNOptimizer` support automatic differentiation, while `CircuitMPS`, MPS gate splitting, and TEBD supply the local tensor-network execution layer ([Quimb tensor optimization](https://quimb.readthedocs.io/en/main/tensor/tensor-optimization.html), [circuit documentation](https://quimb.readthedocs.io/en/latest/tensor/tensor-circuit.html), [1D algorithms](https://quimb.readthedocs.io/en/latest/tensor/tensor-1d.html)). This support does not remove the need for gradient validation: dynamic contraction simplifications and SVD truncation can change which autodiff path is valid.

## Historical baseline support

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

## Historical frontier at 2026-08-23

Lab 001 is complete and qualifies the dense QR behavioral reference and exact encoder/QR refactor at $N=1,2$. The deprecated low-qubit head comparison is preserved as negative design evidence: alternative full-system parameterizations do not test locality when $N\leq R$. The in-flight dense $N=3,R=2$ lab isolates bounded support. Separately, MPS must now be implemented as a small-system correctness backend: at $N=1,2,3$, an untruncated MPS path must reproduce the same dense-vector states, probabilities, reverse updates, losses, gradients, and fixed-budget training behavior before it is used at larger $N$. Passing that gate validates the algorithmic implementation—not a scaling claim—but is sufficient to begin controlled large-$N$ tests. See [the implementation reference](implementations/dense-qr-controller-reference.md), [open question](questions/scalable-trajectory-reversal.md), and [research frontier](ideas/research-frontier.md).

## Related pages

- [Weak-measurement quantum diffusion](../../../wiki/concepts/weak-measurement-quantum-diffusion.md)
- [Trajectory versus ensemble recovery](../../../wiki/comparisons/trajectory-vs-ensemble-recovery.md)
- [Companion implementation](../../../wiki/implementations/liu-quantum-diffusion-companion.md)
- [[implementations/dense-qr-controller-reference|Dense QR trajectory-controller reference]]
