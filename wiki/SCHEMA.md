# Global wiki schema

The root wiki is SciCode2's canonical project-wide knowledge layer. It compiles reusable scientific knowledge across papers and self-describes the project by linking its strategies, workflows, resources, papers, benchmarks, local benchmark wikis, talk, and skills.

## Scope

- Global pages synthesize reusable concepts, methods, models, implementations, comparisons, questions, and project architecture.
- Paper identity and raw files remain under `papers/`; the wiki cites them rather than copying them.
- A compact `papers/<paper-id>` entity page may route to canonical assets, compiled topics, companion implementations, and consuming benchmarks; it is not a paper summary.
- Benchmark-specific thesis, experiment evidence, and active decisions remain authoritative in `benchmarks/<benchmark-id>/wiki/`.
- Project pages summarize ownership and relationships, then link to the README, schema, skill, catalog, or implementation that owns the details.

## Required files and page types

The wiki contains `index.md`, `thesis.md`, `log.md`, `sources.yml`, and this schema. Compiled pages live in `concepts/`, `methods/`, `models/`, `implementations/`, `comparisons/`, `questions/`, `project/`, `papers/`, and `benchmarks/` when warranted by the material.

Use lowercase kebab-case filenames. Every compiled page has YAML frontmatter containing `title`, `page_type`, `status`, `updated`, `source_refs`, and `idea_ids`. Concept, method, comparison, model, and implementation pages also carry one to three controlled `topics` for sidebar browsing: `Correlated Systems`, `Topological Phases`, `Quantum Information`, and `Machine Learning`. Project pages instead carry one to three controlled `project_topics`: `Agentic Research Infrastructure`, `Autonomous Research Workflows`, `Research Knowledge Systems`, `Computational Benchmark Design`, and `Human-in-the-Loop Research`. Keeping the taxonomies separate prevents project architecture from polluting scientific topic retrieval. Every compiled page visibly includes `Summary`, `Sources`, and `Last updated`, and ends with `Related pages`.

## Links and provenance

Use path-qualified Obsidian links such as `[[project/research-loop|Research loop]]`. Cite sources with standard Markdown links whose relative target and fragment are stored directly in the page, for example `[Liu et al. (2025), §II.A–C](../papers/liu2025mqdm/paper.pdf#Sec.II.A-II.C)`. The label identifies the source and locator without exposing the workspace path; the target must remain portable without dashboard-specific citation parsing.

Global scientific claims must distinguish source evidence, synthesis, inference, contradiction, and uncertainty. A benchmark may consult global knowledge, but consequential global material must be incorporated into its local wiki with benchmark-local provenance before it becomes part of the benchmark's evidence chain.

Paper and companion-repository snapshots are separate provenance records even when they share a folder. Static repository inspection establishes architecture and interfaces only; it does not establish runtime correctness or reproduction of paper results.

## Ownership

- `$wiki-ingest` performs routine integration into either the global or a benchmark wiki.
- `$wiki-query` queries one scope or a combined global-plus-benchmark scope without mutation by default.
- `$wiki-lint` checks each wiki independently and validates cross-scope links where present.
- The dashboard renders the graph from wiki links, source references, paper identity, and benchmark relationships; graph edges are derived, not maintained separately.
