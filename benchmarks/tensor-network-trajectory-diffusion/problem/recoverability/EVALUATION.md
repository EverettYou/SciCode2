# Author-only evaluation design

Status: analytic anchors plus a numerically verified N=2,4 reference grid now
exist in [Lab 009](../../labs/lab-009-encoded-recoverability/REPORT.md). Larger-case
release and formal interval-arithmetic certification remain pending. Do not expose this directory in a
blind solver workspace merely by hiding it from the prompt.

## Quantity being graded

Grade intervals containing the unrestricted deterministic optimum in TASK.md.
Runtime and memory rank solutions only after correctness and precision gates.
Do not use Lab 007 target-state fidelities as expected answers for this channel.

For finite exact computations, a useful canonical certificate convention is:

- A_c,h: effective Kraus maps from logical input dimension 2 to physical dimension
  D=2^N, including the encoding and square roots of record-mask probabilities;
  h indexes erased outcomes compatible with c.
- v_c,h=vec_row(A_c,h^dagger), with indices (logical output a, physical input b).
- C_c=sum_h v_c,h v_c,h^dagger / 4.
- Recovery Choi matrix J_c has the same output/input ordering and is unnormalized.

Then a primal certificate obeys

    J_c >= 0,   Tr_output J_c = I_D,
    L = sum_c Tr(C_c J_c).

A dual certificate obeys

    Y_c = Y_c^dagger,   I_2 tensor Y_c - C_c >= 0,
    U = sum_c Tr(Y_c).

These conventions follow directly from F_e=sum_(c,h,r)|Tr(R_c,r A_c,h)|^2/4.
Zero-probability records contribute zero. An independent verifier constructs C_c
from the public physical instance; it must not trust a submitted C_c.

At larger N, alternate certificates/representations are allowed. Their admissible
formats and independent verifiers must be established before benchmark release.
In particular, bounding a restricted recovery ansatz is not an upper bound on
the unrestricted optimum. A dense certificate with exponentially many records
is not assumed feasible within the challenge budget.

## Required gates

| Gate | Check | Present status |
|---|---|---|
| Physical definition | Kraus completeness, encoding isometry, record probabilities, inaccessible-reference boundary | Independent tensor/dense encoded instrument checks pass at N=1–4 |
| Analytic anchors | No noise gives 1; a completely input-erasing channel gives 1/4; a projective single-qubit Z measurement gives 1/2 | Implemented in Lab 008 |
| Certificate validity | Hermiticity, PSD, recovery trace preservation, dual slack PSD, independently rebuilt objective | Exact anchors plus saved full-space N=2,4 numerical certificates |
| Optimality | Primal/dual agreement for small nontrivial encoded instances | N=2,4 complete grid, repaired gaps below 1e-8; see Lab 009 |
| Numerical reliability | Precision/solver tolerance, truncation and sampling error; reproducible independent comparisons | Lab 007 supplies transferable controls, not validation of the new channel |
| Larger instances | Valid interval of required width inside resource budget | N=6,g=.5,eta=.75 verified at width 1.51e-5; N=8 pending |
| Record advantage | F_opt(eta=1) >= F_opt(eta=.75) | Mathematical ordering: the fully informed receiver may erase records itself |
| Interpretation | Claims follow from intervals; no automatic phase-transition conclusion | Numerical checks plus author review before release |

Use tolerances with explicit error accounting. An eigensolver reporting a tiny
negative eigenvalue is a diagnostic, not a rigorous certificate by itself.
For a dense dual slack S, a certified lower eigenvalue bound lambda_min(S)>=-delta
allows replacement Y -> Y+delta I_D, increasing the upper bound by D*delta.
Use controlled arithmetic or a justified backward-error bound for delta. Primal
feasibility requires a valid recovery or a repaired certificate with its objective
recomputed. Record such corrections instead of silently clipping claimed answers.

The current anchor verifier uses floating-point residuals at tolerance 1e-10,
backed by an independent exact derivation. It does not provide rigorous interval
arithmetic or establish a universal tolerance for larger certificates.

## Sampling and trends

All-record enumeration and trajectory Monte Carlo are distinct evaluation modes.
For sampling, require independent evaluation samples and a prespecified confidence
construction (target simultaneous coverage at least 99% over the released grid).
Do not accept narrow intervals produced by repeated stopping on favorable data.
Record uncertainty from approximating each branch as well as Monte Carlo error.

If [L1,U1] and [L0,U0] enclose the two optimal fidelities, a valid advantage interval
is [L1-U0,U1-L0], intersected with [0,1]. An empty intersection is a failure.
Only claim a resolved record advantage if its lower endpoint exceeds zero after
all error accounting. Interval overlap is not proof of absence of an effect.

No monotonicity in N or g is imposed as an evaluator invariant without a proof
for this specific constructed family. Do not equate the one-qubit 1/2 anchor
with every multi-qubit project's exact value. For projective measurements on
all physical sites the effective channel is entanglement breaking, so 1/2 is
an upper bound on single-logical-qubit entanglement fidelity, not generally an
achievable value for an arbitrary encoded measurement ensemble.

## Resistance to evaluator gaming

- Recompute outcomes and channel operators independently of solver output.
- Reject nonfinite values, malformed dimensions, invalid CPTP maps, and omitted
  record-probability factors. Preserve complex conjugation and fidelity conventions.
- Include limiting cases and independently certified held-out small instances.
- Test a recovery on an entangled input; known-state reset earns 1/4, not 1.
- If a solver returns a tighter valid interval than the gold solution, accept it.
  If certified intervals are disjoint, audit the reference as well as the solver.
- Counterexample/mutation tests must reject invalid trace constraints and falsely
  low upper bounds. Lab 008 implements these for its certificate path.

## Release condition

Publish only after a full reference run, a second implementation or independently
verified certificate route, resource calibration, and blind-model trials. Persist
the frozen instance manifest, verifier version, reference hashes, confidence
policy, and complete pass criteria. JSON schema checks alone do not validate physics.

## Encoded reference implementation

Use [verify_saved.py](../../labs/lab-009-encoded-recoverability/scripts/verify_saved.py)
to reconstruct channel objectives with dense gates and explicit Bell states, then
check every saved recovery/dual certificate. The verifier does not import CVXPY.
[certificates.py](../../labs/lab-009-encoded-recoverability/scripts/certificates.py)
constructs PSD factors, completes a trace-nonincreasing recovery by reset, and
shifts the dual by its PSD-factor reconstruction residual. Repair penalties are
included in reported bounds. The double-precision arithmetic guard is 1e-12 per
normalized branch; this is numerical validation, not a formal interval proof.

The fully observed polar formula independently checks all eta=1 results. A
second solver checks the N=2,g=.5,eta=.75 instance. Support-reduced optimization
agrees with the original full-space N=4,g=.5 result and is verified only after
lifting its certificates back into the full physical space.
