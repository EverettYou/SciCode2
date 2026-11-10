# Evaluation plan: version 0.2-draft

This is an author-only plan. It defines qualitative criteria for the current research design and records unfilled empirical evidence. It is not a completed evaluator or an assertion that the candidate meets SciCode2's difficulty condition. The same objective and rubric apply to A and B.

## Allowed solver input and output contract

Allowed initial files are the selected prompt variant and exactly `inputs/README.md`, `inputs/seed-codes.json`, and `inputs/target-family.json`. References to public papers and documentation discovered using the allowed internet are permitted. No author-side solution, proposal, review, wiki, lab, skill, audit, rubric, history or source allocation proposal is supplied. The seed matrices and topology conventions are public input data, not answer keys. The solver may generate and export larger documented instances and ideal graphs to support its scale claims.

Outputs may use any sensible portable format. They must include reusable executable code, code/noise/graph manifests, quadratic models and projections, physical embeddings and coupler assignments, resource records, exact small-case validation evidence, and an English report. Do not require the solver to use the author's wiki/lab workflow or directory layout. Preserve failures as well as successes.

## Reference checks and valid alternatives

| Criterion | Independent check | Valid alternatives and limits |
| --- | --- | --- |
| Code and objective | Recompute binary commutation, syndrome equations and stabilizer membership. Verify the stated noise likelihood and tie policy. | Equivalent row operations, coordinate relabeling and proved reductions are valid. No preferred gadget or logical basis is required. |
| Quadratic reduction | On finite exact cases compare the original constrained optimum with projected ground states; justify general penalty/projection conditions. | Sound optimal outputs and attained optimum are required. A declared deterministic tie rule need not enumerate all tied answers. No unproved removal of logical classes. |
| Minor embedding | Independently check branch nonemptiness, disjointness, connectivity, all isolated variables and every nonzero source interaction against the saved target edge list. | Branch sets may be trees or other connected subgraphs; no preferred layout. A failed heuristic search is not an impossibility certificate. |
| Physical energy and constraints | Rebuild logical and consistent-chain physical energies; check the declared affine relation, penalties, scales and all supplied device/group bounds. | Exact arithmetic, rigorous bounds, or justified numerical tolerances are valid. If no device limits exist, conditional feasibility is the correct claim. |
| Controlled comparison | Reproduce at least two defensible designs with the automatic reference, matched targets/budgets and separated formulation/placement contrasts. Check all preprocessing, reuse, recovery and restart costs. | No mandatory percentage improvement or preferred method. A negative conclusion needs reproducible comparisons; trivial answer encoding is accounted as classical decoding. |
| Decoding and recovery | Keep evaluation errors out of decoder inputs. Count missing/invalid outputs. Separate syndrome validity, objective quality and logical failure; audit before/after recovery and appropriate controls. | Classical and synthetic samples are allowed diagnostics. No QPU distribution, physical speedup or threshold follows from them. |
| Scientific conclusion | Trace the recommendation or capacity limitation to exact witnesses and measured comparisons at the claimed scale. | A justified resource frontier or limitation can answer the question. Unsupported narrative, only tiny sanity checks, or a single default embedding is insufficient. |

The reference and evaluator should be independent of the candidate's construction wherever possible. Exact integer/binary checks have zero algebraic tolerance. Floating-point comparisons require tolerances derived from coefficient precision, calculation error and the scale used, not an arbitrary hidden pass threshold. Sampling claims require reported denominators, seeds and uncertainty with a stated construction; no universal confidence level is imposed by the organizer emails. Near ties require explicit handling.

## Resource and feasibility calibration

This draft imposes no hidden wall-time or memory cap and no target qubit count, chain length, speedup or success-probability threshold. Comparison budgets must be declared by the researcher before their measured comparisons, with actual construction, search, preprocessing, recovery and reuse costs reported. An execution environment's unavoidable limit is an infrastructure constraint until it is explicitly part of a frozen task budget.

Before a scored test, the organizer should use a separately authorized reference pilot to select achievable nontrivial code/graph sizes, fixed instance and syndrome generation, machine capabilities, numerical tolerances and any hard resource limits. Retain the existing null metadata fields until evidence supports replacing them. A planning estimate is not a measured feasibility result. Pilot output must include measured runtime, peak memory, storage, required threads/accelerators and active scientific effort. If the pilot reduces to a standard recipe, revise or prune the candidate rather than making budgets artificially tight.

## Readiness and task version

Current status: reference-pending, no scored-test freeze, no reference solution/evaluator, no model trials. The finite sanity inputs are prepared; scale-study achievability and the independent implementation of these checks remain pending. `task-version.json` hashes the exact drafts, inputs, requirements and rubric. A material change to objective, data, guidance, rubric or budget requires a new version and preservation of prior texts and evidence.

The author-side [initial snapshot](history/initial-design/README.md) preserves the pre-audit formulation, including its stronger tied-ground-state condition. No trial is associated with that prior form. No C prompt is created because no hindsight execution has occurred.

## Candidate screening and full-trial handoff

The [audit](AUDIT.md) records one-hint, niche-fact, routine-workflow, recipe and clean-run risks. Example bank comparison is pending-access, not passed. These documented risks do not prove model difficulty. If full trials are later authorized, use test-benchmark in an isolated fresh session with only the chosen frozen prompt and allowed inputs, verified strongest available model/highest effort, internet enabled, and complete transcript/output preservation. Use calibrate-benchmark for scoring and case evidence. Neither this document nor artifact-integrity checks launch a dry run, reference experiment or model trial.
