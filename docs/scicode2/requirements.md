# SciCode2 proposal and difficulty requirements

Recorded on 2026-10-07 from two organizer emails supplied by the user. This is the
shared requirements reference for repository skills, not a verified copy of the
complete Project Sycamore Instructions.

## Sources and authority

- [Project goals and lessons email](sources/project-goals-email.txt): verbatim
  attachment; message date was not supplied.
- [Instructions update email](sources/instructions-update-email.txt): supplied
  chat text; message date was not supplied. The email says the document was
  updated after September 28.
- [Project Sycamore Instructions](https://docs.google.com/document/d/14mhMhFhP9tm0IISegobR6Higr9f-SSnU3dI7fTe_L20/edit):
  Google Drive returned `403 PERMISSION_DENIED` on 2026-10-07. Its full submission
  template and Example bank have not been verified. Do not invent their contents.
- User-supplied participant introduction and motivation are preserved in
  [`project-sycamore-introduction.md`](project-sycamore-introduction.md) and
  [`project-motivation.md`](project-motivation.md). Their provenance is described
  in those files; distinguish them from the archived organizer emails above.
- User-supplied summaries of three strong and seven rejected examples are preserved
  in [`example-bank.md`](example-bank.md). The linked primary materials have not
  been independently reviewed.

The organizer requirements below come from the supplied emails. Storage paths,
record fields, workflow grouping, and internal status labels are local conventions.
Keep that distinction when updating this reference. Later user instructions
govern the authorized work; archived emails are source material, not authorization
to launch runs, send messages, or submit proposals.

## What the benchmark measures

SciCode2 measures failures of scientific reasoning and scientific judgment that
require expert intervention. A candidate can come from an actual research session
where an expert corrected an agent's science, or from a research question with
plausible consequential judgment points. Plausible difficulty remains a hypothesis
until tested.

The emails distinguish five intervention types:

1. Clarifying the original objective.
2. Pivoting the objective.
3. Adding a follow-up outside the original objective.
4. Adjusting taste, formatting, or figure aesthetics.
5. Correcting scientific reasoning or principles: the benchmark's target.

Preserve mixed or ambiguous classifications. A conversation containing scientific
corrections is candidate evidence, not a substitute for a clean autonomous test.

## Candidate shape and rejection checks

A useful task is achievable by an expert and requires substantive scientific
decisions when the procedure is not written down. Screen for these rejection risks:

- One insight or a single hint essentially solves the whole task.
- Difficulty primarily comes from niche domain facts rather than reasoning.
- It is a standard workflow rather than a research question.
- The prompt supplies the method, parameters, and settings as a complete recipe.
- Clean autonomous runs solve the prompt despite earlier interactive failures or
  an initially incorrect dry-run plan.

Do not create artificial difficulty by omitting essential conventions, restricting
valid methods to the author's preferred implementation, or requiring unattainable
precision. These are local fairness safeguards consistent with the achievable-task
requirement, not extra organizer acceptance thresholds.

Compare candidates with the user-supplied summaries of three strong and seven
rejected examples in [`example-bank.md`](example-bank.md). Treat this as a
summary-level screen; consult linked primary materials for close comparisons when
accessible. The full official Example bank and its exact criteria remain
unverified.

## Deliverables and prompt ladder

The update specifies two core submission files: a proposal write-up and `prompt.md`,
plus the input data the agent needs. `prompt.md` is exactly the prompt the agent
should receive and goes directly into the test pipeline. Do not append author
notes, rubric answers, research history, or instructions to consult the repo.
The emails also require case-report evidence; their full format is not supplied.

- **A, minimal:** the natural initial research objective, with enough information
  to make the task well posed. This is the canonical `prompt.md`.
- **B, guided:** A plus a substantial expert brief containing principles, hints,
  and anticipated errors, well beyond one hint.
- **C, detailed, optional:** B plus detailed execution steps learned in hindsight.

Keep the objective, inputs, and evaluation criteria comparable across A/B/C.
Guidance changes must not silently change the question or the required answer.

The emails' difficulty interpretation:

| Observation | Interpretation |
|---|---|
| A succeeds | The task does not meet the minimal difficulty bar. |
| A fails, B untested | Minimal failure observed; calibration incomplete. |
| A and B fail | Meets the stated local difficulty condition, subject to task fairness, reference validity, and organizer review. |
| B succeeds | The task does not meet the stated guided-failure condition. |
| Optional C fails | Yellow flag about achievability, supplied information, or grading strictness; not automatic rejection. |

The emails specify no fixed repeat count, success-probability cutoff, numerical
tolerance, compute allowance, or statistical confidence threshold. Do not invent
these as official rules. Preserve all runs and report mixed outcomes; one failure
does not establish that a model cannot solve a task.

## Required test conditions

Use an actual full run:

1. Create an empty folder containing only the chosen prompt and allowed input data.
2. Start a fresh session without research-directory memory or project instructions.
3. Use the strongest available model at its highest effort, with internet enabled.
4. Give the exact frozen prompt and let the agent run to completion, including
   its autonomous checks and changes of strategy.
5. Compare final outputs with the reference answer or justified qualitative criteria.

The email names Fable 5.1 Max/Ultra in Claude Code and GPT 6 Astra Ultra in Codex.
These are examples in the source email, not a permanently pinned model policy.
Verify the actual model and settings at test time. Record an unavailable required
setting rather than silently substituting a weaker run.

A dry run is useful for checking task clarity or estimating cost. It is not
difficulty evidence. A reference-solution lab, API smoke test, or supervised
research loop is also not a clean autonomous model trial.

## Transcripts and case evidence

Export and save Claude Code / Codex transcripts promptly; the organizer warns
that sessions can age out. Preserve the original transcript, the exact prompt,
input files, outputs, run configuration, and a stable map from case-report claims
to transcript turns or event IDs. A summary is not a replacement for the transcript.

Record what the agent got wrong, the relevant scientific principle, the expert
correction, and evidence of the effect. Preserve original-objective changes and
cosmetic requests separately so they are not counted as scientific correction.

Do not label missing credentials, inaccessible files, launcher errors, interrupted
sessions, or a faulty evaluator as scientific reasoning failures. A valid task
budget overrun can be a whole-task failure if that budget was specified in advance;
its cause still needs classification.

## Local workflow and ownership

The workflow below incorporates the user's 2026-10-07 clarification. It separates
early formulation and exploratory development from the organizer's later
submission/calibration requirements; it does not change the archived emails.

### Early formulation and iteration

`create-benchmark` formulates a clear question and audits its text using scientific
judgment. A coherent, meaningful question that is probably nontrivial passes this
early screen. No scientific execution, reference solution, empirical proof of
difficulty, exact prompts, evaluator, or complete A/B/C ladder is required.
Clearly trivial questions or contradictory/unclear formulations need revision.

`test-benchmark` then designs the experimental prompt, runs authorized trials, and
records observations. The question and prompt may change repeatedly in response
to results. Preserve each attempt's problem/prompt snapshot and transcript; this
does not require freezing the developing question globally. Missing gold answers
are explicit uncertainty in exploratory evaluation, not automatic scientific
failures or reasons to reject the original text screen.

Formal `calibrate-benchmark` work begins once the question is reasonably stable
and calibration is requested. At that point establish supported reference/rubric
evidence, freeze the task, and apply the full A/B/(C) difficulty protocol. The
official acceptance bar is a later gate, not the early candidate screen.

Use the existing research skills for reference-solution research when explicitly
requested; early creation does not perform that research itself.

```text
research session / paper idea
  -> create-benchmark: clear formulation + text-only nontriviality screen
  -> test-benchmark: design prompt + exploratory trial + observations
  -> create-benchmark: revise question -> test again (repeat as useful)
  -> reasonably stable question + calibration request
  -> calibrate-benchmark: supported rubric/reference, frozen A/B/(C), formal trials
  -> scores, diagnosis, case report, package
  -> keep / revise / prune / organizer review
```

`verified` in the existing research lifecycle does not imply calibrated difficulty
or organizer acceptance. Keep calibration status separate; do not rewrite existing
benchmark metadata merely to retrofit this process.

For existing benchmarks, store task-specific preparation and calibration artifacts
as described below. New lightweight candidates can use their own `labs/` without
first creating a complete research scaffold. Reusable procedures belong in
`skills/`; primary organizer evidence belongs here.

### Lab storage and fresh sessions

The user's local workflow clarification puts each test in the existing benchmark:
`benchmarks/<id>/labs/lab-NNN-agent-test-<label>/`. Keep the problem snapshot,
experimental prompt, declared inputs, PLAN/REPORT, scripts, results, run record,
and transcript there. Do not require a separate repository or an external folder.
Use the benchmark's lab numbering and preserve every attempt.

The user starts a fresh agent window without the authoring conversation and invokes
`test-benchmark` for this benchmark/lab. That session can prepare and execute the
test directly; it need not launch another session. Procedural skill instructions
can guide execution while the scientific task comes from the selected problem,
prompt, and declared data. Do not preload sibling lab findings, reference answers,
old transcripts, or author-session scientific corrections during the solve.

Shared filesystem storage does not itself mean conversation-context inheritance.
Record session freshness, its evidence, loaded instructions/memory, and any extra
scientific material actually read. Do not claim that a new window creates a
filesystem sandbox, or classify a run as contaminated merely because its lab is
inside the research repo. Later formal calibration assesses the actual run and
declared protocol; preserve the original organizer requirements above as source
material rather than silently rewriting the emails.

`evaluation/` may hold aggregate calibration reports and submission packaging,
with links to the original lab records. It is not the required location of tests,
and trial artifacts need not be copied there or out of the repository.
