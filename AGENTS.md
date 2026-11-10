# SciCode2 repository workflows

The enduring project goal is to identify meaningful research questions where an
AI assistant needs expert scientific judgment, then preserve the full evidence of
the collaboration and interventions. Before proposal or candidate work, read the
[participant-facing Project Sycamore introduction](docs/scicode2/project-sycamore-introduction.md)
as well as the organizer requirements below. Keep the introduction's broad
participant context distinct from the source-grounded organizer requirements and
local conventions.

For SciCode2 proposal, candidate-screening, prompt, model-test, difficulty,
intervention-audit, or submission-packaging work, read
[`docs/scicode2/requirements.md`](docs/scicode2/requirements.md). This reference
archives the organizer emails and distinguishes them from local conventions.

Repository skills are maintained in [`skills/README.md`](skills/README.md).
Read the relevant `SKILL.md` directly when it is not in the session's skill catalog:

- [`create-benchmark`](skills/create-benchmark/SKILL.md): formulate the question
  and audit its text for coherence and likely nontriviality. A plausible
  nontrivial problem passes; no scientific execution or finalized prompts required.
- [`test-benchmark`](skills/test-benchmark/SKILL.md): design experimental prompts,
  run authorized trials in benchmark-local labs from a fresh user-opened agent
  session, preserve evidence, and feed back into question revisions.
- [`calibrate-benchmark`](skills/calibrate-benchmark/SKILL.md): after the question
  stabilizes and calibration is requested, freeze the task and assess difficulty;
  decisions, intervention classification, case report, submission package.

Existing paper, research-scaffold, lab, wiki, and talk skills remain responsible
for their own workflows. Research verification does not establish model difficulty
or organizer acceptance. Dry runs do not replace full autonomous tests.

The normal development cycle is create → test → revise the question → test again,
then formal calibration. Do not bring later reference/evaluator/A/B/C requirements
forward as gates for early creation or ordinary exploratory testing.

Tests live in `benchmarks/<id>/labs/lab-NNN-agent-test-<label>/`; no external repo
or workspace is required. The user starts a new window without the authoring chat
and invokes test-benchmark there. Procedural skills can guide the test; read the
selected problem/prompt and declared inputs without preloading scientific answers,
prior trial reports, or research history. Record actual session/context conditions.
