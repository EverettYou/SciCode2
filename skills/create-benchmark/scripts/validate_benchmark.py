#!/usr/bin/env python3
"""Validate a SciCode2 benchmark proposal and its repository links."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

MAILBOX_SCRIPTS = Path(__file__).resolve().parents[2] / "consult-human" / "scripts"
sys.path.insert(0, str(MAILBOX_SCRIPTS))
from research_mailbox import (  # noqa: E402
    AUTHORS,
    CATEGORIES,
    MESSAGE_OPERATION,
    MESSAGE_TYPES,
    PRIORITIES,
    THREAD_ID_PATTERN,
    THREAD_STATUSES,
    parse_thread,
)


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
IDEA_ID_PATTERN = re.compile(r"^[ckx]-[0-9]{3,}$")
PLACEHOLDER_PATTERN = re.compile(
    r"\{\{[^}]+\}\}|"
    r"\[(?:Specify|State|List|Define|Describe|Identify|Record|Turn|Explain|Break|Cite|Populate|"
    r"Introduce|Connect|Fix|Confirm|Develop|Distill|Present|Interpret|Collect|Summarize|"
    r"Document|Add|Scientific|Numerical|"
    r"Misleading|Dependency|Scope|cores|peak|working|none)"
    r"[^\]]*\]",
    re.IGNORECASE,
)
STAGES = {
    "problem-opened",
    "researching",
    "solution-drafted",
    "verified",
}
REQUIRED_FILES = (
    "README.md",
    "pyproject.toml",
    "metadata.yml",
    "problem/README.md",
    "problem/TASK.md",
    "labs/README.md",
    "wiki/SCHEMA.md",
    "wiki/index.md",
    "wiki/thesis.md",
    "wiki/log.md",
    "wiki/sources.yml",
    "wiki/ideas/research-frontier.md",
    "src/README.md",
    "note/main.tex",
    "note/references.bib",
)
LAB_NODE_PATTERN = re.compile(r"^lab-[0-9]{3,}-[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_FIELDS = (
    "benchmark_id",
    "title",
    "stage",
    "paper_ids",
    "summary",
    "idea_sources",
    "research_question",
    "scientific_domain",
    "expected_outcomes",
    "expected_outputs",
    "evidence_requirements",
    "estimated_active_hours",
    "workstation_feasible",
    "expert_review",
    "expert_notes",
)
TASK_SECTION_WORD_LIMIT = 250
TASK_SECTION_ALIASES = {
    "Why this is unresolved": ("Why this is unresolved", "Knowledge gap"),
    "Scope and approach": ("Scope and approach", "Scope and approach boundary"),
}


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def find_repo_root(benchmark_dir: Path) -> Path:
    for candidate in (benchmark_dir, *benchmark_dir.parents):
        if (candidate / "papers" / "papers.yml").is_file() and (
            candidate / "benchmarks" / "benchmarks.yml"
        ).is_file():
            return candidate
    raise SystemExit("could not locate repository root from benchmark path")


def validate_string_list(errors: list[str], metadata: dict, field: str) -> None:
    value = metadata.get(field)
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        errors.append(f"{field} must be a non-empty list of strings")


def validate_readme(errors: list[str], benchmark_dir: Path) -> None:
    path = benchmark_dir / "README.md"
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8")
    for marker in (
        "## Research goal",
        "## Current research status",
        "## Start here",
        "## Source foundation",
        "## Reading discipline",
        "**Central question:**",
        "**Current thesis:**",
        "**Active frontier:**",
        "**Active lab:**",
        "**Latest supported evidence:**",
        "**Main uncertainty:**",
        "**Next decisive action:**",
        "**Blockers or pending human input:**",
        "**Last meaningful update:**",
    ):
        if marker not in content:
            errors.append(f"README.md is missing onboarding marker: {marker}")


def level_two_sections(content: str) -> dict[str, str]:
    """Return Markdown level-two sections without consuming deeper headings."""
    headings = list(re.finditer(r"^##[ \t]+(.+?)[ \t]*$", content, re.MULTILINE))
    sections: dict[str, str] = {}
    for index, match in enumerate(headings):
        start = match.end()
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        sections[match.group(1).strip()] = content[start:end].strip()
    return sections


def markdown_word_count(content: str) -> int:
    """Count prose/math tokens consistently for proposal section budgets."""
    without_urls = re.sub(r"https?://\S+", " ", content)
    return len(re.findall(r"[A-Za-z0-9]+(?:['’_-][A-Za-z0-9]+)*", without_urls))


def validate_task(errors: list[str], benchmark_dir: Path, metadata: dict) -> None:
    path = benchmark_dir / "problem" / "TASK.md"
    if not path.is_file():
        return
    content = path.read_text(encoding="utf-8")
    sections = level_two_sections(content)

    for canonical, aliases in TASK_SECTION_ALIASES.items():
        present = [heading for heading in aliases if heading in sections]
        if len(present) > 1:
            errors.append(
                f"problem/TASK.md has duplicate '{canonical}' sections: "
                + ", ".join(present)
            )
            continue
        if not present:
            continue  # Legacy benchmarks may predate the bounded proposal sections.
        count = markdown_word_count(sections[present[0]])
        if count > TASK_SECTION_WORD_LIMIT:
            errors.append(
                f"problem/TASK.md '{canonical}' exceeds {TASK_SECTION_WORD_LIMIT} words "
                f"({count}); move implementation detail to labs or wiki/ideas"
            )

    question_section = sections.get("Research question", "")
    question_paragraph = question_section.split("\n\n", 1)[0].strip()
    normalized_task_question = re.sub(r"\s+", " ", question_paragraph)
    normalized_metadata_question = re.sub(
        r"\s+", " ", str(metadata.get("research_question", "")).strip()
    )
    if normalized_task_question and normalized_task_question != normalized_metadata_question:
        errors.append(
            "problem/TASK.md Research question must match metadata.yml research_question; "
            "when it changes, also review Why this is unresolved and Scope and approach"
        )


def validate_idea_sources(
    errors: list[str], metadata: dict, repo_root: Path
) -> None:
    idea_sources = metadata.get("idea_sources")
    if not isinstance(idea_sources, list) or not idea_sources:
        errors.append("idea_sources must be a non-empty list")
        return

    cited_papers = set(metadata.get("paper_ids") or [])
    allowed_fields = {"followup_ideas", "natural_followups", "potential_pitfalls"}
    for position, source in enumerate(idea_sources):
        label = f"idea_sources[{position}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be a mapping")
            continue
        paper_id = source.get("paper_id")
        source_field = source.get("source_field")
        item_index = source.get("item_index")
        role = source.get("role")
        if paper_id not in cited_papers:
            errors.append(f"{label}.paper_id must appear in paper_ids")
        if source_field not in allowed_fields:
            errors.append(f"{label}.source_field is not an assessment idea field")
        if (
            not isinstance(item_index, int)
            or isinstance(item_index, bool)
            or item_index < 0
        ):
            errors.append(f"{label}.item_index must be a zero-based integer")
        if not isinstance(role, str) or not role.strip():
            errors.append(f"{label}.role must be non-empty text")
        if paper_id not in cited_papers or source_field not in allowed_fields:
            continue
        assessment_path = repo_root / "papers" / paper_id / "assessment.yml"
        if not assessment_path.is_file():
            continue
        assessment = load_yaml(assessment_path) or {}
        items = assessment.get(source_field)
        if not isinstance(items, list):
            errors.append(f"{label} points to a missing or non-list assessment field")
        elif isinstance(item_index, int) and not isinstance(item_index, bool):
            if item_index < 0 or item_index >= len(items):
                errors.append(f"{label}.item_index is outside the assessment list")


def validate_problem_sources(errors: list[str], metadata: dict, benchmark_dir: Path) -> None:
    """Validate explicit user-supplied questions without inventing paper reviews."""
    sources = metadata.get("problem_sources")
    if not isinstance(sources, list) or not sources:
        errors.append("user-provided-problem requires non-empty problem_sources")
        return
    valid_paths = set()
    for position, source in enumerate(sources):
        label = f"problem_sources[{position}]"
        if not isinstance(source, dict):
            errors.append(f"{label} must be a mapping")
            continue
        value = source.get("path", "")
        relative = Path(value) if isinstance(value, str) else Path()
        if (not isinstance(value, str) or not value or relative.is_absolute()
                or ".." in relative.parts or not relative.parts or relative.parts[0] != "problem"):
            errors.append(f"{label}.path must be a safe benchmark-relative problem path")
            continue
        path = benchmark_dir / relative
        if not path.is_file() or not path.resolve().is_relative_to(benchmark_dir.resolve()):
            errors.append(f"{label}.path does not resolve to a local problem file")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if source.get("sha256") != digest:
            errors.append(f"{label}.sha256 does not match the immutable problem input")
        if not isinstance(source.get("origin"), str) or not source["origin"].strip():
            errors.append(f"{label}.origin must record the supplied input's provenance")
        valid_paths.add(relative.as_posix())
    ideas = metadata.get("idea_sources")
    if not isinstance(ideas, list) or not ideas:
        errors.append("idea_sources must identify a supplied problem source")
        return
    for position, idea in enumerate(ideas):
        if (not isinstance(idea, dict) or idea.get("source_path") not in valid_paths
                or idea.get("source_field") != "user-provided-research-question"
                or not isinstance(idea.get("role"), str) or not idea["role"].strip()):
            errors.append(f"idea_sources[{position}] must identify a registered problem question")


def validate_idea_graph(errors: list[str], benchmark_dir: Path, metadata: dict) -> None:
    # Legacy compatibility hook; the active schema stores idea history as markdown
    # pages under wiki/ideas/ and does not call this YAML validator.
    path = benchmark_dir / "wiki" / "ideas" / "research-frontier.md"
    if not path.is_file():
        return
    graph = load_yaml(path)
    ideas = graph.get("ideas") if isinstance(graph, dict) else None
    if not isinstance(ideas, list) or not ideas:
        errors.append("wiki/ideas/research-frontier.md must contain a non-empty ideas list")
        return

    nodes: dict[str, dict] = {}
    parent_map: dict[str, list[str]] = {}
    tracks: set[str] = set()
    assessment_origins = 0
    open_nodes = 0
    for position, idea in enumerate(ideas):
        label = f"ideas[{position}]"
        if not isinstance(idea, dict):
            errors.append(f"{label} must be a mapping")
            continue
        idea_id = idea.get("idea_id")
        if not isinstance(idea_id, str) or not IDEA_ID_PATTERN.fullmatch(idea_id):
            errors.append(f"{label}.idea_id must look like c-001, k-001, or x-001")
            continue
        if idea_id in nodes:
            errors.append(f"duplicate idea_id: {idea_id}")
            continue
        nodes[idea_id] = idea
        idea_track = idea.get("track")
        if idea_track not in {"code", "knowledge", "cross"}:
            errors.append(f"{idea_id}.track must be code, knowledge, or cross")
        else:
            tracks.add(idea_track)
        idea_status = idea.get("status")
        if idea_status not in {"frontier", "active", "kept", "pruned", "distilled"}:
            errors.append(f"{idea_id}.status is unsupported")
        if idea_status in {"frontier", "active"}:
            open_nodes += 1
        for field in ("statement", "rationale"):
            if not isinstance(idea.get(field), str) or not idea[field].strip():
                errors.append(f"{idea_id}.{field} must be non-empty text")
        parents = idea.get("parent_ids")
        if not isinstance(parents, list) or any(
            not isinstance(item, str) or not item.strip() for item in parents
        ):
            errors.append(f"{idea_id}.parent_ids must be a list of idea IDs")
            parents = []
        elif len(parents) != len(set(parents)):
            errors.append(f"{idea_id}.parent_ids must not contain duplicates")
        parent_map[idea_id] = parents
        origins = idea.get("origin_refs")
        if not isinstance(origins, list) or any(
            not isinstance(item, str) or not item.strip() for item in origins
        ):
            errors.append(f"{idea_id}.origin_refs must be a list of references")
            origins = []
        if not parents and not origins:
            errors.append(f"root idea {idea_id} must have at least one origin_refs entry")
        for origin in origins:
            match = re.fullmatch(r"metadata\.idea_sources\[([0-9]+)\]", origin)
            if match:
                assessment_origins += 1
                source_index = int(match.group(1))
                if source_index >= len(metadata.get("idea_sources") or []):
                    errors.append(f"{idea_id} has out-of-range origin reference: {origin}")
        if idea_status in {"frontier", "active"} and (
            not isinstance(idea.get("next_action"), str) or not idea["next_action"].strip()
        ):
            errors.append(f"{idea_id}.next_action is required while the idea is open")
        if idea_status in {"kept", "pruned", "distilled"} and (
            not isinstance(idea.get("decision"), str) or not idea["decision"].strip()
        ):
            errors.append(f"{idea_id}.decision is required for {idea_status} ideas")
        for field in ("evidence", "artifacts"):
            values = idea.get(field)
            if not isinstance(values, list) or any(
                not isinstance(item, str) or not item.strip() for item in values
            ):
                errors.append(f"{idea_id}.{field} must be a list of paths or references")
        artifact_values = idea.get("artifacts")
        if not isinstance(artifact_values, list):
            artifact_values = []
        if idea_status == "distilled" and not artifact_values:
            errors.append(f"{idea_id}.artifacts is required for distilled ideas")
        if idea_status != "distilled" and artifact_values:
            errors.append(f"{idea_id}.artifacts must stay empty until the idea is distilled")
        stable_roots: set[str] = set()
        for artifact in artifact_values:
            if not isinstance(artifact, str) or not artifact.strip():
                continue
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{idea_id} has unsafe artifact path: {artifact}")
                continue
            if len(artifact_path.parts) < 2 or artifact_path.parts[0] not in {"src", "note"}:
                errors.append(
                    f"{idea_id} distilled artifact must live under src/ or note/: {artifact}"
                )
                continue
            stable_roots.add(artifact_path.parts[0])
            if not (benchmark_dir / artifact_path).exists():
                errors.append(f"{idea_id} distilled artifact does not exist: {artifact}")
        if idea_status == "distilled" and idea_track == "code" and "src" not in stable_roots:
            errors.append(f"distilled code idea {idea_id} must produce an artifact under src/")
        if (
            idea_status == "distilled"
            and idea_track == "knowledge"
            and "note" not in stable_roots
        ):
            errors.append(
                f"distilled knowledge idea {idea_id} must produce an artifact under note/"
            )

    for idea_id, parents in parent_map.items():
        for parent_id in parents:
            if parent_id == idea_id:
                errors.append(f"{idea_id} cannot be its own parent")
            elif parent_id not in nodes:
                errors.append(f"{idea_id} has unknown parent: {parent_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(idea_id: str) -> None:
        if idea_id in visiting:
            errors.append(f"idea graph contains a cycle at {idea_id}")
            return
        if idea_id in visited:
            return
        visiting.add(idea_id)
        for parent_id in parent_map.get(idea_id, []):
            if parent_id in nodes:
                visit(parent_id)
        visiting.remove(idea_id)
        visited.add(idea_id)

    for idea_id in nodes:
        visit(idea_id)
    missing_tracks = {"code", "knowledge", "cross"} - tracks
    if missing_tracks:
        errors.append(
            "idea graph must seed code, knowledge, and cross tracks; missing: "
            + ", ".join(sorted(missing_tracks))
        )
    if assessment_origins == 0:
        errors.append("idea graph must trace at least one root to metadata.idea_sources")
    if metadata.get("stage") != "verified" and open_nodes == 0:
        errors.append("idea graph must retain at least one frontier or active node")


def validate_workspace_nodes(errors: list[str], benchmark_dir: Path) -> None:
    labs_root = benchmark_dir / "labs"
    lab_nodes = sorted(path for path in labs_root.iterdir() if path.is_dir()) if labs_root.is_dir() else []

    if not lab_nodes:
        errors.append("labs must contain at least one lab-NNN-slug folder")

    for node in lab_nodes:
        relative = node.relative_to(benchmark_dir)
        if not LAB_NODE_PATTERN.fullmatch(node.name):
            errors.append(f"invalid lab node folder name: {relative}")
        report = node / "REPORT.md"
        plan = node / "PLAN.md"
        if not report.is_file():
            errors.append(f"lab node is missing REPORT.md: {relative}")
        else:
            content = report.read_text(encoding="utf-8")
            frontmatter = {}
            if content.startswith("---\n"):
                end = content.find("\n---\n", 4)
                if end >= 0:
                    try:
                        loaded = yaml.safe_load(content[4:end])
                    except yaml.YAMLError as error:
                        errors.append(f"lab REPORT.md has invalid YAML frontmatter: {relative}: {error}")
                    else:
                        if isinstance(loaded, dict):
                            frontmatter = loaded
            required_metadata = ("document_type", "lab_id", "status", "idea_ids", "wiki_context", "related_labs")
            for field in required_metadata:
                if field not in frontmatter:
                    errors.append(f"lab REPORT.md frontmatter is missing '{field}': {relative}")
            if frontmatter.get("document_type") != "lab_report":
                errors.append(f"lab REPORT.md document_type must be 'lab_report': {relative}")
            if not isinstance(frontmatter.get("idea_ids"), list):
                errors.append(f"lab REPORT.md idea_ids must be a list: {relative}")
            if not isinstance(frontmatter.get("wiki_context"), list):
                errors.append(f"lab REPORT.md wiki_context must be a list: {relative}")
            if not isinstance(frontmatter.get("related_labs"), list):
                errors.append(f"lab REPORT.md related_labs must be a list: {relative}")
            for marker in ("## Motivation", "## Design", "## Findings", "## Wiki ingest handoff"):
                if marker not in content:
                    errors.append(f"lab REPORT.md is missing '{marker}': {relative}")
        if not plan.is_file():
            errors.append(f"lab node is missing PLAN.md: {relative}")
        else:
            content = plan.read_text(encoding="utf-8")
            for marker in ("## Objective", "## Stable interfaces", "## Steps", "## Completion criteria"):
                if marker not in content:
                    errors.append(f"lab PLAN.md is missing '{marker}': {relative}")


def validate_talk(errors: list[str], project_root: Path) -> None:
    talk_root = project_root / "talk"
    if not (talk_root / "README.md").is_file():
        errors.append("missing project-root talk/README.md")
        return
    threads_root = talk_root / "threads"
    known_benchmarks = {
        entry.get("benchmark_id")
        for entry in (load_yaml(project_root / "benchmarks" / "benchmarks.yml") or [])
        if isinstance(entry, dict)
    }
    thread_ids: set[str] = set()
    paths = sorted(threads_root.glob("*.md")) if threads_root.is_dir() else []
    for path in paths:
        relative = path.relative_to(project_root)
        try:
            thread = parse_thread(path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(f"invalid talk thread {relative}: {error}")
            continue
        thread_id = thread.get("id")
        if not isinstance(thread_id, str) or not THREAD_ID_PATTERN.fullmatch(thread_id):
            errors.append(f"invalid thread ID in {relative}: {thread_id}")
        elif thread_id in thread_ids:
            errors.append(f"duplicate talk thread ID: {thread_id}")
        else:
            thread_ids.add(thread_id)
            if not path.name.startswith(f"{thread_id}-"):
                errors.append(f"talk filename must begin with {thread_id}-: {relative}")
        if not re.fullmatch(r"T-[0-9]{4,}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", path.name):
            errors.append(f"invalid talk thread filename: {relative}")
        if thread.get("status") not in THREAD_STATUSES:
            errors.append(f"{thread_id} has invalid status")
        if thread.get("priority") not in PRIORITIES:
            errors.append(f"{thread_id} has invalid priority")
        if thread.get("category") not in CATEGORIES:
            errors.append(f"{thread_id} has invalid category")
        for field in ("title", "created", "updated"):
            if not isinstance(thread.get(field), str) or not thread[field].strip():
                errors.append(f"{thread_id} is missing {field}")
        if not isinstance(thread.get("context", ""), str):
            errors.append(f"{thread_id}.context must be text")
        benchmark_ids = thread.get("benchmark_ids")
        if not isinstance(benchmark_ids, list) or any(
            not isinstance(item, str) or item not in known_benchmarks for item in benchmark_ids
        ):
            errors.append(f"{thread_id}.benchmark_ids must reference known project benchmarks")
        related = thread.get("related")
        if not isinstance(related, list) or any(
            not isinstance(item, str) or not item.strip() for item in related
        ):
            errors.append(f"{thread_id}.related must be a list of project-relative paths")
        else:
            for item in related:
                related_path = Path(item)
                if related_path.is_absolute() or ".." in related_path.parts:
                    errors.append(f"{thread_id} has unsafe related path: {item}")
        messages = thread.get("messages")
        if not isinstance(messages, list) or not messages:
            errors.append(f"{thread_id} must contain at least one message")
            continue
        if thread.get("status") == "closed" and (
            messages[-1].get("author") != "user" or messages[-1].get("type") != "decision"
        ):
            errors.append(f"{thread_id} may only be closed by a final user decision message")
        seen_messages: dict[str, dict] = {}
        for position, message in enumerate(messages, start=1):
            expected_id = f"M-{position:03d}"
            if message.get("id") != expected_id:
                errors.append(f"{thread_id} message {position} must use ID {expected_id}")
            if message.get("author") not in AUTHORS:
                errors.append(f"{thread_id}/{expected_id} has invalid author")
            if message.get("type") not in MESSAGE_TYPES:
                errors.append(f"{thread_id}/{expected_id} has invalid message type")
            for field in ("created", "content"):
                if not isinstance(message.get(field), str) or not message[field].strip():
                    errors.append(f"{thread_id}/{expected_id} is missing {field}")
            if message.get("type") in {"edit", "retraction"}:
                operation = MESSAGE_OPERATION.fullmatch(str(message.get("content", "")))
                target = seen_messages.get(operation.group(1)) if operation else None
                if message.get("author") != "user" or not target or target.get("author") != "user":
                    errors.append(f"{thread_id}/{expected_id} must target an earlier user message")
                if message.get("type") == "edit" and (
                    not operation or not (operation.group(2) or "").strip()
                ):
                    errors.append(f"{thread_id}/{expected_id} edit must contain replacement text")
            seen_messages[message.get("id")] = message


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_dir", type=Path)
    args = parser.parse_args()
    benchmark_dir = args.benchmark_dir.resolve()
    repo_root = find_repo_root(benchmark_dir)
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (benchmark_dir / relative).is_file():
            errors.append(f"missing required file: {relative}")
    metadata_path = benchmark_dir / "metadata.yml"
    if not metadata_path.is_file():
        for message in errors:
            print(f"ERROR: {message}")
        raise SystemExit(1)

    metadata = load_yaml(metadata_path)
    if not isinstance(metadata, dict):
        raise SystemExit("metadata.yml must contain a YAML mapping")
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"metadata.yml is missing field: {field}")

    benchmark_id = metadata.get("benchmark_id")
    if not isinstance(benchmark_id, str) or not ID_PATTERN.fullmatch(benchmark_id):
        errors.append("benchmark_id must use lowercase kebab-case")
    elif benchmark_id != benchmark_dir.name:
        errors.append("benchmark_id must equal the benchmark folder name")
    if not isinstance(metadata.get("title"), str) or not metadata["title"].strip():
        errors.append("title must be non-empty text")
    if not isinstance(metadata.get("summary"), str) or not metadata["summary"].strip():
        errors.append("summary must be non-empty text")
    if (
        not isinstance(metadata.get("research_question"), str)
        or not metadata["research_question"].strip()
    ):
        errors.append("research_question must be non-empty text")
    if metadata.get("stage") not in STAGES:
        errors.append("stage is not a supported lifecycle value")
    if metadata.get("workstation_feasible") not in {"yes", "no", "uncertain"}:
        errors.append("workstation_feasible must be yes, no, or uncertain")
    if metadata.get("expert_review") not in {"pending", "reviewed"}:
        errors.append("expert_review must be pending or reviewed")
    direct_problem = metadata.get("source_mode") == "user-provided-problem"
    if direct_problem:
        if not isinstance(metadata.get("paper_ids"), list):
            errors.append("paper_ids must be a list (may be empty for a direct problem)")
        validate_problem_sources(errors, metadata, benchmark_dir)
    else:
        validate_string_list(errors, metadata, "paper_ids")
        validate_idea_sources(errors, metadata, repo_root)
    for field in (
        "scientific_domain",
        "expected_outcomes",
        "expected_outputs",
        "evidence_requirements",
    ):
        validate_string_list(errors, metadata, field)
    validate_readme(errors, benchmark_dir)
    validate_task(errors, benchmark_dir, metadata)
    validate_workspace_nodes(errors, benchmark_dir)
    validate_talk(errors, repo_root)
    hours = metadata.get("estimated_active_hours")
    if hours is not None and (
        not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours <= 0
    ):
        errors.append("estimated_active_hours must be null or a positive number")

    index = load_yaml(repo_root / "benchmarks" / "benchmarks.yml") or []
    matches = [entry for entry in index if entry.get("benchmark_id") == benchmark_id]
    if len(matches) != 1:
        errors.append("benchmark must have exactly one benchmarks.yml index entry")
    elif any(
        matches[0].get(field) != metadata.get(field)
        for field in ("title", "stage", "summary")
    ):
        errors.append("index title, stage, and summary must match metadata.yml")

    paper_index = load_yaml(repo_root / "papers" / "papers.yml") or []
    known_papers = {entry.get("id") for entry in paper_index}
    for paper_id in metadata.get("paper_ids") or []:
        if paper_id not in known_papers:
            errors.append(f"unknown paper_id: {paper_id}")
            continue
        source_assessment = repo_root / "papers" / paper_id / "assessment.yml"
        if not source_assessment.is_file():
            errors.append(f"source paper has no assessment.yml: {paper_id}")
            continue
        assessment = load_yaml(source_assessment) or {}
        if assessment.get("stage") != "reviewed":
            errors.append(f"source paper is not reviewed: {paper_id}")
        global_page = repo_root / "wiki" / "papers" / f"{paper_id}.md"
        if not global_page.is_file():
            errors.append(f"paper is not ingested into the global wiki: wiki/papers/{paper_id}.md")

    ignored_tree_parts = {".venv", ".uv-cache", ".uv-python", "__pycache__"}
    for path in benchmark_dir.rglob("*"):
        relative = path.relative_to(benchmark_dir)
        if any(part in ignored_tree_parts for part in relative.parts):
            continue
        if path.is_file() and path.suffix.lower() in {
            ".bib",
            ".md",
            ".tex",
            ".txt",
            ".yaml",
            ".yml",
        }:
            content = path.read_text(encoding="utf-8")
            if PLACEHOLDER_PATTERN.search(content):
                errors.append(f"unresolved design prompt in {relative}")

    for message in errors:
        print(f"ERROR: {message}")
    if errors:
        raise SystemExit(1)
    print(f"Validated benchmark proposal: {benchmark_id}")


if __name__ == "__main__":
    main()
