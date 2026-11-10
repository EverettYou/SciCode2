# Local density extension plan

## Objective

Test whether inexpensive local density positivity detects violations in the global candidate moments.

## Stable interfaces

Exploratory scripts and data stay in this lab. Supported final interfaces are documented in [the stable implementation](../../src/README.md); the promoted portable replay imports no lab module.

## Steps

Hypothesis: the strongest global cubic anticommutator moment relaxation still admits nonrepresentable local4site RDMs. First reconstruct exact local1/2RDM maps using Gaussian-integer Fourier phases and independently verify on known physical states. Test whether a candidate moment vector admits a positive local density matrix, block diagonal in both spin counts. If a nonzero mismatch is observed beyond numerical residuals, append localdensity PSD/matching constraints to a global relaxation and measure the bound improvement/cost. Do not promote a primal infeasibility heuristic as a certified improved energy bound; export the joint dual and validate it exactly. Retain a negative feasibility result as evidence for pruning.

The cluster is2x2, all256Fockstates,25particle blocks(max36),2578real variables,198local1/2RDM moment matches plus trace. Local particle count is not fixed. Scale Fourier equations by16/256 for exact integer coefficients.


## Completion criteria

Record actual findings, resources, uncertainty, failed attempts, and evidence paths. A promoted lower bound requires both a valid physical/operator formulation and independent numerical error control. A negative branch completes when its discriminating experiment supports a documented prune decision.
