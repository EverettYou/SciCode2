# Wiki schema

The wiki is LLM-maintained local research knowledge. Canonical paper folders live outside the benchmark under `../../papers/` and are ingested once into the global wiki. Local pages cite those global entries plus completed `../labs/*/REPORT.md` and selected lab artifacts; do not create a local raw-source directory.

## Required pages

- `index.md`: top-level local research map that indexes the synthesis and ideas families.
- `thesis.md`: current synthesis, strongest support, contradictions, alternatives, and open questions.
- `ideas/`: hypothesis, frontier, branching, pruning, and distillation pages. These replace `ideas.yml`; preserve IDs and history in the page content.
- `log.md`: append-only operational history.
- `sources.yml`: provenance ledger for ingested raw materials. It stores paths, revisions, ingest times, and affected wiki pages; it never copies or summarizes source content.
- `concepts/`, `methods/`, `implementations/`, `comparisons/`, and `questions/`: compiled pages created when warranted by the material, not one page per heading, source file, or code module by default.

## Page conventions

Use lowercase kebab-case filenames and YAML frontmatter with `title`, `page_type`, `status`, `updated`, `source_refs`, and `idea_ids`. Below the title, every compiled page visibly includes `**Summary**`, `**Sources**`, and `**Last updated**`, and ends with `## Related pages`.

Use path-qualified Obsidian links such as `[[concepts/locality|Locality]]` and global links such as `[[wiki/papers/paper-id|Paper entry]]`; relative Markdown links remain valid for portability. Cite source-backed claims with standard Markdown links whose relative target is stored directly in the page. Mark unsupported statements `(needs verification)`. State inference, uncertainty, contradictions, and superseded claims explicitly.

Global paper ingest compiles concepts, claims, evidence, assumptions, limitations, and any companion repository's architecture, interfaces, algorithms, dependencies, conventions, tests, and failure modes. Local synthesis may interpret that material for this benchmark, but it must link back to the global page and never copy source code or treat unexecuted code behavior as experimental evidence.

Every local citation or lab ingest creates or updates exactly one entry in `sources.yml`. Use global-wiki paths under `wiki/` for papers and benchmark-relative paths under `labs/` for evidence. Record a stable revision and list every local wiki page changed by the operation.

## Ownership

- `$wiki-ingest` previews takeaways and planned changes, then integrates raw sources and updates affected pages, index, thesis, and log. It pauses for materially ambiguous categorization or interpretation.
- `$wiki-query` reads the wiki and returns cited synthesis; it does not mutate by default.
- `$wiki-lint` audits structure, provenance, links, coverage, contradictions, and staleness.
