# SciCode2

SciCode2 turns reviewed papers into long-horizon computational-research benchmarks.

Start with the [global wiki](wiki/index.md) for the project map, research strategy, knowledge architecture, workflows, papers, benchmarks, talk, and reusable skills. Use the local [dashboard](dashboard/README.md) to browse and edit the live workspace.

Canonical catalogs remain in [`papers/papers.yml`](papers/papers.yml) and [`benchmarks/benchmarks.yml`](benchmarks/benchmarks.yml). Detailed operational contracts remain with the resources that own them; the wiki connects and summarizes those resources without duplicating them.

The organizer's [proposal and difficulty requirements](docs/scicode2/requirements.md)
are archived separately from the research workflow. Use the [benchmark preparation,
testing, and calibration skills](skills/README.md#proposal-testing-and-calibration)
to turn research candidates into measured benchmark proposals.

The participant-facing [Project Sycamore introduction](docs/scicode2/project-sycamore-introduction.md)
records the project's purpose, expected researcher–AI collaboration, and iterative
workflow. Read it alongside the organizer requirements before starting candidate work.
The [motivation and task-design principles](docs/scicode2/project-motivation.md)
and [strong and rejected example summaries](docs/scicode2/example-bank.md) preserve
additional project context for candidate screening.

## Development environment

This repository is managed as a uv project. Install the locked dependencies and create the local `.venv` with:

```bash
uv sync
```

Run project commands through uv so they use the managed environment, for example:

```bash
uv run python dashboard/server.py
```

Commit both [`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock); `.venv/` is local-only.

Each folder under `benchmarks/` is a separate nested uv project with its own `pyproject.toml`, `uv.lock`, and `.venv`. The root environment is for dashboard and repository tooling; benchmark environments are for experiment-specific numerical stacks. They intentionally do not inherit root `site-packages`, because that would make imports depend on untracked ambient state. Run benchmark commands from the benchmark directory or use `uv --project benchmarks/<benchmark-id> ...`.

The project-level [`.tmp/`](.tmp/README.md) directory is reserved for short-lived staging used by paper downloads and benchmark creation. Its per-operation subdirectories are ignored and cleaned after each run; the directory itself remains visible as the shared temporary workspace.

## LLM-assisted tooling

API-assisted workflows load `OPENAI_API_KEY` from the ignored project `.env` and keep generated caches and credential-free usage records under `.tmp/`. The shared runtime uses stateless OpenAI Responses calls with strict Structured Outputs and content fingerprints, so unchanged evidence is served from the local cache. Individual workflows may select a model with their own environment variable and otherwise fall back to `OPENAI_MODEL`.

Wiki structure is always checked offline. To add the advisory semantic review:

```bash
uv run python skills/wiki-lint/scripts/lint_wiki.py . --semantic
```

Set `OPENAI_SEMANTIC_LINT_MODEL` to override the semantic-lint model. `OPENAI_API_TIMEOUT_SECONDS` and `OPENAI_API_MAX_RETRIES` configure the shared client. Use `--semantic-limit 5` for a small live smoke test; semantic findings report review candidates and never edit Wiki files.
