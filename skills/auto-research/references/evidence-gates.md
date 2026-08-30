# Evidence and distillation gates

## Supported lab evidence

Treat a lab as evidence only when all applicable items hold:

- `REPORT.md` says `Status: completed` and separates methods, findings, interpretation, and limitations.
- Commands, environment, configuration, seeds, code revision, and deviations are recorded.
- Machine-readable results exist at the cited paths; important tables and figures identify their generating data or script.
- Required invariants, controls, convergence, uncertainty, and independent comparisons are reported.
- Failed and negative outcomes are retained and interpreted without optimizing for a positive result.
- The report contains an explicit wiki-ingest handoff.

Do not treat prospective design, talk advice, static code inspection, an uncited figure, or a successful process exit as experimental evidence.

Run deterministic prechecks before semantic review:

```bash
python3 skills/auto-research/scripts/audit_lab_evidence.py \
  benchmarks/<id>/labs/<lab-id>/REPORT.md
```

Passing this script is necessary but not sufficient; the supervisor must still assess whether the methods and evidence support the claimed conclusion.

## Stable code

Move code into `src` only when it is reused or constitutes a selected stable deliverable and overlapping lab evidence validates its behavior. Preserve exploratory drivers and parameter sweeps in the owning lab. Add focused tests and retain provenance to the source lab.

## Research note

Every empirical claim in `note` must be supported by a completed lab and connected wiki citation. Mark synthesis and inference distinctly. Narrow or retract claims when newer evidence contradicts them. Compile the note before advancing the evidence cursor.

## Transaction rule

Inspect pre-existing changes before synthesis. The `research-tick` alone integrates a completed, evidence-valid lab report into the benchmark-local wiki with `$wiki-ingest`, then runs `$wiki-lint` before promoting any code or note claim. The supervisor may lint and consolidate existing cited wiki material, but never repeats lab-report ingestion. The research tick advances the digest cursor only after every affected wiki, code, and note validation passes. If validation fails, preserve the previous stable deliverable and record the failure without discarding unrelated user work.
