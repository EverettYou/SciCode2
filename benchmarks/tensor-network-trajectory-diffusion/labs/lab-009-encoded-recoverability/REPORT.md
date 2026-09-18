---
document_type: lab_report
lab_id: lab-009
status: completed
idea_ids:
  - k-003
wiki_context:
  - ../../wiki/ideas/recoverability-candidate.md
related_labs:
  - lab-008-recoverability-anchors
---

# Encoded small-system recoverability

## Motivation

Determine whether the proposed physical-optimum benchmark has a nontrivial,
verifiable reference solution before selecting larger sizes or difficulty targets.

## Design

Use the exact constructed encoder and partially observed one-layer weak-measurement
channel in the candidate TASK. Compare eta=.75 and eta=1 on identical physical codes.
Preregistered execution and evidence gates are in PLAN.md.

## Methods

The experiment combines two physical constructions, branchwise convex optimization,
explicit feasibility repair, and solver-independent recovery verification.

### Physical construction and observable

`physical.py` implements exactly the encoding, one-layer tilted weak measurement,
and independently erased records in the candidate TASK. It evolves the two
encoding columns with tensor-index gates. A second construction uses full dense
gates and explicit unnormalized Bell-state channel outputs. These agree at N=1–4.
Kraus completeness and encoding isometry are checked. All classical records are
enumerated; there is no Monte Carlo error or training.

For each record c, the objective is C_c=sum_h vec(A_c,h^dagger)
vec(A_c,h^dagger)^dagger/4. Optimize a recovery Choi matrix J with J>=0 and
Tr_output J=I. The trace-constraint dual gives Y with I_2 tensor Y>=C.
Each branch objective is normalized by Tr(C) to avoid confusing small physical
record probabilities with solver tolerance; the weight is restored in the sum.
The total Tr(C) across records is 1/2 under this convention.

### Feasibility repair and independent verification

For a returned primal, take a PSD factor X and J0=XX^dagger. Bound the largest
eigenvalue of T=Tr_output J0 by its maximum absolute row sum, choose scale s at
least that bound, and complete J0/s by |0><0| tensor (I-T/s). This gives a
trace-preserving recovery in exact arithmetic. Its achieved objective is the
reported lower bound, including any loss from the repair.

For a returned dual, form slack S=I tensor Y-C, its positive-part factor B, and
residual E=S-BB^dagger. Shifting Y by (norm(E,F)+guard) I makes its slack PSD
in exact arithmetic by norm(E,2)<=norm(E,F). The resulting increase in Tr Y is
included in the upper bound. The arithmetic guard is 1e-12 per normalized branch.
All reported results are double-precision numerical bounds; no formal interval
arithmetic certification of the physical matrix construction is claimed.

`verify_saved.py` reconstructs C using dense gates and explicit Bell evolution,
checks record weights and all saved matrices/factors, then recomputes aggregates.
It imports no optimizer. Fully observed optima independently agree with
sum_c (Tr sqrt(A_c^dagger A_c))^2/4. A Clarabel solve overlaps the SCS result
at N=2,g=.5,eta=.75.

### Fully observed analytic optimum and upper bound

For one known effective Kraus map A, let Q=sqrt(A A^dagger) and t=Tr Q.
Polar recovery achieves t^2/4 on that unnormalized branch. The dual choice
Y=t Q^T/4 has trace t^2/4 and is feasible: on its support, the rank-one PSD
condition reduces to vec(A^dagger)^dagger (I tensor Y)^+ vec(A^dagger)/4=1.
The zero-support case contributes zero. Thus summing t^2/4 over known outcomes
is the optimum at eta=1 for any encoded instance in this task, not only an
empirical fit to the small grid. Providing additional outcomes cannot decrease
optimal recovery, so that value is also an upper bound when eta<1.

The [explicit joint-state action check](results/explicit-recovery-action-v1.json)
factors the saved Choi matrices into recovery Kraus operators and evolves Bell
inputs directly. At N=2,4,g=.5,eta=.75, its fidelities match the saved lower bounds
within 2.2e-15; joint-state traces agree with one within 2.6e-15. This computation
uses neither the SDP objective matrix nor its trace-score formula.

### Support reduction and bounded scaling pilot

With m erased outcomes, at most 2^m effective Kraus maps each have two columns,
so their joint output support has dimension at most min(2^N,2^(m+1)). Optimize
on that support, then lift the recovery and dual to the full physical space and
apply the same repairs. The full-space verifier counts projection residuals;
a potentially inaccurate reduced problem cannot silently certify the full one.
At N=4,g=.5 this route agrees with the original dense-space solve.

The initial N=6 uniform-precision pilot was interrupted after 121 saved branches
when a support-64 branch became expensive. Its partial artifacts are preserved.
The adaptive continuation re-verifies and reuses those branches, allows eps=1e-6
with iteration caps on support>=32, and includes each actual weighted gap in the
aggregate. The target for this larger pilot is 1e-4, not the small-case 1e-8.

## Findings

The complete small grid and one larger pilot meet their numerical precision gates;
standard recovery baselines show why the original difficulty threshold was too loose.

### Complete N=2,4 reference grid

All 12 cells passed independent numerical verification. The table rounds the
fidelities for readability; exact intervals and propagated differences are in
[small-grid-comparison-v1.json](results/small-grid-comparison-v1.json).

| N | g | F_opt, eta=.75 | F_opt, eta=1 | Advantage of full records |
|---|---|---|---|---|
| 2 | .2 | .9912739275 | .9915539522 | .0002800247 |
| 2 | .5 | .9415251392 | .9434263703 | .0019012312 |
| 2 | .8 | .8186717872 | .8235305531 | .0048587659 |
| 4 | .2 | .9990110806 | .9993466939 | .0003356134 |
| 4 | .5 | .9825753510 | .9845573658 | .0019820149 |
| 4 | .8 | .8854752523 | .8898112353 | .0043359831 |

Maximum aggregate gap in the primary SCS grid is about 4.75e-10, well below the
1e-8 calibration target. All six record advantages have positive lower bounds.
At N=4, partial-record runs took about 212,29,20 seconds for g=.2,.5,.8 respectively;
fully observed runs took about two seconds each. N=2 runs took less than a second.
These are measured single-thread CPU wall times with some concurrent independent
validation work, not universal performance guarantees.

Clarabel's N=2,g=.5 result had a repaired gap about 2.10e-9 and enclosed the tighter
SCS interval. Some solver calls reported inaccurate status or intermediate NumPy
warnings; all retained objective and certificate arrays are finite and independently
pass the feasibility checks. Solver status alone is not the acceptance criterion.

### Controls

Twelve tests pass: independent physical constructions at N=1–4, Kraus/analytic
limits, dual and primal mutation rejection, and fully observed transpose-recovery
checks. Separate SDP limiting cases recover F=1 without noise and F=.5 for
fully recorded projective measurement at N=2. Their numerical bounds enclose the
exact values. Reset-to-known-state is distinguished by the earlier Lab 008 anchor.

### The original difficulty threshold is too loose

[Transpose baseline v2](results/transpose-baselines-v2.json) uses no training and
no SDP. It constructs a CPTP transpose recovery and uses the fully observed
analytic optimum as an upper bound. At N=4 its interval widths are .000484,
.004371,.013777 for g=.2,.5,.8; at N=6 they are .000929,.004748,.013338. Every
one passes the old .02 gate. Measured N=6 runtime is about 1.6–1.9 seconds per cell.
The effect to be measured is itself much smaller than .02.

Baseline v1 used a maximum-row-sum bound on an almost-projector to normalize its
recovery; that bound unnecessarily degraded performance. V2 uses a spectral bound
with explicit eigendecomposition residual and orthogonality allowance. V1 remains
as an implementation caution and is not evidence that standard recovery is weak.

### N=6 pilot

The N=6,g=.5,eta=.75 pilot completed on 2026-09-08. All 729 record branches were
independently verified. The final result is

    0.9662998449042627 <= F_opt <= 0.9663149318108604,
    interval width = 1.5086906598e-5.

The analytic fully observed value is 0.9675171289514439, giving a resolved
record advantage in [0.0012021971405835, 0.0012172840471812]. See
[n6-comparison-v1.json](results/n6-comparison-v1.json) and the
[final verification](results/n6-g05-e075-refined/verification.json).

The first adaptive result had width 2.123522e-4. One branch, [1,0,0,0,0,-1],
contributed about 93% of the width because an inaccurate primal required a costly
feasibility repair. Refining only that branch with eps=1e-8 and 20,000 maximum
iterations took 11.3 seconds and reduced the total width below the 1e-4 target.
The initial partial run and the wider adaptive result remain available.

Adaptive solve plus refinement took 816.6 seconds (13.6 minutes), excluding the
approximately 4.6-minute interrupted uniform run. The adaptive producer recorded
peak RSS about 1.31 GiB. Reused work and the interrupted attempt must be counted
when quoting end-to-end cost. No N=8 experiment was launched.

The [explicit N=6 recovery-action check](results/explicit-recovery-action-n6-v1.json)
applies recovery Kraus operators to joint Bell inputs on every record. It matches
the saved lower bound within 5.6e-14 and has trace residual 1.7e-13. Negative Choi
eigenvalues removed in this diagnostic have total weighted mass 2.9e-13; the
primary certificate verifier checks the original saved factors and completions.
These are controlled numerical checks, not a formal interval proof.

## Reproduction and provenance

See [README.md](README.md) for solve/test/verify commands. Runtime is a separate
uv-locked environment: Python 3.13.2, NumPy 2.5.3, CVXPY 1.9.2, SCS 3.3.1,
Clarabel 0.11.1. BLAS and OMP thread counts are one. No root or historical benchmark
lock was modified. Each completed solve records its source hashes and lock hash;
raw and repaired certificates are retained alongside progress and summary files.
All recorded source revisions are archived in results/source-snapshots-v1 and
coverage.json reports no missing revisions. A diagnostic-only correction removed
an inherited pre-refinement solver_value field from the final summary; the previous
summary/verification are retained, and all bounds/certificate arrays are unchanged.

The optimizer API follows the official [CVXPY solver documentation](https://www.cvxpy.org/tutorial/solvers/index.html)
and [complex/PSD constraint documentation](https://www.cvxpy.org/tutorial/constraints/index.html).
The SDP scientific basis is [Fletcher, Shor and Win](https://arxiv.org/abs/quant-ph/0606035).
The candidate physical family is author-constructed and matches the task definition.

## Limitations

These are finite-instance numerical optima for the specified encoding and channel.
They imply neither a universal scaling law nor a phase transition. The small grid
does not demonstrate 10–20 active hours of work or low AI success probability.
Independent numerical checks do not constitute a formal interval-arithmetic proof.
The current full-space certificate format and all-record enumeration still grow
exponentially; larger execution and verification costs need separate calibration.

## Search decision

Keep the physical-optimum formulation: it now has nontrivial reproducible reference
results and a resolved record effect. Retire .02 as a useful difficulty gate.
Keep 1e-8 for N=2,4 reference checks, the now-demonstrated 1e-4 pilot at N=6, and next test N=8 at g=.5,.8
with the same width before freezing a challenge grid. Defer N=12,16 as required sizes. This rejects
one simple baseline; it does not prove that AI or another straightforward method
cannot solve the revised task.

## Wiki ingest handoff

Ingest this report and selected comparison/certificate artifacts into the
recoverability candidate, evidence inventory and local thesis. Preserve the
historical fixed-target task and Lab 007's narrower evidence boundary.
