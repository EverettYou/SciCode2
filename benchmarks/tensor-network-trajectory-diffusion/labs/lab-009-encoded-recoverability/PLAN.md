# Lab 009: close encoded small-system recovery bounds

## Objective

User-authorized continuation: implement the candidate's exact encoded channel,
close optimal-recovery bounds at N=2,4, and measure the record-retention advantage.
Choose larger-size pilot targets only after measuring precision and cost.

## Stable interfaces

The physical definition is problem/recoverability/TASK.md; it is unchanged.
Lab-local scripts and a separate locked uv environment own this experiment.
No original checkpoint, source snapshot, or root dependency lock is modified.
Inputs: N, g, eta, solver, tolerance, output directory. Outputs: numerical primal
and dual certificates, independently recomputed residuals, bounds, timings, hashes.

## Steps

1. Build the encoding and instrument; compare independent tensor/dense constructions,
   Born completeness, isometry, complex Choi conventions, and limiting cases.
2. Solve N=2 at g=.2,.5,.8 and eta=.75,1 using an SDP. Check SCS and Clarabel on
   overlapping cases and compare fully observed optima with the polar formula.
3. Repair primal/dual feasibility explicitly; count repair costs in bound widths.
   Preserve raw solver outputs and reconstructed certificates. Distinguish numerical
   verification from formal interval-arithmetic proof.
4. If controls pass, solve N=4 on the same grid. Initial compute allocation is
   20 minutes; checkpoint each record and adjust implementation based on measured
   cost rather than launch an unbounded larger run.
5. Test N=6 only if cost and accuracy support a bounded pilot. Record the actual
   achieved gap instead of silently relaxing the draft's small-case 1e-8 target.
6. Update report, candidate evidence/evaluation/difficulty, and wiki with findings.

## Completion criteria

At least N=2,4 nontrivial g=.5 cases have independently checked enclosing numerical
bounds, or a concrete failure/shortcut changes the next experiment. Prefer the
three-strength grid when feasible. Report whether record advantage is resolved,
which accuracy is attainable, and a justified next size/precision recommendation.
No AI failure-rate or phase-transition claim follows from this lab alone.

## Measured precision-allocation refinement

N=6 uniform eps=1e-9 stalled on support-64 branches after 121 records. Preserve
that partial run. Reuse its verified certificates; cap support>=64 at 1000 SCS
iterations and support>=32 at 2000, eps=1e-6. Smaller supports retain eps=1e-9.
All approximate solves require full-space repair and their actual weighted gaps
enter the aggregate interval. Target 1e-4 for this bounded N=6 pilot.

The initial 20-minute allocation is extended to a bounded 30-minute total compute
pilot to finish all 729 N=6 branches and independent verification after successful
small-grid closure. The interrupted uniform run counts toward that cost. No N=8
run is launched in this continuation.
