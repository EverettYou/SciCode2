#!/usr/bin/env python3
"""Create a review-ready SciCode2 benchmark scaffold."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml


BENCHMARK_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PAPER_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
TEXT_SUFFIXES = {".bib", ".md", ".tex", ".toml", ".txt", ".yaml", ".yml"}
EMPTY_DIRS = (
    "labs",
    "wiki",
    "wiki/concepts",
    "wiki/methods",
    "wiki/implementations",
    "wiki/comparisons",
    "wiki/questions",
    "src",
    "note",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark_id")
    parser.add_argument("--title", required=True)
    parser.add_argument("--paper-id", action="append", required=True, dest="paper_ids")
    parser.add_argument("--summary", required=True)
    parser.add_argument(
        "--idea",
        required=True,
        help="selected or synthesized direction derived from assessment ideas",
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    return parser.parse_args()


def load_yaml(path: Path):
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_yaml(path: Path, content) -> None:
    path.write_text(
        yaml.safe_dump(content, sort_keys=False, allow_unicode=True, width=100),
        encoding="utf-8",
    )


def validate_inputs(args: argparse.Namespace, repo_root: Path) -> list[dict]:
    if not BENCHMARK_ID_PATTERN.fullmatch(args.benchmark_id):
        raise SystemExit("benchmark_id must use lowercase kebab-case")
    if not args.title.strip() or not args.summary.strip() or not args.idea.strip():
        raise SystemExit("title, summary, and idea must be non-empty")
    if len(set(args.paper_ids)) != len(args.paper_ids):
        raise SystemExit("paper IDs must not be repeated")

    paper_index = load_yaml(repo_root / "papers" / "papers.yml") or []
    publications = {entry.get("id"): entry for entry in paper_index}
    selected = []
    for paper_id in args.paper_ids:
        if not PAPER_ID_PATTERN.fullmatch(paper_id):
            raise SystemExit(f"invalid paper_id: {paper_id}")
        if paper_id not in publications:
            raise SystemExit(f"paper not found in papers/papers.yml: {paper_id}")
        paper_dir = repo_root / "papers" / paper_id
        assessment_path = paper_dir / "assessment.yml"
        pdf_path = paper_dir / "paper.pdf"
        if not assessment_path.is_file():
            raise SystemExit(f"paper has no assessment.yml: {paper_id}")
        if not pdf_path.is_file():
            raise SystemExit(f"paper has no local paper.pdf: {paper_id}")
        assessment = load_yaml(assessment_path) or {}
        if assessment.get("stage") != "reviewed":
            raise SystemExit(f"paper is not reviewed: {paper_id}")
        selected.append({"id": paper_id, "publication": publications[paper_id]})
    return selected


def render_scaffold(root: Path, replacements: dict[str, str]) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        content = path.read_text(encoding="utf-8")
        for token, value in replacements.items():
            content = content.replace("{{" + token + "}}", value)
        path.write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    skill_root = Path(__file__).resolve().parents[1]
    scaffold = skill_root / "assets" / "benchmark-scaffold"
    benchmarks_root = repo_root / "benchmarks"
    index_path = benchmarks_root / "benchmarks.yml"
    target = benchmarks_root / args.benchmark_id

    if not scaffold.is_dir():
        raise SystemExit(f"missing scaffold assets: {scaffold}")
    if not index_path.is_file():
        raise SystemExit(f"missing benchmark index: {index_path}")
    if target.exists():
        raise SystemExit(f"benchmark already exists: {target}")

    selected = validate_inputs(args, repo_root)
    index = load_yaml(index_path) or []
    if not isinstance(index, list):
        raise SystemExit("benchmarks/benchmarks.yml must contain a YAML list")
    if any(entry.get("benchmark_id") == args.benchmark_id for entry in index):
        raise SystemExit(f"benchmark already indexed: {args.benchmark_id}")

    paper_list = "\n".join(
        f"- `{item['id']}` — {item['publication'].get('title', 'Untitled paper')}"
        for item in selected
    )
    replacements = {
        "BENCHMARK_ID": args.benchmark_id,
        "TITLE": args.title.strip(),
        "SUMMARY": args.summary.strip(),
        "IDEA": args.idea.strip(),
        "PAPER_LIST": paper_list,
        "PRIMARY_PAPER_ID": args.paper_ids[0],
        "DATE": datetime.now(timezone.utc).date().isoformat(),
    }

    staging_root = repo_root / ".tmp"
    staging_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="create-benchmark-", dir=staging_root))
    try:
        temp_name = staging
        staged = Path(temp_name) / args.benchmark_id
        shutil.copytree(scaffold, staged)
        render_scaffold(staged, replacements)
        for relative in EMPTY_DIRS:
            (staged / relative).mkdir(parents=True, exist_ok=True)

        metadata_path = staged / "metadata.yml"
        metadata = load_yaml(metadata_path)
        metadata.update(
            {
                "benchmark_id": args.benchmark_id,
                "title": args.title.strip(),
                "paper_ids": args.paper_ids,
                "summary": args.summary.strip(),
            }
        )
        write_yaml(metadata_path, metadata)

        next_index = index + [
            {
                "benchmark_id": args.benchmark_id,
                "title": args.title.strip(),
                "stage": "problem-opened",
                "summary": args.summary.strip(),
            }
        ]
        index_temp = Path(temp_name) / "benchmarks.yml"
        write_yaml(index_temp, next_index)

        os.replace(staged, target)
        try:
            os.replace(index_temp, index_path)
        except Exception:
            shutil.rmtree(target)
            raise

    finally:
        shutil.rmtree(staging, ignore_errors=True)

    print(f"Created {target}")
    print(f"Registered {args.benchmark_id} in {index_path}")
    print("Next: complete the proposal, ingest its referenced paper folders into the global wiki, then initialize the local wiki and use the project-root talk for human supervision.")


if __name__ == "__main__":
    main()
