# v0.7 Decoder: rubric v1 scored against the original deliverables

Date: 2026-10-16. Scope: nine existing attempts, seven scientific submissions; see standard-answer.md for the original prompt hash.

## 1. Nature and limits of the scoring

This is a post hoc local 100-point scale created at the user's request in this round, not official SciCode weights or an evaluator frozen before the original runs. Existing pass/fail/unknown judgments and original score files are retained. Quantification in this version helps compare completion; a total-score threshold does not substitute for scientific correctness or formal difficulty calibration. The A/B difficulty conditions remain incomplete.

The main score follows the original R1-R4 and explicit deliverables, totaling 100 points. The original problem permits unresolved with valid bounds, so honest preservation of unknowns does not itself lose points. The problem specifies no algorithm; correct alternatives are accepted equally. A smaller valid R3 N0 is compared separately as strength of the result; a valid but larger N0 is not treated as a failed proof.

General proportional anchors: 0=missing or a core error; approximately 25%=fragments only; approximately 50%=substantial completion with a clear gap; approximately 75%=mostly complete with a specific reservation; 100%=sufficient evidence for the requirement. Half-points or quarter-points are allowed, with reasons and evidence locations. Do not deduct twice for the same defect: for example, claims about approximation bias are primarily scored under A3, while D items assess only the required small-size API.

Infrastructure failures are unknown/NA, not scientific zeroes. An incomplete submission must also be distinguished from the absence of a reference answer. Each score records what the submission actually stated, what independent checks support, and what remains unknown. A new proof supplied by reviewers cannot be represented as work completed in the AI's original submission.

## 2. Main scoring table: 100 points

| ID | Maximum | Requirement | Evidence for full credit and main deduction grounds |
| --- | --- | --- | --- |
| A1 | 5 | R1 coverage | All 21 O0/O1/O2 entries for N=2,...,8, with intervals/uncertainties or justified unresolved; deduct corresponding coverage for missing entries |
| A2 | 8 | R1 basis for phase classification | Increasing two-dimensional sizes, probability coverage, statistics, and extrapolation sufficiently support the classifications; slow decline/apparent plateaus alone do not determine zero/positive limits; a theorem can directly support a phase region without mandatory repeat MC |
| A3 | 8 | R1 uncertainty control | Statistical, finite-size, and approximation errors reported separately, with justified numerical error estimates; chi differences are not presented as true-bias upper bounds. Do not repeat deductions here for gaps in central-region limiting-risk inference already scored under A2 |
| A4 | 5 | R1 figure and classification semantics | Distinguish rigorous sufficient bounds, rigorous undecodability, numerical boundaries, and unknowns; bound roots are not true transitions; figures/tables agree with answers |
| A5 | 4 | R1 structural consistency | Phase classifications respect information inclusion/equivalence classes, inheriting subsets where necessary; handle the N4 anomaly and asymmetry appropriately; individual sufficient bounds need not all be strictly nested |
| B1 | 4 | R2 model/geometry | Correct noise, conditional independence of observations, boundaries, and binary success condition; no access to hidden information or replacement of the noise channel |
| B2 | 4 | R2 information order | O2-to-O1-to-O0 degradation, risk inequalities, and inclusion of decodable sets; cross-N ordering must actually be proved if used |
| B3 | 5 | R2 charge equivalence | O1(N2)=O0, N3=N6, N5=N7=N8 reveal full integer q, and N4 is a separate class; only relations relied on by the answer need proof; incorrect all-N monotonicity is not rewarded |
| B4 | 2 | R2 special ranks | Correct irrep probabilities and small-N exceptions where used, particularly SU2 and N4 determinant coincidences; avoid the incorrect identification O2(N2)=O0 |
| C1 | 3 | R3 statement | Explicit integer N0, every N>=N0 and every p, and the risk conclusion as L tends to infinity; domain and endpoints complete |
| C2 | 5 | R3 witness/decoder | A valid auxiliary rule and feasible witness, or an equivalent valid direct Bayes/posterior argument; the implication from failure to a spanning component and its required conditions is sound; hiding is not mistaken for sufficiency |
| C3 | 6 | R3 correlations | Valid treatment of shared-edge orientations, side edges/chords, and conditional independence of readouts; effective alternatives such as matrices, stochastic coarse-graining, and grouped Cauchy-Schwarz are accepted equally |
| C4 | 4 | R3 exponential bound and certification | Fixed-path probability, path count, length lower bound, strict all-p factor<1, and finite prefactor; numerical optimization alone without a certified global maximum warrants a reservation |
| C5 | 2 | R3 scope of conclusions | Sufficient N0 is clearly not the minimum/a phase boundary, and r>=1 does not mean undecodability; evidence is auditable; smaller N0 separately records result strength |
| D1 | 6 | R4 joint partition sum | Preserve shared orientations at the two ends of the same edge, with correct local probabilities and logical sectors; do not independently orient vertices or replace sector posterior with MAP |
| D2 | 3 | R4 exact algorithm | Exact or certified as required for L<=4,N<=8; explain contraction/enumeration and complexity; approximations at larger L do not compromise the small-size commitment |
| D3 | 5 | R4 independent verification | Compare against independent enumeration/reference without reusing the same core error; evidence supports the required precision and coverage; retain the limitations of existing external heldout checks |
| D4 | 3 | R4 numerical range | Positive-probability records are not misclassified as zero through underflow; normalization/log/high precision and endpoints work; distinguish platform differences from original-environment gaps |
| D5 | 3 | decode interface | Return a valid edge set with the correct syndrome and a logical decision compatible with the posterior rule used; exceptions and invalid outputs can be located |
| E1 | 4 | answers.json | Structure, 21 entries, endpoint uncertainties/unresolved forms, and R3_N0 agree with the report |
| E2 | 3 | Report/figures | Phase diagram, R2/R3 proofs, evidence, and limitations are provided in locatable files; scientific points are not deducted for personal aesthetic preferences |
| E3 | 3 | Source/reproduction/resources | API, dependency environment, commands, seeds/resource descriptions support reproduction; the 8CPU/32GiB/no-GPU requirements are documented |
| E4 | 5 | Data/unconditional accounting | Raw data, seeds, stopping rules, trial denominators, and exceptions/invalid outputs counted as failures; reserved slots distinguished from actual execution |

Subtotals: R1=30, R2=15, R3=20, R4=20, deliverables/reproducibility=15.

## 3. Scientific pass conditions are not replaced by the total score

R1: exact unknowns may remain unresolved, but high scores elsewhere cannot turn a key definite phase classification without sufficient evidence, or an approximation difference presented as a true error bound, into a pass.

R3: a fatal gap in the core witness, correlations, or strict all-p bound means this requirement is unmet; a valid larger N0 still passes. Arithmetic evidence in the original submission is listed separately from independent repairs after review.

R4: the small-size precision and interface required by the problem must be met. Passing ordinary heldout checks does not establish robustness over the entire positive-probability input domain; stress-test gaps should identify engineering and platform aspects. Such readily repairable problems should not alone be treated as failures of the scientific judgment sought by SciCode.

Whole task: review each main requirement, allowing qualified/partial/unknown outcomes; no post hoc automatic pass threshold of 80 points. Without guided B, there is no formal A/B difficulty conclusion.

## 4. Discussion-detail diagnostics: no extra points within the 100-point score

The following address whether the AI handled each detail properly. Each run is marked E=explicitly correct discussion, I=implicit or only partly developed, M=no discussion found, X=explicit error/inference with insufficient evidence, NA=not required by a valid alternative method, U=no scientific submission. M does not automatically mean failure of the original task; X requires a specific claim and location.

| ID | Diagnostic question | Relation to the original task |
| --- | --- | --- |
| Q01 | D_r(N) is the full-p set; more information cannot shrink it but need not strictly enlarge it | Core R2 meaning |
| Q02 | N5 already recovers full integer q; exact saturation for N>=7, with N6 an exception | R2 core |
| Q03 | mod4 and mod6 do not contain one another; no all-N ordering | Required when making cross-N comparisons |
| Q04 | Non-nested standalone sufficient bounds do not imply that true phases violate information ordering | R1 interpretation |
| Q05 | Transfer reliable Z4 decodable subsets to full integer q | R1/R2 consistency |
| Q06 | Distinguish Z4 confusion of pure triples with singles from mixed triples with singles | Feature mechanism |
| Q07 | High-p active-component orientation identity and the scope of its proof | Optional enhanced analysis |
| Q08 | O1 cannot see neutral pairs, while O2 hiding becomes rarer with N | R3/phase-diagram mechanism |
| Q09 | Separate binary X,C from latent sigma orientation; sigma is not given to the decoder | Core model |
| Q10 | Difference-component self-avoidance follows from degree 0/2, not physical repulsion | Required when using a path proof |
| Q11 | M is the minimum compatible count; only 11 forces true hiding, while 01/10 leaves the count unchanged | Required when using this coarse constraint |
| Q12 | Hiding is necessary, not sufficient, and applies to the specified auxiliary decoder | Required when using a hiding proof |
| Q13 | Decoder score/minimum or maximum edge count/Chernoff conditions enter the probability bound | Required for the corresponding proof approach |
| Q14 | Correct explanation of orientation-matrix states and every element | Applies to the direct matrix approach; NA for alternatives |
| Q15 | Occupation and orientation matrices have different state spaces | Applies to the two-matrix approach; NA for alternatives |
| Q16 | Shared off-path edges/chords cannot be independently resampled vertex by vertex | Core correlations; valid avoidance can receive E |
| Q17 | R*<=R_aux compares average risks, and the exponential bound is not a critical exponent | Core proof conclusion |
| Q18 | The partition function preserves global orientations; small-size exact computation is separate from large-size MPS | R4 core |
| Q19 | Separate phase estimates/sufficient bounds/unknowns and statistical/finite-size/approximation uncertainties | R1 core |
| Q20 | Every exception counts as a failure; reserved slots are not completed trials | Explicit deliverable requirement |
| Q21 | Illustrate sigma, F, and endpoint summation element by element | New teaching request in this discussion; not required by the original task |

Using a,b for both matrix indices and arrival counts in this chat was a notation error in the review explanation; it must not be recorded as a shared error in the seven AI submissions. The reference answer uses alpha,beta and n_V,n_barV instead.

## 5. Preservation and review

scores-v1.json retains weights, item scores, reasons, evidence, and diagnostics; scores-v1.csv facilitates sorting; scorecards.md supports human review. All original run directories are read-only. New review conclusions and differences from existing reviews are listed separately, without overwriting the old scores.json. These detailed weights can be frozen in advance for a future batch of new tests; for this batch they remain a post hoc detailed review.
