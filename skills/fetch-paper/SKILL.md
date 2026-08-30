---
name: fetch-paper
description: Find and archive paper metadata, PDFs, and source files for SciCode2 research.
---

# Fetch Paper

Use this skill when a paper must be found, downloaded, archived, or made available for later assessment. Keep each paper in `papers/<paper-id>/` and preserve provenance.

## Workflow

1. Search arXiv with `scripts/fetch_arxiv.py search <query>` when the identifier is unknown.
2. Confirm the title, authors, and arXiv identifier before downloading.
3. Run `scripts/fetch_arxiv.py download <arxiv-id> --paper-id <paper-id> --output-root papers`.
4. Inspect the downloaded metadata and source archive. Use the PDF as a fallback when no source is available.
5. Never overwrite an existing version silently; record the arXiv version and download timestamp.

The downloader validates both IDs before it creates any directory. It stages each fetch in the project-level `.tmp/` directory and moves it into `papers/<paper-id>/` only after all required files and checksums are present. The per-fetch staging directory is removed on success or failure; the project-level `.tmp/` directory is retained as the shared temporary workspace.

A complete target is left unchanged. An incomplete target is reported as an error for manual resolution rather than overwritten.

## Stored artifacts

```text
papers/<paper-id>/
├── provenance.json
├── paper.pdf
├── source.tar
└── source/                 # extracted only when requested
```

The script uses arXiv's public export and download endpoints. It does not infer missing metadata or alter the paper's content. For non-arXiv papers, preserve the publisher URL and add the files manually under the same paper directory.

## Reproducibility

Record the source URL, arXiv version, retrieval timestamp, and local SHA-256 checksums in `provenance.json`. Copy downloaded source archives into a benchmark's `problem/papers/` only when licensing and research needs have been reviewed.
