---
name: create-benchmark
description: Formulate or revise a clear SciCode2 research question and audit its text for scientific coherence and likely nontriviality. Use for early candidate creation and problem revisions between trials; prompt engineering, experiments, reference research, and calibration belong to later workflows.
---

# Create Benchmark

Formulate the problem clearly and make a lightweight scientific judgment from
its text and supplied context. Read [the shared requirements](../../docs/scicode2/requirements.md),
especially [the early-stage workflow](../../docs/scicode2/requirements.md#early-formulation-and-iteration),
and [design-guidelines.md](references/design-guidelines.md).

## Inputs and scope

Accept a research goal, paper idea, existing question, scientific correction, or
feedback from a previous trial. Read the supplied problem and enough available
context to understand it. Preserve actual source provenance; a reviewed-paper
assessment is not required for a directly supplied question.

Use scientific judgment to review the formulation. Do not implement a solution,
run simulations or model trials, build a reference answer, or conduct a research
program to justify passing this screen. Additional research is a later task,
not a prerequisite for early acceptance.

## Formulate and audit

State one central question, its motivation, relevant system/regime, supplied or
anticipated inputs, desired scientific outputs, essential conventions, and scope.
Make the goal understandable while leaving consequential methods and scientific
decisions open. Keep genuinely unresolved choices explicit rather than filling
in an execution recipe, arbitrary numerical target, or invented reference result.

Check whether the question is coherent, scientifically meaningful, plausibly
achievable, and probably nontrivial. Look for an obvious formula substitution,
standard routine, trivial shortcut, or single immediate insight that already
settles it. Also flag unclear objectives, contradictory assumptions, niche-fact
lookup, and artificial difficulty from missing information.

A coherent question that probably needs substantive scientific judgment **passes
this early screen**. A plausible unresolved challenge is enough; do not demand a
proof of difficulty, a completed reference solution, a fully specified evaluator,
or evidence that a frontier model fails. Missing experiments are expected here.

Report a short assessment: `pass-to-testing`, `revise-formulation`, or
`trivial-or-invalid`, with the concrete reason and any uncertainty. These are
local editorial recommendations, not human expert approval or calibrated results.
Compare the Example bank when available; unavailable examples do not block this
text-only screen.

## Output and revision

Write or update the problem statement at its existing canonical path, normally
`problem/TASK.md`; a new lightweight candidate can use the user's destination.
A concise proposal is enough. Do not require `prompt.md`, A/B/C variants, a frozen
evaluation plan, verified answers, a wiki/idea tree, or a first lab to finish creation.
Use [research-workspace.md](references/research-workspace.md) only if the user also
requests repository organization; it does not authorize scientific execution.

When revising after a test, use the observed feedback to improve the question's
clarity or scientific substance. Preserve the superseded formulation and link the
relevant trial. Keep existing metadata/onboarding summaries consistent when the
central question materially changes, without resetting the research lifecycle.
Do not make an arbitrary harder task merely to force an agent failure.

## Handoff

Return the formulated question, short textual audit, and important open choices.
A passing candidate is ready for **exploratory testing** with
[test-benchmark](../test-benchmark/SKILL.md), which designs the experimental prompt
and records each trial in a new lab under this benchmark. The user starts testing
from a fresh agent window without the authoring context. Iterate question → test
→ question revision → test.

Only after the question is reasonably stable and calibration is requested should
[calibrate-benchmark](../calibrate-benchmark/SKILL.md) freeze the task and evaluate
formal A/B/(C) difficulty. Explicit reference-solution research, when needed, uses
the existing research workflows rather than expanding this early creation step.
