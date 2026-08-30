# Supervisor-synthesis cycle

The hourly worker is both an evidence integrator and a high-level research supervisor. Absence of new evidence is an observation to diagnose, not an automatic no-op or immediate failure.

## Entry and talk precedence

1. Acquire the supervisor-synthesis lease and reload active state.
2. Inspect benchmark-linked open talk threads. Process a latest user-authored message before synthesis or steering. Acknowledge, apply the decision to durable artifacts, reply with a resolution, and leave closure to the user.
3. Compute `evidence_digest.py` and run `detect_stall.py`.

## Classification behavior

- `evidence-changed`: audit every changed completed report and selected result artifact, then apply the semantic evidence gates. Verify that each qualifying report already has a completed `$wiki-ingest` handoff from the `research-tick`; when it does not, record the missing handoff as the next research-tick action and do not ingest it here. Run periodic `$wiki-lint` over the current local wiki, automatically repairing only deterministic mechanical findings. Then consolidate existing provenance-backed wiki material where needed. Treat stale-thesis, possible-contradiction, source-not-integrated, and coverage findings as review candidates, never as permission to rewrite scientific synthesis without evidence. Promote stable code and/or the note only when their evidence and wiki provenance already validate. The research tick, not this supervisor, advances the evidence digest. If an evidence gate fails, classify the work as `awaiting-analysis` rather than supported evidence.
- `healthy-in-flight`: record a concise healthy observation; do not increment no-progress counters or change direction.
- `observation-window`: record `no-progress`, then re-run stall detection so a newly crossed threshold is handled in the same tick.
- `awaiting-human`: continue independent work if available; do not duplicate the thread or guess the answer.
- `stalled`: perform the global diagnosis below.
- `inactive`: no-op and release the lease.

A completed controlled negative result is evidence. An hour without a completed result may be healthy.

## Wiki maintenance boundary

The local benchmark wiki is the authoritative record of the benchmark's thesis and evidence. The `research-tick` is its sole raw-evidence ingestor; the hourly supervisor maintains its health and synthesis without repeating report ingest.

- Verify that a completed report was ingested by the research tick before treating it as available for promotion. A missing handoff is a bounded research-tick task, not a supervisor ingestion task.
- Run `$wiki-lint` periodically and repair only unambiguous structural issues such as broken links, index omissions, or formatting.
- Consolidate across pages only from existing, cited evidence: identify recurring but unnamed concepts or methods, clarify cross-lab comparisons, improve related-page navigation, and restructure thesis, question, or idea-frontier summaries when their underlying provenance is preserved.
- Do not silently update a stale thesis merely because it is old. A stale-thesis finding requires newer evidence; preserve the prior claim or tension where material, and use `$consult-human` if the interpretation changes the central question or a consequential decision.
- The supervisor never advances the evidence digest cursor; it leaves that transaction to the research tick after the full evidence-to-wiki validation path succeeds.

## Global stagnation diagnosis

Read the whole decision surface rather than only the last lab:

- `wiki/thesis.md`, questions, comparisons, concepts, methods, implementations, source coverage, and contradictions;
- `wiki/ideas/` ancestry, competing branches, frontier actions, pruning criteria, and evidence;
- active and completed lab reports, result manifests, failures, invariants, budgets, and heartbeats;
- recent controller events and steering decisions;
- benchmark scope/evidence requirements and unresolved talk threads.

Classify the primary cause as `technical-block`, `awaiting-analysis`, `scientific-stall`, `frontier-exhausted`, `scope-decision`, or `looping`. Identify the cheapest observation that can change the posterior over important ideas.

## Steering authority

Act autonomously within approved scope to repair a technical block, improve observables/controls/convergence, redesign a lab, select another existing frontier, or prune a branch with recorded evidence. Respect the direction-change cooldown unless new decisive evidence makes delay harmful.

Use `$consult-human` before changing the central research question, approved scope, major budget, deliverables, external dependencies, or choosing among scientifically consequential alternatives that the wiki cannot discriminate. Reuse an existing coherent open thread; otherwise open one focused thread with evidence, real options, consequences, a recommendation, and one question. Pause only the dependent branch and continue independent work.

After an approved central-question change, update the whole question context in the same transition: `metadata.yml.research_question`, `problem/TASK.md`, the benchmark README, wiki thesis, and active idea frontier. In `TASK.md`, rewrite `Why this is unresolved` and `Scope and approach` to match the new question; each section must remain at or below 250 words. Preserve the superseded question and rationale in the append-only wiki/idea history. Run the benchmark validator so stale question text or an overlong scope cannot silently survive steering.

Record every material decision:

```bash
python3 skills/auto-research/scripts/record_steering_decision.py \
  benchmarks/<id> --diagnosis scientific-stall --action redesign-lab \
  --summary "Current sweep cannot distinguish the locality predictors." \
  --recommendation "Add matched-CMI points near the predicted transition." \
  --idea-id k-001 --wiki-path wiki/questions/recovery-locality-boundary.md \
  --lab-path labs/lab-002/REPORT.md
```

Update the relevant `wiki/ideas/` pages separately with ancestry, evidence, decision, and next action. Never delete a failed direction to make the search appear linear.

## Exit

Validate any src/note/wiki changes, record one terminal outcome, and release the lease. Report the evidence integrated or diagnosis, decision, affected artifacts, validation, and pending human thread.
