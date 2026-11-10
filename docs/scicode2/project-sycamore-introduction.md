# Project Sycamore: participant introduction

This page preserves the participant-facing introduction supplied by the user on
2026-10-16. It is background context, separate from organizer emails archived in
[`requirements.md`](requirements.md).

For the scientific-computation motivation and task-design principles, see
[`project-motivation.md`](project-motivation.md). For concrete strong and rejected
candidate examples, see [`example-bank.md`](example-bank.md).

## Purpose

Project Sycamore asks researchers to work alongside an AI assistant as they would
with a capable but fallible junior collaborator. The researcher chooses a problem
from their own field that they want answered and do not already know, tests the
assistant's independent ability, and keeps a complete record of the collaboration.

The project's aim is to find research questions that are meaningful and achievable
by an expert, but where an AI is likely to make consequential scientific mistakes
and need expert intervention. The central evidence is what the assistant got wrong,
why it was wrong, and how expert guidance changed the work.

## Participant workflow

1. Choose a genuine, open research question from the researcher's field.
2. Test the question on a frontier agent for a few hours. Observe whether it can
   solve the problem independently and where its reasoning fails. If it succeeds
   easily, strengthen the question or choose another.
3. Propose the candidate by explaining the problem, desired answer, why it is
   difficult, and how an answer could be checked. A completed solution is not
   required for the proposal.
4. After approval, work with the AI to reach a trusted answer, intervening when
   needed, and convert the checks into automatic tests.
5. Keep a record throughout, especially of when and why the researcher had to
   intervene.

The introduction estimates 15–20 hours for proposal approval and another 10–20
hours to build a problem. A first candidate may be rejected or reshaped; iteration
and early feedback are expected. Around hour five, the coordinator plans to discuss
which candidate is worth pursuing. Participants may also later become peer
reviewers or Team Leads.

## How this maps to this repository

The participant introduction describes the collaboration in broad terms. The
repository's [organizer requirements](requirements.md) preserve more specific
requirements and distinguish organizer evidence from local workflow conventions.
The local development cycle is formulate → test → revise → test again, followed by
formal calibration once the question is stable and calibration is requested. Do
not treat approval, complete prompt ladders, reference solutions, or formal
difficulty evidence as prerequisites for early candidate formulation unless the
current organizer instructions explicitly require them.

For a candidate, use [`create-benchmark`](../../skills/create-benchmark/SKILL.md)
to formulate and text-audit the question, then [`test-benchmark`](../../skills/test-benchmark/SKILL.md)
for authorized exploratory trials and durable records. Use
[`calibrate-benchmark`](../../skills/calibrate-benchmark/SKILL.md) only when the
question is stable and formal calibration is requested. Preserve full transcripts
and distinguish scientific corrections from clarification, goal changes, added
requests, and cosmetic preferences.

Questions for the Sycamore team can be sent to the Slack channel
`#project-sycamore-help-desk`; this note records that contact route but does not
authorize an agent to send messages.
