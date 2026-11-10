---
title: Problem-design strategy
page_type: project
status: active
updated: 2026-10-07
project_topics:
- Computational Benchmark Design
- Agentic Research Infrastructure
source_refs:
- benchmarks/README.md
- skills/README.md
- docs/scicode2/requirements.md
idea_ids: []
---

# Problem-design strategy

**Summary**: Early creation uses textual scientific judgment to pass clear, probably nontrivial questions into iterative testing; formal minimal/guided difficulty calibration follows after the question stabilizes.

**Sources**: [Organizer requirements](../../docs/scicode2/requirements.md); [benchmark lifecycle](../../benchmarks/README.md); [`create-benchmark`](../../skills/create-benchmark/SKILL.md)

**Last updated**: 2026-10-07

`create-benchmark` clarifies the scientific question and audits its text. A coherent,
meaningful question that probably requires substantive scientific judgment passes
the early screen. No implementation, experiment, reference answer, exact prompt
ladder, or proof of model failure is required at this point
[Early formulation](../../docs/scicode2/requirements.md#early-formulation-and-iteration)
[Creation workflow](../../skills/create-benchmark/SKILL.md#formulate-and-audit).

The full research workspace is optional at creation. Existing TASK.md conventions,
including two 250-word sections, remain local document conventions rather than
organizer acceptance limits. Detailed lab and reference-solution design is later
work, separately requested and owned by the research workflows
[Optional organization](../../skills/create-benchmark/references/research-workspace.md#workflow).

Candidate selection also accepts scientific corrections from research sessions
and directly supplied questions. Screen out tasks dominated by one hint, niche
facts, routine execution, or a complete prescribed recipe
[Candidate checks](../../docs/scicode2/requirements.md#candidate-shape-and-rejection-checks).

Early suitability is a provisional judgment about scientific substance and
plausible achievability. Missing empirical validation is expected, not grounds to
fail a reasonable candidate. The normal development loop designs a prompt, tests,
revises the question, and tests again; each attempt is preserved without finalizing
the whole task prematurely
[Iterative testing](../../skills/test-benchmark/references/prompt-design.md).

Tests live in `labs/lab-NNN-agent-test-<label>/` under the same benchmark as the
problem. The user starts each new attempt in a fresh agent window. Procedural
testing instructions may guide execution without inheriting authoring-session
scientific corrections or preloading earlier solutions; an external repository
is not required
[Lab storage and fresh sessions](../../docs/scicode2/requirements.md#lab-storage-and-fresh-sessions).

Once the question is stable and formal calibration is requested, establish the
reference/rubric and freeze the task. The submission-facing proposal and exact
solver `prompt.md` are separate artifacts.
A is the natural initial task; B adds a substantial expert brief; optional C adds
hindsight execution detail. Complete clean runs of A and B must both fail to meet
the emailed difficulty condition. A dry-run plan or historical supervised failure
is insufficient. C failure raises an achievability question rather than automatic
rejection. Preserve successes and mixed outcomes; the emails specify no fixed
trial count or success-rate threshold
[Prompt ladder](../../docs/scicode2/requirements.md#deliverables-and-prompt-ladder)
[Full-run conditions](../../docs/scicode2/requirements.md#required-test-conditions).

Research verification, local calibration, and organizer acceptance are distinct.
The current local research lifecycle does not establish that a model failed a
clean prompt. The Example bank comparison remains pending access
[Workflow boundary](../../docs/scicode2/requirements.md#local-workflow-and-ownership).

The central question is allowed to evolve as evidence changes the frontier. A material revision must update its unresolved rationale and scope in the same transition, synchronize metadata, onboarding, thesis, and frontier, and retain the superseded formulation in the research history rather than allowing proposal text to drift silently.

## Related pages

- [[project/overview|Project overview]]
- [[project/research-loop|Research loop]]
- [[project/knowledge-layer|Knowledge-layer design]]
- [[papers/index|Papers]]
- [[benchmarks/index|Benchmarks]]
