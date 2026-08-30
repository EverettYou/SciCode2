"""Compressed evidence and cached LLM labels for knowledge-graph communities."""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from openai import OpenAI


PROMPT_VERSION = "community-label-v1"
COMMUNITY_NAMING_INSTRUCTIONS = """You name communities in a scientific research knowledge graph.

Choose the single best scholarly category label for each supplied community. The label should read like a concise paper keyword or taxonomy heading and describe the central shared subject, not merely one prominent page.

Prefer a concept that:
1. recurs across multiple members;
2. is supported by high-centrality members;
3. bridges multiple page types such as papers, concepts, methods, and comparisons;
4. remains valid if any one member is removed.

Use only the supplied evidence. Prefer established scientific terminology and a precise 2–5 word English noun phrase. Scientific topics and project topics are separate taxonomies: for a project-heavy community, use the project topics and workflow evidence rather than forcing a scientific field label.

Do not copy a specific paper title. Do not use author names, dates, explanations, or generic labels such as “Quantum Physics”, “Machine Learning”, “Research”, or “Methods” when the evidence supports a more specific category. Silently compare plausible labels and return only the requested structured result."""

LABEL_RESPONSE_SCHEMA = {
    "type": "json_schema",
    "name": "community_labels",
    "description": "One concise scholarly label for each supplied graph community.",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "labels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "community_id": {"type": "integer"},
                        "label": {"type": "string", "minLength": 2, "maxLength": 64},
                    },
                    "required": ["community_id", "label"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["labels"],
        "additionalProperties": False,
    },
}

WORD_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9+./'’–-]*")
TITLE_STOPWORDS = frozenset({
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "via", "with",
})
GENERIC_LABELS = frozenset({
    "machine learning", "methods", "physics", "project", "quantum physics", "research", "science",
})


def _shorten(value: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", str(value)).strip()
    if len(compact) <= limit:
        return compact
    shortened = compact[: limit - 1]
    boundary = shortened.rfind(" ")
    return f"{shortened[:boundary if boundary > limit // 2 else limit - 1].rstrip()}…"


def _shared_title_phrases(pages: list[dict[str, Any]], limit: int = 8) -> list[tuple[str, int]]:
    counts: Counter[str] = Counter()
    forms: dict[str, str] = {}
    for page in pages:
        words = [word for word in WORD_PATTERN.findall(page.get("title", "")) if word.casefold() not in TITLE_STOPWORDS]
        seen: set[str] = set()
        for width in (3, 2):
            for start in range(len(words) - width + 1):
                phrase = " ".join(words[start:start + width])
                key = phrase.casefold()
                if key not in seen:
                    counts[key] += 1
                    forms.setdefault(key, phrase)
                    seen.add(key)
    ranked = sorted(
        ((forms[key], count) for key, count in counts.items() if count >= 2),
        key=lambda item: (-item[1], -len(item[0].split()), item[0].casefold()),
    )
    return ranked[:limit]


def _representative_nodes(
    members: list[dict[str, Any]], page_by_id: dict[str, dict[str, Any]], limit: int = 12
) -> list[dict[str, Any]]:
    ranked = sorted(members, key=lambda node: (-node.get("weighted_degree", 0), node["label"].casefold()))
    selected: list[dict[str, Any]] = []
    represented_types: set[str] = set()
    for node in ranked:
        page_type = str(page_by_id[node["id"]].get("page_type", "reference"))
        if page_type not in represented_types:
            selected.append(node)
            represented_types.add(page_type)
    for node in ranked:
        if node not in selected:
            selected.append(node)
        if len(selected) >= limit:
            break
    return selected[:limit]


def community_evidence(
    graph: dict[str, Any], pages: list[dict[str, Any]], community: dict[str, Any]
) -> str:
    """Build a bounded evidence packet from metadata and compact Markdown-derived summaries."""
    page_by_id = {page["page_id"]: page for page in pages}
    members = [
        node for node in graph["nodes"]
        if node["community"] == community["id"] and node["id"] in page_by_id
    ]
    member_pages = [page_by_id[node["id"]] for node in members]
    scientific_topics = Counter(topic for page in member_pages for topic in page.get("topics", []))
    project_topics = Counter(topic for page in member_pages for topic in page.get("project_topics", []))
    phrases = _shared_title_phrases(member_pages)

    lines = [
        f"<community id=\"{community['id']}\" member_count=\"{len(members)}\">",
        "Shared title phrases: " + ("; ".join(f"{phrase} ({count})" for phrase, count in phrases) or "none"),
        "Scientific topics: " + ("; ".join(f"{topic} ({count})" for topic, count in scientific_topics.most_common()) or "none"),
        "Project topics: " + ("; ".join(f"{topic} ({count})" for topic, count in project_topics.most_common()) or "none"),
        "All member titles:",
    ]
    ranked_members = sorted(members, key=lambda node: (-node.get("weighted_degree", 0), node["label"].casefold()))
    for node in ranked_members:
        page = page_by_id[node["id"]]
        lines.append(f"- [{page.get('page_type', 'reference')}] {_shorten(page.get('title', node['label']), 140)}")

    lines.append("Representative evidence (ranked by graph centrality with type coverage):")
    for node in _representative_nodes(members, page_by_id):
        page = page_by_id[node["id"]]
        topic_text = ", ".join([*page.get("topics", []), *page.get("project_topics", [])]) or "none"
        lines.append(
            f"- type={page.get('page_type', 'reference')}; centrality={node.get('weighted_degree', 0):.2f}; "
            f"title={_shorten(page.get('title', node['label']), 140)}; topics={topic_text}; "
            f"summary={_shorten(page.get('summary', ''), 380) or 'none'}"
        )
    lines.append("</community>")
    return "\n".join(lines)[:14000]


def _evidence_key(model: str, evidence: str) -> str:
    payload = f"{PROMPT_VERSION}\n{model}\n{evidence}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _load_cache(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"version": 1, "entries": {}}
    if not isinstance(loaded, dict) or not isinstance(loaded.get("entries"), dict):
        return {"version": 1, "entries": {}}
    return loaded


def _save_cache(path: Path, cache: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(cache, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp") as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    temporary.replace(path)


def _valid_label(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    label = re.sub(r"\s+", " ", value).strip().strip(".\"'")
    words = WORD_PATTERN.findall(label)
    if not 1 <= len(words) <= 6 or len(label) > 64 or "\n" in label:
        return None
    if label.casefold() in GENERIC_LABELS:
        return None
    return label


def enrich_community_labels(
    graph: dict[str, Any],
    pages: list[dict[str, Any]],
    *,
    cache_path: Path,
    api_key: str,
    model: str = "gpt-5.6",
    timeout_seconds: float = 20,
    client_factory: Callable[..., Any] = OpenAI,
) -> dict[str, int]:
    """Apply cached or newly generated LLM labels, preserving local fallbacks."""
    if not api_key:
        return {"cached": 0, "generated": 0, "fallback": len(graph["communities"])}

    cache = _load_cache(cache_path)
    entries = cache["entries"]
    missing: list[tuple[dict[str, Any], str, str]] = []
    cached = 0
    for community in graph["communities"]:
        evidence = community_evidence(graph, pages, community)
        key = _evidence_key(model, evidence)
        cached_label = _valid_label(entries.get(key, {}).get("label"))
        if cached_label:
            community["label"] = cached_label
            community["label_source"] = "openai-cache"
            cached += 1
        else:
            missing.append((community, evidence, key))

    generated = 0
    if missing:
        dynamic_input = "\n\n".join(evidence for _, evidence, _ in missing)
        client = client_factory(api_key=api_key, timeout=timeout_seconds)
        response = client.responses.create(
            model=model,
            instructions=COMMUNITY_NAMING_INSTRUCTIONS,
            input=dynamic_input,
            text={"format": LABEL_RESPONSE_SCHEMA},
            max_output_tokens=max(800, len(missing) * 120),
            store=False,
        )
        payload = json.loads(response.output_text)
        expected = {community["id"]: (community, key) for community, _, key in missing}
        for item in payload.get("labels", []):
            community_id = item.get("community_id")
            label = _valid_label(item.get("label"))
            if community_id not in expected or not label:
                continue
            community, key = expected[community_id]
            community["label"] = label
            community["label_source"] = "openai"
            entries[key] = {"label": label, "model": model, "prompt_version": PROMPT_VERSION}
            generated += 1
        if generated:
            _save_cache(cache_path, cache)

    return {"cached": cached, "generated": generated, "fallback": len(graph["communities"]) - cached - generated}
