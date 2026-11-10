# Seven valid AI submissions: an aspect-by-aspect comparative research report

Date: 2026-10-16. Follows the established rubric v1, preserving the original weights and scores.

## Reading entry points

- [Complete PDF](output/pdf/comparative-scoring-report-en.pdf): 58 pages, with navigable contents and evidence index.
- [Complete editable text](comparative-scoring-report.md).
- [Itemized comparison CSV](comparison-long.csv): 44 questions × 7 valid runs, totaling 308 records.
- [Complete evidence and scoring-snapshot JSON](comparative-report.json).

## Page navigation

| Pages | Contents |
| --- | --- |
| 1 | Summary, subjects, and main findings |
| 2-3 | Navigable contents |
| 4 | Inclusion and exclusion of nine attempts; scoring conventions |
| 5-27 | 23 scored aspects of the original task, each on a separate page with a seven-run table |
| 28-48 | 21 discussion details, each question on a separate page with a seven-run table |
| 49-54 | Eight summary tables covering totals, the full criterion matrix, error categories, proof approaches, algorithms and checks, per-run characteristics, and related comparisons |
| 55 | Research conclusions and fairness limits |
| 56-58 | Evidence-file index |

The report contains 54 tables: 44 per-question comparisons, 8 cross-run summaries, 1 inclusion/void-attempt table, and 1 evidence index. Fable01/02 are void because of API failures; they receive no scientific zeroes and do not enter the ranking.

## Version and validation

The original rubric score source is the parent directory's reference-v1/scores-v1.json, SHA-256: 3864e0c08bbd58126fa64ae44530d2fc3a92a7f11e734531512e488a2b7a0d8a.

build_comparative_report.py verifies that every table contains all seven runs, scores and statuses match the frozen version, and evidence files and line numbers are valid, then generates PDF source, text, JSON, and CSV. inputs preserves the row-by-row narratives from three domain audits. The text distinguishes possible errors, actual findings, insufficient evidence, implementation defects, and valid alternative approaches.

Original results and the previous reference documents are read-only; no new model trials or production phase-diagram simulations were performed. The PDF passed a complete page-by-page overview and enlarged checks of representative pages. See data-qa.json for data validation, pdf-qa.json for visual validation, and manifest.json for final-file and source hashes.
