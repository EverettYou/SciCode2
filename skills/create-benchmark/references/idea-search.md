# Idea search protocol

Treat research as an evolutionary search over a persistent idea graph. Local `wiki/ideas/` pages are the decision graph and `wiki/thesis.md` plus compiled concept, method, implementation, comparison, and question pages are the knowledge context used to grow it; lab folders produce new raw evidence; root `src/` and `note/` hold stable deliverables.

## Node model

Use IDs such as `c-001` for code ideas, `k-001` for knowledge ideas, and `x-001` for cross-track ideas.

```yaml
- idea_id: c-002
  track: code
  status: frontier
  parent_ids: [x-001]
  origin_refs: []
  statement: Replace the dense recovery step with a local tensor contraction.
  rationale: The reference implementation exposes locality but does not exploit it.
  next_action: Design labs/lab-002-local-contraction/REPORT.md and PLAN.md from a cited wiki query.
  evidence: []
  artifacts: []
  decision: ''
```

- `track`: `code`, `knowledge`, or `cross`.
- `status`: `frontier`, `active`, `kept`, `pruned`, or `distilled`.
- `parent_ids`: immediate ancestors. Use one parent for a branch and two or more for a cross.
- `origin_refs`: external roots such as `metadata.idea_sources[0]`, a paper location, or a repo provenance record. Root nodes require at least one origin.
- `statement`: the idea, hypothesis, design move, or question.
- `rationale`: why it deserves search budget.
- `next_action`: the concrete experiment, derivation, reading, or synthesis needed next.
- `evidence`: links to lab reports/results, wiki pages, source locations, or counterexamples used to make a decision.
- `artifacts`: stable outputs under root `src/` or `note/` produced when an idea is distilled. Never list labs or wiki pages here.
- `decision`: why the idea was kept, pruned, or distilled.

Only `distilled` nodes may have non-empty `artifacts`. A distilled `code` node must point under `src/`; a distilled `knowledge` node must point under `note/`. Use `evidence` for all lab and wiki references.

Write origin references containing brackets as a block list or quote them; do not write an unquoted flow list such as `[metadata.idea_sources[0]]`:

```yaml
origin_refs:
- metadata.idea_sources[0]
```

## Search operators

- **Branch:** create multiple children that vary one consequential assumption, method, scale, interpretation, or diagnostic.
- **Cross:** create a child with multiple parents when combining ideas yields a new testable direction. Do not merely concatenate their wording.
- **Test:** move a frontier idea to active and attach the lab or wiki query that can change its status.
- **Keep:** retain supported or strategically useful ideas in the pool even when they are not currently active.
- **Prune:** preserve the node and evidence, set `status: pruned`, and write the reason. Never delete a dead end; it prevents repeated search.
- **Distill:** promote stable, evidence-backed code from labs into root `src/` or supported synthesis from the wiki into root `note/`; record the output and preserve its ancestry.

## Frontier discipline

Allocate effort explicitly. Prefer ideas with high scientific value, information gain, tractability, and ability to discriminate among explanations. Penalize duplication, weak identifiability, prohibitive cost, and dependence on unavailable evidence.

Keep the frontier diverse: include exploitation of strong branches and exploration of alternatives. After each meaningful result, update affected nodes, generate new children or crosses, prune dead ends, and choose the next active nodes. Do not overwrite an idea into a materially different one; create a child so the search history remains visible.

## Track interaction

- A wiki query can generate a code child when synthesis suggests an algorithm or diagnostic.
- A lab result can generate a knowledge child when behavior requires a new explanation; ingest the report before relying on it as wiki context.
- A cross node can combine a code mechanism with a conceptual hypothesis and then branch back into both tracks.
- `labs/` and `wiki/` evolve during research; root `src/` and `note/` are selected stable products, not dumps of everything explored.

## Lab and wiki relationship

- Name labs `labs/lab-NNN-slug/`. `REPORT.md` is the lab's narrative raw source: motivation and design first, then methods, findings, limitations, and search decisions. `PLAN.md` is the executable contract for the code agent. Keep node-local scripts, results, and figures in their corresponding subdirectories.
- Lab scripts may import stable core functions from `src/`; never copy exploratory lab code there merely to share it.
- The wiki is not organized one page per lab or one page per source. `$wiki-ingest` extracts topics, claims, methods, comparisons, and contradictions from raw sources and integrates them across whichever pages are affected.
- Wiki pages use relative Markdown links or unambiguous Obsidian wikilinks and cite raw paths. Important edges should state a relationship such as `supports`, `challenges`, `extends`, `depends-on`, `alternative-to`, `motivates`, or `tested-by`.
- Query the wiki to create candidate ideas and labs; ingest completed lab reports to close the loop.
