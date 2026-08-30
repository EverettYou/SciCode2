# Paper to Benchmark Dashboard

This local dashboard has two linked catalogs:

- **Papers:** all records in `papers/papers.yml`, enriched by optional `papers/<paper-id>/assessment.yml` files.
- **Benchmarks:** all records in `benchmarks/benchmarks.yml`, enriched by `benchmarks/<benchmark-id>/metadata.yml` details and cited `paper_ids`.
- **Wiki:** project and cross-paper knowledge compiled under root `wiki/`, with searchable pages, backlinks, source references, and links into papers and benchmark workspaces.

Paper processing labels are derived automatically:

`listed → fetched → assessed → reviewed`

- `listed`: publication metadata exists, but the paper files have not been fetched.
- `fetched`: local paper files exist, but no `assessment.yml` exists.
- `assessed`: an AI-generated or provisional `assessment.yml` exists.
- `reviewed`: the assessment has been manually corrected and its `stage` is `reviewed`; the paper is ready to inform benchmark design. Benchmark citations remain visible as paper–benchmark links, not as a separate paper stage.

Assessed papers receive a transparent 0–100 suitability score derived from the seven dimensions in `assessment.yml`. Individual ratings remain visible because the score is a sorting aid, not a scientific conclusion.

## Layout

The dashboard keeps page, static, backend, test, and validation concerns separate:

```text
dashboard/
├── frontend/pages/             # browser entry pages
├── frontend/static/css/        # shared styles
├── frontend/static/js/         # page and shared browser code
├── frontend/static/generated/  # generated catalog data
├── backend/               # FastAPI application and domain services
├── tests/                 # backend unit tests
└── scripts/               # dashboard maintenance checks
```

The public routes remain stable: `/`, `/papers.html`, `/paper.html`,
`/benchmarks.html`, `/benchmark.html`, `/wiki.html`, `/talk.html`,
`/document.html`, and `/code.html`. This preserves existing links while the
files are organized internally.

Regenerate the data after editing publication, paper, or benchmark metadata:

```bash
uv run python skills/assess-paper/scripts/build_dashboard_data.py
```

Regenerate the data and serve it locally from the repository root:

```bash
uv run ./run_dashboard.sh
```

The launcher runs the server with `nohup`, records its PID under `.tmp/`, and writes persistent output to `.tmp/dashboard-8000.log`. It returns the terminal prompt after startup and keeps the local website running if that terminal disconnects. Manage it with:

```bash
./run_dashboard.sh status
./run_dashboard.sh logs
./run_dashboard.sh restart
./run_dashboard.sh stop
```

`status` distinguishes a **current** dashboard from a **stale** one. A stale
dashboard still owns its port, but its backend entry point or service modules
have changed since it started. Running `./run_dashboard.sh start` then safely
restarts that tracked process with the current code. If another application
owns the port, the launcher reports its PID and command rather than replacing it
silently. A dashboard process from this project whose state file is missing is
recognized and refreshed automatically. To explicitly replace an unrelated
process, use `./run_dashboard.sh start --takeover` (or
`./run_dashboard.sh stop --takeover`).

Open <http://localhost:8000>. To use another port, prefix both launch and management commands with `SCICODE_DASHBOARD_PORT=<port>`. The home page summarizes the inventory and shows the derived project knowledge graph; use the navigation bar to switch among Papers, Benchmarks, Wiki, and Talk.

## Shared page shell

`frontend/static/js/site-shell.js` renders the site header and navigation from one
source on every dashboard path. Each page in `frontend/pages/` contains exactly one
`<div id="site-header"></div>` mount and loads the shared script. Run:

```bash
python3 dashboard/scripts/validate_shell.py
```

The validator rejects missing mounts or scripts and page-local headers—the failure modes that would split ownership of the shell again. Opening an HTML file directly uses `redirect-to-dashboard.js` to reach the local dashboard server, but the shell also renders when the page is served statically.

The Wiki page renders root `wiki/*.md` through read-only local API routes. Its graph and backlinks are derived from wikilinks, `source_refs`, paper IDs, and benchmark metadata rather than a separately maintained graph file.

The home-page knowledge graph uses four relevance signals: direct wikilinks (×8), shared source overlap (×2), Adamic–Adar common-neighbor relevance (×1.5), and page-type affinity (×0.25). Louvain detection supplies communities and cohesion scores. The renderer preserves a readable backbone, then uses a bounded 1.75 × node-count edge budget to add authored direct links that close local loops and bridge communities; direct links are solid and inferred relevance links are dashed. It caches deterministic positions, sizes nodes by weighted degree, and supports type/community coloring, pan, and zoom. Graph insights are limited to actionable signals: predicted connections have no authored wikilink but do have provenance or common-neighbor evidence, while anomaly cards identify isolated nodes, fragile single-edge community bridges, unsupported authored bridges, and community outliers for review.

When `OPENAI_API_KEY` is available to the server, community names are generated from bounded evidence packets containing shared title phrases, controlled scientific or project topics, all member titles, compact summaries, page types, and graph centrality. The model returns one strict structured label per community. Results are cached in `.tmp/community-labels.json` by model, prompt version, and evidence fingerprint, so unchanged communities do not incur another request. `OPENAI_COMMUNITY_NAMING_MODEL` selects the model (default `gpt-5.6`) and `OPENAI_API_TIMEOUT_SECONDS` controls the request timeout. Missing credentials, API failures, and invalid labels fall back to deterministic local naming.

`GET /api/wiki/search?q=<query>&scope=global` provides token+graph retrieval. It ranks lexical matches and then propagates relevance across one graph hop; raw wiki pages and their citations remain the evidence layer.

## Natural-language catalog search

The Papers and Benchmarks search bars use progressive enhancement without a separate AI control:

1. each keystroke immediately applies the local exact and substring search;
2. after a 350 ms pause, `GET /api/catalog/search` merges lexical rank with cosine similarity from locally cached OpenAI embeddings;
3. a longer query containing constraints such as stage, feasibility, validation, inclusion, or exclusion is automatically refined over only the top 20 candidates with a strict Structured Outputs response.

The semantic index is compiled from publication metadata, available assessment fields, benchmark metadata, and the current benchmark-thesis summary. PDFs and full Markdown files are not sent on each search. Document vectors are stored as a contiguous float32 matrix in `.tmp/catalog-search-vectors.npy`, with fingerprints and row mappings in `.tmp/catalog-search-metadata.json`; repeated complex-query refinements are fingerprint-cached separately, and API usage is appended to `.tmp/llm-usage.jsonl`. API or network failures leave the immediate local search usable.

Configuration defaults are `text-embedding-3-small` at its native 1536 dimensions and `gpt-5.6-luna` for constrained-query refinement. Override them with `OPENAI_SEARCH_EMBEDDING_MODEL`, `OPENAI_SEARCH_EMBEDDING_DIMENSIONS`, and `OPENAI_SEARCH_MODEL` in the ignored project `.env`.

Because the first index build sends the compact catalog fields described above to OpenAI, semantic catalog search is disabled until that data flow is explicitly approved. Set `OPENAI_CATALOG_SEARCH_ENABLED=true` in `.env` to opt in. Without it, the endpoint returns an unavailable response and the browser silently retains first-layer local search.

## Benchmark research workspace

Click a benchmark title to open `benchmark.html?id=<benchmark-id>`. The detail page is the benchmark's scientific control surface, assembled from canonical benchmark files rather than a second metadata copy:

- the header and research brief expose the central question, scope, source papers, and full task;
- the workflow strip shows framing, knowledge search, active experiment, and distillation state;
- the current thesis and idea frontier show what is presently believed, competing branches, and keep/prune gates;
- the active lab exposes its objective, execution sequence, completion criteria, stop conditions, and report/plan links;
- the evidence contract keeps expected hypotheses distinct from the checks required before making claims;
- the action rail shows the next decisive action, research artifact counts, resource envelope, workspace links, and a compact decisions/blockers inbox.

The benchmark API derives this view from `README.md`, `metadata.yml`, `problem/TASK.md`, local wiki pages, lab reports/plans, stable-source files, and project-root talk threads. The talk remains a separate supervision surface at `talk.html`; it is intentionally secondary on the benchmark page.

## Project talk

The talk retains the chat-style split view for durable user–agent supervision. Threads may be opened by either actor, replies append to canonical project-root Markdown, user messages support audited edit/retract operations, and only users close or reopen threads. Benchmark pages link only the few open decisions and blockers back to this full conversation surface.

## Paper workspace

Clicking a paper title opens `paper.html?id=<paper-id>`. The page shows source links, ratings, task types, assessment, follow-up ideas, pitfalls, and a local PDF viewer when `paper.pdf` is available.

Use the workspace as an inventory and light editor:

- Click a rating or processing label to select a controlled-vocabulary value.
- Click an assessment card to copy its paper ID, context type, and text for pasting into Codex; copied context ends with `---`.
- Click a benchmark ID in the benchmark list or detail header to copy it for the same context workflow.
- Double-click an assessment card to edit it in place; it saves on blur.
- Drag the handle on a saved follow-up idea or potential pitfall to reorder that list; the new order saves on drop.
- Use `+` to create a follow-up or pitfall draft, and `×` to remove an item after confirmation.
- Long Follow-up ideas and Potential pitfalls lists have their own vertical scroll area.

The dashboard preserves metadata revisions under `papers/<paper-id>/history/` when inline edits are saved. Use Codex for substantive scientific discussion and for changes requiring paper-level reasoning; the authoritative editing protocol is in the repository [`README.md`](../README.md#paper-assessment-workflow).
