---
title: Knowledge-layer design
page_type: project
status: active
updated: 2026-08-23
project_topics:
- Research Knowledge Systems
- Agentic Research Infrastructure
source_refs:
- benchmarks/local-petz-recovery-ladder/wiki/SCHEMA.md
- benchmarks/README.md
- skills/README.md
idea_ids: []
---

# Knowledge-layer design

**Summary**: SciCode2 uses a federated knowledge graph: the root wiki compiles reusable cross-paper and project knowledge, while each benchmark wiki owns its local thesis, implementation context, and experiment evidence.

**Sources**: [Benchmark knowledge contract](../../benchmarks/README.md); [example local schema](../../benchmarks/local-petz-recovery-ladder/wiki/SCHEMA.md); [`wiki-ingest`](../../skills/wiki-ingest/SKILL.md)

**Last updated**: 2026-08-23

Raw papers, repository snapshots, completed lab reports, and selected artifacts remain immutable sources. Wiki pages reorganize their claims into concepts, methods, implementations, comparisons, questions, and synthesis with claim-level provenance; they do not copy sources or create one summary page per document [Local benchmark wiki schema](../../benchmarks/local-petz-recovery-ladder/wiki/SCHEMA.md).

The root wiki additionally describes the project itself. It links to the canonical resources that own operational detail, so the graph can refer to its own workflows and implementation without duplicating them.

During benchmark research, the local wiki is authoritative. Agents may query the global wiki for transferable knowledge, but must incorporate consequential material into the local evidence chain before relying on it. Validated benchmark findings may later be promoted into global synthesis while retaining links to their originating report and artifacts.

The rendered graph is derived from wiki links, `source_refs`, paper IDs, and benchmark metadata. There is no second manually edited graph database.

## Related pages

- [[project/research-loop|Research loop]]
- [[project/agent-workflow|Agent workflow]]
- [[papers/index|Papers]]
- [[benchmarks/index|Benchmarks]]
- [[project/skills|Reusable skills]]
