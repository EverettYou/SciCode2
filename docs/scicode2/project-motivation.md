# SciCode 2 motivation and task design

This note preserves the motivation text supplied by the user on 2026-10-16. The
original document title, author, and date were not included, so this is recorded as
user-supplied source material rather than independently verified organizer text.
The original pasted text is retained at
[`sources/project-motivation.txt`](sources/project-motivation.txt).

## Motivation

Current coding systems can increasingly implement prescribed numerical methods and
operate existing scientific workflows. Scientific computation also requires
constructing a justified procedure when the method is not specified: formulating
the computational problem, choosing relevant effects and approximations, selecting
methods, balancing accuracy and cost, diagnosing failures, and deciding what
evidence makes a result trustworthy.

SciCode 2 is intended to evaluate the transition from executing a scientific
workflow to constructing one that is scientifically justified. Its target is the
frontier of human–AI collaboration: problems that current frontier systems cannot
yet solve reliably on their own, but that a capable scientist can bring to a
validated solution in roughly 10–20 hours using current tools. The measured work is
the expert scientific judgment that still must be supplied, rather than total
implementation effort or unaided human time.

## Task design principles

- Begin with a scientific objective and practical constraints, not a complete
  computational recipe.
- Prefer new, modified, or previously unanalyzed systems whose answers cannot be
  obtained by retrieval alone.
- Make the difficulty depend on substantive scientific decisions and interpretation
  of intermediate results, rather than generic software engineering or obscure
  facts alone.
- Allow more than one scientifically reasonable solution strategy.
- Keep tasks solvable and computationally practical, and support them with at
  least one validated reference solution and enough information for independent
  work.
- Evaluate results with domain-appropriate evidence such as numerical targets,
  invariants, limiting cases, convergence, statistical properties, independent
  methods, or qualitative phase-diagram features. Automate checks when practical.

These principles complement the source-grounded requirements archived in
[`requirements.md`](requirements.md). If a conflict arises, verify against the
current organizer instructions rather than treating this unattributed pasted text
as higher authority.
