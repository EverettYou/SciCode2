# Local run and evidence contract

This is a repository convention, not the organizer's submission schema.

Exploratory development requires an immutable snapshot of each attempt, not a
globally finalized question or prompt ladder. `task_version` identifies that
attempt's problem/prompt revision. Reference/evaluator revisions may be null with
an explanation; no unknown result should be converted into a scientific failure.
Formal calibration records identify the later frozen task and supported rubric.

## Benchmark-local test lab

Default to one attempt per lab in the existing benchmark:

```text
benchmarks/<id>/
  problem/TASK.md
  labs/
    README.md
    lab-NNN-agent-test-<label>/
      PLAN.md                 # intended execution/settings, then deviations
      REPORT.md               # prospective first; actual observations after run
      problem-snapshot.md     # exact question used in this attempt
      prompt.md               # exact experimental prompt/selected variant
      inputs/                 # declared solver input data
      scripts/                # attempt-local implementation
      results/                # generated data, outputs, evaluation evidence
      transcripts/            # original session export, with completeness noted
      run.json
      score.json              # when an evaluation is actually available
```

The lab is the working directory and durable test record. No external folder or
repo is required. Select the next unused lab number; do not overwrite another
attempt. The user opens a new context-free agent session and invokes the test
skill for the benchmark/lab. Freshness refers to the conversation and loaded
scientific context, not the lab's filesystem location.

Read only the current problem and selected attempt's declared scientific materials
during the solve. Other research files may remain in the repo; do not preload
their answers, guidance, or old results. Record actual context, not a purported
filesystem barrier. Resume the same lab only to continue the same attempt.

Record these fields in `run.json`; use `null` with an explanation for unavailable
observations, rather than inventing values:

| Field | Required meaning |
|---|---|
| `run_id`, `task_version`, `variant` | Unique attempt, immutable problem/prompt snapshot identity, and actual prompt label (A/B/C for calibration). |
| `purpose` | `preflight`, `exploratory`, or `calibration`. |
| `benchmark_id`, `lab_id`, `problem` | Owning benchmark/lab and exact problem snapshot path/hash. |
| `prompt` | Author snapshot path and SHA-256 of exact bytes given to the agent. |
| `inputs` | Allowed relative paths and SHA-256 hashes; include generated-data seed/revision if applicable. |
| `evaluator_revision`, `reference_revision` | Available grading/reference provenance; nullable for exploration, frozen and supported for formal calibration. |
| `client`, `model`, `effort` | Actual client/version and selected model/effort, with how verified. |
| `internet`, `tools`, `hardware`, `budget` | Actual access/settings and any declared limits. |
| `session_id`, `solver_workspace` | Actual session identity and the benchmark-local lab path. |
| `isolation` | Session freshness and its evidence (including user declaration), loaded instructions/memory/scientific context, and clean/supervised/inherited-context classification. This field does not assert filesystem isolation. |
| `started_at`, `ended_at`, `execution_status` | Timestamp with offset; completed/interrupted/launch-error/preflight-only. |
| `interventions` | Human messages/actions during the attempt, or an explicit empty list. |
| `transcript` | Durable raw export path, format, SHA-256, event locator convention, export time and completeness. |
| `outputs` | Saved output paths/hashes and any missing expected artifacts. |
| `resource_use`, `errors` | Observed usage and execution problems. |

Store scoring separately in `score.json` so capture and judgment have distinct
provenance. It records evaluator revision, each criterion, observed value/evidence,
pass/fail/unknown, whole-task result, failure category, and reviewer uncertainty.
Keep evaluator stdout/stderr or review notes when they support the decision.

Finish REPORT.md with observations, output paths, uncertainty, and next revision
feedback; add the lab to `labs/README.md`. A completed trial is evidence of agent
behavior, not automatically a validated scientific finding or calibration pass.

If a session only exposes a bounded or summarized transcript, record that limit;
do not label it a complete original export. Re-read the evidence paths before
claiming archival success. A manifest alone is not evidence of an executed trial.
