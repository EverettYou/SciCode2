# Decoder v0.7: standard answer and detailed scoring v1

2026-10-16. Corresponds to the original prompt hash d89b765a; post hoc local scoring, not official weights or formal A/B difficulty calibration.

## Review entry points

- [Standard answer PDF](output/pdf/standard-answer-en.pdf): 7 pages, covering the model, information relations, rigorous-bound phase diagram for 21 entries, exact posterior, and N0=13 proof.
- [Rubric and per-run scoring PDF](output/pdf/rubric-and-scorecards-en.pdf): 7 pages, with 23 criteria/100 points, 21 discussion diagnostics, per-run deductions, and evidence.
- [Complete itemized reasons and source links](scorecards.md): 161 scientific-deliverable scores and discussion-detail locations; the two API failures are separately listed as unknown.
- [Wide-table CSV](scores-v1.csv), [Itemized-detail CSV](score-details-v1.csv), [Complete JSON](scores-v1.json).
- [Reference answers.json](reference-answers.json), [Safe endpoints for 21 entries](reference-bounds.csv), [Rational endpoint certificates](reference-bound-certificates.json).
- [Editable standard-answer source](standard-answer.md), [Editable rubric source](rubric.md), [PDF source files](output/pdf/), and [audits](audits/).

## Reading conventions

The total score measures completion and does not replace key scientific pass conditions. GPT01/02 can receive 100 points because the original task permits unresolved; this does not mean the full true phase diagram is solved. Fable/Opus completed substantial correct work, but have key gaps in central phase regions and approximation guarantees. Valid alternative proofs do not lose points for avoiding an arrow matrix; later teaching figures do not retroactively penalize the original submissions.

The old REPORT.md and scores.json in the parent directory are preserved. This version corrects the attribution of Opus01's explanation; see the scorecards. All external original runs are read-only. No new model runs or production phase-diagram experiments were performed.

## Generation and validation

Run build_reference_records.py first, then draw_reference_phase.py and build_pdf_sources.py. Finally, compile the two TeX files in output/pdf using the existing XeLaTeX/latexmk. Plotting uses the system Python's matplotlib; see the source for font and dependency constraints. See manifest.json for generated-file SHA-256 hashes and 423 source-location checks, and pdf-qa.json for PDF visual checks.

Existing independent scientific checks are preserved in the parent directory's results; this version does not repeat production numerical experiments. The tmp/pdfs directory contains only page-by-page visual-review materials.
