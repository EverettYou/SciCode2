---
title: Research loop
page_type: project
status: active
updated: 2026-08-23
project_topics:
- Autonomous Research Workflows
- Agentic Research Infrastructure
source_refs:
- benchmarks/README.md
- skills/README.md
idea_ids: []
---

# Research loop

**Summary**: Benchmark research repeatedly turns compiled knowledge into competing ideas and discriminating labs, then feeds completed evidence back into the wiki until stable code and a research note can be delivered.

**Sources**: [Benchmark workspace](../../benchmarks/README.md); [`auto-research`](../../skills/auto-research/SKILL.md)

**Last updated**: 2026-08-23

The core loop is:

```text
problem references → wiki ingest → compiled knowledge → idea or next lab
                           ↑                         ↓
                           └──── completed report ──┘

compiled knowledge + supported evidence → src + note
```

`wiki/ideas/` preserves branches, crossings, frontier choices, and pruned dead ends. Labs are optimized for information gain: they state alternatives, execute controlled computations, retain machine-readable results, and interpret failures instead of selecting only positive outcomes [Benchmark README](../../benchmarks/README.md).

The wiki and idea graph have different jobs. The wiki compiles current knowledge; the idea graph preserves ancestry and decisions. Stable implementations move into `src/` only after lab evidence justifies them, and the final note contains supported results rather than the full exploratory history.

## Related pages

- [[project/problem-design-strategy|Problem-design strategy]]
- [[project/knowledge-layer|Knowledge-layer design]]
- [[project/agent-workflow|Agent workflow]]
- [[benchmarks/index|Benchmarks]]
