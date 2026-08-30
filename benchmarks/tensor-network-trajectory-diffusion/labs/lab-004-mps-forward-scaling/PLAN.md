# Lab 004 execution plan: MPS forward-trajectory resource sweep

## Objective

Measure whether the now parity-validated MPS forward weak-measurement backend
can execute larger one-dimensional chains without dense-vector construction.

## Scope

Run six weak-measurement steps on eight seeded random product-state trajectories
at $N=4,8,16,24,32$. Apply a seeded, fixed sequence of valid local Kraus
outcomes directly on a canonical MPS with `cutoff=0` and no max-bond cap.
This isolates the cost of conditioned local updates from outcome-sampling
overhead. Record wall time, realized bond dimension, norm residual, and the
dense-vector bytes that would be needed only for comparison. This lab contains no reverse controller: the current
frozen companion policy emits a global dense QR unitary and therefore is not a
large-$N$ algorithm.

## Interpretation

Passing shows that the *forward MPS trajectory backend* operates at these
sizes in this low-entanglement setting. It neither establishes learned reverse
control nor a general scalability claim.

## Stable interfaces

`seed, N -> product_MPS`; `MPS, fixed_local_outcome, site -> normalized_MPS`; and `run(N) -> resource_record`.

## Steps

1. Prepare seeded product MPS states.
2. Apply six fixed-record weak-measurement layers.
3. Record norm, bond dimension, time, and dense storage context.

## Completion criteria

Each size completes with finite normalized states and a reloadable resource record.
