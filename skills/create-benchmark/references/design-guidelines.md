# Early problem-formulation review

This is a text-only screen. Apply scientific judgment to the problem and supplied
context; conducting the research is outside create-benchmark's scope.

## What to inspect

- A clear, coherent scientific question and a meaningful desired result.
- Enough physical/mathematical context and conventions to understand the task.
- Plausible achievability, with no obvious internal contradiction.
- Consequential choices or unresolved reasoning that make the problem probably
  nontrivial; more code, longer runtime, and unfamiliar terminology alone do not.
- Obvious shortcuts: direct substitution, a standard workflow that already settles
  the question, or one immediately applicable insight that removes the challenge.
- Artificial difficulty caused by ambiguity, omitted essentials, or arbitrary limits.

A task need not demonstrate publishable novelty or an entirely unprecedented
method to pass this initial screen. State anticipated scientific difficulty as a
judgment, not an observed model failure.

## Early decision

- `pass-to-testing`: coherent, meaningful, and likely nontrivial. Unknown details
  and the absence of experiments/reference answers do not prevent this outcome.
- `revise-formulation`: the objective or assumptions need a concrete textual fix.
- `trivial-or-invalid`: explain the obvious solution/shortcut or fundamental flaw.

Do not require a complete method, exact thresholds, numerical results, reference
code, proof of hardness, an expert brief, or a calibrated rubric. A reviewer can
say what likely requires judgment without solving it. Early pass means worth a
trial, not that the official difficulty gate has been met.

## Statement and iteration

Keep background, central objective, regime/scope, desired outputs, and essential
conventions clear. Existing research TASK.md files retain their local structure;
where their two 250-word sections apply, keep those concise. New lightweight
candidates need no full research scaffold to pass screening.

Record important uncertainties and source provenance. After a trial, revise the
question using its actual observations and retain the old formulation. Prompt
wording, model configuration, empirical checks, and eventual A/B/C preparation
belong to the [testing workflow](../../test-benchmark/SKILL.md).
