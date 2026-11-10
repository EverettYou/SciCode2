# Experimental prompt design and iteration

Use after a research question has passed the early text screen. The problem can
still evolve. Do not require a final A/B/C ladder or completed reference answer
before the first exploratory trial.

## Turn the question into a trial

Read the current problem statement. Write `prompt.md` as the exact initial task
for this attempt: scientific objective, necessary inputs/conventions, desired
outputs, allowed resources, and any meaningful known success checks. Leave
substantive scientific choices open. Do not expose author notes, prior solutions,
research workflows, or another attempt's transcript.

If the question lacks an essential convention, resolve that in the problem text
through [create-benchmark](../../create-benchmark/SKILL.md). If a detail is merely
an untested method or an unknown performance threshold, keep it open rather than
inventing a recipe or benchmark target.

Create the attempt under the benchmark's `labs/lab-NNN-agent-test-<label>/`.
Keep `prompt.md`, `problem-snapshot.md`, allowed `inputs/`, scripts, generated
results, transcripts, and the run record in that lab. Use the lab as the working
directory; no external repository/workspace is required. A lightweight candidate
can likewise keep tests in its own `labs/` directory.

The user invokes test-benchmark from a fresh window without the authoring chat.
Read the selected problem and declared inputs, not sibling lab findings or author
solutions. A neutral PLAN/REPORT scaffold can organize the attempt without adding
scientific guidance. Record actual loaded instructions and any extra context.

## Snapshot each attempt

Record the problem revision, exact prompt/data hashes, model/settings, and run ID.
This is a reproducibility snapshot of one attempt, not a requirement that the
research question or future prompts are finalized. Reference/evaluator revisions
may be null for exploratory tests; record what can and cannot be evaluated.
Use [the lab/run record](run-record.md) and `purpose: exploratory` for development.

The run can test clarity, expose shortcuts, observe autonomous strategy changes,
or produce scientific results. Compare outputs with known principles, available
reference evidence, and independent checks when possible. A missing gold answer
makes some outcomes unknown; it does not turn them into scientific failures.

## Use feedback to revise the question

Report what the attempt actually showed, which issues belong to prompt wording,
which expose a flaw in the question, and which are scientific errors supported by
evidence. Retain successful, failed, supervised, interrupted, and inconclusive runs.

Revise prompt wording here. Return scientific-objective changes to create-benchmark
and preserve the prior problem version. Test the revised question/prompt in a new
session. Do not erase development runs or quietly describe them as identical trials.
Do not enlarge scope or choose arbitrary precision merely to force failure.

## Prepare for later calibration

Only when the question is reasonably stable and formal calibration is requested,
use the calibration skill to establish a supported evaluation plan and freeze a
task version. Then prepare the variants needed for calibration:

- A: the standalone natural initial task in `prompt.md`.
- B: exact A plus a substantial expert brief, saved as `prompt-b.md`.
- Optional C: exact B plus hindsight execution steps, saved as `prompt-c.md`.

Keep their objective, input data, and rubric comparable. `task-version.json`
records hashes and reference/evaluator revisions for the frozen set. Exploration
can use hints earlier when useful, with their actual context recorded; a complete
ladder is not a prerequisite for ordinary testing.

Write results and revision feedback into this lab's `REPORT.md`. The final
reviewer-facing proposal, case report, and submission package are
assembled by [calibrate-benchmark](../../calibrate-benchmark/SKILL.md). The emails
specify no universal run count, numerical threshold, or complete submission format.
