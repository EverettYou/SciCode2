# Bounded research cycle

One research tick may perform multiple read-only checks but at most one material transition.

## Entry

1. Acquire the research lease using the policy TTL and retain its token.
2. Reload state. Stop with a no-op unless status is `active`.
3. Inspect relevant open talk threads. When the latest active message is from the user, acknowledge it and apply the guidance before selecting unrelated work. Clear `pending_human_thread_id` only after the decision is durably applied.
4. Read benchmark metadata, the problem task, local `wiki/ideas/` pages, local wiki index/thesis, recent wiki log, and active lab reports/plans. Read the global wiki index/thesis and follow only links relevant to the current uncertainty.
5. Respect `expert_review` and lab-specific review gates. A pending review allows source ingest, lint, query, and proposal refinement, but not experimental execution.

## Priority order

Choose the first state-advancing action that applies:

1. Apply an answered human checkpoint.
2. Ingest one missing immutable problem reference.
3. Ingest one newly completed, evidence-valid lab report and selected results.
4. Fix deterministic wiki-lint failures caused by the current loop.
5. Resume one checkpointed stage of the active lab.
6. Analyze existing results and complete the lab report when gates pass.
7. Query `global+benchmark:<benchmark-id>` for multiple candidate ideas or next labs, keeping global synthesis distinct from benchmark-local evidence, then update one frontier decision.
8. Create one prospective lab folder and plan when authorized.
9. Record a genuine blocker or completion state.

Do not design a new lab while an active lab has an unresolved result that can cheaply change the frontier.

## Lab execution

- Make PLAN stages independently executable and shorter than the research cadence when practical.
- Record commands, configuration hashes, seeds, environment, revisions, deviations, and artifact paths.
- Use a heartbeat only after a measurable checkpoint; process existence alone is insufficient.
- Keep experimental scripts/results/figures in the lab. Import stable functions from `src` rather than copying them.
- Interpret failed or null experiments. A controlled negative result can be supported evidence.
- Stop or redesign when the pre-registered discrimination, invariant, convergence, or budget conditions fail.

## Exit

Run the smallest relevant validation, record one terminal outcome with `loop_state.py record-run`, and release the lease even after failure. Use a normalized failure signature such as `lab-002:solver:nonconvergence`, excluding timestamps and random paths.
