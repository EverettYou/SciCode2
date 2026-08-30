#!/usr/bin/env python3
"""Lint a SciCode2 global or benchmark wiki for deterministic structural issues."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from scripts.llm import LLMConfigurationError, LLMSettings, StructuredLLM
from semantic_wiki_lint import semantic_lint


LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
WIKILINK_PATTERN = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
NONPORTABLE_CITATION_PATTERN = re.compile(
    r"\[@[a-z][a-z0-9_-]*:[a-z0-9][a-z0-9_-]*(?:,\s*[^\]]+)?\]|\(source:\s*[^)]+\)",
    re.IGNORECASE,
)
RESOLVER_CITATION_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:global|benchmark|source):[A-Za-z0-9][A-Za-z0-9_.:-]*",
    re.IGNORECASE,
)
LOG_PATTERN = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (ingest|query|lint) \| .+$")
REQUIRED_WIKI_FILES = ("SCHEMA.md", "index.md", "thesis.md", "log.md", "sources.yml")
SPECIAL_FILES = {"SCHEMA.md", "index.md", "log.md"}
REQUIRED_FRONTMATTER = {"title", "page_type", "status", "updated", "source_refs", "idea_ids"}
TOPIC_PAGE_TYPES = {"concept", "method", "comparison", "model", "implementation"}
TOPICS = {
    "Correlated Systems",
    "Topological Phases",
    "Quantum Information",
    "Machine Learning",
}
PROJECT_TOPICS = {
    "Agentic Research Infrastructure",
    "Autonomous Research Workflows",
    "Research Knowledge Systems",
    "Computational Benchmark Design",
    "Human-in-the-Loop Research",
}
PAGE_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    data = yaml.safe_load(text[4:end])
    return data if isinstance(data, dict) else None


def linkable_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`]*`", "", text)


def text_without_fenced_code(path: Path) -> str:
    """Keep inline citation-like text while excluding literal fenced examples."""
    text = path.read_text(encoding="utf-8")
    return re.sub(r"^(?:```|~~~).*?^(?:```|~~~)\s*$", "", text, flags=re.DOTALL | re.MULTILINE)


def resolver_citation_ids(path: Path) -> list[str]:
    """Return nonportable source IDs that require a resolver to become citations."""
    return RESOLVER_CITATION_PATTERN.findall(text_without_fenced_code(path))


def local_links(path: Path) -> list[str]:
    links = []
    for target in LINK_PATTERN.findall(linkable_text(path)):
        target = target.strip().split("#", 1)[0].split("?", 1)[0]
        if target and not re.match(r"^[a-z]+://|^mailto:", target):
            links.append(target)
    return links


def local_link_path(page: Path, target: str, project_root: Path) -> Path:
    """Resolve filesystem links and validated dashboard-root HTML routes."""
    if re.fullmatch(r"/[a-z][a-z0-9-]*\.html", target):
        return project_root / "dashboard" / "frontend" / "pages" / target.removeprefix("/")
    return (page.parent / target).resolve()


def wikilinks(path: Path) -> list[str]:
    links = []
    for body in WIKILINK_PATTERN.findall(linkable_text(path)):
        target = body.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target)
    return links


def lint(scope: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    wiki = scope / "wiki"
    benchmark_scope = (scope / "metadata.yml").is_file() and scope.parent.name == "benchmarks"
    project_root = scope.parent.parent if benchmark_scope else scope

    def source_exists(ref: str) -> bool:
        if re.match(r"^https?://", ref):
            return True
        raw = Path(ref.split("#", 1)[0])
        if raw.is_absolute() or ".." in raw.parts:
            return False
        root = project_root if benchmark_scope and ref.startswith("wiki/") else scope
        return (root / raw).exists()
    if not wiki.is_dir():
        return ["missing wiki/ directory"], warnings

    for name in REQUIRED_WIKI_FILES:
        if not (wiki / name).is_file():
            errors.append(f"missing wiki/{name}")

    pages = sorted(wiki.rglob("*.md"))
    relative_pages = {path.relative_to(wiki) for path in pages}
    inbound: Counter[Path] = Counter()
    outgoing: defaultdict[Path, list[Path]] = defaultdict(list)
    titles: defaultdict[str, list[Path]] = defaultdict(list)

    for page in pages:
        rel = page.relative_to(wiki)
        if rel.as_posix() not in SPECIAL_FILES:
            if not PAGE_NAME_PATTERN.fullmatch(page.name):
                errors.append(f"wiki page filename must use lowercase kebab-case: wiki/{rel}")
            text = page.read_text(encoding="utf-8")
            if NONPORTABLE_CITATION_PATTERN.search(linkable_text(page)):
                errors.append(
                    f"nonportable citation syntax in wiki/{rel}; use [readable label](relative-path#locator)"
                )
            resolver_ids = sorted(set(resolver_citation_ids(page)), key=str.casefold)
            if resolver_ids:
                errors.append(
                    f"resolver-style source ID in wiki/{rel}: {', '.join(resolver_ids)}; "
                    "use [readable label](relative-path#locator)"
                )
            data = frontmatter(page)
            if data is None:
                errors.append(f"missing or invalid frontmatter: wiki/{rel}")
            else:
                missing = sorted(REQUIRED_FRONTMATTER - data.keys())
                if missing:
                    errors.append(f"missing frontmatter fields in wiki/{rel}: {', '.join(missing)}")
                title = data.get("title")
                if isinstance(title, str) and title.strip():
                    titles[title.strip().casefold()].append(rel)
                updated = data.get("updated")
                if not isinstance(updated, (str, date)) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(updated)):
                    warnings.append(f"missing or invalid updated date: wiki/{rel}")
                refs = data.get("source_refs")
                if not isinstance(refs, list) or not refs:
                    warnings.append(f"no raw source_refs: wiki/{rel}")
                else:
                    for ref in refs:
                        if not isinstance(ref, str) or not ref.strip():
                            errors.append(f"invalid source_ref in wiki/{rel}")
                            continue
                        if not source_exists(ref):
                            errors.append(f"unresolved raw source_ref in wiki/{rel}: {ref}")
                if data.get("page_type") in TOPIC_PAGE_TYPES:
                    topics = data.get("topics")
                    if not isinstance(topics, list) or not 1 <= len(topics) <= 3 or not all(
                        isinstance(topic, str) and topic in TOPICS for topic in topics
                    ):
                        errors.append(f"topic-indexed page needs one to three controlled topics in wiki/{rel}")
                if data.get("page_type") == "project":
                    project_topics = data.get("project_topics")
                    if not isinstance(project_topics, list) or not 1 <= len(project_topics) <= 3 or not all(
                        isinstance(topic, str) and topic in PROJECT_TOPICS for topic in project_topics
                    ):
                        errors.append(f"project page needs one to three controlled project_topics in wiki/{rel}")

            for marker in ("**Summary**:", "**Sources**:", "**Last updated**:", "## Related pages"):
                if marker not in text:
                    errors.append(f"missing visible page field '{marker}' in wiki/{rel}")


        for target in local_links(page):
            resolved = local_link_path(page, target, project_root)
            try:
                target_rel = resolved.relative_to(wiki.resolve())
            except ValueError:
                if not resolved.exists():
                    errors.append(f"broken local link in wiki/{rel}: {target}")
                continue
            if resolved.is_dir():
                resolved = resolved / "index.md"
                target_rel = resolved.relative_to(wiki.resolve())
            if not resolved.is_file():
                errors.append(f"broken wiki link in wiki/{rel}: {target}")
            elif target_rel in relative_pages:
                inbound[target_rel] += 1
                outgoing[rel].append(target_rel)

        for target in wikilinks(page):
            raw_target = Path(target)
            if raw_target.is_absolute() or ".." in raw_target.parts:
                errors.append(f"unsafe Obsidian wikilink in wiki/{rel}: [[{target}]]")
                continue
            if target.startswith("wiki/") and benchmark_scope:
                project_root = scope.parent.parent
                external = project_root / (target if raw_target.suffix == ".md" else f"{target}.md")
                if not external.is_file():
                    errors.append(f"broken global wikilink in wiki/{rel}: [[{target}]]")
                continue
            if target.startswith("benchmarks/") and "/wiki/" in target and not benchmark_scope:
                external = scope / (target if raw_target.suffix == ".md" else f"{target}.md")
                if not external.is_file():
                    errors.append(f"broken benchmark wikilink in wiki/{rel}: [[{target}]]")
                continue
            if "/" in target:
                target_rel = raw_target if raw_target.suffix == ".md" else raw_target.with_suffix(".md")
                candidates = [target_rel] if target_rel in relative_pages else []
            else:
                stem = raw_target.stem
                candidates = [candidate for candidate in relative_pages if candidate.stem == stem]
            if not candidates:
                errors.append(f"broken Obsidian wikilink in wiki/{rel}: [[{target}]]")
            elif len(candidates) > 1:
                errors.append(
                    f"ambiguous Obsidian wikilink in wiki/{rel}: [[{target}]] -> "
                    + ", ".join(map(str, candidates))
                )
            else:
                inbound[candidates[0]] += 1
                outgoing[rel].append(candidates[0])

    for title, paths in titles.items():
        if len(paths) > 1:
            errors.append(f"duplicate wiki title '{title}': " + ", ".join(map(str, paths)))

    indexed: set[Path] = set()
    frontier = [Path("index.md")]
    while frontier:
        current = frontier.pop()
        for target in outgoing.get(current, []):
            if target not in indexed:
                indexed.add(target)
                frontier.append(target)
    for rel in sorted(relative_pages):
        if rel.as_posix() in SPECIAL_FILES:
            continue
        if rel not in indexed:
            warnings.append(f"page unreachable from wiki/index.md: wiki/{rel}")
        if inbound[rel] == 0:
            warnings.append(f"orphan wiki page: wiki/{rel}")

    registry_path = wiki / "sources.yml"
    registered_paths: list[str] = []
    if registry_path.is_file():
        try:
            registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            registry = None
            errors.append(f"invalid wiki/sources.yml YAML: {error}")
        if not isinstance(registry, dict) or registry.get("version") != 1:
            errors.append("wiki/sources.yml must be a version 1 mapping")
        sources = registry.get("sources") if isinstance(registry, dict) else None
        if not isinstance(sources, list):
            errors.append("wiki/sources.yml must contain a sources list")
            sources = []
        source_ids: set[str] = set()
        source_paths: set[str] = set()
        for position, source in enumerate(sources):
            label = f"wiki/sources.yml sources[{position}]"
            if not isinstance(source, dict):
                errors.append(f"{label} must be a mapping")
                continue
            source_id = source.get("source_id")
            if not isinstance(source_id, str) or not source_id.strip() or any(
                character.isspace() for character in source_id
            ):
                errors.append(f"{label}.source_id must be non-empty and contain no whitespace")
            elif source_id in source_ids:
                errors.append(f"duplicate source_id in wiki/sources.yml: {source_id}")
            else:
                source_ids.add(source_id)
            if source.get("kind") not in {"paper", "repository", "lab", "query", "project", "skill", "talk", "other"}:
                errors.append(f"{label}.kind is unsupported")
            raw_value = source.get("path")
            if not isinstance(raw_value, str) or not raw_value.strip():
                errors.append(f"{label}.path must be non-empty text")
            else:
                raw = Path(raw_value)
                unsafe_boundary = (
                    benchmark_scope and not raw_value.startswith(("wiki/", "labs/", "problem/"))
                ) or (not benchmark_scope and raw_value.startswith("wiki/"))
                if raw.is_absolute() or ".." in raw.parts or unsafe_boundary:
                    errors.append(f"unsafe source path in {label}: {raw_value}")
                elif not (project_root if benchmark_scope and raw_value.startswith("wiki/") else scope / raw).exists():
                    errors.append(f"unresolved source path in {label}: {raw_value}")
                elif raw_value in source_paths:
                    errors.append(f"duplicate source path in wiki/sources.yml: {raw_value}")
                else:
                    source_paths.add(raw_value)
                    registered_paths.append(raw_value)
            revision = source.get("revision")
            if not isinstance(revision, str) or not revision.strip():
                errors.append(f"{label}.revision must be non-empty text")
            ingested_at = source.get("ingested_at")
            if not isinstance(ingested_at, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", ingested_at
            ):
                errors.append(f"{label}.ingested_at must be a UTC timestamp")
            updated_pages = source.get("updated_pages")
            if not isinstance(updated_pages, list) or not updated_pages:
                errors.append(f"{label}.updated_pages must be a non-empty list")
            else:
                for updated_page in updated_pages:
                    if not isinstance(updated_page, str):
                        errors.append(f"invalid updated page in {label}")
                        continue
                    page_path = Path(updated_page)
                    if (
                        page_path.is_absolute()
                        or ".." in page_path.parts
                        or not updated_page.startswith("wiki/")
                        or page_path.suffix != ".md"
                        or not (scope / page_path).is_file()
                        ):
                            errors.append(f"unresolved updated page in {label}: {updated_page}")

    log = wiki / "log.md"
    if log.is_file():
        headings = [line for line in log.read_text(encoding="utf-8").splitlines() if line.startswith("## [")]
        for heading in headings:
            if not LOG_PATTERN.fullmatch(heading):
                errors.append(f"malformed wiki log heading: {heading}")

    if not benchmark_scope:
        return errors, warnings

    for report in sorted((scope / "labs").glob("lab-*/REPORT.md")):
        text = report.read_text(encoding="utf-8")
        metadata = frontmatter(report) or {}
        completed = str(metadata.get("status") or "").casefold() in {"complete", "completed"}
        if completed or re.search(r"^- Status:\s*(complete|completed)\s*$", text, re.MULTILINE | re.IGNORECASE):
            rel = report.relative_to(scope).as_posix()
            if rel not in registered_paths:
                warnings.append(f"completed lab report not registered in wiki/sources.yml: {rel}")

    return errors, warnings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scope", type=Path)
    parser.add_argument(
        "--semantic",
        action="store_true",
        help="run the optional cached LLM knowledge-health review after structural lint",
    )
    parser.add_argument(
        "--semantic-model",
        help="override OPENAI_SEMANTIC_LINT_MODEL for this run",
    )
    parser.add_argument(
        "--semantic-limit",
        type=int,
        help="review only the first N semantic pages (useful for a smoke test)",
    )
    parser.add_argument(
        "--semantic-refresh",
        action="store_true",
        help="ignore cached semantic results and call the model again",
    )
    args = parser.parse_args()
    if args.semantic_limit is not None and args.semantic_limit < 1:
        parser.error("--semantic-limit must be at least 1")
    scope = args.scope.resolve()
    errors, warnings = lint(scope)
    for message in errors:
        print(f"ERROR: {message}")
    for message in warnings:
        print(f"WARNING: {message}")
    print(f"Wiki lint: {len(errors)} error(s), {len(warnings)} warning(s)")

    if args.semantic:
        if errors:
            print("SEMANTIC SKIPPED: fix structural errors before semantic review")
        else:
            project_root = scope.parent.parent if (scope / "metadata.yml").is_file() else scope
            try:
                settings = LLMSettings.from_project(
                    project_root,
                    model_env="OPENAI_SEMANTIC_LINT_MODEL",
                )
                if args.semantic_model:
                    settings = LLMSettings(
                        api_key=settings.api_key,
                        model=args.semantic_model,
                        timeout_seconds=settings.timeout_seconds,
                        max_retries=settings.max_retries,
                    )
                relative_scope = scope.relative_to(project_root)
                scope_key = "global" if relative_scope == Path(".") else relative_scope.as_posix()
                cache_key = re.sub(r"[^a-zA-Z0-9_.-]+", "-", scope_key)
                llm = StructuredLLM(
                    settings,
                    cache_path=project_root / ".tmp" / f"semantic-wiki-lint-{cache_key}.json",
                    usage_path=project_root / ".tmp" / "llm-usage.jsonl",
                )
                findings, stats = semantic_lint(
                    scope,
                    llm,
                    limit=args.semantic_limit,
                    refresh=args.semantic_refresh,
                    progress=lambda current, total: print(
                        f"Semantic lint: reviewing batch {current}/{total}...", flush=True
                    ),
                )
            except LLMConfigurationError as error:
                print(f"SEMANTIC ERROR: {error}")
                raise SystemExit(2) from error
            except Exception as error:
                print(f"SEMANTIC ERROR: {type(error).__name__}: {error}")
                raise SystemExit(2) from error

            for finding in findings:
                print(
                    f"SEMANTIC {finding['severity'].upper()} [{finding['confidence']:.2f}] "
                    f"{finding['path']}:{finding['line']} {finding['kind']}: {finding['claim']}"
                )
                print(f"  Reason: {finding['reason']}")
                if finding["evidence_paths"]:
                    print(f"  Evidence: {', '.join(finding['evidence_paths'])}")
                print(f"  Suggested action: {finding['suggested_action']}")
            print(
                f"Semantic wiki lint: {len(findings)} finding(s), {stats.pages} page(s), "
                f"{stats.batches} batch(es), {stats.cached_batches} cached; "
                f"API tokens {stats.input_tokens} input / {stats.output_tokens} output"
            )
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
