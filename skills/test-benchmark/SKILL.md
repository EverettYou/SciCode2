---
name: test-benchmark
description: Design prompts and run SciCode2 trials in benchmark-local labs from a fresh user-opened agent session. Preserve each attempt's inputs, settings, transcripts, and outputs, and feed observations into question revisions. Also execute formal A/B/C trials when later calibration is requested.
---

# Test Benchmark

Read [the shared requirements](../../docs/scicode2/requirements.md). Read
[the run record](references/run-record.md) when preparing or recording a trial.
Accept a formulated question or a later frozen task, and an authorized execution
scope. Read [prompt-design.md](references/prompt-design.md) for prompt preparation,
exploratory feedback, and later A/B/C construction. Infer whether the user wants
prompt design, preflight, exploratory execution, or a calibration run; do not
start a full trial when asked only to design its protocol.

## Lab location and session entry

Run tests in `benchmarks/<id>/labs/lab-NNN-agent-test-<label>/`, following the
benchmark's existing lab numbering. No external workspace or separate repository
is required. For a lightweight candidate, use its own `labs/` directory without
requiring a complete research scaffold. Each new attempt normally gets a new lab;
resume an existing lab only when continuing that same attempt.

The user opens a fresh agent window/session without the authoring conversation
and invokes test-benchmark there, naming the benchmark or lab. That fresh session
can prepare and execute the test directly. Do not require it to create another
session, launch an external solver, or move files outside the repository.

Read the current problem statement, this procedural skill, and the selected lab's
declared materials. Keep the test context focused: do not preload prior trial
reports/transcripts, reference answers, solution code, wiki synthesis, or scientific
corrections from the authoring session. Their presence elsewhere in the same repo
is not itself context inheritance. Record what was actually loaded, including any
project instructions or memory, rather than claiming filesystem isolation.

If invoked in an ongoing authoring conversation, prepare the lab and a short
startup instruction for the user's fresh window. Do not label execution with
inherited scientific context as a fresh test. User-declared session freshness is
usable; record its basis without inventing independent verification.

## Explore and iterate

Ordinary testing is developmental: design a prompt for the current question,
run it, inspect the observations, revise the question with
[create-benchmark](../create-benchmark/SKILL.md), and test again. A final prompt
ladder, frozen evaluator, completed reference solution, and calibration-ready
problem are not prerequisites for exploratory trials.

Preserve a problem/prompt snapshot for every attempt. The question can change
between attempts; each trial remains traceable to exactly what it tested. Report
preliminary scientific checks and uncertainties without claiming formal calibrated
difficulty. Dry runs check clarity only; use complete runs to observe actual agent
behavior. Formal calibration happens later on a reasonably stable question.

## Prepare a clean trial

1. Prepare the current attempt's exact prompt and allowed-data hashes. Record the
   problem revision and available evaluation checks. For exploratory trials,
   reference/evaluator gaps are explicit limitations rather than launch blockers.
   For formal calibration trials, verify the frozen task and supported rubric.
2. Initialize the benchmark-local lab with a problem snapshot, exact `prompt.md`,
   allowed input data, a prospective `REPORT.md`, and an execution `PLAN.md`.
   Keep scripts, outputs, transcripts, and run records in this lab as specified in
   [the lab/run contract](references/run-record.md). The plan records procedure,
   configuration, and intended checks; do not insert undeclared solution hints.
3. Record whether the session is fresh, resumed, or inherited from research, and
   which scientific/project context was loaded. Scope the solve to the selected
   problem, prompt, and declared data. Do not read sibling labs or author answers
   during the attempt. A repo-local lab is valid; being outside the repo is not
   a condition for testing. Later formal calibration records the actual context
   and applies its declared protocol without inventing an isolation guarantee.
4. Verify the strongest available model, its highest effort, internet access,
   runtime/hardware, tool configuration, and any prespecified budget. Record actual
   values; do not assume that the current chat has the requested settings.
5. Establish a transcript-export path before launch. Check actual installed-client
   help or available session tooling rather than inventing CLI flags or session
   storage formats. Never copy the user's entire session store or credential files.

Use a fresh user-opened session for each new clean trial, with no inherited author
conversation or earlier scientific corrections. This skill supplies the test
procedure; the selected prompt supplies the scientific task and any intentional
guidance. A subagent inheriting an author conversation is not a fresh-window
substitute. Record any actual extra context or intervention.

If required model/effort or internet access is unavailable, finish useful preflight
work and state the missing capability without claiming a completed equivalent run.
Lack of a session-launch API or external sandbox does not block a test already
started in the user's fresh window. Do not create a new sidebar chat merely
because this skill was invoked.

## Execute and preserve

Run the exact task to a terminal outcome, allowing autonomous computation, checks,
and strategy changes. Do not rescue a formal trial with expert hints. If a human
intervenes, preserve the event and label the affected attempt supervised; a new
clean attempt requires a new session and run ID.

Record actual start/end times, completion or interruption, tool failures, resource
use when available, all output artifacts, and the original transcript. Export
promptly on completion or interruption; do not rely on session retention. Preserve
raw evidence in the lab's `transcripts/`, outside ignored `.tmp/` storage. Use
the exact raw format available and do not replace it with a summary.

Keep secrets out of shareable exports. If a transcript contains credentials or
unrelated private material, retain the private original and create a separately
identified redacted sharing copy, preserving stable event references and a
redaction record. Do not silently alter the evidentiary original.

## Completion

Write the run record and verify that referenced files exist and hashes match.
Complete the lab's `REPORT.md` with actual methods, observations, artifacts,
limitations, and implications for the next question revision; keep `PLAN.md` as
the execution record and record deviations. Update the benchmark's lab index.
Report whether the trial was exploratory or formal, full, clean, completed,
interrupted, or preflight-only; identify material context/configuration limits.
For development, report observations and return question revisions to create-benchmark.
After the question stabilizes and calibration is requested, hand supported
reference evidence and suitable trials to
[calibrate-benchmark](../calibrate-benchmark/SKILL.md). A successful process exit
or the agent's self-assessment is not a scientific evaluation result.
