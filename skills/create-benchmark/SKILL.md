---
name: create-benchmark
description: Design a SciCode2 research benchmark from reviewed-paper followups, pitfalls, and reference repositories. Create the problem, evolutionary idea graph, initial LLM-maintained wiki, first lab with REPORT.md and PLAN.md, and stable solution boundary. Use when creating or revising a benchmark proposal, research frontier, lab design, wiki initialization, or distillation plan before human review.
---

# Create Benchmark

Create a coherent research project scaffold and stop at the human design-review gate. Use `$consult-human` and the project-root talk for unresolved checkpoints. Do not fabricate experimental findings, treat lab scripts as stable source, or present the final research note as completed.

## Inputs

Require:

- one or more stable `paper_id` values whose assessments have `stage: reviewed`;
- the assessments' `followup_ideas` and `potential_pitfalls`;
- any companion repository already recorded in a selected paper's canonical folder, or an explicit plan to work without one;
- an optional high-level direction from the user;
- a unique lowercase kebab-case `benchmark_id` and human-readable title.

If no direction is supplied, select a promising follow-up or combine compatible items. Preserve materially different alternatives in local `wiki/ideas/` pages; ask the user only when choosing among them would produce fundamentally different projects.

## Read before designing

1. Read every selected paper's complete `assessment.yml`, especially `followup_ideas` and `potential_pitfalls`, plus its provenance and paper PDF or source as needed.
2. Inspect each reference repository's purpose, license, revision, structure, executable entry points, and relation to the cited papers.
3. Read [references/design-guidelines.md](references/design-guidelines.md) for question selection and distillation rules.
4. Read [references/idea-search.md](references/idea-search.md) before creating or changing the idea graph.
5. Read [references/metadata-schema.md](references/metadata-schema.md) before writing `metadata.yml`.

## Organize the project

Treat research as search over an evolving pool of ideas. Maintain its history in local `wiki/ideas/` pages: branch promising ideas, cross compatible ideas, test selected frontier nodes, retain useful alternatives, prune dead ends without deleting them, and distill only supported survivors.

Use this compounding research loop:

```text
problem references ──wiki-ingest──> wiki ──wiki-query──> idea / next lab
        ^                                      |                 |
        |                                      └─────────────────┘
        └──────── labs/*/REPORT.md <── run PLAN.md and scripts

wiki + supported lab evidence ──distill──> src + note
```

- A paper folder is the single owner of its PDF, assessment, provenance, source archive, and any companion repository under `papers/<paper-id>/repo/`. Do not copy either papers or repositories into a benchmark.
- Ingest each selected paper folder into the global wiki first. The benchmark records `paper_ids` and its local wiki cites those global pages; it does not repeat paper or repository ingest locally.
- Organize `labs/` as experiment folders `lab-NNN-slug/`. Each starts with a partially populated `REPORT.md` containing motivation and design, plus a `PLAN.md` that turns the design into executable steps.
- Lab agents implement `PLAN.md` in node-local `scripts/`, importing stable core functions from `src/`; they keep data and figures node-local and finish `REPORT.md` with evidence, analysis, limitations, and search decisions.
- Ingest completed lab reports and selected result artifacts with `$wiki-ingest`; query the updated wiki with `$wiki-query` to synthesize new ideas or the next lab. Use `$wiki-lint` periodically.
- Keep stable deliverables at the benchmark root: reusable code in `src/` and the final LaTeX research note in `note/`.
- Create cross-track children whenever wiki synthesis suggests a computation or a lab result demands a new explanation.
- Keep benchmark-root `README.md` as a concise onboarding and current-status view. Point agents into metadata, the proposal, wiki, idea frontier, active lab, root `src/` and `note/`, and relevant talk threads; do not duplicate the research-loop or human-supervision protocols there.

## Workflow

1. Inventory the assessment ideas. Treat follow-ups as seed directions and pitfalls as constraints, branching axes, evidence requirements, or substantive questions.
2. Select or synthesize the initial research seed. Record its assessment provenance in `metadata.yml.idea_sources`.
3. Initialize `wiki/ideas/research-frontier.md` with a cross-track root such as `x-001`, link it to selected metadata sources, and state why it deserves search budget and what action should expand it.
4. Generate children rather than forcing an immediate final question. Include plausible alternatives across code and knowledge tracks; cross ideas only when the combination creates a new testable direction.
5. Select a coherent current frontier and distill it into one proposal-level research question. Preserve rejected candidates as frontier, kept, or pruned nodes instead of erasing them.
6. Separate source-backed facts from proposed hypotheses. Write `problem/TASK.md` with background, a `Why this is unresolved` section of at most 250 words, the current central question, expected outcomes, a `Scope and approach` section of at most 250 words, outputs, and evidence requirements. When the central question changes, update both bounded sections and synchronize metadata, README, thesis, and frontier in the same transition.
7. Run `scripts/create_benchmark.py` to create the folder and index entry. The script stages work in the project-level `.tmp/` workspace and removes its per-run staging directory on normal success or failure. Do not copy papers or repositories into the benchmark; resolve companion code through the selected paper's canonical folder and global-wiki entry.
8. Initialize the local `wiki/index.md`, `wiki/thesis.md`, `wiki/ideas/research-frontier.md`, and `wiki/sources.yml` by citing the global pages for every selected paper. Store each claim citation as portable standard Markdown, `[readable label](relative-path#locator)`; do not use source IDs or dashboard-resolved citation syntax. Do not re-ingest sources locally. Record operations in append-only `wiki/log.md`.
9. Create the first lab folder. Populate motivation and prospective design in `REPORT.md`; write `PLAN.md` with executable stages, success/failure criteria, expected artifacts, and the `src/` interfaces it may import.
10. Define keep, prune, cross, and distill conditions. Labs and wiki pages may evolve; only supported stable outputs belong in root `src/` and `note/`.
11. Use the project-root talk through `$consult-human`; never create a talk inside the benchmark. Open one durable thread linked to this `benchmark_id` per unresolved scientific choice, scope decision, lint conflict, checkpoint, or user-initiated task. Use multiple benchmark IDs only for genuinely cross-benchmark discussion.
12. Refresh the benchmark README with the current thesis, active frontier and lab, evidence state, main uncertainty, next decisive action, and pending human input. Replace every bracketed prompt. Run `scripts/validate_benchmark.py` and `$wiki-lint`, then rebuild dashboard data.
13. End with `stage: problem-opened` and `expert_review: pending`. Present the proposal, initial wiki thesis, idea frontier, first lab, provenance, feasibility risks, and derived user/agent queue counts to a human reviewer through the dashboard.

## Commands

```bash
python3 skills/create-benchmark/scripts/create_benchmark.py \
  <benchmark-id> \
  --title "<title>" \
  --paper-id <paper-id> \
  --summary "<one-sentence objective>" \
  --idea "<selected or synthesized assessment idea>"

python3 skills/create-benchmark/scripts/validate_benchmark.py \
  benchmarks/<benchmark-id>
```

Use `--repo-root` when running outside the repository root. Never overwrite an existing benchmark or silently replace an upstream snapshot.

## Deliverable boundary

A complete run creates a review-ready research design, not a completed benchmark result. It must contain:

- `metadata.yml` and a matching canonical index entry;
- local `wiki/ideas/` pages with traceable roots, explicit frontier actions, and preserved branching/pruning history;
- a proposal-style problem that references canonical paper folders and global-wiki entries;
- an initialized, interlinked wiki with a non-duplicating `sources.yml` provenance ledger, index, evolving thesis, and append-only log;
- an initial lab `REPORT.md` with motivation/design and a corresponding executable `PLAN.md`;
- a closed wiki-query → idea → lab → wiki-ingest loop;
- stable-output plans for root `src/` and `note/`;
- links to relevant threads in the project-root user–agent supervision talk;
- no fabricated results, unsupported feasibility claims, or unrecorded source provenance.
