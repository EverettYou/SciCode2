---
name: auto-research
description: Run, supervise, pause, resume, or stop an unattended SciCode2 benchmark research loop using both benchmark-local and global knowledge. Use when Codex should reconcile research schedules, execute a bounded wiki-query/idea/lab/wiki-ingest transition, synthesize evidence into src and note, diagnose a stalled frontier, or escalate a consequential decision through the project talk.
---

# Auto Research

Coordinate existing benchmark skills and artifacts; do not replace their scientific protocols. Keep research execution bounded and resumable, and make the hourly supervisor responsible for both evidence synthesis and research-direction diagnosis.

## Resolve the operation

Accept a benchmark directory and one operation:

- `start`: initialize state and idempotently reconcile two project-local schedules.
- `status`: report durable state, actual schedule state, current lab, evidence cursor, stall signals, and pending talk decision.
- `pause`: pause both schedules and set local state to `paused`.
- `resume`: reconcile and enable both schedules, then set state to `active`.
- `stop`: delete both schedules after resolving their exact IDs, then set state to `complete` only when the benchmark is scientifically complete; otherwise set it to `paused`.
- `research-tick`: execute at most one bounded research transition.
- `supervisor-synthesis-tick`: integrate new evidence or diagnose and steer a stalled loop.

Infer `start` when the user invokes the skill with a benchmark but no operation. Never create schedules merely because the skill was loaded.

## Validate the benchmark

Require `metadata.yml`, `problem/`, `wiki/`, `labs/`, `src/`, and `note/`. Confirm that `metadata.yml.benchmark_id` matches the directory. Read the project `README.md` and global wiki index/thesis, then benchmark metadata, problem task, local idea graph, local wiki schema/index/thesis, and relevant open talk threads before the first mutation.

Initialize deterministic control state with:

```bash
python3 skills/auto-research/scripts/loop_state.py init \
  benchmarks/<benchmark-id> --research-minutes 10 --synthesis-minutes 60
```

Read [references/state-schema.md](references/state-schema.md) before changing control-state fields directly. Prefer the bundled scripts.

## Control schedules

For `start`, `pause`, `resume`, and `stop`, read [references/scheduling.md](references/scheduling.md). Use the Codex automation-management capability; do not install OS cron entries or emulate a scheduler with a background shell process. Resolve actual automations before mutation, prefer updating matching IDs, and never create duplicates.

After both schedules are reconciled, save their IDs and transition state to `active`. If scheduling is unavailable, leave the loop paused and report the missing capability; manual ticks remain usable.

## Run a research tick

Read [references/research-cycle.md](references/research-cycle.md). Acquire the `research` lease, re-check active status, process relevant user-authored talk replies, then execute at most one state-advancing action. Always release the lease.

Use `$wiki-ingest` for sources and completed lab reports, `$wiki-query` with `global+benchmark:<benchmark-id>` for cited idea/lab decisions, `$wiki-lint` after wiki changes, and `$consult-human` for consequential judgment. All wiki citations written by this loop must use portable standard Markdown: `[readable label](relative-path#locator)`, with no source-ID or dashboard-resolved citation syntax. Treat the benchmark wiki as authoritative for local thesis and evidence; use the global wiki to discover transferable knowledge, then bring consequential primary evidence into the local chain. Preserve idea ancestry and unsuccessful branches. Do not execute an unapproved lab or convert prospective text into findings.

## Run a supervisor-synthesis tick

Read [references/supervisor-synthesis.md](references/supervisor-synthesis.md) and [references/evidence-gates.md](references/evidence-gates.md). Acquire the `supervisor-synthesis` lease and process relevant talk replies first.

Compute the candidate-evidence digest and classify progress. Apply the evidence gates before promotion:

```bash
python3 skills/auto-research/scripts/evidence_digest.py benchmarks/<benchmark-id>
python3 skills/auto-research/scripts/detect_stall.py benchmarks/<benchmark-id>
```

- Verify that newly supported lab evidence has already been handed off to the local wiki by the `research-tick`; if that handoff is missing, record it as the next research-tick action and do not duplicate the ingest. Run periodic `$wiki-lint`, then consolidate only existing, provenance-backed wiki material into clearer synthesis, concepts, methods, comparisons, questions, or idea-frontier structure.
- Treat stale-thesis, contradiction, and source-coverage lint findings as evidence-backed review candidates. Fix only deterministic wiki mechanics automatically. A consolidation may reorganize or summarize established evidence, but may not create a new scientific finding; use `$consult-human` when interpretation is consequential or ambiguous.
- Treat a fresh lab heartbeat as healthy in-flight work.
- Record a no-progress observation when neither condition holds; once thresholds trigger, diagnose the entire wiki/idea/lab graph and steer, prune, redesign, or consult the user.

Never equate a negative result with absent evidence when it passes the evidence gates. Do not change direction on a single quiet cycle. The research tick advances the evidence digest cursor only after every affected wiki, code, and note validation has passed.

## Boundaries

- Never modify immutable problem references or repository snapshots.
- Never treat talk messages, controller logs, prospective lab prose, or static code inspection as experimental evidence.
- Never silently broaden the central question, compute budget, dependencies, or deliverables.
- Never close or impersonate a user in a talk thread.
- Never let overlapping ticks edit the same benchmark; use leases and expiring checkpoints.
- Preserve unrelated user changes and validate every distilled solution change before advancing the evidence cursor.

## Completion

Report the operation, schedule reconciliation, action performed, artifacts changed, evidence or stall classification, validation, and any talk thread awaiting the user. A quiet successful tick may report a concise no-op; a blocked tick must state the durable next step.
