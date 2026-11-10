# Prospective formulation and embedding audit

## Objective

After a subsequent user instruction, identify a validated resource tradeoff or limitation that changes the choice of formulation/embedding to take to D-Wave. This plan is not authorization to execute.

## Stable interfaces

No implementation is prescribed or available. Future interfaces should accept explicit CSS matrices, syndrome/noise data and a versioned target manifest; emit a quadratic model, projection, branch-set witness, programmed coefficients and validation/resource records. Tiny reference solvers may remain lab-local.

## Steps

1. Freeze a modest classical budget and instance protocol before measuring. Audit code algebra and toric seams; record all logical sectors. Resolve or explicitly parameterize device limits.
2. Select credible alternative representations from the literature and independent reasoning. Prove reduction conditions and verify exact small-case minima, ties and projection.
3. On fixed source graphs compare embedding alternatives with a reproducible automatic baseline and comparable budgets. Independently check every embedding witness and programmed-coefficient constraint.
4. Compare surviving representations end to end under comparable search effort. Account for auxiliary count, chain tails, scaling, failures and initial/amortized cost across independent syndromes.
5. Audit optional post-processing on controlled offline samples, with a no-post-processing control. Separate objective gaps from logical failure and report uncertainty where sampled.
6. Preserve negative results, update the wiki and keep/prune/cross decisions, then propose the next scientific operation. Distill stable interfaces only from supported evidence.

## Expected artifacts and decision points

Use portable records for input matrices/noise/seeds, target node/edge lists and provenance, QUBO/Ising coefficients and projection, embedding branch sets and source-edge witnesses, independent correctness results, and resource comparisons. Suggested filenames such as instances.json, model.json, embedding.json, validation.json and resources.csv are author-side planning conventions, not mandatory solver output names.

The initial [input fixtures](../../evaluation/inputs/README.md) are sanity data only. The first design decision is whether the exact reduction and embedding can be independently verified. Incorrect reductions are retained as rejected branches with counterexamples. The next decision is whether a crossed formulation/placement comparison changes a resource recommendation; inconclusive results require narrower claims or a better comparison, not a fabricated winner. A timeout is recorded as a search failure. Pre-solving and all other preprocessing remain charged.

Workload and computational envelope are unmeasured. Before execution, propose and record an achievable workstation budget, comparison suite and stopping rule from the available environment; do not treat that proposal as a measured active-hours or memory estimate. Record runtime, peak memory, storage and parallelism in the pilot. Scored-test budgets are selected only after the reference evidence exists.

## Completion criteria

A reproducible correct construction or documented limitation, independently checked on overlapping exact cases and both required code families; budgeted baseline comparisons; explicit device/proxy boundaries; no unsupported QPU advantage or global-optimality claim. If the pilot cannot establish nontrivial workstation feasibility, revise the public scope before scored-test calibration.
