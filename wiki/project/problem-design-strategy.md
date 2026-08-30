---
title: Problem-design strategy
page_type: project
status: active
updated: 2026-08-23
project_topics:
- Computational Benchmark Design
- Agentic Research Infrastructure
source_refs:
- benchmarks/README.md
- skills/README.md
idea_ids: []
---

# Problem-design strategy

**Summary**: A SciCode2 benchmark is a novel, evidence-backed computational research proposal that demands scientific judgment, fits a workstation, and preserves the provenance of both its question and solution.

**Sources**: [Benchmark lifecycle](../../benchmarks/README.md); [`create-benchmark`](../../skills/create-benchmark/SKILL.md)

**Last updated**: 2026-08-23

Benchmark design starts from reviewed paper assessments but must extend, combine, perturb, or stress-test the source work. A viable problem has a central question, a concise explanation of why it remains unresolved, a concise scope and approach, expected outcomes, evidence requirements, limitations, and concrete code and research-note deliverables [Skills catalog, create-benchmark/SKILL.md](../../skills/create-benchmark/SKILL.md). The unresolved rationale and scope are each capped at 250 words; detailed architectures and execution recipes belong in idea or lab artifacts.

The task should require consequential choices about formulation, approximation, experiment design, validation, and interpretation. Its expected active effort is bounded, its computation is workstation-feasible, and its conclusions can be supported by reproducible numerical evidence rather than inaccessible ground truth.

Human design review is the gate between a scaffolded proposal and active research. Review asks whether the question is novel and coherent, provenance is complete, the initial experiment can change an important decision, and stop or pruning criteria are meaningful [Benchmark README](../../benchmarks/README.md).

The central question is allowed to evolve as evidence changes the frontier. A material revision must update its unresolved rationale and scope in the same transition, synchronize metadata, onboarding, thesis, and frontier, and retain the superseded formulation in the research history rather than allowing proposal text to drift silently.

## Related pages

- [[project/overview|Project overview]]
- [[project/research-loop|Research loop]]
- [[project/knowledge-layer|Knowledge-layer design]]
- [[papers/index|Papers]]
- [[benchmarks/index|Benchmarks]]
