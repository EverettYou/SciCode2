# Ingest protocol

## Provenance

Use paths relative to the selected wiki scope for internal sources. Every claim citation must use standard Markdown: `[readable label](relative-path#locator)` for internal material and `[readable label](https://canonical-source-url#locator)` for external material. The target is stored directly in the page and must resolve without a dashboard-specific resolver; never make a local mirror merely to cite an external page. Benchmark examples are global paper pages such as `wiki/papers/<id>.md` and local evidence such as `labs/lab-003-foo/REPORT.md`; global raw-source examples are `papers/<id>/paper.pdf`, `papers/<id>/repo/src/module.py`, `benchmarks/<id>/labs/<lab>/REPORT.md`, and `skills/<skill>/SKILL.md`. Add a page, section, figure, table, commit, result key, symbol, test, heading, or line locator whenever possible. Do not cite another wiki page as though it were the primary source. Mark unsupported claims `(needs verification)`.

## Integration units

Create pages around durable concepts, methods, entities, comparisons, and questions. Record source-level provenance only in `wiki/sources.yml`; do not create source-summary pages or mirror a paper's section structure. A paper entity page may exist as a routing node for its canonical assets, compiled topics, implementations, and benchmark uses, but it must remain compact and avoid duplicating topic synthesis. The registry entry lists the compiled pages changed by the ingest without duplicating their content.

If a paper folder includes a repository, treat the folder as a bundle and the paper and code snapshot as separate sources with separate revisions and `updated_pages`. Static code inspection supports statements about architecture and interfaces, not runtime correctness or reproduction of paper results. Create a paper-to-code comparison when the implemented objective, level of description, or algorithm differs materially from the paper method a reader might otherwise assume it realizes.

Reusable scientific pages belong globally. When promoting knowledge from a benchmark wiki, move the general synthesis and leave benchmark-specific hypotheses, decisions, implementation constraints, and lab evidence local. Replace duplicate local pages with cross-scope links and append migration records; do not maintain parallel full copies.

## Claims

For consequential claims, preserve:

- the claim and calibrated confidence;
- supporting and challenging raw sources;
- scope and assumptions;
- whether it is source-reported, lab-observed, or wiki synthesis;
- related concepts, methods, comparisons, questions, and ideas.

## Contradictions

Never overwrite an older claim just because a new source disagrees. Record both scoped claims, identify possible reasons for disagreement, update the thesis only to the degree justified, and create an open question when the conflict is unresolved.

## Idempotence

Before ingest, inspect the matching `sources.yml` entry and log. Re-ingesting the same revision should not duplicate pages, links, or log claims. If a source changed, update its revision and affected-page list and explain which compiled conclusions changed.

## Ingest preview

Before mutation, show the human the extracted takeaways, possible contradictions, planned page changes, and proposed thesis effect. Human review is mandatory for ambiguous ontology, conflicting interpretations, or consequential scope changes. A routine ingest may continue after a visible preview when the user already authorized the operation and no material decision remains.
