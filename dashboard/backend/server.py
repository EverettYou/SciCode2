#!/usr/bin/env python3
"""Local Paper to Benchmark server with safe assessment and research-talk editing."""

from __future__ import annotations

import os
import re
import logging
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, Any, Literal

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from dashboard.backend.community_naming import enrich_community_labels
from dashboard.backend.knowledge_graph import build_knowledge_graph, retrieve_pages


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from scripts.llm import LLMConfigurationError, load_project_env  # noqa: E402
load_project_env(PROJECT_ROOT)
from dashboard.backend.catalog_search import CatalogSearch  # noqa: E402

DASHBOARD_FRONTEND_ROOT = PROJECT_ROOT / "dashboard" / "frontend"
DASHBOARD_PAGES_ROOT = DASHBOARD_FRONTEND_ROOT / "pages"
DASHBOARD_STATIC_ROOT = DASHBOARD_FRONTEND_ROOT / "static"
PAPERS_ROOT = PROJECT_ROOT / "papers"
PAPERS_INDEX = PAPERS_ROOT / "papers.yml"
BENCHMARKS_ROOT = PROJECT_ROOT / "benchmarks"
BENCHMARKS_INDEX = BENCHMARKS_ROOT / "benchmarks.yml"
WIKI_ROOT = PROJECT_ROOT / "wiki"
BUILD_DATA = PROJECT_ROOT / "skills" / "assess-paper" / "scripts" / "build_dashboard_data.py"
COMMUNITY_LABEL_CACHE = PROJECT_ROOT / ".tmp" / "community-labels.json"
CATALOG_SEARCH = CatalogSearch(PROJECT_ROOT)
WIKI_SEARCH = CatalogSearch(PROJECT_ROOT, index_name="wiki-search")
PAPER_ID_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")
BENCHMARK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WIKI_PAGE_PATTERN = re.compile(r"^[a-z0-9]+(?:[/-][a-z0-9]+)*$")
WIKILINK_PATTERN = re.compile(r"(?<!!)\[\[([^\]]+)\]\]")
RESOURCE_ROOTS = {"README.md", "papers", "benchmarks", "skills", "talk", "wiki"}
BENCHMARK_CATALOG_MARKER = "<!-- dashboard:benchmark-catalog -->"

sys.path.insert(0, str(PROJECT_ROOT / "skills" / "consult-human" / "scripts"))
from research_mailbox import (  # noqa: E402
    create_thread,
    load_mailbox,
    reply_thread,
    revise_user_message,
    transition_thread,
)

ALLOWED_ASSESSMENT_FIELDS = {
    "research_area", "summary", "computational_core", "computational_depth",
    "scientific_judgment", "validation_ease", "workstation_feasible",
    "reference_solution_feasible", "non_searchable_extension_possible",
    "supervision_confidence", "followup_ideas", "potential_pitfalls",
    "suggested_task_types", "ai_assessment", "stage",
}
LEVEL_FIELDS = {
    "computational_depth", "scientific_judgment", "validation_ease", "supervision_confidence",
}
FEASIBILITY_FIELDS = {
    "workstation_feasible", "reference_solution_feasible", "non_searchable_extension_possible",
}
LIST_FIELDS = {
    "research_area", "followup_ideas", "potential_pitfalls", "suggested_task_types",
}
STAGE_VALUES = {"listed", "fetched", "assessed", "reviewed"}
BENCHMARK_STAGE_VALUES = {"problem-opened", "researching", "solution-drafted", "verified"}

app = FastAPI(title="Paper to Benchmark", docs_url="/api/docs", redoc_url=None)
LOGGER = logging.getLogger(__name__)


@app.middleware("http")
async def disable_local_static_cache(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".html", ".css", ".js")):
        response.headers["Cache-Control"] = "no-store"
    return response


class PatchRequest(BaseModel):
    patch: dict[str, Any]


class ThreadCreateRequest(BaseModel):
    title: str
    message: str
    priority: str = "normal"
    category: str = "task"
    context: str = ""
    related: list[str] = Field(default_factory=list)


class ThreadReplyRequest(BaseModel):
    message: str
    message_type: str = "response"


class ThreadMessageMutationRequest(BaseModel):
    action: str
    content: str = ""


class ThreadTransitionRequest(BaseModel):
    status: str
    message: str


class BenchmarkStageRequest(BaseModel):
    stage: str


class PaperSearchTarget(BaseModel):
    kind: Literal["paper"]
    paper_id: str


class BenchmarkSearchTarget(BaseModel):
    kind: Literal["benchmark"]
    benchmark_id: str


class WikiSearchTarget(BaseModel):
    kind: Literal["wiki"]
    page_id: str
    scope: str


class TalkSearchTarget(BaseModel):
    kind: Literal["talk"]
    thread_id: str


SearchTarget = Annotated[
    PaperSearchTarget | BenchmarkSearchTarget | WikiSearchTarget | TalkSearchTarget,
    Field(discriminator="kind"),
]


class SearchResultPayload(BaseModel):
    search_id: str
    entity_type: Literal["paper", "benchmark", "wiki", "talk"]
    entity_id: str
    target: SearchTarget
    title: str
    stage: str = ""
    score: float = 0.0
    semantic_score: float = 0.0
    lexical_score: float = 0.0
    match_type: Literal["keyword-semantic", "conceptual"]
    reason: str = ""
    refined_relevance: float | None = None


class SearchResponsePayload(BaseModel):
    query: str
    scope: str
    stage: str | None = None
    mode: str
    complex_query: bool
    results: list[SearchResultPayload]


def load_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    loaded = yaml.safe_load(path.read_text())
    return default if loaded is None else loaded


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    loaded = yaml.safe_load(text[4:end])
    return (loaded if isinstance(loaded, dict) else {}), text[end + 5:].lstrip()


def wiki_page_id(path: Path, wiki_root: Path = WIKI_ROOT) -> str:
    return path.relative_to(wiki_root).with_suffix("").as_posix()


def wiki_links(markdown: str) -> list[str]:
    links = []
    for body in WIKILINK_PATTERN.findall(markdown):
        target = body.split("|", 1)[0].split("#", 1)[0].strip()
        if target and WIKI_PAGE_PATTERN.fullmatch(target) and target not in links:
            links.append(target)
    return links


def wiki_navigation_kind(page_id: str, page_type: str) -> str:
    """Return the shared sidebar role used by global and benchmark wikis."""
    normalized_type = page_type.strip().casefold()
    return "catalog" if (
        normalized_type in {"collection", "index"}
        or page_id == "index"
        or page_id.endswith("/index")
    ) else "page"


def benchmark_catalog_markdown() -> str:
    """Render current benchmark links from the canonical benchmark index."""
    entries = sorted(benchmark_index().values(), key=lambda item: str(item.get("title", "")).casefold())
    lines = []
    for entry in entries:
        benchmark_id = str(entry.get("benchmark_id", ""))
        if not BENCHMARK_ID_PATTERN.fullmatch(benchmark_id):
            continue
        title = str(entry.get("title") or benchmark_id).replace("[", "\\[").replace("]", "\\]")
        dashboard_url = f"/benchmark.html?id={benchmark_id}"
        wiki_index = BENCHMARKS_ROOT / benchmark_id / "wiki" / "index.md"
        if wiki_index.is_file():
            wiki_url = f"/wiki.html?scope=benchmark%3A{benchmark_id}&page=index"
            wiki_link = f"[(wiki)]({wiki_url})"
        else:
            wiki_link = "(wiki unavailable)"
        lines.append(f"- **{title}** — {wiki_link} [(dashboard)]({dashboard_url})")
    return "\n".join(lines) or "- No benchmark workspaces are available yet."


def rendered_wiki_source(path: Path, raw: str) -> str:
    """Inject live benchmark navigation into the one generated global wiki page."""
    if path.resolve() == (WIKI_ROOT / "benchmarks" / "index.md").resolve():
        return raw.replace(BENCHMARK_CATALOG_MARKER, benchmark_catalog_markdown())
    return raw


def wiki_record(
    path: Path, include_markdown: bool = False, wiki_root: Path = WIKI_ROOT
) -> dict[str, Any]:
    raw = rendered_wiki_source(path, path.read_text(encoding="utf-8"))
    metadata, markdown = split_frontmatter(raw)
    heading = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    summary = re.search(r"^\*\*Summary\*\*:\s*(.+)$", markdown, re.MULTILINE)
    page_id = wiki_page_id(path, wiki_root)
    page_type = str(metadata.get("page_type") or ("index" if path.name == "index.md" else "reference"))
    record = {
        "page_id": page_id,
        "title": str(metadata.get("title") or (heading.group(1) if heading else page_id)),
        "page_type": page_type,
        "navigation_kind": wiki_navigation_kind(page_id, page_type),
        "status": str(metadata.get("status") or "active"),
        "updated": str(metadata.get("updated") or ""),
        "summary": summary.group(1).strip() if summary else "",
        "topics": metadata.get("topics") if isinstance(metadata.get("topics"), list) else [],
        "project_topics": metadata.get("project_topics") if isinstance(metadata.get("project_topics"), list) else [],
        "source_refs": metadata.get("source_refs") if isinstance(metadata.get("source_refs"), list) else [],
        "links": wiki_links(markdown),
    }
    if include_markdown:
        record["markdown"] = markdown
    return record


def wiki_records(wiki_root: Path = WIKI_ROOT) -> list[dict[str, Any]]:
    if not wiki_root.is_dir():
        return []
    return [
        wiki_record(path, wiki_root=wiki_root)
        for path in sorted(wiki_root.rglob("*.md"))
        if path.name not in {"SCHEMA.md", "log.md"}
    ]


def wiki_search_id(scope: str, page_id: str) -> str:
    if scope == "global":
        return f"wiki:global:{page_id}"
    benchmark_id = scope.removeprefix("benchmark:")
    return f"wiki:benchmark:{benchmark_id}:{page_id}"


def wiki_search_target(scope: str, page_id: str) -> dict[str, str]:
    return {"kind": "wiki", "page_id": page_id, "scope": scope}


def wiki_search_documents(
    records: list[dict[str, Any]], wiki_root: Path = WIKI_ROOT, scope: str = "global"
) -> list[dict[str, Any]]:
    """Compile the same compact search-document shape used by catalog search."""
    documents = []
    for record in records:
        page_id = str(record["page_id"])
        try:
            page_path = wiki_root / f"{page_id}.md"
            markdown = rendered_wiki_source(page_path, page_path.read_text(encoding="utf-8"))[:6000]
        except OSError:
            markdown = ""
        fields = [
            f"Title: {record.get('title', '')}",
            f"Page type: {record.get('page_type', '')}",
            f"Status: {record.get('status', '')}",
            f"Summary: {record.get('summary', '')}",
            f"Topics: {', '.join(str(item) for item in record.get('topics', []))}",
            f"Project topics: {', '.join(str(item) for item in record.get('project_topics', []))}",
            f"Links: {', '.join(str(item) for item in record.get('links', []))}",
            f"Page content: {markdown}",
        ]
        text = "\n".join(item for item in fields if not item.endswith(": "))
        documents.append({
            "search_id": wiki_search_id(scope, page_id),
            "entity_type": "wiki",
            "entity_id": page_id,
            "target": wiki_search_target(scope, page_id),
            "title": str(record.get("title", page_id)),
            "stage": str(record.get("status", "active")),
            "linked": bool(record.get("links")),
            "text": text,
            "compact": text[:2600],
        })
    return documents


def wiki_fallback_results(
    records: list[dict[str, Any]], query: str, scope: str, limit: int
) -> list[dict[str, Any]]:
    results = []
    for item in retrieve_pages(records, query, limit):
        page_id = str(item["page_id"])
        token_score = float(item.get("token_score", 0))
        graph_score = float(item.get("graph_score", 0))
        direct = token_score > 0
        results.append({
            "search_id": wiki_search_id(scope, page_id),
            "entity_type": "wiki",
            "entity_id": page_id,
            "target": wiki_search_target(scope, page_id),
            "title": str(item.get("title", page_id)),
            "stage": str(item.get("status", "active")),
            "score": float(item.get("score", 0)),
            "semantic_score": graph_score,
            "lexical_score": token_score,
            "match_type": "keyword-semantic" if direct else "conceptual",
            "reason": "Token and graph match" if direct else "Related through the knowledge graph",
        })
    return results


def safe_wiki_page(page_id: str, wiki_root: Path = WIKI_ROOT) -> Path:
    if not WIKI_PAGE_PATTERN.fullmatch(page_id):
        raise HTTPException(status_code=404, detail="Wiki page not found")
    path = (wiki_root / f"{page_id}.md").resolve()
    try:
        path.relative_to(wiki_root.resolve())
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Wiki page not found") from error
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Wiki page not found")
    return path


def benchmark_wiki_root(benchmark_id: str) -> Path:
    root = benchmark_dir(benchmark_id) / "wiki"
    if not (root / "SCHEMA.md").is_file():
        raise HTTPException(status_code=404, detail="Benchmark wiki not found")
    return root


def safe_project_resource(resource_path: str) -> Path:
    relative = Path(resource_path)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise HTTPException(status_code=404, detail="Resource not found")
    if relative.parts[0] not in RESOURCE_ROOTS or any(part.startswith(".") for part in relative.parts):
        raise HTTPException(status_code=404, detail="Resource not found")
    path = (PROJECT_ROOT / relative).resolve()
    try:
        path.relative_to(PROJECT_ROOT.resolve())
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Resource not found") from error
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Resource not found")
    return path


def paper_index() -> dict[str, dict[str, Any]]:
    return {entry["id"]: entry for entry in load_yaml(PAPERS_INDEX, [])}


def benchmark_index() -> dict[str, dict[str, Any]]:
    return {entry["benchmark_id"]: entry for entry in load_yaml(BENCHMARKS_INDEX, [])}


def validate_benchmark_id(benchmark_id: str) -> None:
    if not BENCHMARK_ID_PATTERN.fullmatch(benchmark_id) or benchmark_id not in benchmark_index():
        raise HTTPException(status_code=404, detail="Benchmark not found")


def benchmark_dir(benchmark_id: str) -> Path:
    validate_benchmark_id(benchmark_id)
    path = BENCHMARKS_ROOT / benchmark_id
    if not path.is_dir():
        raise HTTPException(status_code=404, detail="Benchmark directory not found")
    return path


def markdown_document(path: Path, folder: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"path": "", "title": "", "metadata": {}, "markdown": "", "sections": {}}
    raw = path.read_text(encoding="utf-8")
    metadata, markdown = split_frontmatter(raw)
    title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+(.+?)\s*$", markdown, re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[match.group(1).strip()] = markdown[match.end():end].strip()
    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "resource_url": f"/api/resources/{path.relative_to(PROJECT_ROOT).as_posix()}",
        "title": title_match.group(1).strip() if title_match else path.stem,
        "metadata": metadata,
        "markdown": markdown,
        "sections": sections,
    }


def status_snapshot(markdown: str) -> dict[str, str]:
    values = {}
    for label, value in re.findall(r"^- \*\*(.+?):\*\*\s*(.+)$", markdown, re.MULTILINE):
        values[label.strip().lower().replace(" ", "_")] = value.strip()
    return values


def benchmark_lab_records(folder: Path) -> list[dict[str, Any]]:
    records = []
    labs_root = folder / "labs"
    if not labs_root.is_dir():
        return records
    for lab_dir in sorted(path for path in labs_root.glob("lab-*") if path.is_dir()):
        report = markdown_document(lab_dir / "REPORT.md", folder)
        plan = markdown_document(lab_dir / "PLAN.md", folder)
        report_metadata = report["metadata"]
        status_match = re.search(r"^- Status:\s*`?([^`\n]+)`?", report["markdown"], re.MULTILINE)
        idea_match = re.search(r"^- Idea IDs:\s*(.+)$", report["markdown"], re.MULTILINE)
        idea_ids = report_metadata.get("idea_ids")
        if not isinstance(idea_ids, list):
            idea_ids = re.findall(r"[ckx]-\d{3,}", idea_match.group(1) if idea_match else "")
        evidence_files = [
            path for area in ("results", "figures") for path in (lab_dir / area).glob("**/*")
            if path.is_file() and path.name != "README.md"
        ]
        records.append({
            "lab_id": str(report_metadata.get("lab_id") or lab_dir.name),
            "title": report["title"],
            "status": str(report_metadata.get("status") or (status_match.group(1).strip() if status_match else "unknown")),
            "idea_ids": [str(idea_id) for idea_id in idea_ids],
            "report": report,
            "plan": plan,
            "evidence_file_count": len(evidence_files),
        })
    return records


def benchmark_payload(benchmark_id: str) -> dict[str, Any]:
    folder = benchmark_dir(benchmark_id)
    metadata = load_yaml(folder / "metadata.yml", {})
    readme = markdown_document(folder / "README.md", folder)
    task = markdown_document(folder / "problem" / "TASK.md", folder)
    thesis = markdown_document(folder / "wiki" / "thesis.md", folder)
    frontier = markdown_document(folder / "wiki" / "ideas" / "research-frontier.md", folder)
    labs = benchmark_lab_records(folder)
    threads = [
        thread for thread in load_mailbox(PROJECT_ROOT)["threads"]
        if not thread.get("benchmark_ids") or benchmark_id in thread["benchmark_ids"]
    ]
    source_files = [path for path in (folder / "src").rglob("*") if path.is_file() and path.name != "README.md"]
    wiki_pages = [path for path in (folder / "wiki").rglob("*.md") if path.name not in {"SCHEMA.md", "log.md"}]
    return {
        "benchmark_id": benchmark_id,
        "metadata": {**benchmark_index()[benchmark_id], **metadata},
        "threads": threads,
        "documents": {
            "readme": readme,
            "task": task,
            "thesis": thesis,
            "frontier": frontier,
        },
        "status_snapshot": status_snapshot(readme["markdown"]),
        "labs": labs,
        "artifacts": {
            "wiki_page_count": len(wiki_pages),
            "lab_count": len(labs),
            "evidence_file_count": sum(lab["evidence_file_count"] for lab in labs),
            "stable_source_file_count": len(source_files),
            "note_exists": (folder / "note" / "main.tex").is_file(),
        },
    }


def project_talk_payload() -> dict[str, Any]:
    return {
        **load_mailbox(PROJECT_ROOT),
        "benchmarks": list(benchmark_index().values()),
    }


def benchmark_ids_from_context(context: str) -> list[str]:
    """Infer structured benchmark links from IDs pasted into free-text context."""
    matches = []
    for benchmark_id in benchmark_index():
        pattern = rf"(?<![A-Za-z0-9._-]){re.escape(benchmark_id)}(?![A-Za-z0-9._-])"
        match = re.search(pattern, context)
        if match:
            matches.append((match.start(), benchmark_id))
    return [benchmark_id for _, benchmark_id in sorted(matches)]


def validate_paper_id(paper_id: str) -> None:
    if not PAPER_ID_PATTERN.fullmatch(paper_id) or paper_id not in paper_index():
        raise HTTPException(status_code=404, detail="Paper not found")


def paper_dir(paper_id: str) -> Path:
    validate_paper_id(paper_id)
    return PAPERS_ROOT / paper_id


def assessment_path(paper_id: str) -> Path:
    return paper_dir(paper_id) / "assessment.yml"


def starter_assessment(paper_id: str) -> dict[str, Any]:
    publication = paper_index()[paper_id]
    return {
        "paper_id": paper_id,
        "title": publication.get("title", ""),
        "authors": ", ".join(author.get("name", "") for author in publication.get("authors", [])),
        "year": publication.get("year"),
        "source_url": publication.get("url") or publication.get("doi") or "",
        "research_area": [],
        "summary": publication.get("abstract", ""),
        "computational_core": "",
        "computational_depth": None,
        "scientific_judgment": None,
        "validation_ease": None,
        "workstation_feasible": "uncertain",
        "reference_solution_feasible": "uncertain",
        "non_searchable_extension_possible": "uncertain",
        "supervision_confidence": None,
        "followup_ideas": [],
        "potential_pitfalls": [],
        "suggested_task_types": [],
        "ai_assessment": "",
        "stage": "listed",
    }


def current_assessment(paper_id: str) -> dict[str, Any]:
    assessment = load_yaml(assessment_path(paper_id), starter_assessment(paper_id))
    if "potential_pitfalls" not in assessment and "known_pitfalls" in assessment:
        assessment["potential_pitfalls"] = assessment.pop("known_pitfalls")
    for field in FEASIBILITY_FIELDS:
        if assessment.get(field) is True:
            assessment[field] = "yes"
        elif assessment.get(field) is False:
            assessment[field] = "no"
    return assessment


def safe_patch(patch: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    unknown = set(patch) - ALLOWED_ASSESSMENT_FIELDS
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unsupported assessment fields: {sorted(unknown)}")
    cleaned = {}
    for field, value in patch.items():
        if value is None or current.get(field) == value:
            continue
        if field in LEVEL_FIELDS and value not in {"low", "medium", "high"}:
            raise HTTPException(status_code=422, detail=f"Invalid value for {field}")
        if field in FEASIBILITY_FIELDS and value not in {"yes", "no", "uncertain"}:
            raise HTTPException(status_code=422, detail=f"Invalid value for {field}")
        if field in LIST_FIELDS:
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise HTTPException(status_code=422, detail=f"{field} must be a list of strings")
            value = [item.strip() for item in value if item.strip()]
        elif not isinstance(value, str):
            raise HTTPException(status_code=422, detail=f"{field} must be text")
        if field == "stage" and value not in STAGE_VALUES:
            raise HTTPException(status_code=422, detail="Invalid stage value")
        cleaned[field] = value
    return cleaned


def atomic_write_yaml(path: Path, content: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(content, sort_keys=False, allow_unicode=True, width=100)
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def backup_assessment(paper_id: str, current: dict[str, Any]) -> Path:
    history = paper_dir(paper_id) / "history"
    history.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    path = history / f"assessment-{stamp}.yml"
    atomic_write_yaml(path, current)
    return path


def rebuild_dashboard() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILD_DATA)], cwd=PROJECT_ROOT, capture_output=True, text=True,
    )
    if result.returncode:
        raise HTTPException(status_code=500, detail=result.stderr.strip() or "Dashboard rebuild failed")


def paper_payload(paper_id: str) -> dict[str, Any]:
    validate_paper_id(paper_id)
    publication = paper_index()[paper_id]
    assessment = current_assessment(paper_id)
    folder = PAPERS_ROOT / paper_id
    return {
        "paper_id": paper_id,
        "publication": publication,
        "assessment": assessment,
        "has_assessment": (folder / "assessment.yml").exists(),
        "assets": {
            "pdf": f"/api/papers/{paper_id}/pdf" if (folder / "paper.pdf").exists() else None,
            "source": f"/api/papers/{paper_id}/source" if (folder / "source.tar").exists() else None,
            "source_url": assessment.get("source_url") or publication.get("url") or "",
        },
    }


def named_knowledge_graph(pages: list[dict[str, Any]], scope: str) -> dict[str, Any]:
    graph = build_knowledge_graph(pages)
    if scope != "global":
        graph["model"]["community_naming"] = {"mode": "local", "fallback": len(graph["communities"])}
        return graph

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    model = os.getenv("OPENAI_COMMUNITY_NAMING_MODEL", "gpt-5.6").strip() or "gpt-5.6"
    try:
        timeout = float(os.getenv("OPENAI_API_TIMEOUT_SECONDS", "20"))
    except ValueError:
        timeout = 20.0
    try:
        stats = enrich_community_labels(
            graph,
            pages,
            cache_path=COMMUNITY_LABEL_CACHE,
            api_key=api_key,
            model=model,
            timeout_seconds=max(1.0, min(timeout, 120.0)),
        )
        graph["model"]["community_naming"] = {
            "mode": "openai" if api_key else "local",
            "model": model if api_key else None,
            **stats,
        }
    except Exception as error:  # The graph remains usable when the optional model is unavailable.
        LOGGER.warning("Community naming fell back to local labels: %s", error)
        graph["model"]["community_naming"] = {
            "mode": "local-fallback",
            "fallback": len(graph["communities"]),
        }
    return graph


def wiki_catalog_payload(wiki_root: Path, scope: str, title: str) -> dict[str, Any]:
    pages = wiki_records(wiki_root)
    page_ids = {page["page_id"] for page in pages}
    return {
        "scope": scope,
        "title": title,
        "pages": pages,
        "graph": named_knowledge_graph(pages, scope),
        "edges": [
            {"source": page["page_id"], "target": target}
            for page in pages for target in page["links"] if target in page_ids
        ],
    }


def wiki_page_payload(wiki_root: Path, page_id: str, scope: str) -> dict[str, Any]:
    page = wiki_record(
        safe_wiki_page(page_id, wiki_root), include_markdown=True, wiki_root=wiki_root
    )
    pages = wiki_records(wiki_root)
    page["scope"] = scope
    page["backlinks"] = [
        {"page_id": candidate["page_id"], "title": candidate["title"]}
        for candidate in pages if page_id in candidate["links"]
    ]
    return page


@app.get("/api/wiki")
def get_wiki_catalog() -> dict[str, Any]:
    return wiki_catalog_payload(WIKI_ROOT, "global", "Global knowledge")


@app.get("/api/wiki/search", response_model=SearchResponsePayload)
def search_wiki(
    q: str, scope: str = "global", limit: int = 12, refine: bool = False
) -> dict[str, Any]:
    query = q.strip()
    if not query or len(query) > 500:
        raise HTTPException(status_code=422, detail="Query must contain 1–500 characters")
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 50")
    wiki_root = WIKI_ROOT
    resolved_scope = "global"
    if scope.startswith("benchmark:"):
        benchmark_id = scope.removeprefix("benchmark:")
        wiki_root = benchmark_wiki_root(benchmark_id)
        resolved_scope = scope
    elif scope != "global":
        raise HTTPException(status_code=422, detail="Unsupported wiki scope")
    records = wiki_records(wiki_root)
    if os.getenv("OPENAI_CATALOG_SEARCH_ENABLED", "").strip().casefold() in {"1", "true", "yes"}:
        try:
            return WIKI_SEARCH.search(
                query,
                scope="wiki",
                limit=limit,
                refine=refine,
                documents=wiki_search_documents(records, wiki_root, resolved_scope),
            ) | {"scope": resolved_scope}
        except LLMConfigurationError:
            pass
        except Exception:
            LOGGER.exception("Wiki semantic search failed; falling back to token+graph search")
    return {
        "query": query,
        "scope": resolved_scope,
        "mode": "token+graph",
        "complex_query": False,
        "results": wiki_fallback_results(records, query, resolved_scope, limit),
    }


@app.get("/api/catalog/search", response_model=SearchResponsePayload)
def search_catalog(
    q: str,
    scope: str = "papers",
    stage: str = "all",
    limit: int = 50,
    refine: bool = False,
) -> dict[str, Any]:
    query = " ".join(q.split())
    if not query or len(query) > 500:
        raise HTTPException(status_code=422, detail="Query must contain 1–500 characters")
    if scope not in {"papers", "benchmarks", "all"}:
        raise HTTPException(status_code=422, detail="Unsupported catalog scope")
    valid_stages = {
        "papers": {"all", "listed", "fetched", "assessed", "reviewed", "linked"},
        "benchmarks": {"all", *BENCHMARK_STAGE_VALUES},
        "all": {"all"},
    }
    if stage not in valid_stages[scope]:
        raise HTTPException(status_code=422, detail="Unsupported stage filter")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail="Limit must be between 1 and 100")
    if os.getenv("OPENAI_CATALOG_SEARCH_ENABLED", "").strip().casefold() not in {"1", "true", "yes"}:
        raise HTTPException(
            status_code=503,
            detail="Semantic catalog search requires explicit server-side opt-in",
        )
    try:
        return CATALOG_SEARCH.search(
            query,
            scope=scope,
            stage=stage,
            limit=limit,
            refine=refine,
        )
    except LLMConfigurationError as error:
        raise HTTPException(status_code=503, detail="Semantic search is not configured") from error
    except Exception as error:
        LOGGER.exception("Catalog search failed")
        raise HTTPException(status_code=503, detail="Semantic search is temporarily unavailable") from error


@app.get("/api/wiki/page/{page_id:path}")
def get_wiki_page(page_id: str) -> dict[str, Any]:
    return wiki_page_payload(WIKI_ROOT, page_id, "global")


@app.get("/api/wiki/benchmark/{benchmark_id}")
def get_benchmark_wiki_catalog(benchmark_id: str) -> dict[str, Any]:
    root = benchmark_wiki_root(benchmark_id)
    title = benchmark_index()[benchmark_id].get("title", benchmark_id)
    return wiki_catalog_payload(root, f"benchmark:{benchmark_id}", title)


@app.get("/api/wiki/benchmark/{benchmark_id}/page/{page_id:path}")
def get_benchmark_wiki_page(benchmark_id: str, page_id: str) -> dict[str, Any]:
    return wiki_page_payload(
        benchmark_wiki_root(benchmark_id), page_id, f"benchmark:{benchmark_id}"
    )


@app.get("/api/resources/{resource_path:path}")
def get_project_resource(resource_path: str) -> Response:
    path = safe_project_resource(resource_path)
    if path.resolve() == (WIKI_ROOT / "benchmarks" / "index.md").resolve():
        return Response(rendered_wiki_source(path, path.read_text(encoding="utf-8")), media_type="text/markdown")
    return FileResponse(path)


@app.get("/api/papers/{paper_id}")
def get_paper(paper_id: str) -> dict[str, Any]:
    return paper_payload(paper_id)


@app.get("/api/papers/{paper_id}/pdf")
def get_pdf(paper_id: str) -> FileResponse:
    path = paper_dir(paper_id) / "paper.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Local PDF unavailable")
    return FileResponse(
        path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{paper_id}.pdf"'},
    )


@app.get("/api/papers/{paper_id}/source")
def get_source(paper_id: str) -> FileResponse:
    path = paper_dir(paper_id) / "source.tar"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Local source unavailable")
    return FileResponse(path, media_type="application/x-tar", filename=f"{paper_id}-source.tar")


@app.post("/api/papers/{paper_id}/assessment/apply")
def apply_assessment_patch(paper_id: str, request: PatchRequest) -> dict[str, Any]:
    current = current_assessment(paper_id)
    patch = safe_patch(request.patch, current)
    if not patch:
        return {"paper": paper_payload(paper_id), "applied": [], "message": "No changes to apply"}
    backup_assessment(paper_id, current)
    atomic_write_yaml(assessment_path(paper_id), {**current, **patch})
    rebuild_dashboard()
    return {"paper": paper_payload(paper_id), "applied": sorted(patch)}


@app.post("/api/papers/{paper_id}/assessment/undo")
def undo_assessment_patch(paper_id: str) -> dict[str, Any]:
    current = current_assessment(paper_id)
    history = paper_dir(paper_id) / "history"
    candidates = sorted(history.glob("assessment-*.yml"), reverse=True) if history.exists() else []
    if not candidates:
        raise HTTPException(status_code=404, detail="No assessment revision available to undo")
    source = candidates[0]
    restored = load_yaml(source, {})
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    atomic_write_yaml(history / f"redo-{stamp}.yml", current)
    atomic_write_yaml(assessment_path(paper_id), restored)
    source.rename(source.with_name(source.name.replace("assessment-", "undone-assessment-", 1)))
    rebuild_dashboard()
    return {"paper": paper_payload(paper_id), "message": "Last assessment patch undone"}


@app.get("/api/benchmarks/{benchmark_id}")
def get_benchmark(benchmark_id: str) -> dict[str, Any]:
    return benchmark_payload(benchmark_id)


@app.patch("/api/benchmarks/{benchmark_id}/stage")
def patch_benchmark_stage(benchmark_id: str, request: BenchmarkStageRequest) -> dict[str, Any]:
    if request.stage not in BENCHMARK_STAGE_VALUES:
        raise HTTPException(status_code=422, detail="Invalid benchmark stage")
    folder = benchmark_dir(benchmark_id)
    metadata_path = folder / "metadata.yml"
    metadata = load_yaml(metadata_path, {})
    catalog = load_yaml(BENCHMARKS_INDEX, [])
    if not isinstance(metadata, dict) or not isinstance(catalog, list):
        raise HTTPException(status_code=500, detail="Benchmark metadata could not be updated")
    updated = False
    for entry in catalog:
        if isinstance(entry, dict) and entry.get("benchmark_id") == benchmark_id:
            entry["stage"] = request.stage
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    metadata["stage"] = request.stage
    atomic_write_yaml(metadata_path, metadata)
    atomic_write_yaml(BENCHMARKS_INDEX, catalog)
    rebuild_dashboard()
    return {"benchmark": benchmark_payload(benchmark_id)}


@app.get("/api/talk")
def get_project_talk() -> dict[str, Any]:
    return project_talk_payload()


@app.post("/api/talk/threads")
def post_project_thread(request: ThreadCreateRequest) -> dict[str, Any]:
    title = request.title.strip()
    message = request.message.strip()
    context = request.context.strip()
    if not title or len(title) > 160:
        raise HTTPException(status_code=422, detail="Title must contain 1–160 characters")
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    if len(context) > 12000:
        raise HTTPException(status_code=422, detail="Context must contain at most 12000 characters")
    try:
        created = create_thread(
            PROJECT_ROOT, title=title, author="user", message=message,
            priority=request.priority, category=request.category,
            context=context, benchmark_ids=benchmark_ids_from_context(context),
            related=request.related,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": created, "talk": project_talk_payload()}


@app.post("/api/talk/threads/{thread_id}/messages")
def post_project_thread_message(thread_id: str, request: ThreadReplyRequest) -> dict[str, Any]:
    message = request.message.strip()
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    try:
        thread = reply_thread(
            PROJECT_ROOT, thread_id, author="user", message=message,
            message_type=request.message_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "talk": project_talk_payload()}


@app.patch("/api/talk/threads/{thread_id}/messages/{message_id}")
def patch_project_thread_message(
    thread_id: str, message_id: str, request: ThreadMessageMutationRequest
) -> dict[str, Any]:
    content = request.content.strip()
    if request.action not in {"edit", "retraction"}:
        raise HTTPException(status_code=422, detail="Action must be edit or retraction")
    if request.action == "edit" and (not content or len(content) > 12000):
        raise HTTPException(status_code=422, detail="Edited message must contain 1–12000 characters")
    try:
        thread = revise_user_message(
            PROJECT_ROOT, thread_id, message_id, author="user",
            action=request.action, message=content,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "talk": project_talk_payload()}


@app.post("/api/talk/threads/{thread_id}/transition")
def post_project_thread_transition(
    thread_id: str, request: ThreadTransitionRequest
) -> dict[str, Any]:
    message = request.message.strip()
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    try:
        thread = transition_thread(
            PROJECT_ROOT, thread_id, author="user", status=request.status, message=message,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "talk": project_talk_payload()}


@app.post("/api/benchmarks/{benchmark_id}/threads")
def post_benchmark_thread(benchmark_id: str, request: ThreadCreateRequest) -> dict[str, Any]:
    benchmark_dir(benchmark_id)
    title = request.title.strip()
    message = request.message.strip()
    context = request.context.strip()
    if not title or len(title) > 160:
        raise HTTPException(status_code=422, detail="Title must contain 1–160 characters")
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    if len(context) > 12000:
        raise HTTPException(status_code=422, detail="Context must contain at most 12000 characters")
    try:
        created = create_thread(
            PROJECT_ROOT, title=title, author="user", message=message,
            priority=request.priority, category=request.category,
            context=context, benchmark_ids=[benchmark_id], related=request.related,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": created, "benchmark": benchmark_payload(benchmark_id)}


@app.post("/api/benchmarks/{benchmark_id}/threads/{thread_id}/messages")
def post_benchmark_thread_message(
    benchmark_id: str, thread_id: str, request: ThreadReplyRequest
) -> dict[str, Any]:
    benchmark_dir(benchmark_id)
    message = request.message.strip()
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    try:
        thread = reply_thread(
            PROJECT_ROOT, thread_id, author="user", message=message,
            message_type=request.message_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "benchmark": benchmark_payload(benchmark_id)}


@app.patch("/api/benchmarks/{benchmark_id}/threads/{thread_id}/messages/{message_id}")
def patch_benchmark_thread_message(
    benchmark_id: str, thread_id: str, message_id: str,
    request: ThreadMessageMutationRequest,
) -> dict[str, Any]:
    benchmark_dir(benchmark_id)
    content = request.content.strip()
    if request.action not in {"edit", "retraction"}:
        raise HTTPException(status_code=422, detail="Action must be edit or retraction")
    if request.action == "edit" and (not content or len(content) > 12000):
        raise HTTPException(status_code=422, detail="Edited message must contain 1–12000 characters")
    try:
        thread = revise_user_message(
            PROJECT_ROOT, thread_id, message_id, author="user",
            action=request.action, message=content,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "benchmark": benchmark_payload(benchmark_id)}


@app.post("/api/benchmarks/{benchmark_id}/threads/{thread_id}/transition")
def post_benchmark_thread_transition(
    benchmark_id: str, thread_id: str, request: ThreadTransitionRequest
) -> dict[str, Any]:
    benchmark_dir(benchmark_id)
    message = request.message.strip()
    if not message or len(message) > 12000:
        raise HTTPException(status_code=422, detail="Message must contain 1–12000 characters")
    try:
        thread = transition_thread(
            PROJECT_ROOT, thread_id, author="user", status=request.status,
            message=message,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    rebuild_dashboard()
    return {"thread": thread, "benchmark": benchmark_payload(benchmark_id)}


@app.get("/")
def get_dashboard_home() -> FileResponse:
    return FileResponse(DASHBOARD_PAGES_ROOT / "index.html")


@app.get("/{page_name}.html")
def get_dashboard_page(page_name: str) -> FileResponse:
    """Serve the established public page URLs from the organized page directory."""
    page = DASHBOARD_PAGES_ROOT / f"{page_name}.html"
    if not page.is_file():
        raise HTTPException(status_code=404, detail="Dashboard page not found")
    return FileResponse(page)


app.mount("/static", StaticFiles(directory=DASHBOARD_STATIC_ROOT), name="dashboard-static")
