# Text-only formulation audit: revision 0.3-general-H

**Recommendation: pass-to-testing.** This is an editorial judgment under the current create-benchmark skill, not expert approval, a calibrated difficulty result or authorization to launch testing.

The revised question is coherent and scientifically meaningful: it asks for an efficient general sparse-check-matrix compiler/embedding algorithm and an efficient evaluation method with a theoretical link to annealing quality. It is plausibly achievable through conditional guarantees and partial comparisons, without requiring a universally optimal embedding or a scalable faithful simulator of arbitrary QPU dynamics.

Substantive judgment remains in coordinating the quadratic representation, hardware routing, coefficient allocation, update strategy and choice of an analytically defensible quality criterion. Standard minor-embedding validity or a single minorminer call does not settle the full objective. This assessment comes from the text and public context; no experiment is evidence for it.

## Changes responding to the user

- Replaced the mandatory CSS H_X/H_Z and fixed toric/Steane suite with a general sparse binary H interface; retained those matrices only as optional legacy examples.
- Defined what H supplies and what must accompany it: syndrome and likelihood weights, plus an optional observable map for logical outcomes. No graphlike column-degree restriction or geometry is assumed.
- Made preprocessing, syndrome reuse, matrix/window updates and evaluation costs algorithmic objectives. Full just-in-time integration is not imposed.
- Made theory-supported embedding evaluation a central result. Stated a transverse-field annealing framework while leaving the criterion, model refinements and proof strategy open.
- Distinguished static energy/robustness guarantees from dynamical success claims. Conditional comparisons and certified limits are valid; empirical search alone is insufficient.
- Kept the document standalone with public scientific references and no private-proposal dependency.

## Remaining open choices

The researcher selects representations, algorithms, quality quantities, useful theoretical regimes, update semantics and illustrative inputs. Universal interface coverage does not imply universal performance guarantees. Statistical dependence beyond independent mechanisms requires an explicitly richer likelihood. These are clear research choices, not missing private materials.

Example bank comparison remains pending access. Reference experiments, quantum simulation, numerical embedding search, model trials, evaluator freezing and formal A/B calibration were not performed and are outside this revision. No claim about model failure or measured research feasibility is made.

The original formulation and the superseded 0.2-design are preserved in author history. T-0007 M005 records the actual user correction. Metadata and summaries track the changed objective without resetting the research lifecycle.

## Document checks

Workspace validator passed; wiki lint reported zero errors and zero warnings. TASK and its convenience copy agree, the objective matches metadata, source hashes and links are intact, and the native LaTeX compiler succeeded. The final five-page PDF was rendered and visually reviewed. These are document checks only; no research algorithm, simulation or embedding search was executed.
