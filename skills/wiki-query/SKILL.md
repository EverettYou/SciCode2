---
name: wiki-query
description: Answer project or benchmark research questions from SciCode2's maintained global and local wikis with traceable citations. Use when locating project knowledge, synthesizing across papers, comparing hypotheses or methods, finding contradictions, generating research directions, selecting a high-information experiment, or gathering context for a benchmark lab.
---

# Wiki Query

Use compiled knowledge before reaching back into raw sources. This operation is read-only by default.

## Select the scope

- `global`: read the project-root `wiki/` for project architecture and cross-paper knowledge.
- `benchmark:<benchmark-id>`: read only that benchmark's local wiki; treat it as authoritative for its thesis and experiment state.
- `global+benchmark:<benchmark-id>`: read the benchmark wiki first, then use the global wiki for transferable context. Keep local evidence and global synthesis visibly distinct.

## Workflow

1. Resolve the scope. Read each selected `wiki/SCHEMA.md`, then its `wiki/index.md` and `wiki/thesis.md`; in a combined query, read the benchmark scope first.
2. Turn the request into a small set of search concepts, code symbols/aliases, relevant page types, and evidence needs.
3. Use the local `/api/wiki/search` token+graph retrieval endpoint when the dashboard is running, or search Markdown with `rg` as the filesystem fallback. Retrieval first scores title, summary, topics, and path tokens, then propagates relevance one hop over the weighted graph; treat the result as candidate ranking, not evidence. Read the highest-ranked concept, method, implementation, comparison, project, and question pages and follow their links. Consult each `wiki/sources.yml` for ingest coverage and revisions.
4. Synthesize across pages instead of concatenating excerpts. Separate established evidence, current wiki synthesis, unresolved contradiction, and your new inference.
5. Cite scope-qualified wiki page paths near claims and include primary paper/code/lab citations when the answer drives a scientific decision. When proposing text for a wiki page, use only portable standard Markdown citations: `[readable label](relative-path#locator)`, never a source ID or dashboard-resolved citation. Distinguish global synthesis, benchmark synthesis, static code inspection, repository-test evidence, and benchmark-lab evidence.
6. For idea generation, propose multiple candidates before selecting one. Score them qualitatively by scientific value, information gain, tractability, discriminating power, and dependency risk.
7. For a next lab, return motivation, hypothesis/alternatives, required wiki context, minimal discriminating design, observables, failure interpretation, and likely idea-graph update. Do not fabricate findings or create the lab unless requested.

Read [references/query-output.md](references/query-output.md) when the answer will seed an idea or lab.

## Write boundary

Do not edit the wiki or labs during an ordinary query. If a synthesis is genuinely reusable, offer to preserve it in the scope that owns it; after approval, prepare it as a candidate source and invoke `$wiki-ingest`. If the user asks to create the idea or lab, update the appropriate artifacts as a separately authorized action. Log a query only when it is saved or repository policy explicitly requires it.

## Answer quality

Say when the wiki lacks coverage. Prefer a source-acquisition or lab proposal over speculation. A good query answer should make the next decision cheaper, not just restate the current thesis.
