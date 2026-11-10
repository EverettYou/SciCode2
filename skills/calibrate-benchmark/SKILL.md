---
name: calibrate-benchmark
description: Evaluate SciCode2 clean runs against frozen reference criteria, interpret the A/B/C difficulty ladder, and prepare a transcript-grounded case report and submission package. Use for keep/revise/prune decisions and intervention audits after trials.
---

# Calibrate Benchmark

Read [the shared requirements](../../docs/scicode2/requirements.md). Use the
prepared task version, evaluation plan, verified reference evidence, run records,
raw transcripts, and outputs. Preparation and execution live in
[create-benchmark](../create-benchmark/SKILL.md) and
[test-benchmark](../test-benchmark/SKILL.md).

Use the benchmark-local `labs/lab-NNN-agent-test-<label>/` records for trials,
including their prompts, run.json, transcripts, results, and reports. Calibration
summaries and final packaging may live in `evaluation/`; that is not a second
test workspace. Do not require copying trials out of the repository. Assess
session freshness and actually loaded context from the records rather than
inferring contamination or independence from directory placement.

## Enter calibration after development

Early creation only formulates a question and judges its likely nontriviality.
Exploratory prompt design, test → question revision → test cycles belong to
test-benchmark and create-benchmark. Do not impose this skill's later evidence
requirements on the initial text screen or automatically calibrate every trial.

When the question is reasonably stable and the user requests calibration, establish
a supported reference outcome and evaluation plan, freeze the problem/prompt/input
version, and prepare the needed A/B/(C) variants using
[prompt-design.md](../test-benchmark/references/prompt-design.md). Explicit reference
research uses existing research workflows. Missing evidence makes calibration
incomplete; it does not revoke an earlier editorial pass merely because it was
based on scientific judgment.

Use independent frozen-version trials for formal difficulty claims. Development
runs remain informative and must be retained; count one toward calibration only
if its exact task, settings, independence, completion, and evaluation all satisfy
the final protocol. Report how the problem was selected or revised, and arrange
fresh authorized trials when those conditions are not met.

## Score before interpreting difficulty

Check that each attempt corresponds to the declared frozen version and has an
actual terminal outcome. Separate full clean runs from dry runs, inherited-context
sessions, supervised attempts, incomplete exports, and exploratory trials.

Apply the prespecified scientific criteria to final outputs, not to the agent's
initial plan or self-assessment. Accept valid alternative methods and conclusions.
When a result contradicts the gold answer, check the reference and rubric too.
Record pass/fail/unknown per criterion with output paths and scientific evidence.

Separate scientific reasoning errors, numerical/implementation errors, insufficient
evidence, legitimate declared-budget overruns, and infrastructure/access failures.
An incomplete run or missing reference makes the difficulty result inconclusive;
do not count it as a scientific failure merely because no answer was produced.

Save per-run `score.json` using the [run/evidence contract](../test-benchmark/references/run-record.md).
Retain every attempt, including successes, and preserve original scores if a
later reference audit changes the interpretation.

## Interpret the ladder

Apply the A/B/C interpretation in the shared requirements. A and B must both fail
in valid full tests to meet the stated local difficulty condition. C is optional;
C failure prompts a fairness/achievability audit, not automatic rejection.

Report counts, variants, versions, settings, and mixed outcomes. Do not cherry-pick
failures, infer a success probability from insufficient trials, or claim formal
acceptance. If the prompt, input, reference criteria, or budget changes, preserve
the previous version and request/perform new authorized trials for the changed
task rather than pooling them as identical evidence.

Write `calibration.md` with a justified local recommendation:

- `keep-for-review`: reference/fairness checks pass and both A/B have valid failure
  evidence; state remaining uncertainties and any mixed outcomes.
- `revise`: solved too easily, dominated by one hint, ambiguous, unfair, or otherwise
  a poor task shape; propose a scientifically motivated revision.
- `prune`: evidence supports abandoning the candidate; retain the reason.
- `incomplete`: missing valid trials, reference evidence, or decisive information.

These are local decision labels. Existing `metadata.yml.stage`, scientific
verification, local difficulty calibration, and organizer acceptance are distinct.

## Transcript-grounded case report

Write `case-report.md` with:

1. Research objective and frozen task identity.
2. Achievable reference outcome and the checks supporting it.
3. A/B/(C) run configuration, final results, and evaluation evidence.
4. Scientific errors and expert interventions, with transcript turn/event locators:
   what the agent asserted, why it is wrong, the correction, and the observed effect.
5. Separate records of objective clarification, pivots, extra requests, aesthetic
   edits, and mixed/uncertain interventions.
6. Limits, untested explanations, valid shortcuts, and the keep/revise/prune rationale.

Do not invent expert interventions from a hypothetical brief or a post-run review.
Historical supervised research and current clean trials are distinct evidence
streams. An autonomous self-correction is not a human scientific intervention.

## Submission package

Prepare the two core files, `proposal.md` and exact A `prompt.md`, plus allowed
input data. Adapt the current formulated question into the final reviewer-facing
proposal, including its scientific judgments, reference/evaluation evidence,
observed difficulty, and limitations. Keep B/C, case reports, references, scores, and transcripts as separate
review evidence; do not put them into the solver input bundle. Record the package
manifest and hashes, and verify links and required inputs.

Check the official template and Example bank if access becomes available. Until
then, state that their complete format/content remains unverified. Preparing the
package does not authorize external submission or messages to the team.

Report the actual measured results, decision, evidence paths, and remaining gaps.
Do not call a task accepted until an organizer decision is actually recorded.
