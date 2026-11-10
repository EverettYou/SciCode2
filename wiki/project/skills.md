---
title: Reusable skills
page_type: project
status: active
updated: 2026-10-07
project_topics:
- Agentic Research Infrastructure
- Autonomous Research Workflows
source_refs:
- skills/README.md
idea_ids: []
---

# Reusable skills

**Summary**: Skills are the procedural layer that moves work through acquisition, assessment, design, research, knowledge maintenance, validation, and human supervision without embedding operational detail in wiki prose.

**Sources**: [Skill catalog](../../skills/README.md)

**Last updated**: 2026-10-07

The project keeps reusable workflows under `skills/`; one-off experimental utilities remain inside the benchmark that owns them [Skills catalog](../../skills/README.md).

Important workflow families include paper acquisition and assessment, benchmark creation, global and local wiki ingest/query/lint, autonomous research coordination, and talk-based human consultation. Each skill owns its inputs, checks, write boundary, and completion contract. This page records their role in the system and links to the [skill catalog](../../skills/README.md) rather than repeating those procedures.

`create-benchmark` formulates a clear problem and reviews its text for scientific
coherence and likely nontriviality. It does not conduct research or require a
reference answer and finalized prompts. `test-benchmark` designs experimental
prompts, records trials, and feeds observations into repeated question revisions.
Each trial lives in the benchmark's own lab, and the user invokes the testing
skill from a new agent window without the authoring conversation. Context
independence is recorded separately from filesystem location
[Test-lab contract](../../skills/test-benchmark/references/run-record.md#benchmark-local-test-lab).
Once the question is stable, requested `calibrate-benchmark` work freezes the task
and applies the formal difficulty protocol and case-report requirements. Detailed
reference research and lab design belong to the existing research workflows.
Launch/export automation still needs implementation or verification for the client
[Calibration skill catalog](../../skills/README.md#proposal-testing-and-calibration).

## Related pages

- [[project/agent-workflow|Agent workflow]]
- [[project/knowledge-layer|Knowledge-layer design]]
- [[project/research-loop|Research loop]]
