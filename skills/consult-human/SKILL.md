---
name: consult-human
description: Manage asynchronous user–agent research supervision through the project-root talk, using decision briefs that explain context, evidence, options, consequences, and a recommended choice. Use when an agent needs scientific or scope judgment, reaches a checkpoint or dead end, must route a lint ambiguity to the user, needs to process a user-initiated request, or must open, reply to, complete, close, or reopen a research conversation.
---

# Consult Human

Use the project-root `talk/threads/*.md` instead of creating Talk threads inside benchmarks or burying consequential questions in chat. Put source material in the thread's free-text `context`; it may include copied paper or benchmark IDs, assessment items, excerpts, links, and instructions. Mirror exact benchmark IDs into `benchmark_ids` for routing. The last message `author` fully determines direction: an open thread authored last by `agent` awaits `user`, and vice versa.

Read [references/interaction-schema.md](references/interaction-schema.md) before changing threads. Use `scripts/research_mailbox.py` so IDs, timestamps, state, and message history remain consistent.

## Open a thread

Open one thread per decision or coherent conversation. Before asking, exhaust safe evidence gathering and read the relevant benchmark, wiki, paper, lab, and prior Talk context. A user should be able to understand the issue without asking the agent to explain the question again.

Every agent-initiated decision request must contain these sections in the message body, in this order:

1. **What this is about** — identify the benchmark/artifact and the scientific or product goal in one or two sentences.
2. **What we know** — summarize the relevant evidence, current state, and important constraints; link durable sources rather than relying on unexplained jargon.
3. **What is unclear or blocked** — state the precise decision that cannot be made autonomously and why it matters now.
4. **Options** — provide two or more materially different choices when they exist. For each, state the main consequence, cost, and what remains reversible. Do not manufacture false alternatives when one action is clearly required.
5. **Recommendation** — name one option as **Suggested** and give the short reason. A recommendation is guidance, not a claim that the user has approved it.
6. **Decision requested** — end with one explicit question that can be answered directly, such as `Please choose A, B, or C, or specify one change.`

Use short paragraphs and bullets for options and consequences. Put long evidence excerpts in `context` or linked artifacts and summarize them in the message. If the question depends on missing evidence, say what is missing and gather it before escalating; do not send a vague “what should we do?”

Use `blocking` only when useful independent work cannot continue. For a non-blocking preference, use `high`, `normal`, or `low` and explain what work can proceed while waiting.

If an agent reply asks a new question or requests a checkpoint, apply the same decision-brief structure above. Do not hide a new decision inside a progress update. Put the decision request at the end, keep it singular, and make the suggested option explicit. If several independent decisions arise, split them into separate Talk threads or clearly number them with a recommendation for each.

```bash
python3 skills/consult-human/scripts/research_mailbox.py open \
  . \
  --author agent \
  --benchmark <benchmark-id> \
  --context "Paper: <paper-id>
Benchmark: <benchmark-id>
Copied evidence or design context." \
  --title "Choose boundary regime" \
  --message "What this is about: ...\n\nWhat we know:\n- ...\n\nWhat is unclear or blocked: ...\n\nOptions:\n- A — ...\n- B — ...\n\n**Suggested: B** — ...\n\nDecision requested: Please choose A or B." \
  --category scientific \
  --priority high \
  --related benchmarks/<benchmark-id>/wiki/thesis.md \
    benchmarks/<benchmark-id>/labs/lab-003/REPORT.md
```

A user-initiated task or suggestion uses the same command with `--author user`; the next reply belongs to the agent. Omit `--benchmark` when the context contains no benchmark ID and repeat it for a cross-benchmark discussion. The dashboard infers these links from exact IDs pasted into `CONTEXT`; it never asks the user to select a scope. Do not duplicate an existing open thread. Continue independent work when possible.

## Reply and transition

At the start of benchmark work, inspect open threads whose last author is `user`. Reply with acknowledgment or a concrete update before acting when appropriate. After implementing guidance, append a `resolution` message with links to durable changes. Leave the thread open for user confirmation; only the user closes it.

```bash
python3 skills/consult-human/scripts/research_mailbox.py list .

python3 skills/consult-human/scripts/research_mailbox.py reply \
  . T-0001 \
  --author agent --type acknowledgment \
  --message "I will compare both regimes in lab-004."

python3 skills/consult-human/scripts/research_mailbox.py reply \
  . T-0001 \
  --author agent --type resolution \
  --message "Implemented in benchmarks/<benchmark-id>/labs/lab-004/REPORT.md and ingested into the wiki."
```

The latest author always hands an open thread to the other side. A user closes a completed or abandoned thread with `transition --author user --status closed`; this is the termination mechanism. Closed threads are append-locked and only the user may reopen them.

## User corrections

A user may edit or retract their own message while the thread is open. Use the dashboard for inline editing, or the deterministic commands below. Both operations append an audit event; they never overwrite or delete the original Markdown message. Treat the materialized edited text as current and ignore a retracted message when deriving the next respondent.

```bash
python3 skills/consult-human/scripts/research_mailbox.py edit \
  . T-0001 M-002 --author user \
  --message "Corrected response."

python3 skills/consult-human/scripts/research_mailbox.py retract \
  . T-0001 M-002 --author user
```

## Boundary

Talk messages coordinate work but are not scientific evidence. When a discussion changes scientific interpretation, preserve the decision in the thread and update the wiki through `$wiki-ingest` using raw evidence. Never invent a user message, invoke a user correction without explicit user action, or silently discard user guidance.
