# SciCode2 Papers

This folder contains the publication catalog and locally processed source material used to identify promising SciCode2 benchmarks.

## Index and per-paper records

- `papers.yml` is the canonical index of all publications. Every paper shown on the dashboard starts here.
- `<paper-id>/assessment.yml` contains SciCode-specific analysis, ratings, follow-up ideas, and its processing stage.
- `<paper-id>/provenance.json` records download provenance, source URLs, retrieval time, and checksums.
- `<paper-id>/paper.pdf` and `<paper-id>/source.tar` are the archived paper and arXiv source when available.

Only papers that have been fetched or assessed need an individual subfolder. A publication present only in `papers.yml` is labeled `listed` by the dashboard.

## Recommended paper folder

```text
papers/
├── papers.yml
└── <paper-id>/
    ├── assessment.yml
    ├── provenance.json
    ├── paper.pdf
    ├── source.tar
    └── source/             # optional extracted LaTeX source
```

Use the stable publication ID from `papers.yml` as the folder name. Preserve external identifiers such as an arXiv ID inside `provenance.json`; do not use them as duplicate folder names.

## Processing lifecycle

`listed → fetched → assessed → reviewed`

- `listed`: listed in `papers.yml` without local paper files.
- `fetched`: local PDF/source files exist without an `assessment.yml` file.
- `assessed`: `assessment.yml` contains a provisional assessment.
- `reviewed`: its assessment has been manually corrected and `stage` is set to `reviewed`; the paper is ready to inform benchmark design. Paper–benchmark citations are tracked separately as graph links.
