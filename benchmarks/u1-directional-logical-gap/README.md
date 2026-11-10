# What Drives the Gain from Directional Noise?

Quantify typical-gap and ambiguous-record contributions to directional logical recovery, with controlled inference and a reserved mechanism prediction.

Current formulation: **v0.2**, revised 2026-10-16. Text-only editorial recommendation: **pass-to-testing**, with feasibility and empirical difficulty unassessed.

- [Current question](problem/TASK.md)
- [Current problem sheet](problem/problem.pdf) ([matching output copy](output/pdf/problem.pdf))
- [Implemented revision and scientific changes](problem/REVISION-v0.2.md)
- [Text-only assessment](problem/EDITORIAL_AUDIT.md)
- [Previous question and PDF](problem/history/review-draft-v0.1/)
- [Metadata](metadata.yml) and [author-side source provenance](problem/SOURCE_REVIEW.md)

Only the current question, PDF and expressly declared model inputs belong in a future solver session. The revision and audit records are author-side material. Exploratory testing is the next workflow stage; formal calibration follows once the question stabilizes.

The PDF is generated directly from `problem/TASK.md`. Rebuild it with `python scripts/build_problem_sheets.py u1-directional-logical-gap` using an environment with pypdf and local pdfLaTeX. The builder writes [editable LaTeX](problem/main.tex), the canonical PDF and its matching output copy; it also embeds the supplied D4 JSON when applicable.
