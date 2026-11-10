# Lab 003 — Cubic positivity and symmetry reductions

## Objective

Establish the exact algebraic scope of the cubic hierarchy and compare full and theorem-specific variants.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

Objective: strengthen the global PQG lower bound with affordable degree-three operator tests, independently audit the CAR algebra, and provide exact-certificate-compatible exports.

Completed baseline: construct T1 anticommutator matrices for all triple annihilators, block by total momentum and spin composition, solve using the shared PQG model, and verify the resulting dual factors with exact dyadic arithmetic. The first validated bound was `E >= -9.847999995266`. The completed full T2′ refinement now gives `E >= -8.764969112905`.

Completed refinements: compare mixed-spin and full T2 anticommutator constraints; use the standard one-sided linear augmentation T2′; reduce moments using D4 and spin-swap signed orbits; retain representative momentum cones and split them using integer reflection character bases. A theorem-backed singlet refinement adds `<S²> = 0`, justified separately by Lieb's theorem, and combines T1 with full T2′. Its exact verified bound is `E0 >= -8.763432534493`.

The final precision comparison used Clarabel on the saved full T2′ model with requested600-second/2-GB watchdog limits. It terminated with exit137 during the native solver call, without a completed solution or watchdog record; no bound is claimed. No additional operator branch is planned. Lab006 separately records the completed negative result from retaining200 shared sixth-degree moments in individual density-assisted cubic Gram matrices.

Validation requirements: direct finite-Fock CAR tests; exact cancellation of degree-six terms; sector and symmetry checks; exact vanishing of cross-character affine maps; physical fixed-number diagonal-state checks; independent reconstruction of cone maps from saved operators/projections; exact Gram-factor and coefficient-residual verification. Record construction, solve, verification time and peak RSS for each completed experiment.

The anticommutator SDP is weaker than separate full cubic Gram positivity. Its feasible dual certificates are nevertheless sums of squares within the stated cubic operator subspace. Singlet-restricted bounds are labeled as theorem-backed bounds on E0, separately from the original N↑ = N↓ = 8 relaxation.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
