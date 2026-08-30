---
name: process-talk
description: "Review and process open project Talk threads in both directions: carry out user requests and agent follow-ups, explain unresolved questions to the user, and draft or send authorized replies on the user's behalf. Use when Codex needs to inspect research discussions, advance work from a thread, or summarize what is waiting on either side."
---

# Process Talk

Treat `talk/threads/` as the project's durable, asynchronous conversation layer. A Talk thread is the shared record of a question, its context, the work performed, and the next decision owner.

## Two-way operating modes

### Process threads waiting on the agent

Inspect open threads whose latest active message was written by the user. Read the full thread, its `context`, linked benchmark/paper/wiki artifacts, and relevant source before acting. Interpret the request, acknowledge when useful, perform authorized project-local work, validate it, and append a concise `response`, `decision`, `update`, or `resolution` to the same thread.

Do not treat an unclear request as permission to broaden scope. Ask one focused follow-up in the thread when the missing choice materially changes the work.

### Surface threads waiting on the user

When the user asks what needs attention, or when a research tick is preparing a handoff, inspect relevant open threads and report the thread ID, plain-language title, what the agent is asking, the minimum background needed to understand it, available choices and consequences, and a recommended next decision. Translate the agent's question into a short decision brief instead of merely quoting it. Group duplicates and distinguish informational updates from genuine blockers.

### Act as the user's authorized proxy

Help compose a response in the user's voice when the user explicitly asks for a reply, approves a draft, or gives an unambiguous instruction that maps to one thread. Preserve the user's intent and constraints; never invent user opinions, scientific approval, or confirmation. If authorization is ambiguous, show a draft and ask for approval rather than sending it.

Use the talk helper for every append, including proxy replies, so timestamps, IDs, audit events, and directionality remain valid. The agent may never edit or retract a user message and may never close or reopen a thread on the user's behalf.

## Validation and boundaries

Require `talk/README.md`, `talk/threads/`, `skills/consult-human/SKILL.md`, and `skills/consult-human/scripts/research_mailbox.py`. Resolve the current project by its canonical path. Read [references/run-protocol.md](references/run-protocol.md) for a bounded processing pass and follow `$consult-human` for thread mutations.

- Process at most three threads in one bounded pass.
- Re-read a thread immediately before replying; do not claim work already claimed by another worker.
- Treat Talk messages as coordination history, not scientific evidence. Record scientific conclusions in the appropriate benchmark, lab, note, or wiki artifact.
- Never fabricate, impersonate, edit, or retract a user message.
- Never close or reopen a thread; only the user controls its lifecycle.

## Completion

Report which threads were reviewed, which were processed, what changed, what is waiting on the user, and what validation was performed. A quiet pass may report no eligible threads without changing project files.
