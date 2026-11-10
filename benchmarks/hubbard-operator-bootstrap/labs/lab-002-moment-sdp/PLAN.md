# Momentum bootstrap experiment

## Objective

Find affordable global moment constraints and select the cubic directions that carry the energy certificate.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

Construct the full quadratic fermionic test space (P, Q, G, occupations and holes), exploit translation and the fixed spin populations, and export a complete affine SDP plus dual Gram factors. Solve a baseline before spending resources on degree-three correlations.

Refine with creation times opposite-spin density, then all two-site cubic families. Use odd anticommutators to cancel degree-six moments; augment with a linear creation operator in one of the two positive Gram matrices. Keep every P/Q/G constraint so residual coordinates remain bounded by one. Compare bound improvement, actual induced matrix sizes, construction time, solving time, and peak RSS. A smaller solver tolerance only merits further work if its certified improvement justifies its cost.

Success requires a reproducible operator construction, exported dual witness, and an independent exact-arithmetic certificate plus independent operator-map audit. Solver optimality flags and primal energies alone are not accepted as validation.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
