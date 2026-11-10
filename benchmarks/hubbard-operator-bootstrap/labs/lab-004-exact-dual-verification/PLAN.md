# Exact dual verification plan

## Objective

Convert approximate dual outputs into independently controlled lower-bound certificates for the specified Hamiltonian.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

Quantize exported real Gram factors to K/2^40. Their Gram matrices are positive semidefinite exactly. Aggregate the integer affine moment maps and dyadic equality multipliers using exact integer arithmetic. Let r=c+E^T lambda-sum A^T Z and d=-e^T lambda-sum b^T Z. PQG implies every occupation/pair moment has absolute value at most1, hence d-||r||_1 is a certified lower bound. Publish the exact numerator/denominator, all factors and residuals, and round the decimal result downward. Independently audit the operator-to-moment translation so verification does not merely establish consistency of arbitrary supplied matrices.

Success: exact arithmetic reconstruction and a valid physical/operator-space certificate. Failure: noninteger maps, overflow bound failure, unbounded coordinates or wrong physical model. Record validation wall time and peak resident memory separately from discovery.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
