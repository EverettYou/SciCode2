# How Much Symmetry Knowledge Does Decoding Need?

Resolve intrinsic and practical logical value of charge versus irrep information for hidden-orientation SU(N) pair errors, focusing on N=3,4 with N=2 as a control.

Current formulation: **v0.8**, revised 2026-10-16. Text-only editorial recommendation: **pass-to-testing**, with feasibility and empirical difficulty unassessed.

- [Current question](problem/TASK.md)
- [Current problem sheet](problem/problem.pdf) ([matching output copy](output/pdf/problem.pdf))
- [Implemented revision and scientific changes](problem/REVISION-v0.8.md)
- [Text-only assessment](problem/EDITORIAL_AUDIT.md)
- [Previous question and PDF](problem/history/review-draft-v0.7/)
- [Metadata](metadata.yml) and [author-side source provenance](problem/SOURCE_REVIEW.md)

Only the current question, PDF and expressly declared model inputs belong in a future solver session. The revision and audit records are author-side material. Exploratory testing is the next workflow stage; formal calibration follows once the question stabilizes.

The PDF is generated directly from `problem/TASK.md`. Rebuild it with `python scripts/build_problem_sheets.py fusion-informed-decoding` using an environment with pypdf and local pdfLaTeX. The builder writes [editable LaTeX](problem/main.tex), the canonical PDF and its matching output copy; it also embeds the supplied D4 JSON when applicable.
