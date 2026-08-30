#!/usr/bin/env python3
"""Maintain a global or benchmark wiki sources.yml provenance ledger."""

from __future__ import annotations

import argparse
import fcntl
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

import yaml


SOURCE_KINDS = {"paper", "repository", "lab", "query", "project", "skill", "talk", "other"}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def scope_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    if not (path / "wiki" / "SCHEMA.md").is_file():
        raise ValueError(f"not a wiki scope: {path}")
    return path


def is_benchmark(root: Path) -> bool:
    return (root / "metadata.yml").is_file() and root.parent.name == "benchmarks"


def safe_relative_path(root: Path, value: str, label: str) -> str:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} must be scope-relative: {value}")
    if not (root / path).exists():
        raise ValueError(f"{label} does not exist: {value}")
    return path.as_posix()


def load_registry(root: Path) -> dict:
    path = root / "wiki" / "sources.yml"
    if not path.is_file():
        return {"version": 1, "sources": []}
    content = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(content, dict) or not isinstance(content.get("sources"), list):
        raise ValueError("wiki/sources.yml must contain a sources list")
    return content


@contextmanager
def registry_lock(root: Path):
    with (root / "wiki" / "SCHEMA.md").open("r", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def atomic_write(path: Path, content: dict) -> None:
    rendered = yaml.safe_dump(content, sort_keys=False, allow_unicode=True, width=1000)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(rendered)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def register_source(
    scope: str | Path,
    *,
    source_id: str,
    title: str | None,
    kind: str,
    source_path: str,
    revision: str,
    updated_pages: list[str],
) -> dict:
    root = scope_path(scope)
    source_id = source_id.strip()
    revision = revision.strip()
    if not source_id or any(character.isspace() for character in source_id):
        raise ValueError("source_id must be non-empty and contain no whitespace")
    if kind not in SOURCE_KINDS:
        raise ValueError(f"invalid source kind: {kind}")
    if not revision:
        raise ValueError("revision must not be empty")
    canonical_path = safe_relative_path(root, source_path, "source path")
    if is_benchmark(root):
        if not canonical_path.startswith(("problem/", "labs/")):
            raise ValueError("benchmark source path must live under problem/ or labs/")
    elif canonical_path.startswith("wiki/"):
        raise ValueError("global source path must live outside wiki/")
    pages = []
    for value in updated_pages:
        page = safe_relative_path(root, value, "updated page")
        if not page.startswith("wiki/") or not page.endswith(".md"):
            raise ValueError(f"updated page must be wiki Markdown: {value}")
        if page not in pages:
            pages.append(page)
    if not pages:
        raise ValueError("at least one updated wiki page is required")

    with registry_lock(root):
        registry = load_registry(root)
        sources = registry["sources"]
        item = next((entry for entry in sources if entry.get("source_id") == source_id), None)
        if item is None and any(entry.get("path") == canonical_path for entry in sources):
            raise ValueError("source path is already registered under another source_id")
        now = timestamp()
        resolved_title = (title or (item or {}).get("title") or "").strip()
        if not resolved_title:
            raise ValueError("title is required when registering a new source")
        values = {
            "source_id": source_id,
            "title": resolved_title,
            "kind": kind,
            "path": canonical_path,
            "revision": revision,
            "ingested_at": now,
            "updated_pages": pages,
        }
        if item is None:
            item = values
            sources.append(item)
        else:
            item.pop("citation_label", None)
            item.update(values)
        registry["version"] = 1
        sources.sort(key=lambda entry: str(entry.get("source_id", "")))
        atomic_write(root / "wiki" / "sources.yml", registry)
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list")
    listing.add_argument("scope")
    registering = commands.add_parser("register")
    registering.add_argument("scope")
    registering.add_argument("--source-id", required=True)
    registering.add_argument("--title")
    registering.add_argument("--kind", choices=sorted(SOURCE_KINDS), required=True)
    registering.add_argument("--path", required=True)
    registering.add_argument("--revision", required=True)
    registering.add_argument("--updated-page", action="append", required=True)
    args = parser.parse_args()
    root = scope_path(args.scope)
    if args.command == "list":
        print(yaml.safe_dump(load_registry(root), sort_keys=False, allow_unicode=True).strip())
    else:
        item = register_source(
            root, source_id=args.source_id, title=args.title,
            kind=args.kind, source_path=args.path,
            revision=args.revision, updated_pages=args.updated_page,
        )
        print(yaml.safe_dump(item, sort_keys=False, allow_unicode=True).strip())


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
