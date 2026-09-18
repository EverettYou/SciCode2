# Lab 008: exact recoverability anchors

## Objective

Make the observable and verification mechanism of the user-requested benchmark
candidate concrete. Complete a bounded anchor lab, not a large-system gold solution.

## Stable interfaces

No root src dependency or promotion. The [candidate](../../problem/recoverability/TASK.md)
defines the prospective physical task. Local anchors accept g,eta in [0,1] and
produce primal/dual residuals and source/environment provenance. Lab 007 is read-only.

## Steps

1. Derive the unencoded one-qubit optimum and construct primal/dual certificates.
2. Verify certificates by independently rebuilding physical objective matrices.
3. Cross-check explicit Bell-state evolution and analytic limits.
4. Test rejection of false upper bounds, invalid trace preservation and NaNs.
5. Audit historical artifact hashes and selected statistics without retraining.
6. Record limitations and the next nontrivial reference experiment.

## Completion criteria

15 anchors match the analytic expression; seven tests pass; 12 historical summary
hashes agree; evidence distinguishes anchors, infrastructure and missing gold results.
