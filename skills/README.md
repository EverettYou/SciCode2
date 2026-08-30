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
