---
title: Project overview
page_type: project
status: active
updated: 2026-10-07
project_topics:
- Agentic Research Infrastructure
- Computational Benchmark Design
source_refs:
- papers/papers.yml
- benchmarks/README.md
- docs/scicode2/requirements.md
idea_ids: []
---

# Project overview

**Summary**: SciCode2 benchmarks scientific reasoning and judgment that still require expert correction. This repository develops candidate questions and reference solutions, then prepares independent model tests and transcript-grounded difficulty evidence.

**Sources**: [Organizer requirements](../../docs/scicode2/requirements.md#what-the-benchmark-measures); [paper catalog](../../papers/papers.yml); [benchmark workspace](../../benchmarks/README.md)

**Last updated**: 2026-10-07

Papers enter a canonical inventory, are fetched and assessed, and become candidates for benchmark design. Benchmarks then conduct a bounded research program rather than asking an agent merely to reproduce a published result [Paper catalog](../../papers/papers.yml) [Benchmark README](../../benchmarks/README.md).

Paper follow-ups are one candidate source. Actual research-session scientific
corrections are another. The organizer's target is scientific judgment rather than
objective clarification, a changed goal, extra requests, or cosmetic adjustments
[Intervention types](../../docs/scicode2/requirements.md#what-the-benchmark-measures).

Research evidence establishes an achievable reference outcome. Difficulty evidence
requires complete independent runs of the exact prompt, including a guided version
with a substantial expert brief. The new preparation/testing/calibration skills
define this second path; they are procedural first versions, not an implemented
cross-client runner. The full official instructions and Example bank remain
unverified because document access was denied
[Requirements and limitations](../../docs/scicode2/requirements.md#sources-and-authority)
[Skill workflow](../../skills/README.md#proposal-testing-and-calibration).

Early candidate creation is lighter: clear formulation and a text-only judgment
of likely nontriviality are sufficient to enter exploratory testing. Prompt design
and test/question-revision cycles precede formal calibration; early creation does
not conduct the research itself
[Development stages](../../docs/scicode2/requirements.md#early-formulation-and-iteration).

The project has four connected surfaces: the paper catalog, benchmark workspaces, this global knowledge graph, and the project-wide talk. Reusable skills define how agents move information and work between those surfaces.

Canonical identity and status remain in [papers/papers.yml](../../papers/papers.yml) and [benchmarks/README.md](../../benchmarks/README.md). The [dashboard](../../dashboard/README.md) serves the human-facing workspace.

## Related pages

- [[papers/index|Papers]]
- [[benchmarks/index|Benchmarks]]
- [[project/problem-design-strategy|Problem-design strategy]]
- [[project/agent-workflow|Agent workflow]]
- [[project/talk|Research talk]]
