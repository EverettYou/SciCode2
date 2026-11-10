# SciCode2 Reusable Skills

This folder contains reusable workflows for designing, validating, and packaging SciCode2 benchmarks. It is part of the overall SciCode2 project, not part of any individual benchmark.

## What belongs here

Add a skill when a workflow is useful across multiple problems and has a stable interface, such as:

- generating or checking reference outputs;
- running convergence and resolution studies;
- testing physical invariants and limiting cases;
- estimating workstation resource requirements;
- compiling project resources and research sources into the global or a benchmark wiki;
- querying global, benchmark, or combined wiki scope for cited synthesis, research ideas, and next experiments;
- linting either wiki scope for structure, provenance, coverage, and consistency;
- coordinating symmetric user–agent supervision through one persistent Markdown file per talk thread;
- distilling supported research into `src/` and a final LaTeX note;
- auditing reproducibility and provenance.

`auto-research` is the top-level unattended coordinator. It reconciles bounded research and supervisor-synthesis schedules, delegates wiki operations to the focused wiki skills, preserves loop state, detects stagnation, and routes consequential judgment through `consult-human`.

`process-talk` is the bidirectional project discussion workflow. It processes user-authored requests, explains agent questions that are waiting on the user, and supports explicitly authorized replies on the user's behalf while preserving the thread audit trail.

One-off utilities should remain in the relevant benchmark’s `scripts/` directory.

## Proposal, testing, and calibration

The shared [organizer requirements](../docs/scicode2/requirements.md) distinguish
the benchmark's scientific-judgment target and difficulty gate from research
development. These repository skills define the reusable workflow:

| Skill | Inputs and outputs |
|---|---|
| [create-benchmark](create-benchmark/SKILL.md) | Clear problem formulation and a text-only coherence/nontriviality screen; likely nontrivial is enough to pass to testing. |
| [test-benchmark](test-benchmark/SKILL.md) | Prompt design and authorized trials in benchmark-local labs from a fresh user-opened session, with durable evidence and question-revision feedback; also executes later formal trials. |
| [calibrate-benchmark](calibrate-benchmark/SKILL.md) | Once the question is stable and calibration is requested: supported rubric/reference, frozen A/B/C, formal difficulty assessment, case report and package. |

Use existing research and wiki skills to build the reference answer. Reference
research labs and the `verified` lifecycle stage do not by themselves establish
autonomous-model difficulty; agent-test labs record the actual trials. Optional
dry runs check clarity; acceptance calibration requires full runs. The new skills
are procedural first versions, not an implemented cross-client launch/export
service. Actual execution must verify the available client's capabilities.

The development cycle is formulate → test → revise the question → test again.
Early creation does not conduct the research, engineer every prompt, or require
a complete reference answer. Prompt design belongs to
[experimental testing](test-benchmark/references/prompt-design.md). Each trial is
snapshotted, while the overall question remains open to revision. Freeze the task
for calibration after development, not at the initial text screen.

Tests use `benchmarks/<id>/labs/lab-NNN-agent-test-<label>/`, including PLAN,
REPORT, prompt, question snapshot, inputs, scripts, results, transcript, and run
records. The user opens a fresh window without authoring context and calls the
test skill there. No external workspace is required. Session/context independence
is recorded separately from file location; do not preload prior scientific answers.
Aggregate calibration packaging may remain in `evaluation/`, linked to these labs.

Optional [repository organization](create-benchmark/references/research-workspace.md)
can accompany creation when requested. Detailed
[reference research/lab design](auto-research/references/research-workspace.md)
belongs to later explicitly requested research work. The former `prepare-benchmark`
entry remains merged into create-benchmark; no additional preparation skill is needed.

The root [AGENTS.md](../AGENTS.md) routes repository agents to these files when
they are absent from the session's skill catalog. This does not install them
globally or make them available in an unrelated workspace.

## Recommended skill layout

```text
skills/
└── <skill-name>/
    ├── SKILL.md                  # purpose, inputs, workflow, and outputs
    ├── scripts/                  # executable implementation
    ├── assets/                   # optional output templates and boilerplate
    ├── references/               # optional methodological notes
    └── tests/                    # smoke tests and example fixtures
```

Use lowercase kebab-case names. Keep each skill narrowly scoped, document assumptions and dependencies, and include a small example or smoke test.
