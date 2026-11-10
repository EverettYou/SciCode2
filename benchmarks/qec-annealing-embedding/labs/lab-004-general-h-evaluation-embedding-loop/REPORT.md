---
document_type: lab_report
lab_id: lab-004-general-h-evaluation-embedding-loop
status: completed
idea_ids:
- k-003
- c-004
- c-003
wiki_context:
- wiki/thesis.md
- wiki/ideas/research-frontier.md
related_labs:
- lab-002-agent-test-general-h
- lab-003-surface-code-encoding-comparison
---

# General-H evaluation-guided compact embedding

Completed scientific investigation, 16 October 2026. User-authorized continuing research with inherited author context, an autonomous scientific child and independent parent review. This is not a blind benchmark trial, formal difficulty calibration, or QPU experiment.

## Motivation

This round closes the requested evaluation → programming → compactness loop **within an explicitly assumed terminal Gibbs model**, on ordinary sparse matrices. A rooted-tree repair certificate can be evaluated without decoding, a partition function, a global spectral gap, or Hilbert-space simulation. It guides selection of compact automatic mappings and physical contact allocation while preserving a reference effective logical energy scale.

The result does not close the broader finite-time quantum-annealing problem. Equilibration is an assumption, not a consequence of a schedule; actual logical decoding success generally remains unordered. No real device profile, analog error, bath or QPU sample was used.

The scientific [report](RESEARCH_REPORT.md) and [theory](THEORY.md) give complete derivations and reproducibility instructions. The [independent theory review](independent/REVIEW_THEORY.md) and [interval method](independent/INTERVAL_METHOD.md) distinguish proofs from numerical checks.

## Design

An autonomous scientific child selected the theory, programming method and ordinary-input study. Frozen main and supplemental protocols identify common candidate budgets, development/held-out/fresh splits and declared physical assumptions. The parent independently reviewed proofs and audited saved programs/probability intervals. No decoding optimum or partition function enters construction or selection.

## Findings

For any valid branch-tree minor embedding, let each edge e carry ferromagnetic strength F_e and descendant external absolute load L_e, with nonchain logical coefficients scaled by alpha. Define delta_e=F_e-alpha L_e. Root repair obeys

    E(sigma)-E(repair(sigma)) >= 2 sum_{wall edges e} delta_e.

Positive margins imply chain-consistent physical ground states. A root-spin/wall-set bijection then proves, for classical Gibbs equilibrium at declared inverse temperature beta,

    P(any chain broken) <= 1-product_e(1+exp(-2 beta delta_e))^(-1).

The computation is linear in tree edges once loads are available. Conditioning on chain consistency yields the full compiled logical Gibbs law at beta*alpha; the root-decoded distribution differs from it by at most the defect bound, plus audited coefficient-rounding error. For a fixed compiled model, full-QUBO ground probability is monotone in alpha. This statement includes auxiliaries and degeneracies; it is not a monotonicity theorem for original-error optimality with excited auxiliaries.

A common margin d=log(K/epsilon)/(2 beta) gives a convenient defect budget for K chain edges. Uniform contact splitting makes maximization of alpha an intersection of affine intervals under all coefficient and signed coupling-group limits. A sparse LP permits variable same-sign contact allocations and chain strengths for fixed roots/trees. The ideal LP contains the uniform feasible class; actual numerical solutions are separately audited and do not certify global optimality.

A second proof removes one branch's transverse driver, bounds its quantum-bath blocks, then restores the driver with an even-Dyson-series correction cosh(beta*sum|Gamma_q|)-1. Unioning branch bounds gives a useful nonzero-driver **quantum equilibrium** chain-consistency bound for sufficiently small declared drivers. It supplies no finite-time QA success ordering or classical conditional-law identity at nonzero driver.

These proofs do not assume a code family, planar H, CSS form, independent rows, bounded column degree, or a known decoding answer. The inherited general sparse-H XOR compiler uses M>sum|w| and includes every auxiliary and isolated variable. Feasible syndromes and finite additive weights are required. Observational/logical-class maximum-likelihood decoding is outside the demonstrated objective.

## Ordinary-instance evidence

The frozen [main protocol](PROTOCOL.md) uses four sparse-matrix generators: random fixed-degree rows; irregular rows with hub columns; rewired band rows; and incidence-plus-hypercheck matrices with a dependent row. It includes n=16,32,64, negative/zero dyadic weights, 12 development and 24 held-out inputs. All 288 minorminer candidate searches succeed on the same ideal Zephyr g=6,t=4 graph. Programming ranges are declared parametric assumptions, not a downloaded Advantage2 profile.

The reference is the first valid compact automatic mapping. All selection rules receive the same eight candidate seeds. Compactness below is mean per-instance physical-qubit reduction against that reference, including zeros.

| Method and evidence split | Fewer qubits | Mean reduction | Quality evidence |
|---|---:|---:|---|
| Uniform certificate-guided pool, all 36 | 29/36 | 5.87% | Reference alpha preserved |
| Uniform guided pool + deletion, all 36 | 33/36 | 6.57% | Reference alpha preserved; defect bound <5% |
| Same rule, main held-out 24 | 22/24 | 6.83% | All independently valid |
| Unconstrained minimum-qubit pool, all 36 | 34/36 | 7.43% | Alpha falls on 13/36 |
| LP-guided pool, same original 36 | — | 6.49% | Smaller than uniform-guided pool on 7/36 |
| LP + deletion, 8 entirely new inputs | 7/8 | 5.53% | Reference alpha preserved; all certified |

The final combination was developed after main results, then checked on new seed-7703 n=32,64 inputs across all four generators. The original held-out labels are not reused as fresh validation for this adaptive combination. All main and LP-refinement constrained/unconstrained deletion trajectories coincide: the acceptance floor adds no measured pruning benefit in these runs. Pool selection and allocation show an effect; pruning's quality constraint alone does not. The common one-step deletion control and protocol clarification retain this null result.

Current evaluator median is 18.6 ms per main candidate, including a full cached target-group scan. The main pool takes 179.3 s of automatic search and 6.70 s of evaluation; main per-instance work totals 197.7 s. Searching eight candidates is additional construction work relative to one candidate, so no end-to-end speedup over a single automatic mapping is claimed. LP solving/allocation for the same 288 candidates takes 4.33 s, with 11.16 s for the complete LP supplement. Rational/outward final verification is charged separately. Data: [main summary](results/analysis_summary.json), [LP](results/lp_summary.json), [fresh combination](results/lp_refinement_summary.json).

## Independent verification and actual probability orders

The independent audit imports neither compiler nor evaluator. It validates all **313 saved selected programs**, including the four defect cases against their actual deleted-node/edge target and regenerated groups, all LP selections, and both LP-refinement controls. Actual binary64 coefficients are exact rationals for range, load, margin and consistency checks; 60-digit outward arithmetic bounds Gibbs defects. Maximum global classical defect upper bound is 0.048767626 and maximum logical-Gibbs rounding-TV correction is 3.56e-13. No guided final alpha falls below its reference. [Witness audit](results/independent_program_audit.json).

Independent positive interval transfer calculations on all 12 ordinary n=16 inputs certify strict **chain-consistent full-QUBO-ground readout** probability ordering on 8/12 for uniform-guided-pruned versus first, and 11/12 for LP-selected versus first. These use separated lower/upper probability intervals, rather than treating improvement of a lower bound as an actual ordering. The same method certifies **0/12** strict unconditional root-decoded-optimum orders; all are inconclusive for that larger event. The expensive reference partition calculations are verification only and never guide selection. [Interval results](results/independent_logical_gibbs_intervals.json).

The terminal full-QUBO ground probabilities are modest, roughly 0.4–16.6% across the n=16 comparisons. A 95% chain-consistency guarantee does not mean 95% decoding success. Small exact physical enumeration provides a concrete limitation: with equal 20-qubit counts and the same defect upper bound, actual chain-break probability rises from 1.20% to 2.08%, while root-decoded-optimum probability rises from 48.6% to 67.2%. The certificate does not rank actual defect rates. [Physical validation](results/physical_gibbs_validation.json).

The quantum bound remains nonvacuous on all 36 main final mappings at beta=20 and Gamma=0.001, with maximum failure upper bound about 0.3394; at Gamma=0.0001 the maximum is about 0.05288. These are declared dimensionless parameters, not a calibrated temperature or freezeout point. Independently checked dense quantum-Gibbs models cover 270 cases with outside drivers retained. Numerical checks support implementation of the proved inequalities; they are not the proof itself.

## Scaling, updates and retained failures

On the unchanged 1,248-site target, n=128 fits 3/4 generators. The mixed-hypergraph case fails all eight heuristic searches. All four n=256 cases exhaust the search budget. These are search failures, not impossibility proofs. All four new n=64 synthetic-defect cases fit after deleting 5% of sites and 1% of surviving edges. [Extension evidence](results/extension_summary.json).

For fixed H and penalty envelope, 160 syndrome/weight updates reuse mappings with revalidation and reevaluation, median 25.7 ms/update. Matrix/window structural changes still require checking new interactions; no general just-in-time or changing-window routing guarantee is proved. [Update audit](results/update_audit.json).

## Procedure, corrections and reproducibility

The scientific child initially chose the method autonomously from the question and latest user scope. The parent subsequently supplied independent derivations, quantum-correction review, event-accounting corrections and witness audits. This is supervised team research with one child, not a fresh single-agent model test. Both actual rollout contexts report GPT-6.1 Sol/high. The original two-hour deadline was retained; no automation or future job was created.

The main protocol was frozen before data. Later extension, LP and combination protocols identify their own post-main timing and fresh inputs. A common-proposal claim was clarified because adaptive deletion paths can diverge; a genuinely common one-step control was added. An early physical assertion conflated full-QUBO ground success with original-error optimality through excited auxiliaries; it was corrected, with the failed trace retained. Independent interval event definitions were reviewed and corrected before final interpretation. Serialization/patching errors were repaired; no final inequality violation or failed instance was discarded.

Use [construct.py](scripts/construct.py) for an input JSON with n, sparse rows, syndrome and weights, optionally an explicit target/groups/ranges. It consumes no family label, hidden feasibility witness or decoding answer. It returns a full saved program or explicit failure/inconclusive status; it is an exploratory reusable implementation, not a guaranteed fast solver for every sparse H. Source compiler/adapter imports are read-only and SHA-256 bound in [source provenance](results/source_provenance.json). Original problem, prompt and prior labs remain unchanged.

[run.json](run.json) records actual timing, context and unchanged dependencies. The transcript index records exact session sources, timestamp slices, hashes and capture completeness; an active parent capture excludes subsequent closeout and the final response. The scientific manifest binds methods, code and result artifacts, excluding self-referential administrative manifests.

## Wiki ingest handoff

Strengthen the local thesis from "no routine useful general-H criterion" to "a useful static/terminal-equilibrium criterion and compactness loop on diverse sparse inputs." Keep finite-time QA, actual original-error success ordering, analog noise, large-instance coverage and changing-window latency unresolved. Preserve Lab 002's inconclusive ordinary pause results and Lab 003's structured-code limitations. Promote no difficulty, expert-review or organizer-acceptance claim from these scientific findings.
