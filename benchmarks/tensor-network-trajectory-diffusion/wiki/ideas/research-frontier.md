---
title: Tensor-network trajectory-learning frontier
page_type: ideas
status: provisional
updated: '2026-09-08'
source_refs:
- labs/lab-009-encoded-recoverability/REPORT.md
- labs/lab-007-paper-hamiltonian-score-matching/REPORT.md
- wiki/papers/liu2025mqdm.md
- problem/TASK.md
- labs/lab-001-local-controller-feasibility/REPORT.md
idea_ids:
- x-001
- c-001
- c-002
- k-001
- c-003
- k-002
- x-002
- x-003
- c-004
---

# Tensor-network trajectory-learning frontier

**Summary**: Lab 001 qualifies the dense QR reference; Lab 002 isolates bounded support at dense $N=3$, $R=2$, while the next algorithmic gate is to reproduce dense-vector execution with MPS at $N=1,2,3$ before testing larger chains.

**Sources**: [MQDM paper synthesis](../../../../wiki/papers/liu2025mqdm.md); [benchmark task](../../problem/TASK.md); [completed Lab 001](../../labs/lab-001-local-controller-feasibility/REPORT.md)

**Last updated**: 2026-09-08

---

## Active ideas

The user-requested [certified-recoverability candidate](recoverability-candidate.md)
adds k-003 as a separate frontier branch. Lab 009 now verifies N=2,4 optima and
an N=6 width-1.51e-5 pilot; N=8 and blind difficulty calibration remain open.

### x-001 — cross — active

- **Parents:** source root.
- **Origin:** `metadata.idea_sources[0]`.
- **Statement:** Replace dense trajectory-level reverse diffusion with a size-transferable tensor-network learning algorithm.
- **Rationale:** It targets the exponential state and policy-output bottlenecks together and creates a new algorithmic capability.
- **Evidence:** Lab 001 completes the frozen three-seed dense-QR loss/fidelity reference and exact encoder/QR regression at $N=1,2$ [completed report](../../labs/lab-001-local-controller-feasibility/REPORT.md#findings).
- **Next action:** Complete the reviewed Lab 002 cells under their existing scope, and specify a separate small-system MPS parity suite. The suite validates state evolution and learning equivalence at $N=1,2,3$ before large-$N$ use.

### c-001 — code — frontier

- **Parent:** `x-001`.
- **Statement:** Implement canonical-MPS sequential weak-measurement sampling and local nonunitary updates.
- **Keep condition:** The MPS path exactly reproduces dense-vector behavior on frozen small-system cases, so it is a trustworthy algorithmic backend for larger-$N$ tests.
- **Next action:** Build a no-effective-truncation parity suite at $N=1,2,3$. Compare dense and MPS outcome probabilities, normalized forward states, reverse updates, losses, automatic gradients, and fixed-budget training/held-out metrics under identical seeds and weights. Only then activate controlled large-$N$ tests.

### c-002 — code — frontier

- **Parent:** `x-001`.
- **Statement:** Optionally compare translation-equivariant finite-range control-Hamiltonian coefficients, compiled into differentiable Suzuki--Trotter layers, against generic QR block gates once $N>R$.
- **Next action:** Do not run at $N\leq2$ as a locality test; retain for a later matched-support comparison if scientifically useful.

### x-002 — cross — active

- **Parents:** `x-001`.
- **Statement:** Compose generic QR-parameterized unitaries on contiguous blocks of at most $R$ sites and test them on dense trajectories in the nontrivial regime $N>R$.
- **Rationale:** QR remains suitable inside a fixed-size local block; scalability depends on bounded support, composition, and sharing across the chain rather than a special Euler-angle gate head.
- **Next action:** Run Lab 002 Stage 1 only: freeze and validate the three dense $N=3$ state-family fixtures before implementing or training controllers.
- **Evidence boundary:** Lab 001 supports the reference interface but supplies no $N>R$ controller evidence [search decision](../../labs/lab-001-local-controller-feasibility/REPORT.md#search-decision).

### x-003 — cross — active

- **Parent:** `x-002`.
- **Question:** At the cheapest nontrivial size, does composing generic bounded-support QR gates retain useful reversal capacity before spatial parameter sharing or tensor-network approximation is introduced?
- **State-conditioned design:** Use exact dense states at $N=3$ and freeze equal-sized splits separately for three initial-state families: computational-basis and seeded random product states; weakly entangled states from a declared depth-one nearest-neighbor circuit with fixed small entangling angle; and the long-range-correlated $\lvert W_3\rangle=(\lvert100\rangle+\lvert010\rangle+\lvert001\rangle)/\sqrt{3}$ state. Keep the qualified global future-record encoder, measurement convention, loss, dtype, and reversal indexing fixed. Compare a full-system $8\times8$ QR controller, $R=2$ QR gates alternating on $[0,1]$ and $[1,2]$, $R=1$ QR product gates, and no control. Position-conditioned heads isolate support from the later spatial-sharing hypothesis.
- **Resource controls:** Generic QR gates on one, two, and three qubits have different intrinsic dimensions, so parameter count, circuit depth, and applied-gate count cannot all be exactly equalized in one comparison without changing the hypothesis class. Predeclare complementary panels: (A) a raw-QR-coefficient-matched panel with 128 real coefficients per reverse step--one full-system gate, four $R=2$ gates, or sixteen $R=1$ gates--and (B) a depth-and-gate-count-matched panel with six sequential gate slots--six global gates, three alternating $[0,1]/[1,2]$ sweeps, or two balanced $0/1/2$ single-site sweeps--while reporting the resulting parameter counts. Both panels use identical record conditioning, split and initialization seed cells, optimizer steps, batch schedule, stopping rule, and wall-time cap. A support conclusion requires qualitatively consistent ordering across panels; disagreement is resource confounding.
- **State-aware staged execution:** This lab's approved contract remains dense-only: run bounded teacher-forced one-step comparisons for five predeclared initialization seeds per state family and resource panel, and permit multistep reversal only for a cell passing its informativeness and numerical gates. MPS reproduction is a separate algorithm-validation effort, not an alteration of this lab's evidence contract.
- **Primary observables:** Report held-out one-step fidelity and reverse loss, per-family and per-trajectory distributions, paired controller differences, and 95% uncertainty intervals across predeclared seed cells. Also record multistep fidelity only after its gate, unitary residual, finite-difference gradient agreement, gradient norms, wall time, peak memory, native parameter count, circuit depth, and applied-gate count. Pooled means are secondary and cannot replace per-family tables.
- **Informativeness gate:** For each state family and resource panel, define $\Delta_{\mathrm{full},1}=F_{\mathrm{full}}-F_{R=1}$. The family is informative for locality only when the lower 95% confidence bound for $\Delta_{\mathrm{full},1}$ exceeds the predeclared practical tolerance $\delta_F=0.05$ in absolute fidelity. Otherwise record **uninformative: $R=1$ saturation or unresolved full-head advantage** and make no claim about $R=2$.
- **Conditional recovery score:** Only in informative cells compute $q=(F_{R=2}-F_{R=1})/(F_{\mathrm{full}}-F_{R=1})$. Treat $q\geq0.5$ with a 95% interval excluding zero as practically useful partial recovery under that state family and resource panel, not as a universal requirement that $R=2$ beat $R=1$ everywhere.
- **Failure attribution:** Add a direct per-trajectory oracle fit of the same fixed gate schedule as a diagnostic, not a learned-controller baseline. If full QR lacks an advantage over $R=1$, classify saturation or uninformativeness. If full QR and oracle $R=2$ succeed but the record-conditioned $R=2$ head fails, classify record decoding or optimization as the bottleneck. If full QR succeeds but both oracle and learned $R=2$ fail after parity and restart checks, classify a support/depth capacity boundary for that family and panel. If all learned heads fail or gradients are unhealthy, classify an optimization/loss failure. If resource panels disagree, classify resource confounding. Preserve ambiguous cells rather than forcing a locality conclusion.
- **Alternatives considered:** A shared $N=3,R=2$ head is more directly size-transferable but confounds bounded support with spatial sharing; an $N=4,R=2$ brickwork test gives clearer bulk geometry but costs more before the minimal support hypothesis is qualified. Preserve both as follow-ups rather than parallel first experiments.
- **Evidence boundary:** This is a human-approved dense support-isolation experiment, not MPS evidence. The state-aware and matched-panel constraints record closed human checkpoint `T-0006`; they are not empirical findings. MPS reproduction at $N=1,2,3$ is a separate correctness gate and does not change this lab's predeclared cells.

### c-004 — code — frontier

- **Parent:** `x-001`.
- **Origin:** Quimb official tensor-optimization, circuit, and 1D algorithm documentation.
- **Statement:** Establish a pinned Quimb backend, using exact parametrized `Circuit` and MPS gate splitting as parity-checked implementations of the same small-system algorithm.
- **Rationale:** Quimb already supplies the needed circuit/TN abstractions, but differentiability through contraction choices and SVD truncation must be demonstrated.
- **Next action:** Use the pinned environment to implement the $N=1,2,3$ dense-to-MPS parity suite, with effectively untruncated MPS first; retain truncation as a later controlled error study.
- **Evidence:** Lab 001 exact-circuit and finite-difference checks validate the environment and execution path at $N\leq2$ with zero optimizer steps; they do not validate the future controller [limitations](../../labs/lab-001-local-controller-feasibility/REPORT.md#analysis-and-limitations).

### k-001 — knowledge — frontier

- **Parent:** `x-001`.
- **Statement:** Test whether required controller range $R$, record memory $W$, and bond dimension $\chi$ remain bounded in a low-entanglement 1D regime.
- **Keep condition:** The parity-validated MPS backend is available and the selected controller remains well-defined at larger sizes.
- **Next action:** After small-system MPS reproduction passes, run controlled large-$N$ sweeps before making any transfer or scalability claim.

## Frontier alternatives

### c-003 — code — frontier

- **Parent:** `c-002`.
- **Statement:** Replace Trotterized feedback with an MPS tangent-space or TDVP score flow.
- **Keep condition:** TEBD controller capacity succeeds but Trotter or gauge error dominates.
- **Prune condition:** No measurable advantage at matched resources.

### k-002 — knowledge — frontier

- **Parents:** `c-001`, `c-002`, `k-001`.
- **Statement:** Identify whether the scaling boundary is controlled by trajectory entanglement, spatial feedback range, temporal record memory, data, or optimization.
- **Next action:** Cross stress-test results after the baseline regime is established.

## Decision rules

- Treat $N\leq R$ only as baseline/interface qualification; it cannot discriminate global from bounded-range control.
- Parameterize each generic local block by dense QR unless a separately motivated alternative is under test.
- Treat small-$N$ MPS reproduction as an implementation-correctness gate, not a scalability result. Require dense parity at $N=1,2,3$ before using MPS at large $N; study truncation error separately.
- Compare a Hamiltonian parameterization only if it answers a numerical, physical, or interpretability question at matched support; it is not a mandatory low-qubit head.
- Reject a Quimb training path if small-system autodiff gradients fail finite-difference checks or become non-reproducible at the truncation cutoff.
- Keep a scalable controller only after one frozen checkpoint transfers to at least two unseen sizes with convergence in $\chi$, $R$, and $W$.
- Treat a growing resource as a scientific boundary and preserve the negative result.
- Distill code only after dense-to-MPS parity and physical invariant tests pass.

## 2026-09-07 — corrected TDVP and frozen transfer

- **Parents:** c-003, c-002, k-001. Historical proposals below remain as history.
- **Evidence:** The corrected site-forward/bond-backward engine matches dense
  small-system states and gradients. The original projected-gate exactness
  claim is withdrawn. One frozen N=5 shared controller executes to N=32,
  but F falls to 0.04674 while local stabilizers remain partly restored
  [Lab 007 findings](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#findings).
- **Retain:** corrected TDVP, individual stabilizer/full-state metrics, and the
  N=3 transfer failure as a negative branch. Do not equate chi-insensitive
  target F with state convergence.
- **Alternatives:** larger Hamiltonian support; mixed-size training; larger
  MPS manifolds. Decoder changes alone cannot resolve a controller that
  already fails with exact state features (inference).
- **Next action:** compare support and training-size controls at matched
  resources; replicate seeds before a robust scaling claim. Keep the current
  question and separate Petz scope unchanged
  [Lab 007 decision](../../labs/lab-007-paper-hamiltonian-score-matching/REPORT.md#search-decision).

## Related pages

- [Current synthesis](../thesis.md)
- [Scalable trajectory reversal](../questions/scalable-trajectory-reversal.md)
- [[implementations/dense-qr-controller-reference|Dense QR trajectory-controller reference]]
