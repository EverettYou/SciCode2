# Benchmark design guidelines

## Design test

A strong proposal has all of the following:

1. **Scientific objective** — answering it requires domain reasoning, not only software construction or parameter tuning.
2. **Non-searchable extension** — at least one consequential model, regime, perturbation, estimator, or comparison differs from the source papers.
3. **Operational specification** — inputs, outputs, units, conventions, allowed resources, and success criteria can be stated without prescribing one implementation.
4. **Evidence plan** — labs can produce exact small cases, invariants, limiting cases, convergence studies, or independent cross-checks where applicable.
5. **Feasible investigation** — the question can be investigated and its claims supported on a workstation at the chosen scale.
6. **A closed research loop** — problem references initialize the wiki, wiki queries motivate labs, completed lab reports update the wiki, and supported survivors reach root `src/` or `note/`.
7. **Preserved provenance** — upstream papers and companion repositories remain identifiable, versioned inputs in canonical `papers/<paper-id>/` folders and global-wiki entries rather than being copied into derived benchmark work.

## Research as evolutionary search

Do not assume the initial idea is the final benchmark question. Treat it as a seed for an evolving pool:

1. Generate children that vary meaningful assumptions, mechanisms, methods, diagnostics, or interpretations.
2. Allocate search effort to a diverse frontier rather than committing immediately to one branch.
3. Use labs and notes to obtain information that changes which ideas deserve further work.
4. Cross code and knowledge ideas when their interaction creates a new hypothesis or method.
5. Keep promising ideas, prune weak or infeasible ideas with explicit evidence, and never erase dead ends.
6. Generate new frontier nodes after each consequential result.
7. Distill stable survivors into root `src/` and `note/` while preserving ancestry in local `wiki/ideas/`; never treat labs or wiki pages as final deliverables.

Judge ideas by scientific value, expected information gain, tractability, discriminating power, and compatibility with available evidence. A large tree is not progress by itself; the pool should improve through selection.

## Design sequence

1. Inventory every `followup_ideas` and `potential_pitfalls` item in the reviewed assessments.
2. Shortlist candidate questions. A candidate may select one follow-up, combine compatible follow-ups, or turn a substantive pitfall into a robustness or failure-boundary investigation.
3. Reject combinations with unrelated objectives, noncommensurate outputs, or evidence demands that exceed the resource envelope.
4. Record selected items in `idea_sources`; use the assessment field and zero-based list index rather than copying long text into metadata.
5. State one central research question that begins with “Determine…”, “Construct…”, “Under what conditions…”, or an equally testable formulation.
6. Write scientifically justified expected outcomes as hypotheses, not guaranteed conclusions. Keep them distinct from the artifacts listed under `expected_outputs`.
7. List public inputs and fixed conventions, then required outputs with formats, units, and quantitative meaning.
8. Identify the smallest exact or analytically controlled experiment and a target regime that adds difficulty without removing interpretability.
9. Define the lab evidence required to support or refute each expected outcome.
10. Estimate active human work, peak memory, runtime, storage, and optional accelerator needs.
11. Record ambiguities, likely shortcuts, licensing concerns, and assumptions for human review.

## Proposal structure

Write `problem/TASK.md` as a short research proposal followed by an executable specification:

- **Background and motivation:** establish only the context needed to understand why the question matters.
- **Why this is unresolved:** in at most 250 words, identify what evidence or mechanism is missing and why the current central question remains open. Keep implementation candidates out unless they are essential to the question.
- **Research question:** ask one central, answerable question.
- **Objective:** state what the investigation must determine, construct, compare, or characterize.
- **Expected outcomes:** give falsifiable or inspectable hypotheses and the insight each outcome would provide; do not fabricate numerical results.
- **Scope and approach:** in at most 250 words, fix the scientific regime, decisive comparisons, and exclusions while leaving legitimate methodological choices to the researcher. Detailed ansatzes, software choices, and execution recipes belong in the idea frontier or lab plans.
- **Project specification:** define inputs, deliverables, conventions, and evidence requirements precisely enough to review.

The central question is expected to evolve as research prunes or crosses ideas. After every material change to it, review and update `Why this is unresolved` and `Scope and approach` in the same transition, then synchronize `metadata.yml`, the benchmark README, wiki thesis, and active frontier. Preserve the former question and rationale in the append-only wiki/idea history rather than leaving stale proposal text.

## Benchmark README contract

Treat the benchmark-root `README.md` as the first-read onboarding summary, not as a copy of the reusable research loop, talk protocol, proposal, or wiki schema. It must let an unfamiliar agent answer three questions quickly: what is the research trying to determine, where does it currently stand, and which artifacts should be read next.

Include:

- the central question, objective, success condition, and consequential scope boundary;
- a compact current-status snapshot covering lifecycle stage, current thesis, active idea frontier, active lab, latest supported evidence, main uncertainty, next decisive action, blockers or pending human input, and last meaningful update;
- an ordered reading path to `metadata.yml`, `problem/TASK.md`, `wiki/index.md`, `wiki/thesis.md`, `wiki/ideas/research-frontier.md`, the active lab, stable solution outputs, and relevant project-root talk threads;
- source-foundation links and a reminder that the README is navigation, not scientific evidence.

Update the status snapshot only after a material evidence, frontier, lab, steering, or human-decision change. Do not turn it into an append-only log or duplicate detailed findings. When the summary becomes stale, detailed wiki, lab, idea, metadata, and talk artifacts remain authoritative and the README must be refreshed.

## Search and distillation rules

- Treat `papers/<paper-id>/` as the immutable public source bundle for a paper and any companion repository.
- Represent branches, crosses, pruning, retention, and distillation in local `wiki/ideas/` pages.
- Put exploratory modifications, reproductions, numerical probes, failures, and generated evidence in lab folders. Treat each completed `REPORT.md` as raw input to the wiki.
- Move code into `src/` only after its interface and scientific role stabilize; record the distilled idea IDs and originating labs.
- Use `$wiki-ingest` to compile papers, reference materials, lab reports, and selected results into an interlinked, provenance-rich wiki with an evolving thesis.
- Use `$wiki-query` to synthesize candidate ideas and next experiments from the maintained wiki rather than repeatedly re-deriving context from raw sources.
- Write the final TeX research note under `note/` from the wiki and reproducible evidence, while discussing consequential pruned alternatives.
- A distilled artifact must live in `src/` or `note/`.
- Link important claims bidirectionally: final-note claim to wiki synthesis and lab evidence, wiki claim to raw source, and solution source component to its originating idea and experiment.

## Human-review gate

The reviewer must decide whether:

- the proposed extension is scientifically worthwhile and truly distinct from reproduction;
- the selected follow-ups and pitfalls genuinely support the central question, with no artificial combination;
- expected outcomes are defensible hypotheses rather than conclusions presented in advance;
- the task is self-contained and neither over-prescriptive nor underspecified;
- expected outputs and evidence requirements are commensurate;
- the proposed labs can support the claims expected in the report;
- stable code lives under root `src/` and the final research note under root `note/`;
- the initial idea graph has a diverse but tractable frontier and explicit pruning criteria;
- the resource estimate is plausible;
- paper copying and any future code reuse comply with provenance and licensing constraints;
- unresolved questions have owners and do not hide a fundamental design choice.

Keep the benchmark at `idea` with `expert_review: pending` until those decisions are recorded.
