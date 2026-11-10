# Phase and information-structure audit

This is a post-hoc local reference/rubric audit of the seven completed scientific runs. It does not modify any source run, launch scientific simulations, establish an unknown true phase, or replace the full R1–R4 evaluation. Original prompt: `/Users/home/Downloads/20261014-102308_d89b765a/prompt.md:139` (R1 permits unresolved); `:149` (size evidence and error separation).

## What can be used as the standard answer

- For every finite L and p, R2 ≤ R1 ≤ R0; hence D0 ⊆ D1(N) ⊆ D2(N). The ordering concerns averaged Bayes risks, not each conditioned record.
- O1 channels: N2 = O0; N3 = N6 = q mod6; N4 = q mod4; N5 = N7 = N8 = integer q. N5 is exact because syndrome parity resolves its apparent q mod5 aliases. Saturation for all N≥7 is strict, with N5 already in that class.
- Full integer q refines both mod4 and mod6. These two modular records are incomparable; neither consecutive-N monotonicity nor enriched p↔1−p symmetry may be presumed.
- Boundary curves from different sufficient inequalities need not nest on their own. Their union can and should be closed under information degradation if a rigorous envelope is presented. A weak universal O1 tail says nothing about the true N dependence.
- No independent gold central O1 thermodynamic phase is established by these archives. Fable calls it nondecodable; Opus calls it decodable; GPT01/02/03 leave it unresolved. The supported reference must preserve this uncertainty.
- O2 has valid all-p sufficient theorems at N≥13 (GPT01/02), 14 (GPT03), 15 (Opus), 19 (Fable). The different N0 values measure proof strength; none establishes the minimum physical N0.

A conservative closed, certified O1 envelope from GPT02 `data/proved_bounds.csv`: N2 [0,.0795] ∪ [.9205,1]; N4 [0,.1060] ∪ [.9191,1]; N3/5/6/7/8 [0,.1090] ∪ [.9096,1]. Exact root equality is not included merely by rounding. The identical non4 sufficient curves discard enough information that mod6 and integer q receive the same proof bound, despite being distinct channels.

## Scientific diagnosis

Every one of the seven valid runs explicitly derives the complete charge equivalence classes, record hierarchy and SU2 orientation-blindness. Thus the later discussion of N5 exactness/saturation is not an omission by these agents. Stronger rank refinements differ by run but a run need only prove the ones its result uses.

The most important unresolved disagreement is scientific inference: slowing finite-size decay can fit a positive limit or a very long decay length. Fable promotes a positive-limit fit into a central nondecodable window while admitting long decay cannot be excluded. All three Opus runs promote slow decay into zero limit. Opus02/03 additionally use an unproved Gaussian/BKT exclusion criterion; Opus01 proposes typical-charge pinning/gapping of the clean loop-model phase. Their two-χ agreement also cannot establish an error bound against the exact posterior. GPT01/02 explicitly retain the corresponding unknown phases. GPT03 accepts a small-N O2 numerical phase assignment with explicit limitations; its central charge remains unknown.

Z4 high-noise behavior is most fully explained by Opus03 report:668–688 and GPT01 proofs:256–268: orientation coins form an affine incidence map; on a boundary-connected active component the mod4 charge is uniform over parity-allowed labels. Additional information remains on closed active components and zero-arrival vertices. This explains weak high-p gain without asserting exact equality of thermodynamic thresholds. It also does not license D1(4) larger than full integer q at any p.

## Recommended aspect scores

Weights below are the assigned R1 (30) + selected R2 (15) part of the local100 rubric, not official weights. Do not infer whole-task success from a subtotal; the unsupported R1 central phase calls remain explicit criterion failures.

| Run | A1 /5 | A2 /8 | A3 /8 | A4 /5 | A5 /4 | B1 /4 | B2 /4 | B3 /5 | B4 /2 | Subtotal /45 | unresolved /21 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Fable03 | 5 | 4 | 7 | 5 | 4 | 4 | 4 | 5 | 2 | 40 | 0 |
| Opus01 | 5 | 5 | 3 | 5 | 4 | 4 | 4 | 5 | 2 | 37 | 0 |
| Opus02 | 5 | 5 | 3 | 5 | 4 | 4 | 4 | 5 | 2 | 37 | 0 |
| Opus03 | 5 | 5 | 3 | 5 | 4 | 4 | 4 | 5 | 2 | 37 | 0 |
| GPT01 | 5 | 8 | 8 | 5 | 4 | 4 | 4 | 5 | 2 | 45 | 11 |
| GPT02 | 5 | 8 | 8 | 5 | 4 | 4 | 4 | 5 | 2 | 45 | 12 |
| GPT03 | 5 | 7 | 8 | 5 | 4 | 4 | 4 | 5 | 2 | 44 | 5 |

A1 coverage; A2 adequate 2D size dependence and phase judgment; A3 honest and supported uncertainty; A4 theorem/bounds/numerical distinction; A5 consistency; B1 model; B2 information order; B3 charge classes; B4 SU2. The machine-readable file contains all score rationales and evidence records.

## Detailed primary-source evidence

### Fable03

- **phase_strength — insufficient_evidence**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:213`: Positive-limit fit at L≤12 used for central phase.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:219`: Exponential decay with length ≥50 explicitly not excluded.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:311`: Final text nevertheless calls central charge region a critical phase.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:69`: CRT table and integer-charge equivalence; N5 already exact.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:82`: Full information order and mod4/mod6 incomparability.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:18`: Bayes data-processing proof.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:128`: Numerical same-N and equivalence checks.
- **z4_feature — explicit_partial_mechanism**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:190`: Both Z4 finite-size endpoints assessed.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:201`: Z4 adds little at high p but more at low p; no exact active-component explanation here.
- **enriched_complement_symmetry — correct_scope_implicit**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:33`: Complement theorem proved only for O0.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:187`: O2 N2 asymmetry explicitly discussed.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/report.md:36`: N19 theorem distinguished from N3 numerical claim.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-fable-5-1/run_03/docs/theory.md:94`: SU2 orientation-blind proposition.

### Opus01

- **phase_strength — insufficient_evidence**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:326`: All-p charge assignment from no plateau and drift.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:329`: Positive narrow phase not excluded.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:337`: Typical charges pin/gap clean critical phase proposed as physical picture, not established theorem.
- **approximation — unsupported_error_bound**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:82`: χ64/χ128 posterior comparison is empirical convergence evidence.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:164`: Observed difference promoted to error bound on R*.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:119`: CRT and saturation classes.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:127`: Both modular channels degraded from integer charge.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:109`: Jensen data-processing proof.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:114`: Center maps O2 to O1.
- **z4_feature — explicit_partial_mechanism**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:268`: High-p crossing shifted/constrained to respect O0 nesting.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:275`: Charge4 defects proposed to explain central disorder.
- **enriched_complement_symmetry — correct_scope_implicit**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:131`: Complement proof restricted to O0; enriched endpoints independently fitted.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:503`: R3 upper bound on smallest N0, not proof numerical N3.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_01/report.md:140`: Complete spin table and noisy-degree interpretation.

### Opus02

- **phase_strength — insufficient_evidence**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:184`: Monotone size drift/log odds used as assignment rule.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:247`: Gaussian/BKT risk≥.45 heuristic promoted to exclusion criterion.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:310`: R96≈.2 yet all-p classification, positive limit acknowledged possible.
- **approximation — unsupported_error_bound**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:301`: Induced bias claimed at most χ comparison deviation.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:319`: Acknowledges empirical control rather than prior bounds.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:54`: CRT all classes and integer/modular risk inclusions.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:45`: Jensen proof.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:86`: Cross-rank LP comparisons and exceptions disclosed; analytical N≥7 order.
- **z4_feature — explicit_partial_mechanism**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:212`: Low/high asymmetric usefulness and high-p numerical nesting check.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:214`: Paired same-sample risk nesting checked, tiny high-p gain.
- **enriched_complement_symmetry — correct_scope_implicit**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:61`: Complement theorem O0 only.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:142`: No proof below N15; allp low-rank remains numerical.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_02/REPORT.md:26`: SU2 orientation-blind degree record included in exact structure.

### Opus03

- **phase_strength — insufficient_evidence**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:239`: All-p charge classification.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:297`: Gaussian stiffness/risk lower bound remains heuristic.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:373`: Late rough/glassy crossover explicitly not excluded.
- **approximation — unsupported_error_bound**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:355`: χ64/χ128 max change said to ensure no R1 answer can change.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:391`: Subset empirical tests, not formal every-sample bound.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:489`: CRT and classes.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:498`: Integer-charge degradation orders.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:17`: Same-N nesting.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:540`: Analytical cross-N≥7 map; no every-consecutive N assertion.
- **z4_feature — explicit_correct_mechanism**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:229`: High-p nesting checked.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:668`: Exact affine incidence calculation on boundary-connected active components.; `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:681`: Z4 retains extra information only at zero-arrival vertices and closed active components.
- **enriched_complement_symmetry — correct_scope_implicit**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:480`: Complement proof O0 only; independently inferred enriched endpoints.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:654`: N15 sufficient proof and low-rank numerical statement separated.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/anthropic__claude-opus-5-5/run_03/report.md:514`: Spin laws and orientation elimination.

### GPT01

- **phase_strength — explicit_supported_conservative**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:55`: Slow central charge decay not promoted to limit.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:86`: O2 all-p conjecture but corresponding entries unresolved.
- **approximation — explicit_supported**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:123`: Complete contraction, rounding perturbation refits, no truncation.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:46`: CRT and full charge classes.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:51`: Integer charge dominates both modular records, no general N order.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:53`: Numerical low-noise Z4 region transferred to integer charge and appropriate O2 rows.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:225`: Constructive SU(N≥5)→SU3 stochastic comparison.
- **z4_feature — explicit_correct_mechanism**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:33`: Apparent upper boundary reversal lies within allowances; ordering prevails.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:256`: Exact closed-active-component orientation sum, used as independent posterior check.
- **enriched_complement_symmetry — explicit_correct_scope**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:53`: No enriched complement symmetry presumed.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:53`: Sufficient roots are not estimated thresholds.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/report.md:5`: N13 theorem vs unresolved small-rank phase.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_01/proofs.md:64`: SU2 orientation integration, not equivalent to syndrome only.

### GPT02

- **phase_strength — explicit_supported_conservative**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51`: Z4 unstable bootstrap/extrapolation unresolved; slowly varying other charges unresolved.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:70`: O2 continuum/rare tails not resolved by sampled decay.
- **approximation — explicit_supported**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:99`: No truncation, rounding perturbation refits and separate uncertainty.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:25`: Full charge classes and N5 parity resolution.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:75`: Center-derived same-N order.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:89`: Exact cross-N statistical channels including N5 parity and N6 exception.
- **z4_feature — explicit_correct_limits**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:51`: Z4 high-p estimate must obey nesting; diagnostics lead unresolved, not anomaly claim.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:173`: Z4 all triple arrival counts have M1; worst-case proof special constant.
- **enriched_complement_symmetry — explicit_counterexample**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:43`: Exact rational L2 richer-record counterexamples.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/proofs.md:219`: μρ<1 only sufficient; equality not phase boundary.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:83`: N13 refined proof.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_02/report.md:78`: All low-rank isomorphisms; SU2 occupancy-only.

### GPT03

- **phase_strength — numerical_inference_with_reservation**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:3`: O2 N3/4 all-p numerical inference vs N14 theorem.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:15`: Narrow unsampled phases cannot be excluded.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:92`: Central charge remains unresolved despite drift.
- **approximation — explicit_supported**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:185`: No truncation, round/log checks.
- **charge_equivalence — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:57`: Complete CRT table, exact equality including spatial law.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:72`: Integer refines mod4/mod6; latter incomparable.
- **information_nesting — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:36`: Center map and average Bayes risk ordering, not each conditional record.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:121`: Cross-N≥5 SU3 refinement with N6 exception.
- **z4_feature — explicit_correct_limits**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:40`: Upper Z4 mean projected to O0 while retaining original uncertainty; no equality theorem.
- **enriched_complement_symmetry — explicit_correct_scope**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/proofs.md:91`: O0 complement not applied to richer records.
- **largeN_vs_phase — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:3`: N14 theorem separate from all-p numerical assignments.; `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:29`: Charge tails sufficient, not guessed thresholds.
- **SU2 — explicit_correct**: `/Users/home/Downloads/20261014-102308_d89b765a/openai__gpt-6-astra/run_03/report.md:155`: SU2 binary exact contraction.

