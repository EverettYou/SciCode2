---
name: wiki-lint
description: Audit SciCode2's global or benchmark wiki for structural integrity and knowledge health. Use after wiki ingest, before wiki-based design or research, or when checking broken links, orphan pages, missing provenance, stale or contradictory claims, index drift, source coverage, cross-scope boundaries, and unresolved knowledge gaps.
---

# Wiki Lint

Check both what can be validated mechanically and what requires scientific judgment. Lint reports problems; it does not erase disagreements to make the wiki look consistent.

## Workflow

1. Read `wiki/SCHEMA.md` and [references/lint-rules.md](references/lint-rules.md).
2. Run:

   ```bash
   python3 skills/wiki-lint/scripts/lint_wiki.py <project-root-or-benchmark-directory>
   ```

   Add `--semantic` for the optional OpenAI-backed knowledge-health review. This mode loads
   `OPENAI_API_KEY` from the project `.env`, uses `OPENAI_SEMANTIC_LINT_MODEL` (falling back
   to `OPENAI_MODEL` and then `gpt-5.6-luna`), and caches strict structured results under
   `.tmp/`. Use `--semantic-limit N` for a bounded smoke test and `--semantic-refresh` only
   when the same evidence should be reviewed again intentionally.

3. Review structural findings: required files, page-format fields, broken or ambiguous Markdown/Obsidian links, including claim citations in the portable `[readable label](relative-path#locator)` form, missing indexed pages, orphan compiled pages, duplicate titles, malformed `sources.yml` entries, and malformed log entries. Reject citation syntaxes that require a source-ID resolver, including backticked or bare `global:...`, `benchmark:...`, and `source:...` IDs outside fenced code examples. For benchmark scope, also check unregistered raw inputs and completed labs. For global scope, check that sources resolve outside `wiki/` and project summaries link to the resources that own their details.
4. Audit semantic health: unsupported claims, contradictions hidden by overwrites, stale thesis statements, concepts mentioned repeatedly without pages, missing inverse links where useful, registered sources that did not change durable synthesis, and high-value gaps. The semantic mode supplies bounded page, neighbor-summary, and provenance packets to the model. Treat every finding as a review candidate rather than established fact.
5. Classify each finding as error, warning, or research opportunity. Cite exact paths. Route findings requiring scientific judgment, ambiguous merges, or prioritization to `$consult-human` as individual threads.

## Fix boundary

Automatically fix only clearly mechanical problems when the user asks: index omissions, link spelling, formatting, or missing reciprocal navigation. Do not automatically resolve scientific contradictions, merge concept pages with distinct meanings, change confidence, or rewrite the thesis. Route substantive corrections through `$wiki-ingest` with source evidence.

## Completion

Report structural status, knowledge-health findings, source coverage, and the highest-value maintenance or research actions as a numbered list with suggested fixes. A zero-error structural result does not imply that the wiki is scientifically complete.

Semantic findings do not change the command exit status and never modify the wiki. API or configuration failures do return a distinct failure because an explicitly requested review did not complete. Token usage is appended to `.tmp/llm-usage.jsonl` without credentials or source text.
