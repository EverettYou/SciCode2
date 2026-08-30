# {{TITLE}}

This README is the benchmark onboarding summary. It points to the current research state; detailed claims and evidence live in the wiki and labs.

## Research goal

**Central question:** [State the current central research question in one sentence.]

**Objective:** {{SUMMARY}}

**Success means:** [State what evidence-backed decision or capability would resolve the benchmark.]

**Scope boundary:** [State the most important included regime and consequential exclusions.]

## Current research status

- **Stage:** `problem-opened`
- **Overall state:** Research design initialized; evidence-producing work has not started.
- **Current thesis:** [Summarize the provisional thesis in one sentence and link `wiki/thesis.md`.]
- **Active frontier:** [List the highest-priority idea IDs and what decision they target.]
- **Active lab:** [Link the active lab report and plan, and state its status.]
- **Latest supported evidence:** No benchmark lab evidence yet; distinguish source support from benchmark findings.
- **Main uncertainty:** [State the uncertainty that most constrains the next research decision.]
- **Next decisive action:** [State one bounded action that would most improve the research state.]
- **Blockers or pending human input:** [Link relevant project-root talk threads, or state none.]
- **Last meaningful update:** {{DATE}}

Update this section only after a material evidence, frontier, lab, steering, or human-decision change. Treat it as a navigation snapshot, not as scientific evidence.

## Start here

Read in this order, stopping when the task has enough context:

1. [`metadata.yml`](metadata.yml) — authoritative identity, scope, research question, expected outputs, evidence requirements, stage, and review state.
2. [`problem/TASK.md`](problem/TASK.md) — full research proposal, conventions, constraints, and reproducibility contract.
3. [`wiki/index.md`](wiki/index.md), then [`wiki/thesis.md`](wiki/thesis.md) — the local knowledge map and current synthesis.
4. [`wiki/ideas/research-frontier.md`](wiki/ideas/research-frontier.md) — idea ancestry, active frontier, next actions, evidence, and pruning decisions.
5. [`labs/README.md`](labs/README.md) — experiment index; follow the active lab links above before reading unrelated labs.
6. [`src/`](src/) and [`note/`](note/) — stable deliverables distilled from supported evidence.
7. [`../../talk/`](../../talk/) — project-level human guidance; find open threads linked to this benchmark ID.

## Independent numerical environment

Each benchmark is a standalone uv project. Add only this benchmark's numerical dependencies to [`pyproject.toml`](pyproject.toml), commit its `uv.lock`, and keep its `.venv` local:

```bash
uv sync
uv run python path/to/experiment.py
```

Do not use `uv sync --active` from a root environment. Benchmark environments share repository files and dependency policy, not installed `site-packages`.

## Source foundation

### Papers

{{PAPER_LIST}}

### Reference implementations and other inputs

See the `paper_ids` in [`metadata.yml`](metadata.yml): each resolves to its canonical [`../../papers/`](../../papers/) folder, including any companion repository. See [`wiki/sources.yml`](wiki/sources.yml) for the cited global-wiki pages.

## Reading discipline

- Use this README to orient and route work, not to substantiate scientific claims.
- Use the global wiki and canonical paper folders for source verification; use local `wiki/thesis.md` and compiled wiki pages for current synthesis, local `wiki/ideas/` pages for research decisions, and lab reports for benchmark evidence.
- Do not reread every raw source or lab by default. Follow the current-status links and the wiki graph first.
- When detailed artifacts disagree with this summary, trust the detailed artifact and refresh this README.
