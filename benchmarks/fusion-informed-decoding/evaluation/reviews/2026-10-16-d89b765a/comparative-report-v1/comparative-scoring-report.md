# Aspect-by-aspect comparative study of seven valid AI submissions

Review population: nine attempts, comprising seven scientific submissions for comparison and two Fable API failures listed separately as void attempts. The comparison unit is the individual run; a single run is not generalized to overall model ability.

The report covers 23 scored aspects of the original task and 21 discussion details. Each question has a seven-row comparison table recording accomplishments, actual issues or evidential limitations, score/coverage status, and source locators. Cross-aspect summaries and issue classifications follow.

The previous rubric weights, scores, and scientific assessments are retained. Original runs are unchanged, and teaching requirements added in this review do not incur retrospective deductions. This is a post hoc local comparison, not a prefrozen official SciCode difficulty test.

Main findings: all seven receive full credit on 18 of the 23 main criteria. Differences concentrate on phase-assignment evidence, approximation-error guarantees, all-p proof certification, extreme numerical range, and failure accounting. High completion scores do not erase key scientific gaps.

GPT01/02 meet all main criteria by giving justified unresolved answers, as permitted by the original task; the true central phase diagram is not thereby fully solved. Fable/Opus are strong on core structure and algorithms, but the evidence for several phase-region conclusions is insufficient.

# Review population, scoring conventions, and evidence

All nine attempts use the same v0.7 task. The original prompt SHA-256 is `d89b765a4af1e50b2824d40d0c2d8590e722202219411bd49f5ea7d63c64d6a9`. This report uses scores-v1.json, whose SHA-256 is `977158e73cc0a4b6292e3df2aba6a8744f04aab664f63cc4be4a74e41b6ea53b`. 

| Run | Archived model label | Treatment in this report | Total | unresolved |
| --- | --- | --- | --- | --- |
| Fable03 | Fable 5.1 | Valid; included in scoring | 92.5/100 | 0/21 |
| Opus01 | Opus 5.5 | Valid; included in scoring | 89.5/100 | 0/21 |
| Opus02 | Opus 5.5 | Valid; included in scoring | 89.5/100 | 0/21 |
| Opus03 | Opus 5.5 | Valid; included in scoring | 88.5/100 | 0/21 |
| GPT01 | GPT 6 Astra | Valid; included in scoring | 100/100 | 11/21 |
| GPT02 | GPT 6 Astra | Valid; included in scoring | 100/100 | 12/21 |
| GPT03 | GPT 6 Astra | Valid; included in scoring | 99/100 | 5/21 |
| Fable01 | Fable 5.1 | API output limit; void | NA | NA |
| Fable02 | Fable 5.1 | API output limit; void | NA | NA |

Void attempts are not assigned scientific zeros and are excluded from the seven-run ranking and model-group means. The 23 main criteria total 100 points: R1 phase diagram 30, R2 exact structure 15, R3 large-N proof 20, R4 posterior 20, and delivery/reproducibility 15. Key scientific pass conditions are assessed individually, without a post hoc automatic total-score pass threshold.

Discussion details do not add points: E=explicit and correct; I=implicit or partially developed; M=no explanation found; X=specific error or insufficiently supported inference; NA=unneeded for a valid alternative method. Teaching diagrams were requested later. Mixing the matrix indices a,b with arrival counts a,b occurred in this chat explanation and is not attributed to the original runs.

The evidence column uses file-ID:line-number locators linked to the appendix file index. Original submissions are distinguished from subsequent independent verification: of 210 ordinary checks, 140 belong to original R4 and 70 are O0 controls; 18 extremely-low-p stress inputs diagnose posterior numerical range. Independent certificates support the theorems but are not retrospectively credited as certification in the original AI submissions.

Possible errors form a checklist; the actual issues/limitations column records observations in this review. No error found means none was identified within the reviewed and tested scope, not a formal proof over the entire parameter domain.

# R1: phase diagrams, assignment evidence, and anomalies

## A1 R1 coverage(5 points)

Review question: Were all record/rank phase-diagram entries delivered?

Scoring requirement: All 21 O0/O1/O2 entries for N=2,...,8, with intervals/uncertainties or justified unresolved; deduct corresponding coverage for missing entries

Scientific significance: R1 requests O0, O1, and O2 at each N=2,…,8: 21 entries. A justified unresolved answer is also valid.

Possible errors (checklist, not errors attributed to all seven): Omitting equivalent rows, supplying only one noise point, or using unresolved to conceal the absence of analysis.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 5/5 | All 21 phase entries and the combined plot are supplied, using exact equivalence of the four charge classes. | Coverage is adequate; the basis for assigning central charge nondecodability is assessed under A2. | [F03-01:213](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:213>); [F03-01:219](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:219>) |
| Opus01 | 5/5 | All 21 entries and the joint plot are supplied, merging duplicate rows by equivalence class. | Coverage is adequate; credibility of the all-p charge conclusion is assessed under A2. | [O01-01:326](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:326>); [O01-01:329](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:329>) |
| Opus02 | 5/5 | All 21 entries and a unified table are supplied, with evidence labels for each class. | Coverage is adequate; having no unresolved entries does not mean every true phase boundary has been proved. | [O02-01:184](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:184>); [O02-01:247](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:247>) |
| Opus03 | 5/5 | All 21 entries are supplied, distinguishing syndrome, Z4, other charge records, and full irreps. | Coverage is adequate; a detailed report does not replace adequate evidence for each conclusion. | [O03-01:239](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:239>); [O03-01:297](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:297>) |
| GPT01 | 5/5 | All 21 entries are supplied; 11 remain unresolved, with proved and inherited subsets. | These unknowns are justified, valid deliverables; their number does not reduce the coverage score. | [G01-01:55](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:55>); [G01-01:86](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:86>) |
| GPT02 | 5/5 | All 21 entries are supplied; 12 unknowns have theorem-based tails and size diagnostics. | Unknowns are not drawn as fabricated phase boundaries; full coverage does not mean the true phase diagram is solved. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-01:70](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:70>) |
| GPT03 | 5/5 | All 21 entries are supplied; five charge entries remain unknown and all-p O2 is labeled numerical. | Coverage is adequate; continuous-parameter risks in the small-N all-p claim are assessed under A2. | [G03-01:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:3>); [G03-01:15](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:15>) |

Comparison: All seven valid submissions cover all 21 entries. Full coverage does not mean all 21 true phase boundaries have been resolved.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## A2 R1 basis for phase assignments(8 points)

Review question: Do the finite-size data adequately support the assigned phases?

Scoring requirement: Increasing two-dimensional sizes, probability coverage, statistics, and extrapolation sufficiently support the classifications; slow decline/apparent plateaus alone do not determine zero/positive limits; a theorem can directly support a phase region without mandatory repeat MC

Scientific significance: Changes in risk with growing two-dimensional size must support the specific choice of a zero limit, positive limit, or unresolved status.

Possible errors (checklist, not errors attributed to all seven): Calling slow decay a zero limit; calling a plateau-like trend and positive-intercept fit a positive limit; presenting a finite grid as proof over a continuous parameter range.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/8 | Exact-posterior data grow in two dimensions, with crossings, fits, and risk distributions. | Slow drift at L≤12 cannot establish a positive limit; the text also does not exclude decay with correlation length≥50. | [F03-01:213](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:213>); [F03-01:219](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:219>) |
| Opus01 | 5/8 | Sizes reach about L48, with log-odds analysis and central-charge drift diagnostics. | Absence of a plateau does not exclude a positive limit; charge pinning of the clean-loop phase remains a physical picture, not a proof. | [O01-01:326](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:326>); [O01-01:329](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:329>) |
| Opus02 | 5/8 | Central integer charge is studied to about L96, comparing sizes and Gaussian/BKT pictures. | Risk remains about 0.2; the heuristic lower bound is not proved to exclude every nondecodable phase of this posterior model. | [O02-01:184](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:184>); [O02-01:247](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:247>) |
| Opus03 | 5/8 | Central charge is studied to about L64, with slow drift and posterior distributions. | Gaussian/BKT exclusion remains heuristic; the text allows a later rough/glassy crossover. | [O03-01:239](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:239>); [O03-01:297](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:297>) |
| GPT01 | 8/8 | Resolved crossings receive extrapolation sensitivity analysis; slow charge and small-N O2 remain unresolved. | The unknown true phases remain unsolved, but insufficient data are not forced into definitive assignments, consistent with the rubric. | [G01-01:55](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:55>); [G01-01:86](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:86>) |
| GPT02 | 8/8 | Unstable Z4 fits and central charge remain unresolved, with the full fit family and bootstrap results. | These are still unknown rather than solved central boundaries; retaining them is consistent with the task. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-01:70](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:70>) |
| GPT03 | 7/8 | Growing two-dimensional exact posteriors and cross-N maps support a numerical small-N O2 all-p assignment. | A finite p grid and late crossovers can still miss structure; these are disclosed, but the all-p assignment still loses one point. | [G03-01:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:3>); [G03-01:15](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:15>) |

Comparison: The main disagreement concerns the central charge phase: Fable assigns a positive limit and Opus a zero limit, but neither evidence base excludes competing explanations. GPT01/02 more reliably retain unresolved status.

Score distribution: 2/7 receive full credit; the other 5/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## A3 R1 error control(8 points)

Review question: Are statistical, finite-size, and numerical-approximation errors separated and justified?

Scoring requirement: Statistical, finite-size, and approximation errors reported separately, with justified numerical error estimates; chi differences are not presented as true-bias upper bounds. Do not repeat deductions here for gaps in central-region limiting-risk inference already scored under A2

Scientific significance: Accurate posteriors for individual samples, adequate finite-sample statistics, and a reliable thermodynamic extrapolation are three different questions.

Possible errors (checklist, not errors attributed to all seven): Declaring a bound on bias relative to the exact posterior merely because results at two bond dimensions are close.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 8/8 | Exact contraction has no bond truncation; statistics and finite-size fit variation are reported. | The inadequate central positive-limit inference is penalized under A2, not again here. | [F03-01:213](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:213>); [F03-01:219](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:219>) |
| Opus01 | 3/8 | Error sources are separated; χ64/128 comparisons and large-size convergence are studied. | Two close approximations cannot bound their common true bias; the stated R* error bound is too strong. | [O01-01:82](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:82>); [O01-01:164](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:164>) |
| Opus02 | 3/8 | χ studies and empirical convergence diagnostics are saved, with acknowledgment that they are not a priori bounds. | Differences from larger χ are still elevated to an induced-bias bound without control relative to the truth. | [O02-01:301](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:301>); [O02-01:319](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:319>) |
| Opus03 | 3/8 | A subset of records receives χ64/128 comparisons; statistical and size errors are reported. | An empirical maximum change on a subset cannot guarantee every phase assignment is unchanged; larger χ can share the same bias. | [O03-01:355](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:355>); [O03-01:391](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:391>) |
| GPT01 | 8/8 | No MPS truncation; rounding-perturbation refits are separated from statistical and size allowances. | The reported extrapolation sensitivity is not claimed as a rigorous thermodynamic confidence interval; no error was found here. | [G01-01:123](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:123>) |
| GPT02 | 8/8 | Exact contraction, numerical-range checks, and nonlinear perturbation refits are reported separately. | Unknowns are not upgraded because numerical errors are tiny; floating-point conditions must still be read in their recorded original environment. | [G02-01:99](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:99>) |
| GPT03 | 8/8 | No bond truncation; bootstrap, fit variants, and round/log checks are supplied. | The size allowance is explicitly not a rigorous confidence bound on the limit; no deduction-worthy issue was found here. | [G03-01:185](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:185>) |

Comparison: Fable and GPT use contraction without bond truncation. The three Opus runs provide useful χ-convergence studies, but their shared bias is unbounded, so the strongest error guarantees are unsupported.

Score distribution: 4/7 receive full credit; the other 3/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## A4 R1 figure and assignment semantics(5 points)

Review question: What type of conclusion do the phase-diagram colors and boundaries represent?

Scoring requirement: Distinguish rigorous sufficient bounds, rigorous undecodability, numerical boundaries, and unknowns; bound roots are not true transitions; figures/tables agree with answers

Scientific significance: Rigorous sufficient subsets, rigorously nondecodable regions, numerical phase boundaries, and unknown regions need distinct meanings.

Possible errors (checklist, not errors attributed to all seven): Calling a root of μρ=1 the true threshold; calling the region where a sufficient condition fails nondecodable; using closed intervals to imply critical-point membership is settled.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 5/5 | The N19 sufficient theorem is separated from numerical inference beginning at N3, with distinct plot sources. | The inadequate central-phase support is assessed under A2, not attributed to conflating the large-N theorem. | [F03-01:36](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:36>) |
| Opus01 | 5/5 | The N15 theorem is separate; finite-N phase assignments are labeled numerical. | N15 is the range this proof establishes, not the smallest physical N0. | [O01-01:503](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:503>) |
| Opus02 | 5/5 | The μρ<1 sufficient region, N15 certification, and failure at N14 are distinguished. | Failure of the certificate at N14 does not imply nondecodability there; low-rank all-p behavior remains numerical inference. | [O02-01:142](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:142>) |
| Opus03 | 5/5 | The N15 theorem and low-rank numerical diagram are discussed separately. | N15 cannot directly validate all-p decoding at N3; the text does not use it that way. | [O03-01:654](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:654>) |
| GPT01 | 5/5 | The plot separately encodes rigorous tails, inherited numerical subsets, and hatched unknowns. | Sufficient-bound endpoints are not threshold estimates; closed-interval JSON does not settle critical-point membership. | [G01-01:53](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:53>); [G01-01:5](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:5>) |
| GPT02 | 5/5 | A rigorous-only plot is provided, separate from statistical estimates and unresolved regions. | μρ=1 is not used as a true phase boundary; an unknown hatched region may contain no internal transition. | [G02-02:219](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:219>); [G02-01:83](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:83>) |
| GPT03 | 5/5 | The N14 theorem, numerical all-p assignment, and charge sufficient tails are separated. | The small-N numerical assignment has an A2 reservation, but is not presented as the N14 theorem. | [G03-01:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:3>); [G03-01:29](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:29>) |

Comparison: All seven distinguish large-N theorems from finite-N numerical inference. A larger N0 is not a scientific error; small-N phase inference still requires a separate A2 assessment.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## A5 R1 structural consistency(4 points)

Review question: Is the phase diagram consistent with information inclusions and equivalences?

Scoring requirement: Phase classifications respect information inclusion/equivalence classes, inheriting subsets where necessary; handle the N4 anomaly and asymmetry appropriately; individual sufficient bounds need not all be strictly nested

Scientific significance: A richer record can first be degraded to a coarser one, so the true decodable set cannot shrink; equivalent channels must agree.

Possible errors (checklist, not errors attributed to all seven): Treating a nominal crossing as a failure of information theory; forcing O1/O2 symmetry about p=1/2; treating every independently derived sufficient bound as a true phase boundary.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/4 | Charge-equivalent rows are reused, with checks of both Z4 endpoints and the information hierarchy. | High-p Z4 gain is small; its local explanation does not reach an exact active-component theorem. | [F03-01:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190>); [F03-01:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201>) |
| Opus01 | 4/4 | The high Z4 endpoint is constrained within errors to respect O0 inclusion; equivalent rows agree. | Adjusting a nominal center does not prove the true thresholds are exactly equal. | [O01-01:268](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268>); [O01-01:275](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275>) |
| Opus02 | 4/4 | Paired same-sample comparisons verify risk inclusion and discuss asymmetric low/high-p Z4 gains. | A tiny high-p difference does not prove channel or threshold equivalence. | [O02-01:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212>); [O02-01:214](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214>) |
| Opus03 | 4/4 | High-p nesting is checked and a Z4 component-orientation identity is derived. | The identity retains information on closed components; it does not show complete high-p reduction to O0. | [O03-01:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229>); [O03-01:668](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668>) |
| GPT01 | 4/4 | The nominal Z4 reversal is explained within its allowance; reliable subsets are transferred to integer q. | An N-independent universal O1 tail bound reflects discarded information, not equality of every true boundary. | [G01-01:33](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33>); [G01-02:256](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256>) |
| GPT02 | 4/4 | Unstable Z4 remains unknown; same-N and cross-N maps support conservative inclusions. | The central unknown has no independent truth; common sufficient tails cannot numerically prove phase-region saturation. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | 4/4 | The high Z4 nominal center is projected to O0 and its uncertainty enlarged to retain the original interval. | This implements exact information ordering in reporting; it is not a threshold-equality theorem. | [G03-01:40](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40>) |

Comparison: All seven check equivalence classes and inclusions. Z4 high-noise differences must be interpreted with their uncertainty and bound semantics; the plots cannot establish that Z4 outperforms integer charge.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

# R2: model and exact information structure

## B1 R2 model and geometry(4 points)

Review question: Does the solution use the specified noise, geometry, and success conditions?

Scoring requirement: Correct noise, conditional independence of observations, boundaries, and binary success condition; no access to hidden information or replacement of the noise channel

Scientific significance: A complete microscopic edge state includes occupancy and orientation; the recovery target is the binary syndrome and logical sector.

Possible errors (checklist, not errors attributed to all seven): Allowing the decoder to see true orientations; independently redrawing the two endpoints; declaring logical success after correcting only the syndrome.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/4 | Microscopic 0/± edge weights 1−p,p/2 define the model; sector partition sums define Bayes risk. | No access to true orientations was found; the text also uses c for a microscopic state, which must be distinguished from a correction. | [F03-02:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:3>) |
| Opus01 | 4/4 | True occupancy and shared orientations define the joint likelihood; recovery targets the logical sector. | The microscopic state is also called c; readers must not confuse it with a binary correction. | [O01-01:105](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:105>) |
| Opus02 | 4/4 | Three-state ψ edges retain opposite endpoint representations; risk and the binary correction API are separate. | Readouts are conditionally independent only given the complete microscopic state, not unconditionally independent across vertices. | [O02-01:40](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:40>) |
| Opus03 | 4/4 | The model uses 0/± flow edges, binary occupancy, syndrome, and top-flux parity. | Directed flow variables do not give additional visible information to the binary correction. | [O03-01:502](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:502>) |
| GPT01 | 4/4 | Geometry and 0/± edge tensors retain shared orientations; a valid correction follows the sector decision. | Hidden orientations enter probability calculations and are not supplied to the decoder; no model substitution was found. | [G01-02:70](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:70>) |
| GPT02 | 4/4 | The rank of H, shortest paths, and correction existence in each sector are proved before posterior-based recovery. | The coarse-constraint auxiliary decoder and the actual exact-posterior decoder serve different purposes. | [G02-02:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:3>) |
| GPT03 | 4/4 | Three-state edges reverse sign at the other endpoint; Gaussian elimination with H and the logical row finds representatives. | Representatives in the same sector may have different weights without affecting the task’s definition of logical success. | [G03-02:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:3>) |

Comparison: All seven valid solutions correctly retain shared microscopic edge states and the binary recovery target. Their structural differences mainly arise in subsequent proofs and inference.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## B2 R2 information ordering(4 points)

Review question: Is information ordering proved by a valid degradation map?

Scoring requirement: O2-to-O1-to-O0 degradation, risk inequalities, and inclusion of decodable sets; cross-N ordering must actually be proved if used

Scientific significance: A degradation map may use only visible records and independent randomness, not the true microscopic input; the comparison concerns average risk.

Possible errors (checklist, not errors attributed to all seven): Inferring a stronger full spatial channel from apparently richer single-vertex information; claiming every fine record has smaller conditional error; assuming monotonicity at every successive N.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/4 | Superadditivity of min proves degradation increases risk; center characters establish the hierarchy. | The comparison is of average risk; no erroneous total order is built from conditional probabilities of individual records. | [F03-02:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:18>); [F03-01:128](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:128>) |
| Opus01 | 4/4 | Jensen data processing is proved; center N-ality degrades an irrep to charge. | True cross-N ordering is limited to constructible garblings; the two integer-charge branches do not form a total order. | [O01-01:109](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:109>); [O01-01:114](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:114>) |
| Opus02 | 4/4 | Jensen and the center map are used; LP reports low-rank exceptions and an analytic map covers N≥7. | Finite local LP tables and the analytic N≥7 range must remain distinct; neither establishes every successive-N comparison. | [O02-01:45](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:45>); [O02-01:86](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:86>) |
| Opus03 | 4/4 | A same-N hierarchy is proved and N≥7 degradation is constructed from likelihood vectors. | Low-rank determinant coincidences prevent a blanket ordering by N. | [O03-01:17](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:17>); [O03-01:540](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:540>) |
| GPT01 | 4/4 | A same-N center map and an N≥5→SU3 construction are supplied, handling N6 separately. | SU4 is not assumed stronger than SU3; average-risk ordering does not hold record by record. | [G01-01:53](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:53>); [G01-02:225](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:225>) |
| GPT02 | 4/4 | Center degradation preserves the full correlated channel; exact cross-N kernels and the N6 exception are listed. | Kernels may read outcomes, not true (a,b); the text checks the kernels for each input. | [G02-01:75](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:75>); [G02-02:89](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:89>) |
| GPT03 | 4/4 | The center map and average Bayes ordering are proved, with an implemented N≥5→SU3 kernel. | The text explicitly notes that a fine record’s conditional error need not be below that of a particular coarse record. | [G03-02:36](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:36>); [G03-01:121](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:121>) |

Comparison: All seven prove O2→O1→O0 at fixed N. Cross-N comparisons are accepted only when backed by maps. GPT also constructs the specific comparison from N≥5 to SU3.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## B3 R2 charge equivalences(5 points)

Review question: Are the complete charge equivalence classes and saturation derived?

Scoring requirement: O1(N2)=O0, N3=N6, N5=N7=N8 reveal full integer q, and N4 is a separate class; only relations relied on by the answer need proof; incorrect all-N monotonicity is not rewarded

Scientific significance: Vertex degree is at most three, q∈[-3,3], and the syndrome supplies q parity; modular information must be analyzed together with parity.

Possible errors (checklist, not errors attributed to all seven): Ignoring parity and wrongly concluding N5 still has aliases; missing the N6 exception; assuming increasing N always adds charge information.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 5/5 | The CRT table gives lcm(2,N), explicitly listing the integer-q class at N5 and every N≥7. | Close data for N3/6 and integer q do not establish exact channel equivalence. | [F03-02:69](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:69>); [F03-02:82](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:82>) |
| Opus01 | 5/5 | M=lcm(2,N) is derived; four classes are listed and only distinct charge classes are simulated. | Only N5/7/8 are fully equivalent; numerical closeness of N3 and N5 does not justify merging them. | [O01-01:119](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:119>); [O01-01:127](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:127>) |
| Opus02 | 5/5 | Equivalent per-configuration likelihood tables prove equivalence; integer-q degradation to both modular records is listed. | The M≥7 criterion uses finite q support and cannot be generalized to higher-degree vertices. | [O02-01:54](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:54>) |
| Opus03 | 5/5 | CRT and degree≤3 yield four classes; divergence explains integer charge. | Knowing divergence still does not reveal n; neutral-pair information remains absent. | [O03-01:489](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:489>); [O03-01:498](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:498>) |
| GPT01 | 5/5 | Equivalences are proved as conditional relabelings for each microscopic state, preserving the full spatial posterior. | Finite-size risks within a class are exactly identical; coincident bounds from different proofs are a separate matter. | [G01-02:46](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:46>); [G01-02:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:51>) |
| GPT02 | 5/5 | Same-parity q values cannot differ by a nonzero multiple of five at N5; N6 retains the ±3 alias. | Consecutive N is not assumed monotone; the common N5/N6 confusion is avoided. | [G02-02:25](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:25>) |
| GPT03 | 5/5 | The CRT four-class table establishes exact equivalence of the joint spatial law as well. | This is channel equivalence, not merely fitted boundaries agreeing within errors. | [G03-02:57](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:57>); [G03-02:72](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:72>) |

Comparison: All seven correctly give four classes: N2; N3/6; N4; N5/7/8. N5 exactness and N≥7 saturation, discussed earlier, are not common omissions in these runs.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## B4 R2 special ranks(2 points)

Review question: Are low-rank representation coincidences and local probabilities correct?

Scoring requirement: Correct irrep probabilities and small-N exceptions where used, particularly SU2 and N4 determinant coincidences; avoid the incorrect identification O2(N2)=O0

Scientific significance: SU2 self-conjugacy and determinant-column coincidences change the available information; generic-N tables cannot be substituted.

Possible errors (checklist, not errors attributed to all seven): Identifying O2 at SU2 with O0; omitting a pure triple returning the conjugate fundamental at N4; treating an odd-parity N3 singlet as zero arrivals.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 2/2 | SU2 spin laws and the additional N4 pure-triple coincidence are listed, with an independent coarsening check. | Integrating SU2 orientations does not discard the extra distinctions between n=0/2 and n=1/3. | [F03-02:94](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:94>) |
| Opus01 | 2/2 | All four SU2 degree laws are given as a noisy-degree record. | Generic-N garbling must also handle low-rank coincidences; the used tables and kernels have been checked. | [O01-01:140](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:140>) |
| Opus02 | 2/2 | SU2 degree laws, low-rank LP, and general irrep tables are checked together. | Generic-N unique-label structure cannot be applied directly at N3/4/6. | [O02-01:26](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:26>) |
| Opus03 | 2/2 | Highest-weight vectors provide an independent check; determinant coincidences at N2 through N6 are listed. | Exact low-rank tables underlie posteriors and cross-N comparisons; a large-N approximation alone is insufficient. | [O03-01:506](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:506>) |
| GPT01 | 2/2 | SU2 spin tables, Pieri/Weyl rules, and independent character checks are supplied. | O2(2)≠O0 is explicit, and the N3 singlet with odd syndrome is retained. | [G01-02:64](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:64>) |
| GPT02 | 2/2 | Pieri/Weyl rules and independent tensor formulas check low ranks; N4 path constants are separate. | An N4 pure triple returning the conjugate fundamental changes the O2 constant; the ordinary mixed-only constant is inapplicable. | [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | 2/2 | Determinant-column coincidences and SU2 probabilities are computed exactly; odd syndrome is retained. | An N3 triple singlet and a zero-arrival singlet are not the same (s,R) record. | [G03-02:142](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:142>) |

Comparison: The low-rank laws used by all seven are supported. SU2 gives an orientation-blind record with additional count information, not a syndrome-only record.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

# R3: large-N theorems and proof chains

## C1 R3 statement(3 points)

Review question: Is an explicit large-N decodability theorem given for every N≥N0 and every noise rate p?

Scoring requirement: Explicit integer N0, every N>=N0 and every p, and the risk conclusion as L tends to infinity; domain and endpoints complete

Scientific significance: R3 requires a sufficient integer and complete quantifiers, not success at a few N,p values or finite sizes. A smaller N0 measures result strength, not the sole criterion for satisfying the requirement.

Possible errors (checklist, not errors attributed to all seven): Proving only p=1/2 or a sparse-noise region while claiming all p.; Treating the smallest numerically tested N as theorem N0, or omitting p=0,1.; Calling N0 the minimum critical rank.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3/3 | The final theorem uses N0=19, covers all larger N and all p, and treats endpoints as known binary errors. | The text retains the earlier memory-20→20 step; the final memory-22→19 revision is explicit and not a conflict in the final answer. | [F03-02:171](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:171>); [F03-02:237](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:237>) |
| Opus01 | 3/3 | N0=15, every N≥15, and p∈[0,1] are explicit, including deterministic endpoints. | No quantifier gap here; 15 does not mean N14 or smaller ranks are nondecodable. | [O01-02:95](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:95>) |
| Opus02 | 3/3 | The opening theorem gives exponential all-p decodability at N0=15 and notes error parameters decrease monotonically with N. | Complete here; 15 is described as this method’s smallest value, not the true minimum. | [O02-02:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:1>) |
| Opus03 | 3/3 | The final N0=15 statement includes all target quantifiers and the size limit. | The statement is complete; the original full-p arithmetic-certification gap is separate under C4. | [O03-02:134](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:134>) |
| GPT01 | 3/3 | N0=13 is explicit; the path factor decreases for larger N and p=0,1 are handled exactly and separately. | No gap here; 13 is an explicit sufficient value. | [G01-02:194](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:194>) |
| GPT02 | 3/3 | The base proof gives 14; large_N_13.md improves the final sufficient integer to 13 while retaining full-p quantifiers. | The final N13 supplement must be included; recording only the base proofs.md value 14 is incomplete. | [G02-02:130](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:130>); [G02-03:132](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/large_N_13.md:132>) |
| GPT03 | 3/3 | N0=14 is explicit, with separate low/high-noise control and endpoint treatment. | No gap here; 14 is a sufficient value from the method. | [G03-02:189](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:189>) |

Comparison: All seven satisfy the R3 statement requirement. Final sufficient integers are 19,15,15,15,13,13,14; their differences reflect proof tightness, not contradictions.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## C2 R3 witness/decoder(5 points)

Review question: Is the failure witness valid, and does the decoder or direct Bayes argument use only visible observations?

Scoring requirement: A valid auxiliary rule and feasible witness, or an equivalent valid direct Bayes/posterior argument; the implication from failure to a spanning component and its required conditions is sound; hiding is not mistaken for sufficiency

Scientific significance: A legitimate executable rule or valid posterior inequality must precede the reduction of logical error to a spanning difference component. Local ambiguity without a selection condition cannot establish that the decoder selects incorrectly.

Possible errors (checklist, not errors attributed to all seven): Letting the decoder use true arrows or true arrival counts.; Equating one singlet/hiding event with logical failure.; Assuming an arbitrary geometric subpath can be flipped feasibly instead of a complete difference component.; Substituting MAP configuration for optimal logical-sector inference without identifying it as an auxiliary rule.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 5/5 | A MAP-support auxiliary decoder is constructed on a legitimately degraded degree record; complete-component flips are feasible and failure supplies a spanning component with likelihood ratio≥1. | No scientific error was found here; assess the actual proof route used. | [F03-02:183](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:183>) |
| Opus01 | 5/5 | Visible irreps are randomly degraded to a degree channel; MAP-configuration component flips and the score inequality give a failure witness. | No scientific error was found here; assess the actual proof route used. | [O01-02:103](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:103>) |
| Opus02 | 5/5 | An injective polymer map and fractional-moment bound directly control wrong-sector posterior mass; no GPT-style auxiliary decoder is needed. | No scientific error was found here; assess the actual proof route used. | [O02-02:8](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:8>) |
| Opus03 | 5/5 | An explicit degradation kernel and MAP-configuration rule give a full chain of degree-0/2 components, feasibility, and a ratio condition. | No scientific error was found here; assess the actual proof route used. | [O03-02:163](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:163>) |
| GPT01 | 5/5 | A weighted feasible decoder uses the observed minimum compatible count m; the true configuration is feasible and a complete spanning-component flip yields W ratio≥1. | No scientific error was found here; assess the actual proof route used. | [G01-02:104](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:104>) |
| GPT02 | 5/5 | Min/max-cardinality decoders use the same visible count constraints; failure witnesses satisfy both local hiding and half-path occupancy conditions. | No scientific error was found here; assess the actual proof route used. | [G02-02:138](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:138>) |
| GPT03 | 5/5 | A minimum-cardinality coarse-count decoder forces at least half the spanning difference edges truly active, with hiding required at 11 vertices. | No scientific error was found here; assess the actual proof route used. | [G03-02:213](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:213>) |

Comparison: All seven have substantive witness/decoder arguments. Opus02’s direct-posterior method is a valid alternative and cannot be penalized for not reproducing GPT01’s weighted decoder.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## C3 R3 correlations(6 points)

Review question: Does the single-path probability correctly handle shared arrows, side edges, and chord correlations?

Scoring requirement: Valid treatment of shared-edge orientations, side edges/chords, and conditional independence of readouts; effective alternatives such as matrices, stochastic coarse-graining, and grouped Cauchy-Schwarz are accepted equally

Scientific significance: Readouts are independent across vertices only after conditioning on complete microscopic edge states. Fixing binary support still leaves shared arrows; an off-path chord may touch two path vertices. Incorrect independence changes the exponential growth factor.

Possible errors (checklist, not errors attributed to all seven): Independently redrawing the orientation at the two ends of one shared edge.; Unconditionally multiplying vertex hiding probabilities.; Handling side edges used once but omitting chords used twice.; Claiming a transfer matrix automatically resolves all external correlations.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 6/6 | Visible random degradation first removes orientation dependence; Bhattacharyya overlaps and grouping by physical side edges handle single/double uses before occupancy-matrix summation. | No independence error was found; an alternative method is not an omitted arrow matrix. | [F03-02:204](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:204>) |
| Opus01 | 6/6 | A valid orientation-blind channel, square-root likelihood overlaps, chord Cauchy–Schwarz, and an occupancy matrix yield the path bound. | No independence error was found; an alternative method is not an omitted arrow matrix. | [O01-02:111](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:111>) |
| Opus02 | 6/6 | General-θ fractional posterior moments and readout overlaps use Cauchy–Schwarz on chords and Jensen at single endpoints; the Perron root bounds the pattern sum. | No independence error was found; an alternative method is not an omitted arrow matrix. | [O02-02:19](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:19>) |
| Opus03 | 6/6 | After random degradation, likelihood depends only on degree; occupancy patterns are summed first, then shared factors are averaged by physical third edge. | No independence error was found; an alternative method is not an omitted arrow matrix. | [O03-02:181](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:181>) |
| GPT01 | 6/6 | With off-path microscopic states fixed, ± orientation matrices and operator norms are used; side edges appearing once/twice handle chords, giving a tighter ηN(p). | No independence error was found; an alternative method is not an omitted arrow matrix. | [G01-02:142](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:142>) |
| GPT02 | 6/6 | The base orientation-norm and chord bounds are complete; the N13 improvement uses positive-cycle expansion, Ihara–Bass, and an analytic tail for residual orientation/cycle correlations. | No independence error was found; an alternative method is not an omitted arrow matrix. | [G02-02:149](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:149>) |
| GPT03 | 6/6 | No arrow matrix is used: honeycomb bipartite grouping and second-moment Cauchy–Schwarz control shared microscopic edges, followed by an occupancy Chernoff matrix. | No independence error was found; an alternative method is not an omitted arrow matrix. | [G03-02:227](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:227>) |

Comparison: All seven actually handle correlations, through different methods. GPT01/02 retain orientation information and obtain stronger sufficient values; garbling and bipartite second-moment methods are more conservative but scientifically valid.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## C4 R3 exponential bound and certification(4 points)

Review question: How does the path bound yield a rigorous L→∞ result, and is the full-p growth factor<1 certified?

Scoring requirement: Fixed-path probability, path count, length lower bound, strict all-p factor<1, and finite prefactor; numerical optimization alone without a certified global maximum warrants a reservation

Scientific significance: Path counts, minimum spanning length, finite prefactors, and a strict margin all need control. A floating-point maximum below one or a dense p scan is evidence, not automatic coverage of the full continuum.

Possible errors (checklist, not errors attributed to all seven): Treating the maximum on a finite grid or from a floating-point optimizer as a rigorous bound over the entire interval.; Using the asymptotic definition of exact μ to assume a common finite prefactor at every length without an ε margin.; Reporting a growth factor<1 without the geometric series or length lower bound.; Crediting a later reviewer-supplied certificate to the original agent.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3.5/4 | Length≥2L−1, L starting points, and the geometric series are supplied; final λ=1.876764 gives N19. Later rational coverage supports squared growth≤0.997854. | The original h19 is floating-point output and the large memory-22 proof was not rebuilt here, reserving half a point for certification/auditability. Later λ>known exact μ can independently replace the large count. | [F03-02:224](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:224>) |
| Opus01 | 4/4 | The μ+δ prefactor, geometric series, and original rational interval cover are complete; existing checks give squared growth≤0.998799. | The original certification is rigorous; a margin near one indicates a conservative bound, not a proof gap. | [O01-02:122](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:122>) |
| Opus02 | 4/4 | Path counts and exponential decay are complete; the original 120-bit interval-arithmetic full-p cover and N monotonicity extend N15 to all larger N. | The original has interval certification; “many grid points” is not a substitute for its interval cover. | [O02-02:26](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:26>) |
| Opus03 | 3/4 | Counting and the geometric series hold; later rational interval coverage supports squared growth≤0.996797. | Original r3_bound.py uses a 200001-point grid plus floating-point optimization without rigorous full-p certification. This original-certificate gap loses one point; no counterexample was found. | [O03-02:199](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:199>); [O03-03:31](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/scripts/r3_bound.py:31>) |
| GPT01 | 4/4 | A three-part rational certificate covers all p with worst-segment growth<0.999129; endpoints and the μ+ε margin are complete. | Original certification is complete; the exponential upper bound may be very loose at practical sizes. | [G01-02:132](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:132>) |
| GPT02 | 4/4 | The N13 supplement bounds the cycle factor with exact return-walk terms and an analytic tail; a rational full-p certificate gives growth<0.999888. | Original certification is complete but technically involved; small-hexagon enumerations are validation examples, not substitutes for the general tail proof. | [G02-02:208](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:208>); [G02-03:62](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/large_N_13.md:62>) |
| GPT03 | 4/4 | A rational full-p certificate, separate high-p analysis, and μ+ε are supplied; existing checks give growth<0.999950. | Original certification is complete; a uniform factor near one permits a very long crossover. | [G03-02:278](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:278>) |

Comparison: Frozen original-submission scores are Fable03 3.5/4, Opus03 3/4, and 4/4 for the others. Existing independent checks support all seven theorems but cannot retrospectively supply original certificates; squared and unsquared factors are not directly rankable.

Score distribution: 5/7 receive full credit; the other 2/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## C5 R3 scope of conclusions(2 points)

Review question: Is the relation between sufficient N0, probability bounds, actual phases, and critical exponents properly limited?

Scoring requirement: Sufficient N0 is clearly not the minimum/a phase boundary, and r>=1 does not mean undecodability; evidence is auditable; smaller N0 separately records result strength

Scientific significance: Boundaries of rigorous decodable subsets, sufficient ranks, and exponential upper bounds may all be conservative. Failure of a proof does not imply physical nondecodability; a larger sufficient N0 is not an error.

Possible errors (checklist, not errors attributed to all seven): Declaring nondecodability when r≥1.; Treating roots of a sufficient bound as true transition boundaries.; Calling the decay rate in an exponential upper bound a true critical exponent.; Misreading average Bayes-risk comparison as recordwise inclusion of failure events.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 2/2 | The N19 theorem is separate from numerical behavior at N≥3; risk ordering uses average Bayes risk. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [F03-02:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:229>) |
| Opus01 | 2/2 | The text calls 15 this method’s upper bound, deliberately discards orientation information, and presents smaller-N all-p behavior only as numerical evidence. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [O01-02:132](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:132>) |
| Opus02 | 2/2 | 15 is explicitly a sufficient value from the current proof; numerical all-p behavior at N≥3 is not presented as a theorem. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [O02-02:39](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:39>) |
| Opus03 | 2/2 | Discarded information, proved N15, and smaller-N numerical extrapolations are separated. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [O03-02:218](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:218>) |
| GPT01 | 2/2 | 13 is not claimed minimal; sufficient roots are not actual phase boundaries and auxiliary risk bounds optimal average risk. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [G01-02:208](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:208>) |
| GPT02 | 2/2 | The growth-factor condition is explicitly sufficient; equality is not interpreted as a phase boundary. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [G02-02:219](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:219>) |
| GPT03 | 2/2 | 14 is not claimed minimal, and the proof bound may be impractical at simulated sizes. | No overclaim was found here; other phase-extrapolation issues are assessed under A2/A3 without duplicate penalties. | [G03-02:313](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:313>) |

Comparison: All seven are generally restrained about R3 scope. Full marks here do not mean the phase diagram is complete or formal difficulty calibration has passed.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

# R4: exact posteriors, numerical range, and decoding

## D1 R4 joint partition sum(6 points)

Review question: Was the correct joint partition sum evaluated, with sums separated by logical sector?

Scoring requirement: Preserve shared orientations at the two ends of the same edge, with correct local probabilities and logical sectors; do not independently orient vertices or replace sector posterior with MAP

Scientific significance: Optimal logical decoding compares the total posterior mass of the two logical sectors. Separating the shared edge orientation, or finding only the single most likely error, changes the probability model specified in the problem.

Possible errors (checklist, not errors attributed to all seven): Sample the orientation at the two endpoints of the same edge independently.; Replace the global joint sum with vertex-by-vertex local likelihoods.; Treat the MAP microscopic configuration as the logical-sector posterior.; Omit the top-boundary logical parity.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [F03-03:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:1>); [REV-01:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-fable-5-1-run_03-checks.json:1>) |
| Opus01 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O01-03:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/src/tm.py:1>); [REV-02:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_01-checks.json:1>) |
| Opus02 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O02-04:43](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:43>); [REV-03:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_02-checks.json:1>) |
| Opus03 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O03-05:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/tm.py:1>); [REV-04:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_03-checks.json:1>) |
| GPT01 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G01-03:232](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:232>); [REV-05:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_01-checks.json:1>) |
| GPT02 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G02-04:175](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:175>); [REV-06:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_02-checks.json:1>) |
| GPT03 | 6/6 | Joint three-state summation preserves shared orientations and separates Z0,Z1 by logical parity. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G03-03:182](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:182>); [REV-07:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_03-checks.json:1>) |

Comparison: All seven receive the same score here; the main differences concern extreme numerical range and evidence for larger-size approximations, rather than the partition-sum definition.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## D2 R4 exact algorithm(3 points)

Review question: Does the prescribed small-size regime L≤4,N≤8 use an exact or certified algorithm?

Scoring requirement: Exact or certified as required for L<=4,N<=8; explain contraction/enumeration and complexity; approximations at larger L do not compromise the small-size commitment

Scientific significance: The small-size exact API is an automatically checkable deliverable. The algorithm should retain all configurations. Its complexity may grow exponentially with width, without first proving that the model is free fermionic.

Possible errors (checklist, not errors attributed to all seven): Call a truncated MPS result an untruncated exact result.; Conflate a large-size approximation with the prescribed small-size API.; Substitute an unimplemented Pfaffian/free-fermion theory for a working algorithm.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [F03-04:25](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:25>) |
| Opus01 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O01-01:67](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:67>) |
| Opus02 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | The public API switches to MPS at L>9; small sizes remain exact, so the no-truncation wording needs qualification. | [O02-05:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:18>) |
| Opus03 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O03-06:12](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/solution.py:12>) |
| GPT01 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G01-03:279](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:279>) |
| GPT02 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G02-04:314](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:314>) |
| GPT03 | 3/3 | The prescribed L≤4 API uses untruncated exact contraction; complexity grows exponentially with width. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G03-03:267](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:267>) |

Comparison: All satisfy the original small-size algorithm requirement. Opus02's public API switches to MPS at L>9, so exactness claims must specify the size range.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## D3 R4 independent validation(5 points)

Review question: Can independent validation detect a shared modeling or implementation error?

Scoring requirement: Compare against independent enumeration/reference without reusing the same core error; evidence supports the required precision and coverage; retain the limitations of existing external heldout checks

Scientific significance: Agreement between two functions sharing the same erroneous core does not prove correctness. Enumeration, different elimination orders, and independently implemented irreps and geometry reduce this risk.

Possible errors (checklist, not errors attributed to all seven): Compare only two wrappers around the same code.; Treat posterior normalization as a complete correctness check.; Describe passing finite tests as correctness for every record.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [F03-05:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/tests_validate.py:18>); [REV-01:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-fable-5-1-run_03-checks.json:1>) |
| Opus01 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [O01-04:8](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/tests/test_small.py:8>); [REV-02:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_01-checks.json:1>) |
| Opus02 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [O02-06:21](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/tests/validate.py:21>); [REV-03:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_02-checks.json:1>) |
| Opus03 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [O03-07:7](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/tests/test_validate_small.py:7>); [REV-04:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_03-checks.json:1>) |
| GPT01 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [G01-04:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/validate.py:1>); [REV-05:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_01-checks.json:1>) |
| GPT02 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [G02-05:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/validate.py:1>); [REV-06:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_02-checks.json:1>) |
| GPT03 | 5/5 | Includes independent small-lattice checks; passes 210/210 external routine posterior checks. | Of 210 cases, 140 are O1/O2 and 70 are extra O0 controls; this is not all records. | [G03-04:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/validate.py:1>); [REV-07:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_03-checks.json:1>) |

Comparison: All routine checks pass, supporting correctness on the tested domain; this is not an exhaustive proof for all legal records.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## D4 R4 numerical range(3 points)

Review question: Can the posterior of a legal record still be evaluated at extremely small but positive probabilities?

Scoring requirement: Positive-probability records are not misclassified as zero through underflow; normalization/log/high precision and endpoints work; distinguish platform differences from original-environment gaps

Scientific significance: Z0 and Z1 may both be tiny while their ratio remains defined. Stepwise normalization cannot restore edge weights or local products that have already underflowed to zero.

Possible errors (checklist, not errors attributed to all seven): Misreport numerical underflow as a zero-probability record.; Normalize only after each column, after already forming extremely small products in ordinary float arithmetic.; Use a dtype name instead of checking the floating-point range across platforms.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 1/3 | Uses ordinary normalization; passes 210/210 routine posterior checks. | Fails 18/18 extremely low-p stress cases; local underflow can make a positive-probability record appear to have zero probability. | [F03-03:198](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:198>); [REV-01:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-fable-5-1-run_03-checks.json:1>) |
| Opus01 | 1/3 | Uses ordinary normalization; passes 210/210 routine posterior checks. | Fails 18/18 extremely low-p stress cases; local underflow can make a positive-probability record appear to have zero probability. | [O01-05:71](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/solution.py:71>); [REV-02:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_01-checks.json:1>) |
| Opus02 | 1/3 | Uses ordinary normalization; passes 210/210 routine posterior checks. | Fails 18/18; some failures depend on platform range, but float p/2 rounding to zero before conversion is a cross-platform issue. | [O02-04:45](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:45>); [REV-03:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_02-checks.json:1>) |
| Opus03 | 1/3 | Uses ordinary normalization; passes 210/210 routine posterior checks. | Fails 18/18 extremely low-p stress cases; local underflow can make a positive-probability record appear to have zero probability. | [O03-08:43](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/api.py:43>); [REV-04:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_03-checks.json:1>) |
| GPT01 | 3/3 | Uses high-precision or log fallback; passes 210/210 routine and 18/18 stress cases. | Passes 18/18 stress cases; finite tests do not replace a proof for every input. | [G01-03:271](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:271>); [REV-05:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_01-checks.json:1>) |
| GPT02 | 3/3 | Uses high-precision or log fallback; passes 210/210 routine and 18/18 stress cases. | Passes 18/18 stress cases; finite tests do not replace a proof for every input. | [G02-04:224](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:224>); [REV-06:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_02-checks.json:1>) |
| GPT03 | 3/3 | Uses high-precision or log fallback; passes 210/210 routine and 18/18 stress cases. | Passes 18/18 stress cases; finite tests do not replace a proof for every input. | [G03-03:187](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:187>); [REV-07:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_03-checks.json:1>) |

Comparison: This item reveals a substantive posterior-API difference: GPT's high-precision or log-domain fallback covers the checked domain; the other four have numerical-underflow gaps.

Score distribution: 3/7 receive full credit; the other 4/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## D5 decode interface(3 points)

Review question: Does decode return a legal correction and choose the maximum-posterior logical sector?

Scoring requirement: Return a valid edge set with the correct syndrome and a logical decision compatible with the posterior rule used; exceptions and invalid outputs can be located

Scientific significance: Correct posterior values are insufficient: the output must be an edge set in the specified geometry, satisfy Hc=s, and have logical parity consistent with the posterior decision. Either sector is valid at a tie.

Possible errors (checklist, not errors attributed to all seven): Output edges outside the geometry.; Return only a logical bit without constructing a correction.; Construct a correction with the correct syndrome but wrong logical parity.; Treat the correction as a microscopic configuration that must recover the true arrows.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [F03-03:280](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/model.py:280>); [REV-01:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-fable-5-1-run_03-checks.json:1>) |
| Opus01 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O01-05:102](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/solution.py:102>); [REV-02:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_01-checks.json:1>) |
| Opus02 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O02-04:143](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/api.py:143>); [REV-03:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_02-checks.json:1>) |
| Opus03 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [O03-08:74](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/api.py:74>); [REV-04:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/anthropic__claude-opus-5-5-run_03-checks.json:1>) |
| GPT01 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G01-03:403](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:403>); [REV-05:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_01-checks.json:1>) |
| GPT02 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G02-04:391](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:391>); [REV-06:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_02-checks.json:1>) |
| GPT03 | 3/3 | All 210/210 routine corrections are legal, with correct syndrome and logical sector. | No specific error found in this item; the conclusion is limited to the reviewed material and checked domain. | [G03-03:312](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:312>); [REV-07:1](</Users/home/Library/CloudStorage/Dropbox/Research/[Mercor]SciCode2/benchmarks/fusion-informed-decoding/evaluation/reviews/2026-10-16-d89b765a/results/openai__gpt-6-astra-run_03-checks.json:1>) |

Comparison: The routine decode interface does not distinguish the seven submissions; these checks do not validate the large-size phase-diagram limit.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

# Deliverables, reproducibility, and unconditional accounting

## E1 answers.json(4 points)

Review question: Is answers.json complete, readable, and aligned with the report's requirements?

Scoring requirement: Structure, 21 entries, endpoint uncertainties/unresolved forms, and R3_N0 agree with the report

Scientific significance: Machine-readable results enable subsequent automated evaluation and comparison. File completeness and reliable scientific classification are separate evaluation dimensions.

Possible errors (checklist, not errors attributed to all seven): Omit record/rank entries.; Provide unparseable JSON or an N0 of the wrong type.; Give different results in the report and machine-readable file.; Treat unresolved as a missing file.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [F03-06:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/answers.json:1>) |
| Opus01 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [O01-06:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/answers.json:1>) |
| Opus02 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [O02-07:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/answers.json:1>) |
| Opus03 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [O03-09:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/answers.json:1>) |
| GPT01 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [G01-05:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/answers.json:1>) |
| GPT02 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [G02-06:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/answers.json:1>) |
| GPT03 | 4/4 | JSON parses, all 21 record/rank entries are present, and N0 is an integer. | Full completeness credit does not mean all 21 phase assignments are resolved; scientific support is scored separately. | [G03-05:1](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/answers.json:1>) |

Comparison: All seven receive the same completeness score; whether evidence supports the phase assignments is assessed separately in A2—A5.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## E2 Report/figures(3 points)

Review question: Are the report, proofs and combined phase diagram complete and locatable?

Scoring requirement: Phase diagram, R2/R3 proofs, evidence, and limitations are provided in locatable files; scientific points are not deducted for personal aesthetic preferences

Scientific significance: Research conclusions must connect to proofs, data and limitations, rather than only a figure or number. Complete deliverables do not automatically close scientific gaps.

Possible errors (checklist, not errors attributed to all seven): Provide a figure without a basis for its classifications.; Give an N0 without a proof.; Scatter graphical and written results so they cannot be located.; Deduct scientific credit for personal aesthetic preferences.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [F03-04:6](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:6>) |
| Opus01 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [O01-01:5](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:5>) |
| Opus02 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [O02-05:4](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:4>) |
| Opus03 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [O03-10:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/README.md:3>) |
| GPT01 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [G01-06:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:3>) |
| GPT02 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [G02-07:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:3>) |
| GPT03 | 3/3 | Report, R2/R3 proofs and combined phase diagram are complete. | Completeness and scientific correctness are separate; full credit here does not remove reservations about phase extrapolation. | [G03-06:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:3>) |

Comparison: All deliver the report; differences in phase extrapolation and approximation-error quality are scored separately in the scientific items.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## E3 Code/reproduction/resources(3 points)

Review question: Do source code, environment, commands and resource records support reproduction?

Scoring requirement: API, dependency environment, commands, seeds/resource descriptions support reproduction; the 8CPU/32GiB/no-GPU requirements are documented

Scientific significance: Reproduction requires the API, dependency versions, random seeds and commands, together with evidence of the CPU, memory and GPU conditions used.

Possible errors (checklist, not errors attributed to all seven): Provide results without code or an execution entry point.; Omit dependency versions and seeds.; Treat a resource-monitoring fragment as a complete run audit.; Describe this small-scale review as a full replay of production experiments.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [F03-04:30](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:30>) |
| Opus01 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [O01-07:1](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/reproduce.sh:1>) |
| Opus02 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [O02-05:24](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:24>) |
| Opus03 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [O03-10:29](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/README.md:29>) |
| GPT01 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Resource monitoring begins during refinement; cumulative CPU figures exclude some development and pilots. | [G01-06:17](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:17>) |
| GPT02 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [G02-07:32](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:32>) |
| GPT03 | 3/3 | Provides code, dependency environment, reproduction commands and resource descriptions. | Production research was not fully replayed, nor was the entire original run independently monitored. | [G03-06:24](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:24>) |

Comparison: All receive full credit under the frozen rubric; this assesses the availability of reproduction materials, rather than certifying all historical resource usage.

Score distribution: 7/7 receive full credit; the other 0/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

## E4 Data/unconditional accounting(5 points)

Review question: Are all attempts, exceptions, stopping rules and raw data accounted for unconditionally?

Scoring requirement: Raw data, seeds, stopping rules, trial denominators, and exceptions/invalid outputs counted as failures; reserved slots distinguished from actual execution

Scientific significance: Dropping difficult records biases risk downward. The exception-as-failure rule must enter the reported metrics; reserved slots must not be presented as completed physical trials.

Possible errors (checklist, not errors attributed to all seven): Remove exceptional samples from the denominator.; Assign hard failure 1 but posterior-min risk only 0.5.; Save only successful posterior evaluations, preventing selection-bias auditing.; Report the reserved slots of an externally terminated batch as completed trials.

| Run | Score | Accomplishments | Actual issues / evidential limitations | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | 4/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions set P0=0.5 and risk/hard tie to 0.5; zero archived exceptions make this a latent defect. | [F03-07:56](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/run_mc.py:56>) |
| Opus01 | 4.5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Reports 2 actual exceptions; hard failure is 1, but reported risk remains 0.5. | [O01-08:146](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/src/mc.py:146>) |
| Opus02 | 4.5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions receive hard failure 1 and risk 0.5; this row makes no inference about their actual count. | [O02-08:49](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/sim.py:49>) |
| Opus03 | 4.5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions receive hard failure 1 and risk 0.5; this row makes no inference about their actual count. | [O03-11:121](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/mc.py:121>) |
| GPT01 | 5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions and invalid outputs receive risk and failure 1; saved-array auditing found no inconsistency. | [G01-06:50](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:50>) |
| GPT02 | 5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions and invalid outputs receive 1; checks of 305024 evaluation rows and 4 archive hashes agree. | [G02-07:61](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:61>) |
| GPT03 | 5/5 | Preserves raw data, seeds, stopping rules and denominators for all attempts. | 340600 archived slots include 200 reservations from a terminated batch; the physical-trial total is unknown. | [G03-06:62](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:62>) |

Comparison: Distinguish risk estimation from hard failure: the task requires exceptions to count as failures, so both should receive 1. Fable's issue has not affected saved estimates; Opus01 has actual triggering records.

Score distribution: 3/7 receive full credit; the other 4/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.

# Discussion details: seven-run comparison for each question

## Q01 D_r(N) is the full-p set; more information cannot shrink it but need not strictly expand it

Question: What set does D_r(N) denote?

Relation to the original task: Core R2 meaning. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: D_r(N)={p∈[0,1]:R*_{r,L}(p,N)→0}; it includes low-noise and high-noise ends and any possible central regions.

Possible confusions: Interpreting D1 as only the interval near p=1; asserting that inclusion guarantees strict expansion.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Finite-L average Bayes risk defines the decodable set and proves same-N inclusion. | D1 is not restricted to the high-p tail; inclusion need not be strict expansion. | [F03-02:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:18>); [F03-01:128](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:128>) |
| Opus01 | E | Jensen proves garbling cannot improve risk, yielding inclusion of D sets. | All-p and endpoint tails belong to the same D; inclusion alone does not imply strict gain. | [O01-01:109](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:109>); [O01-01:114](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:114>) |
| Opus02 | E | D0⊆D1(N)⊆D2(N) is explicit and holds pointwise in the parameters. | The definition does not require D to have exactly two intervals; topology still depends on evidence. | [O02-01:45](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:45>); [O02-01:86](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:86>) |
| Opus03 | E | Same-N nesting applies over the entire p∈[0,1] range. | The central all-p charge assignment has an A2 gap without changing the definition of D. | [O03-01:17](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:17>); [O03-01:540](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:540>) |
| GPT01 | E | The hierarchy theorem and inherited subsets apply over the whole noise axis. | Reliable plotted subsets are not the full solution for D; unknown regions may be decodable. | [G01-01:53](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:53>); [G01-02:225](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:225>) |
| GPT02 | E | Finite-patch risk ordering yields full-p set inclusion, retaining unresolved entries. | Sufficient tails are known subsets, not a definition restricting D to tails. | [G02-01:75](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:75>); [G02-02:89](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:89>) |
| GPT03 | E | Average Bayes-risk ordering and the hierarchy are explicit. | Conditional risk of individual fine records need not be monotone; average-risk and D inclusions still hold. | [G03-02:36](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:36>); [G03-01:121](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:121>) |

Comparative conclusion: All seven use the full-parameter decodable set and data processing. More information guarantees no shrinkage, not strict expansion.

## Q02 N5 already recovers integer q; N≥7 strictly saturates, with N6 exceptional

Question: Why is N5 already exact, N≥7 saturated, and N6 exceptional?

Relation to the original task: R2 core. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: Only q values of the same syndrome parity need distinguishing. The apparent mod-5 collisions at N5 cross parity and are separated by the syndrome.

Possible confusions: Counting seven integer q values and concluding N≥7 is necessary; incorrectly inferring from N5 exactness that all N≥5 are exact.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | The table explicitly gives no q aliases at N5 and N≥7, with only ±3 merged at N3/6. | N5 exactness is a strict parity/CRT result, not a numerical observation. | [F03-02:69](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:69>); [F03-02:82](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:82>) |
| Opus01 | E | lcm(2,N) gives equivalence of N5/7/8 and a separate N3/6 class. | N6 cannot join the full-integer class; it is correctly distinguished. | [O01-01:119](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:119>); [O01-01:127](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:127>) |
| Opus02 | E | Per-configuration tables and bit-for-bit checks verify N5/7/8 equivalence. | Numerical checks supplement the analytic finite-support argument, not replace it. | [O02-01:54](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:54>) |
| Opus03 | E | The CRT table identifies N5/7/8 with exact integer divergence. | Charge information does not increase monotonically at consecutive integers; N6 is exceptional. | [O03-01:489](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:489>); [O03-01:498](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:498>) |
| GPT01 | E | The syndrome recovers mod2N at odd N, so N5 already suffices. | N3/6 and the integer class are not the same channel merely because weak proof tails coincide. | [G01-02:46](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:46>); [G01-02:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:51>) |
| GPT02 | E | Separate parity sets prove apparent mod5 aliases at N5 are removed by syndrome. | At N6, ±3 have the same parity and residue and remain merged. | [G02-02:25](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:25>) |
| GPT03 | E | The exact four-class table includes isomorphism of the joint spatial law. | Saturation is strict at every finite L and p, not just equality of thermodynamic boundaries. | [G03-02:57](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:57>); [G03-02:72](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:72>) |

Comparative conclusion: All seven explicitly analyze parity/CRT. N5 is equivalent to N7/8, while N6 still merges q=±3.

## Q03 mod4 and mod6 are incomparable; N cannot be totally ordered

Question: Can mod4 and mod6 be ordered relative to each other?

Relation to the original task: Required when making cross-N comparisons. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: The two modular records lose different information; only integer q refines both.

Possible confusions: Assuming N4>N3 guarantees better information; treating Z4 merging ±2 and Z6 merging ±3 as the same degradation.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | mod4 and mod6 are explicitly incomparable, with two branches below integer q. | Neither numerical similarity nor N magnitude is treated as a total information order. | [F03-02:69](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:69>); [F03-02:82](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:82>) |
| Opus01 | E | Integer q degrades separately to mod4/mod6, giving two independent risk chains. | The branches are not forced into an order; numerical all-p inference is assessed separately. | [O01-01:119](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:119>); [O01-01:127](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:127>) |
| Opus02 | E | Two integer-to-modular risk chains are given; cross-N LP separately discloses exceptions. | A larger-N record refining both branches does not make the branches refine one another. | [O02-01:54](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:54>) |
| Opus03 | E | Integer divergence degrades to each modular record without asserting all-N monotonicity. | Z4’s special boundaries do not directly imply N4 globally outperforms or underperforms N3. | [O03-01:489](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:489>); [O03-01:498](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:498>) |
| GPT01 | E | No general N monotonicity is assumed; integer q refines both modular records. | Independent curve differences are separated from information ordering; no erroneous ordering was found. | [G01-02:46](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:46>); [G01-02:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:51>) |
| GPT02 | E | Different N4 aliases are listed; successive-N improvement is explicitly not assumed. | This is a full-channel relation on finite support, not a judgment from a single-p plot. | [G02-02:25](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:25>) |
| GPT03 | E | No prior ordering of mod-four and mod-six is assumed; integer q refines both. | Equivalence classes and the partial order are exact results, not fit-dependent. | [G03-02:57](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:57>); [G03-02:72](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:72>) |

Comparative conclusion: All seven use the correct branched inclusions and do not base results on a total order of consecutive N values.

## Q04 Nonnested individual sufficient bounds do not imply true phases violate information ordering

Question: Do nonnested sufficient-bound curves mean the true phase regions violate information ordering?

Relation to the original task: R1 interpretation. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: Different inequalities may discard different information, so independently proved subsets need not automatically be closed under the strongest available comparisons.

Possible confusions: Inferring a physical anomaly from a nominal reversal of weak bounds; ranking true thresholds by roots from different sufficient proofs.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | I | The N19 sufficient theorem and finite-N diagram are separated; nominal Z4 differences are handled. | The principle that independent weak bounds may be nonnested is not separately developed; coverage is implicit. | [F03-01:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190>); [F03-01:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201>) |
| Opus01 | I | Crossings are adjusted to O0 nesting and the theorem has a separate table. | No separate rule closes the sufficient-bound envelope under inclusions; this is an explanatory reservation. | [O01-01:268](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268>); [O01-01:275](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275>) |
| Opus02 | I | Paired risk nesting is checked; numerical diagrams and polymer sufficient regions are separate. | The text does not separately discuss nonnesting caused by information discarded in different sufficient proofs. | [O02-01:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212>); [O02-01:214](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214>) |
| Opus03 | I | High-p nesting is verified, with sufficient bounds and exact orientation structure separately supplied. | Component-level explanation is not a complete analysis of the sufficient-bound envelope. | [O03-01:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229>); [O03-01:668](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668>) |
| GPT01 | E | Sufficient roots are explicitly not thresholds; the apparent reversal lies within allowances. | A common weak O1 bound is not treated as equality of true boundaries at different N. | [G01-01:33](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33>); [G01-02:256](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256>) |
| GPT02 | E | μρ<1 is explicitly sufficient; unstable Z4 fits remain unresolved. | Equality at a root is not assigned a phase, avoiding “proof failure means nondecodable.” | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | I | Sufficient tails and numerical boundaries are separated; the nominal Z4 center is projected to respect ordering. | The inclusion closure of all independent bounds is not fully developed; coverage is implicit. | [G03-01:40](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40>) |

Comparative conclusion: GPT01/02 handle the semantics most explicitly. The others largely implement them through inclusion constraints or numerical processing, without all separately explaining sufficient bounds versus true phases.

## Q05 Transfer reliable Z4 decodable subsets to integer q

Question: Are reliable Z4 decodable subsets transferred to integer q?

Relation to the original task: R1/R2 consistency. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: Integer q can be reduced modulo four, so D1(4)⊆D1(5)=D1(7)=D1(8).

Possible confusions: Giving integer q a known decodable region smaller than a reliable Z4 subset; treating an unvalidated nominal fit center as a rigorous conclusion.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | I | The integer-q refinement of Z4 and numerical nesting are established. | Transferable reliable Z4 subsets are not separately tabulated; they are implicit in the hierarchy. | [F03-01:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190>); [F03-01:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201>) |
| Opus01 | I | Two exact risk chains guarantee integer q is no weaker than Z4. | No separate transfer rule excludes the donor endpoint allowance. | [O01-01:268](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268>); [O01-01:275](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275>) |
| Opus02 | I | Integer-q risk≤Z4 risk is explicit, with paired checks. | Subset transfer is implicit in the theorem; reliable intervals are not systematically closed under inclusions. | [O02-01:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212>); [O02-01:214](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214>) |
| Opus03 | I | Integer-charge degradation and high-p nesting both hold. | The all-p charge assignment covers the subset but has an A2 gap; it is not a reliable proof of all-p decoding. | [O03-01:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229>); [O03-01:668](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668>) |
| GPT01 | E | Only reliable portions outside the donor’s endpoint allowance are explicitly transferred. | Numerical transfers retain their numerical source labels and are not promoted to rigorous theorems. | [G01-01:33](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33>); [G01-02:256](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256>) |
| GPT02 | E | Exact information ordering organizes conservative intervals; unknown Z4 fits do not force transfer of nominal centers. | Proved tails are retained; unstable nominal crossings are not used as donors. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | I | Integer records refine Z4 and explicitly contain the full O0 decodable region. | Reliable numerical Z4 transfers are not listed individually as in GPT01. | [G03-01:40](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40>) |

Comparative conclusion: GPT01 explicitly transfers numerical subsets outside the endpoint allowance. GPT02 organizes conservative bounds using exact information relations. For the others, transfer is mostly implicit in the inclusion theorem.

## Q06 Distinguish Z4 pure-triple/single and mixed-triple/single ambiguities

Question: How do pure and mixed triples become ambiguous at Z4?

Relation to the original task: Feature mechanism. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: q=±3 becomes confused with ∓1 modulo four. Pure triples are distinguishable with integer charge, whereas mixed triples already have q=±1.

Possible confusions: Treating all triple aliases as new Z4 losses; deriving both true endpoint shifts directly from a local alias.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | I | The charge table lists q=3~−1 and −3~1 and discusses asymmetric Z4 behavior at low/high p. | Pure versus mixed triples are not fully traced to every local hiding pattern and both endpoints. | [F03-01:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190>); [F03-01:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201>) |
| Opus01 | I | Z4 triple aliases are tabulated and a charge4-defect picture is proposed. | This local/effective-model physical picture does not prove both threshold shifts. | [O01-01:268](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268>); [O01-01:275](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275>) |
| Opus02 | I | The CRT table lists triple aliases and discusses different low/high-p gains. | Pure triples are not individually contrasted with mixed triples that were already ambiguous. | [O02-01:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212>); [O02-01:214](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214>) |
| Opus03 | E | The N4 low-rank table and high-p affine-incidence analysis distinguish the cases. | Local losses alone still do not fix true boundaries; the mechanism’s scope is retained. | [O03-01:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229>); [O03-01:668](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668>) |
| GPT01 | E | Charge classes and exact orientation summation jointly explain Z4 triple ambiguities. | The high-p identity retains closed-component information and cannot prove threshold equality with O0. | [G01-01:33](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33>); [G01-02:256](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256>) |
| GPT02 | I | Every N4 triple has M=1, and the path constant explicitly changes to a special value. | The link from local counts to high/low-p thresholds is not fully developed; coverage is implicit. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | I | The charge-alias table is correct and information ordering controls the high Z4 endpoint. | Pure/mixed local mechanisms are not used to fully explain the asymmetric endpoints. | [G03-01:40](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40>) |

Comparative conclusion: Opus03/GPT01 give more complete mechanisms. The others mostly supply equivalence tables or coarse constraints, without tracing every local pattern to the two-end behavior.

## Q07 High-p active-component orientation identity and its scope

Question: Is there an exact active-component explanation for weak Z4 gains at high p?

Relation to the original task: Optional enhanced analysis. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: For a fixed active graph, random-orientation mod-4 charge is the affine image of a binary incidence map; closed components retain constraints.

Possible confusions: Upgrading a small high-p gain to channel or threshold equivalence O1(4)=O0; ignoring closed active components and zero-arrival vertices.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | M | Weak high-p Z4 improvement is noted and finite-size endpoints are supplied. | No active-component affine-incidence identity was found; this is a missing optional enhancement. | [F03-01:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190>); [F03-01:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201>) |
| Opus01 | M | Small high-p gain and nesting are discussed alongside a defect picture. | No exact component orientation sum is supplied; the physical picture cannot substitute for that identity. | [O01-01:268](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268>); [O01-01:275](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275>) |
| Opus02 | M | Paired posterior comparisons show a very small high-p gain. | No exact uniform-image proof for the active graph is supplied; empirical checks cannot replace it. | [O02-01:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212>); [O02-01:214](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214>) |
| Opus03 | E | Charge is proved uniform over parity-allowed labels on boundary-connected active components. | Closed active components and zero-arrival vertices retain extra information; threshold equivalence does not follow. | [O03-01:229](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229>); [O03-01:668](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668>) |
| GPT01 | E | Pr(k/x)=2^(c0−D) times closed-component charge-sum constraints is derived and independently checked. | The text explicitly uses the identity to check posteriors, not to assume high-noise channel equivalence. | [G01-01:33](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33>); [G01-02:256](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256>) |
| GPT02 | M | Special Z4 M values and conservative diagram handling are supplied. | The exact component identity given by Opus03/GPT01 was not found. | [G02-01:51](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51>); [G02-02:173](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173>) |
| GPT03 | M | Nominal high-end uncertainty and information-order projection are explained. | No active-component orientation identity is supplied; the original task did not require this enhancement. | [G03-01:40](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40>) |

Comparative conclusion: Opus03 and GPT01 independently derive exact identities. The same component analysis was not found in the others. This is an enhanced explanation, not an added original-task penalty.

## Q08 Neutral pairs remain invisible to O1; O2 hiding becomes rarer with N

Question: Why does O1 saturate while O2 can continue to improve with N?

Relation to the original task: R3/phase-diagram mechanism. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: A neutral V,Vbar pair always has integer charge zero. In O2, the probability that multiple arrivals yield a lower-count label decreases as N^-2.

Possible confusions: Equating integer q with the full arrival count; treating N^-2 as an independent vertex-failure probability; using O1 saturation to prove its central phase nondecodable.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Irrep ambiguities of 1/N² and 2/N² are listed, followed by random degradation to noisy degree. | Neutral pairs remain invisible in full q; saturation cannot establish central nondecodability. | [F03-02:113](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:113>) |
| Opus01 | E | An orientation-blind degree garbling describes count ambiguity by 1/N² and 2/N². | The large-N theorem handles correlation through deliberate degradation, not independent original orientations at each vertex. | [O01-01:140](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:140>) |
| Opus02 | E | A degree-record kernel precedes the polymer/Chernoff path bound. | Original O2 vertex observations are correlated; independence is used only in the legitimately degraded count channel. | [O02-01:76](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:76>) |
| Opus03 | E | Additional random coins give a uniform drop rate for each n, followed by path-overlap control. | 1/N² is not a single logical-failure probability and cannot simply be multiplied over all vertices. | [O03-01:574](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:574>) |
| GPT01 | E | Shared-arrow matrix norms bound pair hiding; the O1 constants do not decrease at large N. | Decoder scores and path-pattern sums remain necessary; hiding is not sufficient for failure. | [G01-02:104](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:104>) |
| GPT02 | E | The O1/O2 α0/α1 table directly displays O1 saturation and O2 decline. | Shared side edges/chords are separately controlled by second moments, not products of marginal hiding rates. | [G02-02:158](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:158>) |
| GPT03 | E | The integer O1 class and degradation of O2 to noisy degree are developed in parallel. | N^-2 strengthens the proof, but actual phases at finite small N require separate evidence. | [G03-02:157](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:157>) |

Comparative conclusion: All seven identify the mechanism and handle it through valid correlation bounds or randomized coarsening. O1 saturation is an exact information fact; it alone does not decide the central thermodynamic phase.

## Q09 Separate binary X,C from latent sigma; sigma is not given to the decoder

Question: Are binary X,C separated from latent arrow σ, and is σ incorrectly supplied to the decoder?

Relation to the original task: Core model. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: X records edge occupancy; σ determines which endpoint of an occupied edge receives V. Together they determine readout probabilities, but correction remains binary; conditioning on hidden variables in analysis does not make them visible to the decoder.

Possible confusions: Assuming a binary operator intrinsically has a direction, or that the task has no additional orientation.; Giving the decoder access to true σ.; Confusing edge identifier ei, occupancy bit Xi, and sign σi.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Support x and ε are separated at the outset, with prior 1−p,p/2,p/2; later visible degree garbling does not retain orientation. | The teaching statement that latent orientation is not provided to the decoder is dispersed, but the legitimate degradation establishes no hidden access. | [F03-02:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:3>) |
| Opus01 | E | Binary x and additional orientation σ are explicit; the private-randomness kernel uses only visible irreps. | Scientific modeling is complete; local arrow diagrams requested in this discussion are not additionally supplied. | [O01-02:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:3>) |
| Opus02 | E | exact_structure models x and orientation before degrading observations to degree-only dependence. | Scientific modeling is complete; the degraded proof need not retain σ states. | [O02-03:3](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/02_exact_structure.md:3>) |
| Opus03 | E | Three-state microscopic y identifies the V endpoint, while correction and success conditions remain binary. | Scientific modeling is complete; missing diagrams are separately assessed under Q21. | [O03-04:10](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/sec_model.md:10>) |
| GPT01 | E | Three-state microscopic variables and binary occupancy are separate; conditioning off-path microstates is only for probability bounds. | Modeling is correct; the original does not illustrate different σ values on the same binary support. | [G01-02:70](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:70>) |
| GPT02 | E | Latent arrows, path reference direction, and endpoint sign sharing are explicit; the auxiliary decoder uses only m. | Modeling and reference direction are clearest; a four-panel teaching diagram is still absent. | [G02-02:108](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:108>) |
| GPT03 | E | Additional orientations and conditionally independent readouts are introduced at the outset; second-moment analysis averages hidden orientations. | Modeling is correct; the second-moment method needs no arrow transfer matrix. | [G03-02:3](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:3>) |

Comparative conclusion: The frozen diagnostic is E for all seven. Reader confusion about arrows mainly concerns presentation depth; no run was found to replace binary correction with a directed operator.

## Q10 Difference components are self-avoiding because degrees are 0/2, not because of physical repulsion

Question: Why may a failure witness be a self-avoiding path rather than an arbitrary walk with loops?

Relation to the original task: Required when using a path proof. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: At honeycomb measured vertices, the difference degree is even and at most three, so a nonzero degree is two. Complete components are simple cycles or paths. Self-avoidance is a property of the difference graph, not an assumed physical repulsion.

Possible confusions: Inferring that every representative is self-avoiding merely because logical operators can be deformed.; Omitting multiple difference components or additional loops.; Confusing even difference degree with an even true arrival count.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Equal syndrome and maximum degree three yield degree0/2; disjoint simple cycles/paths follow, with a bottom–top component for logical failure. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [F03-02:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:190>) |
| Opus01 | E | Degree0/2 and spanning components are explicit; complete-component flips preserve local feasibility. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [O01-02:103](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:103>) |
| Opus02 | E | Direct posterior decomposition distinguishes cycles, same-side paths, and spanning paths; an odd number of spanning components changes logical sector. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [O02-02:8](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:8>) |
| Opus03 | E | The MAP-support difference decomposes by degree0/2; a spanning component witnesses failure. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [O03-02:166](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:166>) |
| GPT01 | E | A separate geometry section establishes simple components and minimum length without assuming actual errors self-avoiding. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [G01-02:7](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:7>) |
| GPT02 | E | Equal-syndrome differences at trivalent detectors force degree0/2 and a spanning component on failure. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [G02-02:145](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:145>) |
| GPT03 | E | The detailed geometry proof covers logical representatives, boundaries, and minimum spanning length. | No error here; stepwise loop-deformation diagrams would be an expository addition, not a change to the structural argument. | [G03-02:8](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:8>) |

Comparative conclusion: All seven are E. The proof counts an extractable simple difference component; it does not restrict all true errors or logical-operator representatives to self-avoiding forms.

## Q11 M is the minimum compatible count; only 11 forces true hiding, while 01/10 preserve the count

Question: Are M, true/candidate arrival counts, and local 00/01/10/11 changes explained correctly?

Relation to the original task: Required when using this coarse constraint. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: In the direct coarse-constraint route, M is the smallest same-parity arrival count allowed by the current readout. Degree≤3 gives n∈{M,M+2}. Only deleting true 11 to 00 forces the true record to hide a pair.

Possible confusions: Treating M as the true count or an observation-independent threshold.; Saying every path vertex must hide.; Ignoring the degree cap and allowing M+2,M+4,… .; Forcing the same notation onto a valid proof that does not use M.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | I | Noisy-degree-channel feasibility is used; double-edge flips change counts by ±2, while alternating patterns preserve them. Equivalent M content is inferable. | Frozen I: equivalent content is dispersed. This is not a scientific error or a requirement to adopt a GPT-style M decoder. | [F03-02:130](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:130>); [F03-02:201](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:201>) |
| Opus01 | I | Degree garbling and double/alternating overlaps cover the same local mechanism without a separate M table. | Frozen I: no dedicated M table; legitimate degradation incurs no method-choice penalty. | [O01-02:62](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:62>); [O01-02:114](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:114>) |
| Opus02 | I | Readout overlaps distinguish equal degree, +2, and −2; the direct-posterior route does not require M. | Frozen I: correspondence to this discussion is not expanded; the direct-posterior method itself needs no M. | [O02-02:19](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:19>); [O02-02:19](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:19>) |
| Opus03 | I | Degradation kernels and overlaps distinguish degrees; M-form content is implicit in feasibility rather than main notation. | Frozen I: local feasibility is correct; M exposition is not the original’s main route. | [O03-02:138](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:138>); [O03-02:184](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:184>) |
| GPT01 | E | m and true n∈{m,m+2} are explicit; only 11 requires B=1, 00 adds a pair, and mixed patterns preserve counts. | Frozen E; teaching notation may standardize m to M to avoid confusion with path length. | [G01-02:106](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:106>); [G01-02:119](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:119>) |
| GPT02 | E | The minimum same-parity count M, min/max decoders, and 11 hiding are all explicit. | Frozen E; this must not be read as saying every vertex has an even total arrival count. | [G02-02:130](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:130>); [G02-02:147](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:147>) |
| GPT03 | E | h is the minimum compatible count with n∈{h,h+2}; min-cardinality and hiding only at 11 are explicit. | Frozen E; original h must be distinguished from the chat’s use of h for side-edge occupancy. | [G03-02:194](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:194>); [G03-02:219](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:219>) |

Comparative conclusion: G01/02/03 are explicit on the direct-M route. F03 and all three Opus runs complete the science through equivalent degree-channel arguments; frozen I means only that the corresponding teaching explanation is dispersed.

## Q12 Hiding is necessary, not sufficient, and applies to the specified auxiliary decoder

Question: Why can hiding bounds control mismatch, and is a necessary condition being mistaken for a sufficient one?

Relation to the original task: Required when using a hiding proof. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: C is a function of global observations, so direct vertexwise mismatch calculation is difficult. The proof bounds failure by necessary local ambiguity plus a global selection condition, permitting overcounting rather than claiming every hiding event causes failure.

Possible confusions: Declaring logical failure after a single hiding event.; Applying the necessary condition to any syndrome-compatible correction while omitting the constructed auxiliary rule’s feasibility constraints.; Calling every geometric path counted by the upper bound a fully signal-compatible solution.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | The degraded failure witness needs a feasible complete component and rD≥1; hiding/overlap is only one part of the probability calculation. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [F03-02:188](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:188>) |
| Opus01 | E | MAP selection and component feasibility precede Bhattacharyya summation; a local low count is not equated with failure. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [O01-02:100](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:100>) |
| Opus02 | E | The direct posterior/polymer inequality bounds total wrong-sector weight, including feasibility and fractional ratios, rather than vertexwise hiding counts. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [O02-02:15](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:15>) |
| Opus03 | E | The complete witness includes a likelihood ratio; local confusion contributes only the overlap. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [O03-02:163](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:163>) |
| GPT01 | E | B=1 is only necessary to delete 11, followed by A≥1 and the auxiliary-risk comparison. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [G01-02:112](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:112>) |
| GPT02 | E | Local hiding, at least/at most half-path activity, and Chernoff are used jointly. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [G02-02:138](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:138>) |
| GPT03 | E | Necessary conditions apply only to the h-constrained auxiliary decoder, with a separate at-least-half-active requirement. | Frozen E: no “hiding means failure” error was found. The current discussion needs a more intuitive account of event inclusion. | [G03-02:213](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:213>) |

Comparative conclusion: None of the seven treats hiding as sufficient. They bound mismatch/wrong-sector probability; rarity of local events must be used together with global candidate selection.

## Q13 Decoder scores/minimum or maximum cardinality/Chernoff conditions enter the probability bound

Question: How does the decoder selection condition enter the whole-path probability bound?

Relation to the original task: Required for the corresponding proof approach. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: An alternating path may have no 11-hiding vertices. Scores, likelihood ratios, or direct posterior weights must also be included to suppress all occupancy patterns and obtain a valid ρ^d.

Possible confusions: Assuming multiplying only 11-hiding factors makes every path probability exponentially small.; Omitting the prior p/(1−p) from the score ratio.; Applying the min-cardinality “at least half active” condition to a max-cardinality rule.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | MAP support yields rD≥1; indicator≤√rD introduces Bhattacharyya overlaps and square-root edge priors. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [F03-02:196](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:196>) |
| Opus01 | E | A component likelihood ratio≥1 leads to the square-root moment; edges contribute √p(1−p) and vertices contribute overlaps. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [O01-02:107](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:107>) |
| Opus02 | E | No hard selection threshold is needed: wrong posterior≤the sum of path ratios, followed by fractional moment r^θ with an equivalent role. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [O02-02:15](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:15>) |
| Opus03 | E | MAP ratio≥1 combines with Bhattacharyya and includes every occupancy pattern. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [O03-02:173](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:173>) |
| GPT01 | E | Score ratio A≥1 combines square-root score weights with hiding rates so both 00 and 11 receive √t. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [G01-02:119](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:119>) |
| GPT02 | E | p selects minimum/maximum cardinality, forcing true active counts ≥/≤d/2 before Chernoff optimization. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [G02-02:190](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:190>) |
| GPT03 | E | Min-cardinality forces u≥d/2; Chernoff and an occupancy matrix average Bernoulli patterns, with separate high-p control. | Frozen E: the scientific step is complete. A direct-posterior route needs no fabricated MAP score threshold. | [G03-02:253](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:253>) |

Comparative conclusion: All seven retain the crucial selection/posterior-weight step. “Every 11 hides” alone is insufficient; valid proofs do not stop at local probabilities.

## Q14 Orientation-matrix states and individual entries are interpreted correctly

Question: When an orientation matrix is used, are ± states, entries, and endpoint normalization correct?

Relation to the original task: Applies to the direct matrix approach; NA for alternatives. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: On fixed active runs the orientation matrix propagates shared arrows. Entries are conditional readout weights given adjacent orientations, not transitions of a binary correction or a row-normalized Markov kernel.

Possible confusions: Treating ± orientations as occupancy 0/1.; Reversing the relative signs of left/right arrivals at the shared vertex.; Omitting the 1/2 prior for each active arrow or endpoint summation.; Requiring every valid proof to use an arrow matrix.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | NA | After valid random degradation, observations depend only on degree and orientations are summed out; no arrow matrix is used. | Frozen NA: a valid alternative, not an omission. | [F03-02:183](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:183>) |
| Opus01 | NA | Visible irreps are first degraded to an orientation-blind channel; ± states need not be retained. | Frozen NA: a valid alternative, not an omission. | [O01-02:97](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:97>) |
| Opus02 | NA | A direct degree-channel posterior proof makes the arrow matrix inapplicable. | Frozen NA: a valid alternative, not an omission. | [O02-02:8](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:8>) |
| Opus03 | NA | The degraded likelihood explicitly omits orientation, which has been legitimately eliminated. | Frozen NA: a valid alternative, not an omission. | [O03-02:158](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:158>) |
| GPT01 | E | Active runs use ± states and a 1/2 prior for the next arrow; endpoint vector (1,1)/√2 has norm one, followed by operator norms. | Frozen E: the formulas are correct; missing entry-by-entry teaching diagrams are assessed under Q21. | [G01-02:155](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:155>) |
| GPT02 | E | Path reference direction, arrivals ui and −ui+1, F/2, endpoint vectors, and rank-dependent matrix norms are explicit. | Frozen E: states/endpoints are adequately explained; four-panel diagrams remain absent. | [G02-02:149](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:149>) |
| GPT03 | NA | Bipartite second-moment Cauchy–Schwarz averages true orientations without an arrow matrix. | Frozen NA: second moments handle the same correlation, not an omission. | [G03-02:227](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:227>) |

Comparative conclusion: Only G01/02 directly use this method and both are E; the others are NA. Drawing an arrow matrix cannot become mandatory for R3 correctness.

## Q15 Occupancy and orientation matrices have different state spaces

Question: Are occupancy-pattern sums distinguished from arrow sums, and where does ρ come from?

Relation to the original task: Applies to the two-matrix approach; NA for alternatives. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: The ± matrix averages latent orientations; the 0/1 matrix sums true Bernoulli occupancy patterns. The latter, together with score/Chernoff weights, produces ρ, not a single-vertex hiding probability. Proofs using only one matrix can also be valid.

Possible confusions: Equating ρ with 1/N².; Resampling the same edge at its two vertices.; Interpreting every transfer matrix as physical time evolution.; Penalizing an alternative proof for using only an occupancy matrix.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | NA | The occupancy/candidate-pattern matrix [[β,1],[1,β]] and binary-sequence sum are explicit; no second arrow matrix can be confused with it. | Frozen NA concerns distinguishing two matrices; occupancy summation itself is explicit, not missing. | [F03-02:220](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:220>) |
| Opus01 | NA | The occupancy matrix is explicit; β comes from readout overlap and side-edge averaging, with no two-matrix distinction needed. | Frozen NA concerns the two-matrix route; the occupancy matrix is a valid core step. | [O01-02:118](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:118>) |
| Opus02 | NA | General-θ edge occupancy weights w and T are explicit; a Perron root controls all patterns after degradation removes orientations. | Frozen NA concerns the two-matrix route and cannot mean pattern summation is absent. | [O02-02:19](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:19>) |
| Opus03 | NA | An occupancy matrix with a common eigenvector is used after true arrows are summed out. | Frozen NA concerns the two-matrix route; the occupancy-matrix content is complete. | [O03-02:186](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:186>) |
| GPT01 | I | Lines125–129 correctly sum equal-occupancy pairs; an orientation matrix is separate, but no occupancy K matrix is separately named. | Frozen I: the equivalent sequence formula is complete; drawing K and its 0/1 states would be clearer, not a correction to the probability bound. | [G01-02:125](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:125>) |
| GPT02 | E | The 0/1 occupancy matrix and Chernoff weights are explicitly separate from the preceding ± orientation matrix. | Frozen E: the two state spaces are most explicit. | [G02-02:190](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:190>) |
| GPT03 | NA | Occupancy A_z and Chernoff are explicit; correlation uses second moments rather than another ± matrix. | Frozen NA concerns the two-matrix route; the 0/1 matrix is already explicit. | [G03-02:253](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:253>) |

Comparative conclusion: G02 explicitly separates the two matrices; G01 gives an inferable formula with shorter teaching explanation. The others do sum patterns, but legitimately avoid the two-matrix route.

## Q16 Shared off-path edges/chords cannot be independently redrawn at each vertex

Question: If a third off-path edge is a chord, is its use twice handled as one shared variable?

Relation to the original task: Core correlations; valid avoidance can receive E. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: A self-avoiding geometric path need not be chordless. One off-path edge may touch two path vertices, so its state must be shared rather than averaged independently at the two endpoints.

Possible confusions: Assuming self-avoiding paths automatically have no chords.; Independently sampling activity or arrows at both ends of one side edge.; Using a matrix within active runs, then independently averaging every side-edge occurrence.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Side edges used once/twice are summed separately; a chord pair gives (1+p)/N² and is uniformly bounded by β². | Frozen E: no missing chord contribution was found. | [F03-02:212](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:212>) |
| Opus01 | E | Chord sharing is explicit; Cauchy–Schwarz controls two-end averaging and separate control handles nonchord single endpoints. | Frozen E: no missing chord contribution was found. | [O01-02:116](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:116>) |
| Opus02 | E | Chords use Cauchy–Schwarz and single endpoints use Jensen; each side edge touches at most two path vertices. | Frozen E: no missing chord contribution was found. | [O02-02:22](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:22>) |
| Opus03 | E | Averaging is grouped by physical third edge rather than independently by vertex. | Frozen E: no missing chord contribution was found. | [O03-02:190](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:190>) |
| GPT01 | E | After conditioning, occurrences j=1,2 of the same third edge are grouped and bounded by ((1−p)τ0+pτ1)^(j/2). | Frozen E: no missing chord contribution was found. | [G01-02:179](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:179>) |
| GPT02 | E | The base proof explicitly handles chords; the N13 improvement retains correlated cycle factors by positive-cycle expansion. | Frozen E: no missing chord contribution was found. | [G02-02:175](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:175>) |
| GPT03 | E | Same-color bipartite vertices depend on disjoint microscopic edges; cross-color Cauchy–Schwarz covers chords. | Frozen E: no missing chord contribution was found. | [G03-02:227](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:227>) |

Comparative conclusion: This is a key detail all seven accomplish. GPT02 retains finer cycle corrections; the other routes relax correlations through valid inequalities.

## Q17 R*<=R_aux compares average risks; an exponential bound is not a critical exponent

Question: Are R*≤Raux and exponential scaling interpreted correctly?

Relation to the original task: Core proof conclusion. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: R is average logical-failure probability. One legitimate rule with vanishing average risk implies vanishing optimal average risk; no recordwise comparison or auxiliary optimality is required. An exponential upper bound does not give a true critical exponent.

Possible confusions: Claiming the optimal decoder does no worse than the auxiliary decoder on every sample.; Using failure-event inclusion as the reason for optimal-risk comparison.; Presenting the exponential upper bound as the exact logical error rate or critical scaling.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Bayes/data-processing risk comparison is explicit; MAP support is auxiliary, not claimed sector-optimal. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [F03-02:13](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:13>) |
| Opus01 | E | Average-risk degradation ordering and the auxiliary bound are explicit; the sufficient theorem and numerical phases are separate. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [O01-02:9](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/proofs/R2_R3_proofs.md:9>) |
| Opus02 | E | Wrong-sector Bayes risk is averaged directly and bounded by path fractional moments, without a recordwise optimality assumption. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [O02-02:15](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/report/03_large_N.md:15>) |
| Opus03 | E | MAP-configuration risk bounds optimal logical risk; the exponential theorem is only sufficient. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [O03-02:163](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/docs/proofs.md:163>) |
| GPT01 | E | Auxiliary risk explicitly bounds optimal risk, with risk≤constant·Lr^(2L−1)/(1−r), not a true phase boundary. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [G01-02:138](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:138>); [G01-02:130](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:130>) |
| GPT02 | E | The complete geometric-series bound and optimal-average-risk comparison are supplied; equality is not a phase boundary. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [G02-02:145](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:145>); [G02-02:208](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:208>) |
| GPT03 | E | Average Bayes ordering is explicit; the loose bound may not visibly decrease at finite simulation sizes. | Frozen E: this step’s scientific meaning is correct. Explaining why R is an average probability is a teaching addition. | [G03-02:189](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:189>); [G03-02:313](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:313>) |

Comparative conclusion: All seven correctly interpret risk and scope. A vanishing upper bound is sufficient evidence of decodability; a nonvanishing upper bound cannot conversely prove nondecodability.

## Q18 The partition function preserves global orientations; distinguish small-size exact inference from large-size MPS

Question: Does the prescribed small-size regime L≤4,N≤8 use an exact or certified algorithm?

Relation to the original task: R4 core. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: The small-size exact API is an automatically checkable deliverable. The algorithm should retain all configurations. Its complexity may grow exponentially with width, without first proving that the model is free fermionic.

Possible confusions: Call a truncated MPS result an untruncated exact result.; Conflate a large-size approximation with the prescribed small-size API.; Substitute an unimplemented Pfaffian/free-fermion theory for a working algorithm.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [F03-04:25](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/README.md:25>) |
| Opus01 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [O01-01:67](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:67>) |
| Opus02 | I | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The public API switches to MPS at L>9; small sizes remain exact, so the no-truncation wording needs qualification. | [O02-05:18](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/README.md:18>) |
| Opus03 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [O03-06:12](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/solution.py:12>) |
| GPT01 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [G01-03:279](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/decoder.py:279>) |
| GPT02 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [G02-04:314](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/decoder.py:314>) |
| GPT03 | E | Exact contraction in the prescribed small-size regime; larger-size methods require separate checking. | The original text and independent checks support the small-size exact construction. | [G03-03:267](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/decoder.py:267>) |

Comparative conclusion: All seven small-size exact constructions are supported; this does not make the Opus large-size MPS exact. Opus02's wording is incomplete, marked I rather than R4 failure.

## Q19 Separate estimates, sufficient bounds, unknowns, and statistical/finite-size/approximation uncertainty

Question: Are estimates, sufficient bounds, unknowns, and the three uncertainty sources clearly separated?

Relation to the original task: R1 core. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: Readers must distinguish data-supported judgments, certified theorems, and possible long-scale crossovers.

Possible confusions: Hiding unknowns behind a polished phase diagram; treating χ differences as bounds; treating zero failures or small sampled risks as a full-p thermodynamic proof.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | I | Exact contraction is separated from statistical/size errors, and possible long decay is disclosed. | The final positive central intercept is still interpreted as a nondecodable phase; disclosure does not remove the inference gap. | [F03-01:213](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:213>); [F03-01:219](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:219>) |
| Opus01 | X | Numerical diagrams, large-N theorems, statistics, and χ diagnostics are distinguished. | χ differences are elevated to error bounds on true R*; the central zero limit also exceeds the evidence. | [O01-01:82](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:82>); [O01-01:164](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:164>) |
| Opus02 | X | Large-χ, log-odds, and multiple-size reports are saved and empirical control is acknowledged. | Induced bias is still claimed bounded by χ differences, and BKT exclusion is not rigorously established. | [O02-01:301](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:301>); [O02-01:319](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:319>) |
| Opus03 | X | Error sources are fully classified; subset χ studies and late-crossover reservations are retained. | A maximum χ change is said to guarantee all R1 answers unchanged without a true-posterior error bound. | [O03-01:355](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:355>); [O03-01:391](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:391>) |
| GPT01 | E | Rigorous subsets, inherited numerical regions, and unknowns are layered; statistics, size, and rounding are assessed separately. | The central thermodynamic phase remains unsolved and is accurately retained as unknown. | [G01-01:123](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:123>) |
| GPT02 | E | A rigorous-only plot, all fits including failures, perturbation checks, and rare-event limitations are supplied. | The 12 unknown entries are justified; this is not a complete solution of all true phase boundaries. | [G02-01:99](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:99>) |
| GPT03 | E | The N14 theorem and small-N numerics are distinguished; bootstrap, size, and rounding are separate. | Small-N all-p assignments retain grid and late-crossover reservations; A2 already deducts one point. | [G03-01:185](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:185>) |

Comparative conclusion: GPT01/02 are most conservative. GPT03 makes a qualified numerical assignment for small-N O2. Fable’s limiting interpretation and Opus’s approximation guarantees are the main risk points.

## Q20 Count every exception as failure; reserved slots are not completed trials

Question: Are all attempts, exceptions, stopping rules and raw data accounted for unconditionally?

Relation to the original task: Explicit deliverable requirement. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: Dropping difficult records biases risk downward. The exception-as-failure rule must enter the reported metrics; reserved slots must not be presented as completed physical trials.

Possible confusions: Remove exceptional samples from the denominator.; Assign hard failure 1 but posterior-min risk only 0.5.; Save only successful posterior evaluations, preventing selection-bias auditing.; Report the reserved slots of an externally terminated batch as completed trials.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | X | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions set P0=0.5 and risk/hard tie to 0.5; zero archived exceptions make this a latent defect. | [F03-07:56](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/src/run_mc.py:56>) |
| Opus01 | X | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Reports 2 actual exceptions; hard failure is 1, but reported risk remains 0.5. | [O01-08:146](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/src/mc.py:146>) |
| Opus02 | X | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions receive hard failure 1 and risk 0.5; this row makes no inference about their actual count. | [O02-08:49](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/hexsym/sim.py:49>) |
| Opus03 | X | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions receive hard failure 1 and risk 0.5; this row makes no inference about their actual count. | [O03-11:121](</Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/symdec/mc.py:121>) |
| GPT01 | E | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions and invalid outputs receive risk and failure 1; saved-array auditing found no inconsistency. | [G01-06:50](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/README.md:50>) |
| GPT02 | E | Preserves raw data, seeds, stopping rules and denominators for all attempts. | Exceptions and invalid outputs receive 1; checks of 305024 evaluation rows and 4 archive hashes agree. | [G02-07:61](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/README.md:61>) |
| GPT03 | E | Preserves raw data, seeds, stopping rules and denominators for all attempts. | 340600 archived slots include 200 reservations from a terminated batch; the physical-trial total is unknown. | [G03-06:62](</Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/README.md:62>) |

Comparative conclusion: X indicates a defect in this detail, not automatic whole-task failure; GPT03 adequately discloses reserved slots, which must not be used to inflate completed-trial counts.

## Q21 Use diagrams to explain sigma, F, and endpoint summation entry by entry

Question: Does the original submission explain σ, matrix entries, and endpoint sums in diagrams without notation conflicts?

Relation to the original task: New teaching request in this discussion; not required by the original task. Coverage statuses in this section do not change the main 100-point score.

Reason for checking: This is a new teaching request in the current discussion. It can assess readability and explanatory depth but cannot be added retroactively to the original 100 points. The chat figure’s a/b conflict arose in this explanation and cannot be attributed to an original run.

Possible confusions: Retroactively treating a later teaching request as mandatory in the original task.; Attributing the chat’s use of a,b for both ± indices and arrival counts to an original submission.; Requiring a valid proof without an arrow matrix to draw a matrix it does not use.

| Run | Status | Content in the submission | Explanatory gaps / caveats / alternative routes | Evidence |
| --- | --- | --- | --- | --- |
| Fable03 | M | No four-panel arrow teaching figure is supplied; the scientific proof first eliminates orientation, so a degree-channel diagram would be more suitable. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| Opus01 | M | No four-panel arrow teaching figure is supplied; diagrams of the degradation kernel and occupancy matrix could be added. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| Opus02 | M | No four-panel arrow teaching figure is supplied; posterior-component maps and fractional moments would be more suitable diagrams. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| Opus03 | M | No four-panel arrow teaching figure is supplied; degree-kernel and chord-grouping diagrams could be added. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| GPT01 | M | Orientation-matrix formulas are present, but no entry-by-entry ± diagram or endpoint-summation figure. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| GPT02 | M | States and reference direction are explained more fully, but no four-panel diagram for each matrix entry is supplied. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |
| GPT03 | M | No four-panel arrow teaching figure is supplied; this method has no arrow matrix and could use a bipartite second-moment diagram. | Frozen M records only the absent new teaching deliverable, without original-task deduction; the chat’s notation conflict is not attributed to this run. |  |

Comparative conclusion: None of the seven meets this newly requested entry-by-entry diagram requirement. It is a shared presentation layer to add to a teaching reference answer, not evidence that all seven R3 proofs are wrong.

# Cross-aspect summaries: scores, methods, errors, and shared capabilities

## Totals, component scores, and key scientific assessments

| Rank | Run | R1/30 | R2/15 | R3/20 | R4/20 | Delivery/15 | Total | Scientific assessment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | GPT01 | 30 | 15 | 20 | 20 | 15 | 100 | Provisional pass with the conservative answer permitted by the task |
| 1 | GPT02 | 30 | 15 | 20 | 20 | 15 | 100 | Provisional pass with the conservative answer permitted by the task |
| 3 | GPT03 | 29 | 15 | 20 | 20 | 15 | 99 | Pass with caveats: numerical all-p extrapolation at small N |
| 4 | Fable03 | 26 | 15 | 19.5 | 18 | 14 | 92.5 | Partial: central-phase evidence / numerical range |
| 5 | Opus01 | 22 | 15 | 20 | 18 | 14.5 | 89.5 | Partial: central extrapolation / approximation guarantees / numerical range |
| 5 | Opus02 | 22 | 15 | 20 | 18 | 14.5 | 89.5 | Partial: central extrapolation / approximation guarantees / numerical range |
| 7 | Opus03 | 22 | 15 | 19 | 18 | 14.5 | 88.5 | Partial; additional caveat on original all-p certification |

Equal totals receive tied ranks. Fable01/02 are void and unranked. Scores follow the established rubric; totals do not replace scientific assessments. For example, insufficient evidence for a definite central-phase conclusion remains a key gap even when structure, algorithms, code, and data earn substantial completion credit.

## Complete matrix and discrimination of the 23 main criteria

| Criterion | Maximum | Fable03 | Opus01 | Opus02 | Opus03 | GPT01 | GPT02 | GPT03 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 R1 coverage | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| A2 R1 basis for phase classification | 8 | 4 | 5 | 5 | 5 | 8 | 8 | 7 |
| A3 R1 uncertainty control | 8 | 8 | 3 | 3 | 3 | 8 | 8 | 8 |
| A4 R1 figure and classification semantics | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| A5 R1 structural consistency | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| B1 R2 model/geometry | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| B2 R2 information order | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| B3 R2 charge equivalence | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| B4 R2 special ranks | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| C1 R3 statement | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| C2 R3 witness/decoder | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| C3 R3 correlations | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| C4 R3 exponential bound and certification | 4 | 3.5 | 4 | 4 | 3 | 4 | 4 | 4 |
| C5 R3 scope of conclusions | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| D1 R4 joint partition sum | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| D2 R4 exact algorithm | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| D3 R4 independent verification | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| D4 R4 numerical range | 3 | 1 | 1 | 1 | 1 | 3 | 3 | 3 |
| D5 decode interface | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| E1 answers.json | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| E2 Report/figures | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| E3 Source/reproduction/resources | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| E4 Data/unconditional accounting | 5 | 4 | 4.5 | 4.5 | 4.5 | 5 | 5 | 5 |

All seven receive full credit on 18/23 criteria. Five criteria discriminate between scores: A2 phase-assignment evidence, A3 error control, C4 exponential bounds and all-p certification, D4 numerical range, and E4 unconditional accounting. Shared high scores reflect supported abilities in exact structure and finite-size algorithms and should remain visible; key differences concern the use of scientific evidence and the scope of numerical commitments.

## Potential errors, actual issues, and affected runs

| Error type checked | Affected runs in this review | Nature of evidence and caveats | Related criteria |
| --- | --- | --- | --- |
| Overextrapolating finite-size trends | Fable03, Opus01/02/03; a milder extrapolation caveat for GPT03 | Key evidence insufficient in the first four; GPT03 has a caveat on an acceptable numerical assignment | A2, Q19 |
| Treating agreement between approximations as a true-error upper bound | Opus01, Opus02, Opus03 | Insufficient approximation-error guarantees; robustness of all phase assignments is not guaranteed | A3, Q18/19 |
| Treating a numerical maximum as rigorous all-p certification | Opus03; milder caveat on the original arithmetic presentation of Fable03 | Certification completeness as submitted; theorem supported after independent supplementary certification | C4 |
| Underflow or false zero-support diagnosis for positive-probability records | Local stress checks for Fable03 and Opus01/02/03 | Implementation-range gap; Linux/macOS differences remain a caveat | D4 |
| Recording posterior risk as 0.5 rather than failure 1 on exceptions | Latent Fable03 code path; code paths in all three Opus runs | Fable archives zero exceptions; Opus01 explicitly reports two, with no inferred counts for the others | E4, Q20 |
| Calling reserved slots completed physical trials | GPT03 specifically checked in this report | Accounting caveat, not classified as scientific failure; 200 reserved slots listed separately | E4, Q20 |
| Missing complete q at N5 or incorrectly claiming monotonicity for all N | All seven correctly handle charge classes | No such core error found in this batch; differences are not invented | B3, Q02/03 |
| Ignoring shared orientations / requiring arrow matrices in every proof | The seven use different valid routes to handle correlations | No scientific reason found to require a single matrix formulation | C3, Q14/16 |

This table distinguishes wrong conclusions, insufficient evidence, numerical implementation, delivery accounting, and review considerations. The true physical conclusion for the central phase region has not been proved; insufficient evidence is not described as proved physical falsity.

## Large-N proof routes and strength of results

| Run | N0 | Proof route used | As-submitted score | Theorem after review |
| --- | --- | --- | --- | --- |
| Fable03 | 19 | Random degree coarse-graining; MAP configurations, Bhattacharyya and occupancy matrices; finite-memory path bounds. | 19.5/20 | Supported; sufficient, not minimal |
| Opus01 | 15 | Random degree coarse-graining, MAP/Bhattacharyya; chords handled through shared side edges; rational certificates. | 20/20 | Supported; sufficient, not minimal |
| Opus02 | 15 | Random degree coarse-graining; direct posterior/polymer injection and fractional moments; interval certificates. | 20/20 | Supported; sufficient, not minimal |
| Opus03 | 15 | Random degree coarse-graining, MAP/Bhattacharyya; occupancy summed before side-edge treatment; original maximum obtained by floating-point optimization. | 19/20 | Supported; sufficient, not minimal |
| GPT01 | 13 | Direct coarse M constraints and parity penalties; orientation norms, chord grouping, occupancy sums; three-part rational certificate. | 20/20 | Supported; sufficient, not minimal |
| GPT02 | 13 | Minimum/maximum edge counts, orientation matrices, and Chernoff; positive-cycle/Ihara-Bass strengthening to N13. | 20/20 | Supported; sufficient, not minimal |
| GPT03 | 14 | Minimum-edge auxiliary decoder; bipartite Cauchy-Schwarz correlation control; Chernoff and rational bounds. | 20/20 | Supported; sufficient, not minimal |

The values 13, 14, 15, and 19 do not conflict: each is a sufficient N0. A smaller valid N0 is stronger and is therefore reported separately; under the original rubric, a larger valid N0 does not constitute R3 failure. A proof can avoid direct orientation matrices through valid garbling or Cauchy-Schwarz; it must not lose points for differing from the teaching route.

## Posterior algorithms, approximation scope, and independent verification

| Run | Small-size exact method | Larger-size research method | Comparison caveats |
| --- | --- | --- | --- |
| Fable03 | Exact three-state frontier transfer matrix, with two-state special cases where appropriate. | The study uses exact contraction: three-state L≤12, two-state L≤16, without MPS truncation. | Exact up to rounding; external small-size checks pass, but do not validate infinite-size extrapolation. |
| Opus01 | Untruncated column transfer matrix with explicit logical parity. | The report states exact ternary L≤14 and binary L≤18; larger sizes through L48 use χ64 MPS. | The χ64/128 difference is an empirical stability check, not a rigorous bound on true bias; see A3. |
| Opus02 | The public API uses an exact frontier at L≤9; L≤4 satisfies R4. | The public API uses χ64 MPS at L>9; production scans also use χ32/48 and other settings. | API and study-scan parameters differ; the README's broad exactness wording does not cover L>9. |
| Opus03 | The public small-size API uses an exact frontier, with valid elimination in two-state special cases. | Exploration at L≤12 uses exact inference; production Q2—Q9 use χ64 MPS at all L, with some χ128 checks. | Truncation weights and χ comparisons are present; these do not automatically certify every production posterior's error. |
| GPT01 | Untruncated three-state column frontier with Decimal fallback. | Dense and exact sparse support storage; sparsification uses no weight threshold. | Deleting zero support in an exact storage variant is not approximate truncation; large-size limits still require extrapolation or theorems. |
| GPT02 | Nonnegative exact column summation, with log-domain inference near endpoints. | compressed.py performs exact support pruning and removes no positive-weight configurations. | Memory is exponential in width; MPS or free fermions are not needed to satisfy the small-size requirement. |
| GPT03 | Exact column-frontier summation with log arithmetic for extremely small probabilities. | The study uses the same kind of exact frontier, without MPS truncation. | The archived study has reserved slots from external termination; exact summation does not mean every planned trial ran. |

| Run | Ordinary posterior | Ordinary case composition | Very-low-p stress | Ordinary correction |
| --- | --- | --- | --- | --- |
| Fable03 | 210/210 | 140 original R4 + 70 O0 | 0/18 | 210/210 |
| Opus01 | 210/210 | 140 original R4 + 70 O0 | 0/18 | 210/210 |
| Opus02 | 210/210 | 140 original R4 + 70 O0 | 0/18 | 210/210 |
| Opus03 | 210/210 | 140 original R4 + 70 O0 | 0/18 | 210/210 |
| GPT01 | 210/210 | 140 original R4 + 70 O0 | 18/18 | 210/210 |
| GPT02 | 210/210 | 140 original R4 + 70 O0 | 18/18 | 210/210 |
| GPT03 | 210/210 | 140 original R4 + 70 O0 | 18/18 | 210/210 |

The maximum ordinary posterior discrepancy is about 1.033e-14, below the original 1e-9 requirement. Stress inputs have strictly positive probability, but local macOS longdouble range differs from the original Linux environment, particularly requiring qualification for Opus02. Computing p/2 in Python float first introduces a separate cross-platform risk of losing the smallest subnormal.

## Run profiles and scope of conclusions

| Run | Established strengths | Main issues or unknowns | Scientific assessment |
| --- | --- | --- | --- |
| Fable03 | Complete exact-posterior and structural analysis; valid N19 sufficient proof. | Positive-risk central charge conclusion does not exclude a long crossover; gaps in extreme range and latent exception fallback. | Partial completion; 92.5 points do not establish the central-phase assignment. |
| Opus01 | Larger two-dimensional sizes and extensive diagnostics; N15 proof. | Charge pinning of the clean-loop phase is a physical explanation; chi differences do not certify true bias. | Partial completion; avoid attributing the same BKT formula as Opus02/03. |
| Opus02 | Large-size MPS study and cross-rank information analysis; direct posterior proof. | BKT exclusion and approximation guarantees are unestablished; API exact range and platform need qualification. | Partial completion; ordinary small-size R4 checks still pass. |
| Opus03 | Independent Z4 active-component identity; larger-size study. | Insufficient central extrapolation and chi-bias guarantees; original all-p arithmetic certification needs supplementation. | Partial completion; supplementary certification supports the N15 theorem. |
| GPT01 | N13 direct matrix proof, Z4 identity, and comprehensive numerical safeguards. | 11/21 phase entries remain unresolved; the full physical phase diagram is not solved. | Provisional pass with the conservative answer permitted by the original task. |
| GPT02 | Strengthened N13 proof, exact support pruning, and detailed certificates. | 12/21 entries unresolved, appropriately retaining undecided ranges. | Provisional pass with the conservative answer permitted by the original task. |
| GPT03 | N14 bipartite proof; exact posterior and endpoint safeguards. | All-p small-N O2 is a numerical assignment; finite-grid/late-crossover caveats remain. | Provisional pass with caveats; slots distinguished from actual trials. |

| Archived model group | Attempts | Valid | Mean among valid runs | Valid-run range | Interpretation |
| --- | --- | --- | --- | --- | --- |
| Fable | 3 | 1 | 92.50 | 92.5-92.5 | Describes a few runs of the same task; cannot establish population success rates |
| Opus | 3 | 3 | 89.17 | 88.5-89.5 | Describes a few runs of the same task; cannot establish population success rates |
| GPT | 3 | 3 | 99.67 | 99-100 | Describes a few runs of the same task; cannot establish population success rates |

# Conclusions and fairness limits

This batch shows strong shared capabilities: exact structure, charge equivalence classes, small-size joint posteriors, and valid corrections are independently completed by all seven. Integer-q recovery at N5 and saturation for N>=7 are not widespread omissions; self-avoiding components and correlations also admit different valid treatments.

Expert judgment is needed to assess whether evidence supports final phase-region and error commitments: slow decline and apparent plateaus do not determine the infinite-size limit; agreement between two truncated results does not bound bias relative to the exact value; floating-point global optimization is not rigorous all-p certification. Numerical range and failure accounting are separately repairable implementation/delivery issues and are not automatically failures of deep scientific ability.

The 100 points for GPT01/02 mean their outputs satisfy the current task commitments on justified unresolved results, valid sufficient bounds, and interfaces. This scoring system does not require a fully solved physical phase diagram as the only acceptable answer. Full credit can therefore coexist with open phase regions.

Scores assess final submissions and saved evidence. Rational proofs supplemented in subsequent review are not credited as present in the original AI submissions, nor represented as actual reruns after expert intervention. Four-cell teaching diagrams were not required by the original task and incur no retrospective deductions; the a/b notation mix-up belongs to this chat explanation.

Without guided-B controls and a complete formal freezing protocol, this does not establish completed SciCode difficulty calibration. Small-sample differences among seven runs do not establish overall model superiority, and the two void API attempts are not scientific failures. The true central O1 phase still requires independent research; a gold answer is not chosen by majority vote.

# Evidence index and traceability records

Main submission root: `/Users/home/Downloads/20261014-102308_d89b765a`. File-ID prefixes F03, O01, O02, O03, G01, G02, and G03 correspond to the run names and archived directories in this report; REV denotes saved independent-review evidence. The number after the colon is the original file line number. Full absolute paths, SHA-256 hashes, and all cited line numbers are stored in `comparative-report.json`. 

| File ID | Archived relative file | Lines cited in this report |
| --- | --- | --- |
| F03-01 | report.md | 36,128,190,201,213,219,311 |
| O01-01 | report.md | 5,67,82,105,109,114,119,127,140,164,268,275,326,329,337,503 |
| O02-01 | REPORT.md | 26,40,45,54,76,86,142,184,212,214,247,301,310,319 |
| O03-01 | report.md | 17,229,239,297,355,373,391,489,498,502,506,540,574,654,668,681 |
| G01-01 | report.md | 5,33,53,55,86,123 |
| G02-01 | report.md | 51,70,75,83,99 |
| G03-01 | report.md | 3,15,29,40,92,121,185 |
| G02-02 | proofs.md | 3,25,89,108,130,138,145,147,149,158,173,175,190,208,219 |
| G01-02 | proofs.md | 7,46,51,64,70,104,106,112,119,125,130,132,138,142,155,179,194,208,225,256 |
| F03-02 | docs/theory.md | 3,13,18,69,82,94,113,130,171,183,188,190,196,201,204,212,220,224,229,237 |
| G03-02 | proofs.md | 3,8,36,57,72,142,157,189,194,213,219,227,253,278,313 |
| O01-02 | proofs/R2_R3_proofs.md | 3,9,62,95,97,100,103,107,111,114,116,118,122,132 |
| O02-02 | report/03_large_N.md | 1,8,15,19,22,26,39 |
| O03-02 | docs/proofs.md | 134,138,158,163,166,173,181,184,186,190,199,218 |
| G02-03 | large_N_13.md | 62,132 |
| O03-03 | scripts/r3_bound.py | 31 |
| O02-03 | report/02_exact_structure.md | 3 |
| O03-04 | docs/sec_model.md | 10 |
| F03-03 | src/model.py | 1,198,280 |
| REV-01 | results/anthropic__claude-fable-5-1-run_03-checks.json | 1 |
| O01-03 | src/tm.py | 1 |
| REV-02 | results/anthropic__claude-opus-5-5-run_01-checks.json | 1 |
| O02-04 | hexsym/api.py | 43,45,143 |
| REV-03 | results/anthropic__claude-opus-5-5-run_02-checks.json | 1 |
| O03-05 | symdec/tm.py | 1 |
| REV-04 | results/anthropic__claude-opus-5-5-run_03-checks.json | 1 |
| G01-03 | decoder.py | 232,271,279,403 |
| REV-05 | results/openai__gpt-6-astra-run_01-checks.json | 1 |
| G02-04 | decoder.py | 175,224,314,391 |
| REV-06 | results/openai__gpt-6-astra-run_02-checks.json | 1 |
| G03-03 | decoder.py | 182,187,267,312 |
| REV-07 | results/openai__gpt-6-astra-run_03-checks.json | 1 |
| F03-04 | README.md | 6,25,30 |
| O02-05 | README.md | 4,18,24 |
| O03-06 | solution.py | 12 |
| F03-05 | tests_validate.py | 18 |
| O01-04 | tests/test_small.py | 8 |
| O02-06 | tests/validate.py | 21 |
| O03-07 | tests/test_validate_small.py | 7 |
| G01-04 | validate.py | 1 |
| G02-05 | validate.py | 1 |
| G03-04 | validate.py | 1 |
| O01-05 | solution.py | 71,102 |
| O03-08 | symdec/api.py | 43,74 |
| F03-06 | answers.json | 1 |
| O01-06 | answers.json | 1 |
| O02-07 | answers.json | 1 |
| O03-09 | answers.json | 1 |
| G01-05 | answers.json | 1 |
| G02-06 | answers.json | 1 |
| G03-05 | answers.json | 1 |
| O03-10 | README.md | 3,29 |
| G01-06 | README.md | 3,17,50 |
| G02-07 | README.md | 3,32,61 |
| G03-06 | README.md | 3,24,62 |
| O01-07 | reproduce.sh | 1 |
| F03-07 | src/run_mc.py | 56 |
| O01-08 | src/mc.py | 146 |
| O02-08 | hexsym/sim.py | 49 |
| O03-11 | symdec/mc.py | 121 |

The original runs and the scientific content of reference-v1 remain unchanged. This edition translates and expands the comparative presentation, checks references, and verifies PDF rendering; there are no new model trials or production phase simulations.

