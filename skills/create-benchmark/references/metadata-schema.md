# Benchmark metadata schema

`benchmarks/<benchmark-id>/metadata.yml` is the canonical detailed record. Keep keys in this order for readable diffs.

```yaml
benchmark_id: lowercase-kebab-case
title: Human-readable benchmark title
stage: problem-opened
paper_ids:
- stable-paper-id
summary: One-sentence scientific objective and proposed investigation.
idea_sources:
- paper_id: stable-paper-id
  source_field: followup_ideas
  item_index: 0
  role: primary-question
research_question: One central, answerable scientific question.
scientific_domain:
- controlled-vocabulary-or-short-label
expected_outcomes:
- scientifically justified hypothesis or anticipated insight
expected_outputs:
- result, artifact, or quantitative observable the project must produce
evidence_requirements:
- exact limit, convergence study, invariant, or independent cross-check produced in labs
estimated_active_hours: null
workstation_feasible: uncertain
expert_review: pending
expert_notes: ''
```

## Constraints

- `benchmark_id`: unique lowercase kebab-case identifier; must equal the folder name.
- `stage`: one of `problem-opened`, `researching`, `solution-drafted`, or `verified`. This skill always creates `problem-opened`.
- `paper_ids`: non-empty list of IDs present in `papers/papers.yml` with local reviewed assessments.
- `summary`: concise objective, not a literature abstract.
- `idea_sources`: non-empty traceability list. Each item identifies a cited `paper_id`, `source_field` (`followup_ideas`, legacy `natural_followups`, or `potential_pitfalls`), zero-based `item_index`, and a concise `role` such as `primary-question`, `supporting-method`, `risk-control`, or `evidence`.
- `research_question`: one central question; do not store several loosely related questions here.
- `expected_outcomes`: scientific hypotheses or anticipated insights. Phrase uncertainty explicitly and do not invent results.
- `expected_outputs`: concrete project deliverables. These are not the same as expected scientific outcomes.
- `evidence_requirements`: checks and studies that must be produced through `labs/`, compiled into `wiki/`, and supported in `note/`; this is not a separate validation package.
- `scientific_domain`, `expected_outcomes`, `expected_outputs`, and `evidence_requirements`: non-empty string lists before human review.
- `estimated_active_hours`: positive number only when supported by a concrete estimate; otherwise `null`.
- `workstation_feasible`: `yes`, `no`, or `uncertain`.
- `expert_review`: `pending` or `reviewed`. This skill always creates `pending`.
- `expert_notes`: empty until a human records a review.

`benchmarks/benchmarks.yml` contains only `benchmark_id`, `title`, `stage`, and `summary`. The detailed record takes precedence when dashboard data is built.

Keep dynamic research-search state out of `metadata.yml`. Store the evolving pool, ancestry, frontier, pruning decisions, evidence, and distilled artifacts in local `wiki/ideas/` pages described by `references/idea-search.md`.
