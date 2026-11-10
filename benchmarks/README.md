# SciCode2 Benchmarks

`benchmarks.yml` is the canonical index. Each benchmark is an evolutionary research loop over immutable references, a persistent LLM wiki, a changing pool of ideas, lab reports and evidence, and stable solution deliverables.

## Index and metadata

- `benchmarks.yml` lists stable identity, title, stage, and a short summary.
- `<benchmark-id>/metadata.yml` contains detailed metadata, cited papers, idea provenance, expected outcomes and outputs, evidence requirements, feasibility, and human-review state.
- Paper–benchmark citations are many-to-many and are recorded through `paper_ids` in `metadata.yml`.

An index entry uses this minimum form:

```yaml
- benchmark_id: driven-kagome-response
  title: Driven Kagome Response
  stage: problem-opened
  summary: Short description of the proposed research benchmark.
```

## Compounding research loop

```text
problem/* -> wiki-ingest -> wiki -> wiki-query -> idea / next lab
               ^                                |
               +------- labs/*/REPORT.md <-------+

wiki + supported evidence -> src + note
```

Ideas branch, cross, and prune throughout the loop. Each benchmark's local `wiki/ideas/` family is the canonical record of seed ideas, parents, current frontier, evidence, decisions, dead ends, and distilled artifacts. Never delete a failed idea; mark it `pruned` and retain the reason so the search does not repeat it.

```text
raw sources:          global wiki citations, completed lab reports, selected results
evolving search:      local wiki/ideas/
compiled knowledge:  wiki/
stable deliverables: src/, note/
```

- `papers/<paper-id>/` preserves a paper's PDF, assessment, provenance, optional source archive, and any companion repository under `repo/` as one public source bundle.
- `labs/` tests ideas. Each lab starts its REPORT.md with motivation/design, derives PLAN.md, executes node-local scripts, and finishes the report for wiki ingest.
- `wiki/` compiles both code and text sources into interlinked concept, method, implementation, comparison, source, question, and evolving-thesis pages.
- root `src/` contains stable core code; labs import it instead of duplicating it.
- root `note/` contains the final LaTeX research note.

Do not edit raw references, ingest prospective lab text as findings, let ordinary wiki queries mutate knowledge, move exploratory code prematurely into `src/`, or write final-note claims without wiki and raw-source provenance.

## Recommended layout

```text
benchmarks/
├── benchmarks.yml
└── <benchmark-id>/
    ├── README.md
    ├── metadata.yml
    ├── problem/
    │   ├── README.md
    │   └── TASK.md
    ├── labs/
    │   ├── README.md
    │   └── lab-001-<slug>/
    │       ├── REPORT.md         # motivation/design first; findings after execution
    │       ├── PLAN.md           # executable implementation plan
    │       ├── scripts/
    │       ├── results/
    │       └── figures/
    ├── wiki/
    │   ├── SCHEMA.md
    │   ├── index.md
    │   ├── thesis.md
    │   ├── ideas/               # frontier, branches, decisions
    │   ├── log.md
    │   ├── sources.yml         # provenance ledger; never source copies
    │   ├── concepts/
    │   ├── methods/
    │   ├── implementations/
    │   ├── comparisons/
    │   └── questions/
    ├── src/
    │   └── README.md
    └── note/
        ├── main.tex
        └── references.bib
```

The wiki is a compiled, Obsidian-compatible graph rather than one note per topic or one summary per source. It connects scientific claims from papers to architectures, interfaces, and algorithms extracted from repositories, then to lab evidence. Ingest may update many pages. The concrete layout under root `src/` follows the chosen language and project interface.

The project-root `talk/threads/` is the single research-supervision forum for every benchmark. Users paste paper IDs, benchmark IDs, excerpts, and other source material into a free-text `context` field rather than choosing a scope. Exact benchmark IDs are mirrored into `benchmark_ids` for routing: an empty list is project-wide, one ID links a benchmark-specific conversation, and multiple IDs link cross-benchmark coordination. Either the agent or user may start a thread and both append messages to the same Markdown file. The final author hands the open conversation to the other side; the agent reports completion and only the user closes or reopens it. Benchmark detail pages display the relevant subset.

`wiki/sources.yml` records global-wiki citations and local lab evidence, with a stable revision, ingest time, and affected local pages. A paper bundle is ingested once from `papers/<paper-id>/` into the global wiki; local benchmark pages cite that entry rather than copying or re-ingesting its paper or repository.

The project-root [`wiki/`](../wiki/index.md) is the federated global knowledge layer. A benchmark queries its local wiki first and may consult global cross-paper knowledge, but consequential material must enter the benchmark's own evidence chain before it supports a local research decision.

## Lifecycle

`problem-opened → researching → solution-drafted → verified`

- `problem-opened`: the benchmark problem is defined and its cited papers and initial research direction are recorded.
- `researching`: wiki queries and lab/ingest cycles are actively refining the frontier.
- `solution-drafted`: stable source and the final research note have been drafted from supported survivors.
- `verified`: problem, research record, labs, and solution have passed the required scientific checks and are ready for use.

At every active stage before `verified`, keep at least one `frontier` or `active` idea unless the project has reached a deliberate stopping point. Distillation promotes stable survivors while other useful branches may remain in the pool.

## Creating a benchmark

Use `skills/create-benchmark/`. It owns the metadata schema, design guidance, scaffold assets, creation script, and structural validator. The `benchmarks/` directory contains project instances and the canonical index, not reusable templates.

Early creation formulates the question and reviews its text for coherence and
likely nontriviality. A plausible nontrivial candidate can proceed without a
reference solution, exact prompts, or a full scaffold. Prompt design and repeated
test/revision cycles use `test-benchmark`; formal calibration follows after the
question stabilizes. The full research layout and validator below apply when a
full workspace is requested, not as early candidate acceptance requirements.

Agent tests are labs too: use `labs/lab-NNN-agent-test-<label>/` for the exact
prompt, problem snapshot, input data, PLAN/REPORT, implementation, results,
transcript, and run record. The user invokes `test-benchmark` from a fresh agent
window for each new attempt. File storage stays inside this benchmark; no external
workspace is required. Keep aggregate calibration reports linked to these labs.

Keep `problem/TASK.md` navigable as the question evolves. `Why this is unresolved` and `Scope and approach` are each limited to 250 words; move detailed architectures, ansatzes, libraries, and execution recipes into `wiki/ideas/` or lab plans. A material central-question change must refresh both bounded sections and synchronize metadata, README, thesis, and frontier while preserving the superseded formulation in research history.
