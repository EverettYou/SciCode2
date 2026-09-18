# Author-only evidence and reference-solution inventory

## What can be reused now

All links below preserve Lab 007 as the owner of its scripts, weights, and data.
The new candidate changes both the input task and accessible information; none
of the old target fidelities are values of the new F_opt.

| Existing material | Verified result | Appropriate role | Boundary |
|---|---|---|---|
| [Paired 64-trajectory audit](../../labs/lab-007-paper-hamiltonian-score-matching/results/tdvp-gap-audit-64-v2/summary.json) | Legacy F=0.285326; dense/corrected TDVP F=0.805041, identical weights and records | Numerical-regression example; checks that simulator error can imitate decoder failure | Not an optimum or a logical-information experiment |
| [Full-rollout gradient audit](../../labs/lab-007-paper-hamiltonian-score-matching/results/tdvp-rollout-gradient-audit-v3/summary.json) | 300-step AD comparison at N=3,5; finite nonzero gradients; recorded float32 gradients agree | Validation pattern for differentiable implementations | Two small cases; not scalable training evidence |
| [Frozen N=5 controller transfer](../../labs/lab-007-paper-hamiltonian-score-matching/results/shared-cluster-n5-transfer-v2/summary.json) | chi=4 F=0.8895805,0.6666554,0.4156769 at N=6,8,12 | Executable algorithmic baseline for the historical problem | State features supplied directly; fixed target; single training seed |
| [Large transfer](../../labs/lab-007-paper-hamiltonian-score-matching/results/shared-cluster-large-transfer-v2/summary.json) | N=32, chi=4 F=0.04674197 | Evidence that a trajectory implementation runs at larger N | No large-N chi convergence; no certified optimum |
| [Convergence comparison](../../labs/lab-007-paper-hamiltonian-score-matching/results/shared-cluster-convergence-v2/summary.json) | N=8 chi=4 vs 8 target fidelities close, but paired state overlap about 0.98365 | Motivation for independent state/certificate checks | Similar target overlap alone does not certify evolution accuracy |
| [Ancilla-locked target](../../labs/lab-007-paper-hamiltonian-score-matching/results/shared-ancilla-n5-transfer-v2/summary.json) | Explicit boundary basis conversion; fixed purified target tested through N=12 | Basis-convention regression | Does not establish recovery of arbitrary logical information |
| [Original tests](../../labs/lab-007-paper-hamiltonian-score-matching/test_tdvp_projector.py) | Dense parity, gradient/finite-difference, QR, feature, basis and no-densification controls | Reusable test ideas and numerical components after adaptation | Not a mandatory method for solvers |

The [final manifest](../../labs/lab-007-paper-hamiltonian-score-matching/results/continuation-final-manifest-v2.json)
records 12 summary hashes. The new [audit script](../../labs/lab-008-recoverability-anchors/scripts/audit_existing.py)
checks those hashes and recomputes selected reported statistics. This checks saved
evidence consistency; it does not rerun training or certify the new physical task.
The historical runtime used ambient Torch 2.6.0, not the declared benchmark lock.

## New verifiable reference material supplied with this draft

[Lab 008](../../labs/lab-008-recoverability-anchors/REPORT.md) supplies the exact
one-qubit Z-measurement specialization, with no encoding. It proves and checks

    F_opt(1,g,eta) = (1+sqrt(1-g^2))/2

for every eta in [0,1], and provides both achieving identity-recovery Choi matrices
and dual matrices. The executable grid covers 15 (g,eta) pairs. An independently
constructed Bell-state channel calculation checks fidelity normalization.
Mutation tests reject a false upper bound and a non-trace-preserving recovery.

This is an analytic reference solution **only for the anchor specialization**.
It is intentionally easy and must not be advertised as the scientific challenge.
Its eta independence is also a warning: retaining more records need not strictly
improve the optimum for every model. The proposed many-body record effect must
be demonstrated, not assumed.

## Encoded reference solution now available

[Lab 009](../../labs/lab-009-encoded-recoverability/REPORT.md) implements the precise
candidate encoding and partially observed instrument. The full N=2,4 grid has
saved primal/dual numerical certificates with repaired gaps below 1e-8. The
[comparison artifact](../../labs/lab-009-encoded-recoverability/results/small-grid-comparison-v1.json)
contains both optimal-fidelity intervals and propagated record advantages.

The verifier constructs dense gates and Bell-state channel outputs independently
of the tensor-based producer. It rebuilds each objective and record probability,
checks recovery trace preservation and PSD factors, and checks the dual residual
shift. It does not import the optimizer. Fully observed results also agree with
the polar formula; SCS and Clarabel overlap at N=2,g=.5,eta=.75. The latter emitted
an inaccurate-status warning, but its independently repaired bounds remain valid
numerically and enclose the tighter SCS interval.

This is a numerical reference for finite instances, not a formal interval proof.
The arithmetic guard, repairs, solver statuses, environment lock and source hashes
are recorded. Physical normalization limits and independent constructions pass.

A [standard transpose-recovery baseline](../../labs/lab-009-encoded-recoverability/results/transpose-baselines-v2.json)
already passes the old 0.02 width at N=4,6 for all three strengths in about 0.03 and
2 seconds per cell respectively. The superseded v1 used an overly conservative
normalization bound; its poor values are retained as implementation history and
must not be used to make the baseline appear weak.

## Remaining release work

1. The N=6,g=.5 reference is now verified at width 1.51e-5. Next test N=8 under a measured budget.
   Do not equate execution at N=6 with convergence at N=8,12,16.
2. Validate the proposed 1e-4 large-case width and verifier resource costs. Choose
   required cells using the resolved physical effect and baseline comparisons.
3. Freeze the complete public interface, input manifest, gold data, independent
   verifier and environment; maintain separate solver and author workspaces.
4. Perform blind model trials. No success-rate or 10–20 active-hour claim exists yet.

## Provenance and conceptual basis

- [Reviewed MQDM assessment](../../../../papers/liu2025mqdm/assessment.yml):
  followup_ideas[0] motivates weak-measurement scaling; potential_pitfalls[0:3]
  motivate physical-validity, observable, and trajectory/ensemble separation.
  [Global synthesis](../../../../wiki/papers/liu2025mqdm.md) owns the paper ingest.
  The companion snapshot is unnecessary for this new draft; no code is copied.
- [Fletcher, Shor and Win](https://arxiv.org/abs/quant-ph/0606035): optimal
  entanglement recovery for fixed encoding/noise as a semidefinite program.
- [Beny and Oreshkov](https://arxiv.org/abs/0907.5391): approximate correction
  and near-optimal recovery; motivates algorithm-independent bounds.
- [Gullans and Huse](https://arxiv.org/abs/1905.05195): purification transitions
  and protected quantum information in monitored dynamics. It does not establish
  a transition in the single-measurement-layer family constructed here.

The new circuit and partial-record channel are an author-proposed test family.
No exhaustive novelty search or nontrivial result for that family is claimed.

## Completed N=6 pilot

[Final reference verification](../../labs/lab-009-encoded-recoverability/results/n6-g05-e075-refined/verification.json)
checks all 729 records and encloses F_opt in [0.9662998449,0.9663149318]. The
[explicit quantum recovery check](../../labs/lab-009-encoded-recoverability/results/explicit-recovery-action-n6-v1.json)
independently reproduces its achieved lower bound. The broader adaptive interval
and the interrupted uniform-precision run remain in Lab 009 as evidence of the
cost of allocating solver precision without regard to aggregate contribution.
