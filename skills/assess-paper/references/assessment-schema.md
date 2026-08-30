# Paper assessment schema

Use `low`, `medium`, or `high` for qualitative ratings. Use `yes`, `no`, or `uncertain` for feasibility and validation fields.

Keep list entries independent because the dashboard displays and edits them as separate cards. Use a folded scalar (`>-`) for a long item or any item containing `:`.

```yaml
paper_id: string
title: string
year: integer
source_url: string
stage: listed | fetched | assessed | reviewed
research_area: [string]
summary: string
computational_core: string
computational_depth: low | medium | high
scientific_judgment: low | medium | high
validation_ease: low | medium | high
workstation_feasible: yes | no | uncertain
reference_solution_feasible: yes | no | uncertain
non_searchable_extension_possible: yes | no | uncertain
supervision_confidence: low | medium | high
followup_ideas: [string]
potential_pitfalls: [string]
suggested_task_types: [string]
ai_assessment: string
```
