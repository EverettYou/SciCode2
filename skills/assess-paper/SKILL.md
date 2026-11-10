---
name: assess-paper
description: Assess papers for SciCode2 benchmark potential and create or revise an assessment.yml file in a paper folder. Use when discussing a paper's computational core, ratings, follow-up ideas, potential pitfalls, benchmark suitability, or when updating paper metadata after expert feedback.
---

# Paper Assessment

Use this skill after paper fetching or when a publication record is available. Treat Codex as the scientific discussion surface and `assessment.yml` as the canonical structured record. The dashboard is an inventory and light editor, not a second research chat.

## Workflow

1. Read the publication metadata and, when available, the abstract, full text, source, and code.
2. Separate facts established by the paper from proposed benchmark extensions. Correct a user's premise politely when the primary source gives a narrower or different result.
3. Summarize the computational core, likely task transformation, validation strategy, and potential failure modes.
4. Assign provisional ratings using the controlled vocabulary in `references/assessment-schema.md`. Record uncertainty explicitly; do not present an abstract-only assessment as a literature-level conclusion.
5. Create or edit `papers/<paper-id>/assessment.yml`. Preserve publication identity fields unless the user explicitly asks to reconcile the catalog as well.
6. Keep each `followup_ideas` and `potential_pitfalls` item independently editable. Use `>-` for long YAML items or any item containing a colon.
7. Review means directly correcting the assessment content, then setting `stage: reviewed`. Validate the YAML and run `scripts/build_dashboard_data.py` after direct-file edits.

## Direct revision protocol

When the user discusses a specific correction or idea in Codex, write the agreed change directly to `assessment.yml`; do not require a duplicate dashboard conversation. Before saving a method comparison, ensure its outputs and metrics are commensurate. Put noncommensurate comparisons, unvalidated approximations, or hidden numerical errors in `potential_pitfalls`.

## Required scientific judgment

Prioritize whether a paper can support a new, non-searchable computational benchmark. Evaluate scientific judgment, reference-solution feasibility, workstation feasibility, validation strength, and likely supervision confidence separately. Do not collapse these into an opaque score.

For SciCode2 proposal suitability, also read
[the shared organizer requirements](../../docs/scicode2/requirements.md). Screen
for one-hint solutions, niche-fact dependence, routine workflows, and prompts that
prescribe the entire recipe. These are provisional assessments; actual difficulty
requires complete clean A/B trials at the later calibration stage. Route early
problem formulation to
[create-benchmark](../create-benchmark/SKILL.md), including candidates originating
from research-session scientific corrections rather than reviewed papers.

The creation handoff is an early textual formulation/suitability screen. Plausible
scientific nontriviality is enough to recommend testing; lack of a completed
reference solution, exact prompts, or difficulty trials is not an early rejection.
Prompt engineering and empirical question refinement happen in test-benchmark;
formal difficulty calibration follows once the question is reasonably stable.

## Commands

Use `scripts/create_assessment.py` to create starter metadata from `papers/papers.yml`. Use `scripts/build_dashboard_data.py` after metadata is edited to regenerate the dashboard data file.
