# Schedule reconciliation

Use this protocol for controller operations. Scheduled tasks are the execution mechanism; `.auto-research/state.yml` is a cache and scientific-control record, not the scheduler authority.

## Resolve existing schedules

1. Find the Codex project ID for the current repository.
2. Inspect the automation store and automation-management interface for the IDs recorded in state and for exact names:
   - `auto-research:<benchmark-id>:research`
   - `auto-research:<benchmark-id>:supervisor-synthesis`
3. Match by ID first, then exact name plus benchmark path in the prompt. Treat ambiguous matches as a controller error and ask the user rather than deleting or merging tasks.
4. Prefer updating an existing task. Create only a missing task.

Use standalone project-local cron automations because both workers must share the benchmark checkout and `.auto-research` state. Do not use isolated worktrees without a separately designed merge protocol. Use the scheduling interface's interval controls rather than writing raw recurrence expressions.

## Desired tasks

Research task:

- interval: 10 minutes;
- project: the current SciCode2 project in local mode;
- name: `auto-research:<benchmark-id>:research`;
- prompt:

```text
Invoke $auto-research in research-tick mode for benchmarks/<benchmark-id>.
Perform at most one bounded, resumable research transition. Honor review gates,
leases, budgets, pause/stop state, evidence rules, and talk supervision.
Report only material progress, a new blocker, completion, or a concise no-op.
```

Supervisor-synthesis task:

- interval: 60 minutes;
- project: the same local project;
- name: `auto-research:<benchmark-id>:supervisor-synthesis`;
- prompt:

```text
Invoke $auto-research in supervisor-synthesis-tick mode for
benchmarks/<benchmark-id>. Process relevant talk replies first. Verify that the
research tick has ingested any newly supported lab evidence; do not duplicate
that ingest. Run periodic $wiki-lint and consolidate only existing,
provenance-backed local-wiki material before promoting anything to src or note.
When evidence has not advanced, distinguish healthy in-flight work from
stagnation, diagnose the wiki/idea/lab graph, and steer or consult the user
under the skill's authority boundaries.
```

Do not put notification preferences inside either prompt.

## Lifecycle

- `start`: initialize state, reconcile both tasks, store exact IDs, enable them, then mark active.
- `pause`: resolve exact IDs, pause both tasks, then mark paused.
- `resume`: reconcile missing/drifted tasks, enable both, then mark active.
- `stop`: resolve and delete both tasks. Mark complete only when completion criteria are already satisfied; otherwise mark paused.
- `status`: compare actual task state with the cached IDs and report drift.

If one mutation succeeds and the other fails, keep state paused, retain the successful ID, and report the partial reconciliation. Never claim the loop is active until both schedules are enabled.
