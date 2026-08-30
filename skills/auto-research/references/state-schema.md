# Auto-research state

Store operational state under `benchmarks/<benchmark-id>/.auto-research/`:

```text
state.yml                    mutable snapshot
events.jsonl                 append-only operational events
steering-decisions.yml       append-only structured supervisor decisions
research.lock                expiring worker lease
supervisor-synthesis.lock    expiring worker lease
```

Operational state and talk discussions are not scientific evidence.

## State invariants

- Keep `schema_version: 1` and a benchmark ID matching the directory.
- Use only `paused`, `active`, `blocked`, or `complete` for status.
- Treat automation IDs as cached opaque values; verify them against the scheduler.
- Advance `last_synthesis_evidence_digest` only after a successful, validated synthesis or an intentional baseline acknowledgment.
- Reset no-evidence and repeated-failure counters only when the corresponding progress actually occurs.
- Keep `pending_human_thread_id` until the user reply is processed and its decision is durably applied.
- Do not delete earlier event or steering records.

## Script operations

```bash
python3 skills/auto-research/scripts/loop_state.py status benchmarks/<id>
python3 skills/auto-research/scripts/loop_state.py transition benchmarks/<id> active
python3 skills/auto-research/scripts/loop_state.py set-schedules benchmarks/<id> \
  --research-id <opaque-id> --synthesis-id <opaque-id>
python3 skills/auto-research/scripts/loop_state.py set-pending-human \
  benchmarks/<id> T-0003
python3 skills/auto-research/scripts/loop_state.py set-pending-human benchmarks/<id>
```

Acquire a lease before worker mutations and retain the returned token:

```bash
python3 skills/auto-research/scripts/loop_state.py acquire benchmarks/<id> \
  --worker research --ttl-minutes 9
python3 skills/auto-research/scripts/loop_state.py release benchmarks/<id> \
  --worker research --token <token>
```

Record exactly one terminal outcome per worker tick. Use a stable action or failure signature so repetition is detectable:

```bash
python3 skills/auto-research/scripts/loop_state.py record-run benchmarks/<id> \
  --worker research --outcome progress --action lab-002:analyze \
  --lab-id lab-002 --lab-stage analyzing --details "Generated tidy comparison table."
```

Use `--heartbeat` only when an active lab produced a real checkpoint or observable runtime progress.
