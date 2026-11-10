# v0.7 Decoder: scientific review of 9 existing runs

Review date: 2026-10-16. The input is the user-supplied
`/Users/home/Downloads/20261014-102308_d89b765a/`.
This round only reviewed existing results, ran small-scale checks and preserved evidence; it did not revise the problem, launch new model trials or repeat the phase-diagram research.

## Conclusion

**The algorithms and theory are strong overall; the main disagreement is whether the finite-size data justify definite phase-diagram assignments.**

Of 9 runs, 7 produced scientific deliverables and 2 Fable runs failed because of API output limits. All 7 valid submissions passed
210 independent routine posterior and correction tests per submission; the key inequalities in their large-N proofs were also supported. The first two GPT submissions explicitly retain unresolved phase regions, as the original task permits.

This local review provisionally passes all three GPT runs, with a reservation about the third run's numerical extrapolation to all-p decodability at small N. The valid Fable run and all three Opus runs are classified as partial completion with substantive gaps.
The main problem in the latter four is a mismatch between the strength of phase-diagram evidence and the conclusions drawn, together with a numerical-robustness gap at extremely low p.
**This is neither a verdict on the charge model's true phase diagram nor formal SciCode difficulty calibration.**

## Evaluation scale used

The review uses R1–R4 of the actual `prompt.md` supplied to the agents and the project's itemwise
**pass / fail / unknown** classifications. Completion is separately described as “provisional pass,” “partial completion,” or “not assessable.”
No numerical weights or official percentage scale frozen before the runs were found, so no aggregate score was invented.

- **R1:** Phase diagrams, size evidence, and the distinction between statistical, finite-size and approximation errors. The original task explicitly permits
  `unresolved` with justified bounds; a conservative answer cannot be classified as failure merely for being conservative.
- **R2:** Correctness of the exact structures used, including information order, equivalence classes and posterior construction.
- **R3:** A valid sufficient N0 with proof. The task does not demand the minimum N0; 13, 14, 15, 19 are not mutually contradictory.
- **R4:** The prescribed interfaces and posteriors for positive-probability records at L≤4, N≤8, with error≤1e-9; independent checks of the correction's syndrome and logical class.

This is a post-hoc scientific review, and the reference checks were also constructed during this round; it must not be presented as a formally frozen pre-run evaluator.
Source requirements: [requirements.md](../../../../../docs/scicode2/requirements.md),
[calibrate-benchmark](../../../../../skills/calibrate-benchmark/SKILL.md).

## Run-by-run assessment

| Run | R1 phase diagram | R2 exact structure | R3 sufficient N0 | R4 routine / endpoint stress | Overall judgment |
| --- | --- | --- | --- | --- | --- |
| Fable 01 | unknown | unknown | unknown | No deliverable | Not scientifically assessable: API output limit |
| Fable 02 | unknown | unknown | unknown | No deliverable | Not scientifically assessable: API output limit |
| Fable 03 | fail: insufficient support for central charge-phase extrapolation | pass | pass: 19 | 210/210; 0/18 | Partial completion |
| Opus 01 | fail: insufficient support for all-p charge assignment and approximation-error guarantees | pass | pass: 15 | 210/210; 0/18 | Partial completion |
| Opus 02 | fail: as above, including an unestablished Gaussian/BKT exclusion argument | pass | pass: 15 | 210/210; 0/18 | Partial completion |
| Opus 03 | fail: as above | pass | pass: 15 | 210/210; 0/18 | Partial completion |
| GPT 01 | pass: justified unresolved entries are separated from numerical phase assignments | pass | pass: 13 | 210/210; 18/18 | Provisional pass |
| GPT 02 | pass: 12/21 entries unresolved, as the original task permits | pass | pass: 13 | 210/210; 18/18 | Provisional pass |
| GPT 03 | pass, with a finite-size extrapolation reservation | pass | pass: 14 | 210/210; 18/18 | Provisional pass with reservation |

R2 pass in the table means that the review supports the shared exact structures and posterior methods. It does not endorse extra phase guarantees inferred from empirical calibration or Gaussian heuristics.
R1 fail means that the support for conclusions required by the problem is inadequate, **not that the proposed physical phase assignments have been proved wrong**.
Machine-readable run-by-run judgments are in [scores.json](scores.json).

## What the independent checks did

### 1. Routine posterior and correction checks

The review independently implemented irrep probabilities, geometry, physical-record generation and generic tensor contraction.
It uses a generic-einsum elimination order rather than calling the submissions' row/column transfer matrices.
The reference program was additionally checked against direct microscopic enumeration on 21 L=2 cases; the maximum difference was 8.67e-19.

Using a fixed new seed 202610160314, the checks cover L=2,3,4, N=2,…,8 and different p values:
each submission is checked on 210 routine records, of which 140 are the O1/O2 cases specified by R4 and 70 are O0 controls.
All 7 pass. All 210 returned corrections per submission are also legal edge sets, satisfy the syndrome and belong to the higher-posterior logical sector.
The largest posterior discrepancy across submissions is **1.033e-14**, far below the required 1e-9.

Evidence: [oracle-check.json](results/oracle-check.json),
[heldout-cases.json](results/heldout-cases.json), and each run's `*-checks.json` in results/.
These finite tests support algorithmic correctness; they do not prove that every input in an unlimited parameter domain is bug-free.

### 2. Numerical limits at extremely low p

At N=8, each detector is assigned its largest absolute charge or the corresponding purely symmetric irrep.
These records force every edge to be active, so the exact posterior is known: P(logical=0)=1 for even L and 0 for odd L.
The records have strictly positive probability for every p>0, regardless of how difficult they are to sample by Monte Carlo.

There are 18 stress inputs at L=2,3,4 and three probabilities: p=1e-180, 1e-310, and the smallest positive binary64 value:

- All three GPT runs pass, using Decimal or log-domain protection.
- Fable and Opus all produce NaN or an incorrect “record probability is zero” error in this review environment.
- This is a numerical implementation gap, usually repairable; it alone does not establish a need for expert scientific judgment.

**Environment qualification:** the checks use macOS NumPy 1.26.4, where `longdouble` has only binary64 range;
the original runs use Linux NumPy 2.1.3. Some extreme-p failures in Opus 02, which uses `longdouble`, are platform-dependent and cannot be attributed unchanged to its original Linux behavior.
However, its `p/2` is computed in Python float before conversion to longdouble; the rounding of half the smallest positive float to zero is platform-independent.
The float64 local products in Fable and Opus 01/03 also have direct underflow risks.

The stress tests are additional post-hoc diagnostics, not hidden official conditions of the original runs. This report gives both the routine passes and the gap in the promise to cover the full positive-probability domain.

### 3. Large-N proofs

The review examined the proof chain “coarsen the visible record → witness an error path → control hidden orientations/edge correlations → bound path growth.”
The honeycomb self-avoiding-walk constant used in the proofs has a published theorem behind it:
[Duminil-Copin–Smirnov](https://arxiv.org/abs/1007.0575).

Independent rational interval covers or recomputation of the submitted rational certificates give:

| Proof | Recomputed upper bound on the uniform growth factor |
| --- | --- |
| Fable, N0=19 | Squared factor ≤0.997854 |
| Opus 01/02, N0=15 | Squared factor ≤0.998799 |
| Opus 03, N0=15 | Squared factor ≤0.996797 |
| GPT 01, N0=13 | Three p intervals respectively <0.999129, 0.998743, 0.967815 |
| GPT 02, N0=13 | <0.999887977; cycle factor and three-hexagon enumeration checks pass |
| GPT 03, N0=14 | <0.999949750 |

All these bounds are strictly less than 1. The GPT 02 certificate also recomputes 100 triangular-lattice return-walk counts and 31,104 hexagon states at each probability.
Fable's λ=1.876764 exceeds the proved honeycomb connective constant and is therefore usable for asymptotic path counting; its memory-22 matrix with approximately 5 million states was not reconstructed in this round.
This is mathematical review and arithmetic validation, not complete formal verification in a proof assistant.

Evidence: [proof-certificate-checks.json](results/proof-certificate-checks.json).

### 4. Consistency of raw results and summaries

Existing data were reaggregated, without resampling physical errors or rerunning the phase diagram:

- GPT 01: 677 main-study NPZ files and 1,319,100 trials; means, failure counts and posterior losses agree.
- GPT 02: 305,024 decoder-evaluation rows; the original archive SHA-256 hashes of four scientific CSV files all match, and rowwise posterior losses agree.
- GPT 03: 423 NPZ files and 340,600 archived trial slots; raw arrays agree with summaries.
  These include 200 conservatively failed reserved slots in an externally terminated batch; this does not establish that 200 physical trials actually completed.

These audits found no inconsistencies. They did not recheck every fit in every submission or establish an external gold answer for every phase region.
Evidence: [saved-data-audit.json](results/saved-data-audit.json).

## The most important scientific issue: R1

### Fable 03: slow decline or an apparent plateau does not imply a positive infinite-size limit

`report.md:19` calls the central charge region a critical non-decodable window;
near `report.md:213`, size fits with a constant term support R∞≈0.2–0.3, with the relevant larger-size data mainly ending at L≤12.
The report also acknowledges that decline at a longer correlation length cannot be excluded. This is insufficient to identify the endpoints as physical phase boundaries; the original task offers unresolved as a valid option.
Its completeness and effort deserve recognition, but an endpoint error of ±0.1 does not automatically cover model uncertainty about whether that window exists at all.

### Opus 01/02/03: slow decline does not imply a zero limit either

These runs extend to L≈48–96 and add valuable diagnostics such as flux variance and log-odds.
However, risk in the central region remains approximately 0.2 at the largest sizes. They exclude a non-decodable phase using “a rough Gaussian/BKT phase should have R*≳0.45–0.47,”
without establishing that this particular quenched posterior model, its boundary conditions and stiffness assumptions imply such a necessary lower bound.
This can exclude one specified heuristic model, but not every positive limit or slow crossover.

More specifically, Opus 02's final `REPORT.md:301` claims that the induced bias is at most the observed difference between χ and a larger χ;
Opus 01 `report.md:164` and Opus 03 `report.md:355` make similar inferences.
Two approximate computations being close establishes only that they are close to each other. If the larger χ shares their bias, the true error remains unknown.
Likewise, agreement between mean hard failure and mean posterior loss is a useful consistency check, but is insufficient to establish posterior exactness.
Thus it does not justify claiming that approximation cannot change any R1 assignment.

These are the expert scientific-review points most worth recording in this batch: **using a heuristic phase description as an exclusion criterion, and treating convergence diagnostics as error bounds.**
They have not yet been tested in actual reruns after expert correction; these post-hoc comments cannot be presented as human interventions that already occurred.

### GPT 01/02: retaining unresolved is consistent with the task

These runs provide exact small-system posteriors, provable sufficient intervals, size evidence and independent large-N theorems,
without forcing every central region into a numerical boundary. GPT 02 leaves 12/21 entries unresolved, which does not automatically cause failure:
the original task explicitly allows this form. They complete the “justified limited conclusions” permitted by the task, rather than fully solving every model's true phase diagram.

GPT 03 labels all-p O2 decodability at N=3,4 as a numerical phase assignment. Its data cover multiple probabilities and increasing two-dimensional sizes, and its posterior has no MPS truncation.
Such a numerical assignment should not incorrectly be required to meet theorem standards, so this round accepts it with a reservation. Its finite grid still cannot prove the entire continuum, especially not on the same footing as the strict theorem for N≥14.

## Implications for benchmark difficulty

- It is incorrect to say “all 9 succeeded”: 2 have no deliverable, and the original reward measures only file production.
- It is also incorrect to say “AI cannot solve this”: the theory and routine exact posterior were completed independently multiple times, and at least two GPT runs satisfy the task's permitted conservative phase-diagram answer format.
- Scientific phase-diagram judgment did produce different conclusions and identifiable reasoning gaps; there is not yet an independently reliable gold answer for the central charge region to adjudicate its true physical phase.
- This batch tested only one problem snapshot and has no guided-B comparison. The configuration specifies `reasoning_effort: max`, but the evidence is insufficient to relabel it as complete formal A/B calibration.
  Under the project standard, **formal difficulty assessment remains incomplete**; this batch cannot establish the requirement that both A and B fail.

## Evidence preservation and review commands

[provenance.json](provenance.json) preserves SHA-256 hashes of the inputs, outputs and original transcripts, together with the validation environment.
[transcript-index.json](results/transcript-index.json) preserves each run's terminal step and additional user-source events.
The final entries of Fable 01/02 explicitly show the `128000 output token maximum` API error.
Other additional user-source content includes automatic recovery prompts, tool-returned images/visualization skills and deliverable-directory information; no scientific correction prompts were found.
This is not an isolation guarantee for every hidden startup context.

```sh
# Use Python with numpy/scipy/numba; set the thread count to 1.
python scripts/make_cases.py
PYTHONDONTWRITEBYTECODE=1 NUMBA_CACHE_DIR=/private/tmp/scicode-review-d89b765a-numba \
  python scripts/check_run.py /absolute/path/to/supplied/model/run_XX
python scripts/check_certificates.py
python scripts/audit_saved_data.py
python scripts/make_review_records.py
```

Run these scripts from this review directory or supply their full paths. They do not invoke the original production phase-diagram launcher.
The original download directory and existing benchmark problem were not rewritten.
