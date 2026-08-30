# Research talk thread schema

Each canonical project thread is `talk/threads/T-NNNN-slug.md` with YAML frontmatter followed by append-only messages. Benchmarks never contain talk copies.

```markdown
---
id: T-0001
title: Choose the primary boundary regime
status: open
priority: high
category: scientific
created: 2026-08-22T12:00:00Z
updated: 2026-08-22T14:30:00Z
context: |-
  Paper: example-paper
  Benchmark: example-benchmark
  [Follow-up idea]
  Test whether the boundary regime changes the recovery threshold.
benchmark_ids:
- example-benchmark
related:
- benchmarks/example-benchmark/wiki/thesis.md
- benchmarks/example-benchmark/labs/lab-003/REPORT.md
---

# Choose the primary boundary regime

## M-001 · agent · question · 2026-08-22T12:00:00Z

**What this is about**: Choose the primary boundary regime for the benchmark.

**What we know**:
- The current evidence supports the narrow regime for the first controlled test.
- The broad regime remains feasible but costs more compute.

**What is unclear or blocked**: The next lab cannot be created until the primary regime is chosen.

**Options**:
- A — narrow regime; cheaper and easier to interpret.
- B — broad regime; more coverage but more confounding.

**Suggested: A** — it isolates the main hypothesis first.

**Decision requested**: Please choose A or B, or specify one change.

## M-002 · user · advice · 2026-08-22T13:00:00Z

Use the narrow regime and preserve the broad alternative.

## M-003 · agent · resolution · 2026-08-22T14:30:00Z

Implemented in `benchmarks/example-benchmark/labs/lab-004/REPORT.md`.

## M-004 · user · edit · 2026-08-22T14:35:00Z

Target: M-002

Use the narrow regime first, but retain both alternatives.

## M-005 · user · retraction · 2026-08-22T14:40:00Z

Target: M-002
```

The next expected author is derived from the last message: after `agent`, the thread awaits `user`; after `user`, it awaits `agent`.

`context` is free text and is the human-facing way to attach source material. It may contain paper IDs, benchmark IDs, copied paper assessment cards, excerpts, links, or instructions. In dashboard-created threads, exact benchmark IDs found in `context` are mirrored into `benchmark_ids`; agents may set the same derived field explicitly. `benchmark_ids: []` means project-wide, one ID links one benchmark, and multiple IDs link a cross-benchmark discussion. All `related` paths are project-root-relative.

Allowed values:

- status: `open`, `closed`;
- author: `agent`, `user`;
- priority: `blocking`, `high`, `normal`, `low`;
- category: `checkpoint`, `scientific`, `scope`, `interpretation`, `conflict`, `resource`, `lint`, `task`, `other`;
- message type: `question`, `advice`, `response`, `acknowledgment`, `update`, `decision`, `resolution`, `edit`, `retraction`.

An `edit` or `retraction` is a user-authored append-only operation targeting an earlier user message. The dashboard materializes edits in place and renders a retraction as withdrawn; audit messages remain in the Markdown history. Retracted messages do not determine the next respondent. Corrections are allowed only while the thread is open.

An agent reports completion with a `resolution` message but does not close the thread. Only the user may close or reopen it. A closed thread accepts no ordinary replies. Never delete, renumber, or rewrite older messages to hide a changed decision.
