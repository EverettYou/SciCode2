# Code-source ingest

Use for immutable repository snapshots under benchmark `problem/repos/`, code artifacts cited by completed labs, and canonical code resources explicitly selected for global project knowledge.

## Read order

1. Adjacent provenance YAML and repository license.
2. README, documentation, manifests, lockfiles, and environment definitions.
3. Entrypoints, public APIs, core modules, configurations, and data-flow boundaries.
4. Tests, examples, numerical checks, and error handling.
5. Only then, supporting modules needed to verify architecture or algorithm details.

Ignore vendored dependencies, generated files, caches, binaries, and bulk data unless they are scientifically consequential.

## Compile into the wiki

Extract architecture, interfaces, algorithms, dependency assumptions, numerical conventions, defaults, supported regimes, tests, known gaps, and failure modes. Create `implementations/` pages for durable components or end-to-end systems; use `methods/` for the underlying scientific/computational method. Link them bidirectionally.

Register the repository in `sources.yml`, then cite exact raw files with a symbol, class/function, configuration key, test name, commit, or stable line locator using a standard Markdown link, for example `[Repository, `src/solver.py · solve_local`](../../papers/example-paper/repo/src/solver.py#solve_local)`. Do not paste large code blocks into the wiki; summarize behavior and link to the canonical raw file.

Static inspection establishes what code appears to do, not that it is correct. Mark runtime or scientific behavior as unverified until supported by repository tests or a benchmark lab. Explicitly record mismatches between paper descriptions, code defaults, and tested behavior.
