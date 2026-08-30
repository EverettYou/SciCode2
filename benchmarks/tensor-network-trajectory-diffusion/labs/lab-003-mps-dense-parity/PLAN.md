# Lab 003 execution plan: small-system MPS/dense parity

## Objective

Validate the MPS implementation of the conditioned trajectory algorithm before
using it at larger system sizes. This is an algorithm-correctness experiment,
not a scaling experiment.

## Fixed comparison

For frozen validation records at $N=1,2,3$, start from the same initial state,
apply the same recorded single-site Kraus operators, normalize after every
site update, and apply the same dense-QR policy unitary in reverse time. The
MPS path uses `MatrixProductState.from_dense`, local MPS gate application, and
no effective truncation (`cutoff=0`, no max-bond limit). The dense path uses
the released companion `WeakMeasurement` and `PolicyModel` conventions.

## Required gates

For every size, compare the first eight frozen validation trajectories and
record:

1. probability of each selected local measurement outcome;
2. normalized state after every forward site update;
3. normalized state after every reverse policy update; and
4. final reverse-state fidelity.

Maximum dense/MPS state error must be at most $10^{-10}$ and maximum selected
outcome-probability error at most $10^{-10}$. A failed gate is recorded without
retuning. Gradient parity and controlled truncation are follow-on gates; this
first run establishes the execution semantics only.

## Stable interfaces

`dense_state, record -> normalized_state`; `MPS, local_kraus, site -> normalized_MPS`; and `frozen_policy(future_record) -> reverse_unitary`.

## Steps

1. Load frozen validation records and initial states.
2. Apply each selected local Kraus operator with dense and MPS backends.
3. Apply identical frozen reverse unitaries and write per-size errors.

## Completion criteria

All three sizes pass declared tolerances with reloadable records.
