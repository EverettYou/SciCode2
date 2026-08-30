#!/usr/bin/env python3
"""Compute a deterministic digest of supported benchmark evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import yaml


COMPLETED_STATUS = re.compile(r"^\s*-?\s*Status:\s*completed\s*$", re.IGNORECASE | re.MULTILINE)
RESULT_SUFFIXES = {".csv", ".json", ".jsonl", ".md", ".tsv", ".txt", ".yaml", ".yml"}


def benchmark_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    if not (path / "metadata.yml").is_file() or not (path / "wiki").is_dir():
        raise ValueError(f"not a benchmark directory: {path}")
    return path


def completed_labs(benchmark: Path) -> list[Path]:
    reports = []
    for report in sorted((benchmark / "labs").glob("lab-*/REPORT.md")):
        if COMPLETED_STATUS.search(report.read_text(encoding="utf-8")):
            reports.append(report.parent)
    return reports


def evidence_files(benchmark: Path) -> list[Path]:
    files = []
    for path in sorted((benchmark / "wiki").rglob("*")):
        # Idea pages record search state, not completed evidence. They should not
        # trigger a supervisor synthesis solely because the frontier changed.
        if "ideas" in path.relative_to(benchmark / "wiki").parts:
            continue
        if path.is_file() and path.suffix.lower() in {".md", ".yml", ".yaml"}:
            files.append(path)
    for lab in completed_labs(benchmark):
        files.append(lab / "REPORT.md")
        for folder_name in ("results", "figures"):
            folder = lab / folder_name
            if not folder.is_dir():
                continue
            for path in sorted(folder.rglob("*")):
                if path.is_file() and path.suffix.lower() in RESULT_SUFFIXES:
                    files.append(path)
    return sorted(set(files), key=lambda item: item.relative_to(benchmark).as_posix())


def digest(benchmark: Path) -> tuple[str, list[str]]:
    hasher = hashlib.sha256()
    relative_paths = []
    for path in evidence_files(benchmark):
        relative = path.relative_to(benchmark).as_posix()
        relative_paths.append(relative)
        hasher.update(relative.encode("utf-8"))
        hasher.update(b"\0")
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                hasher.update(chunk)
        hasher.update(b"\0")
    return hasher.hexdigest(), relative_paths


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark")
    parser.add_argument("--files", action="store_true")
    args = parser.parse_args()
    try:
        benchmark = benchmark_path(args.benchmark)
        value, files = digest(benchmark)
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"error: {error}") from error
    result = {"digest": value, "file_count": len(files)}
    if args.files:
        result["files"] = files
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
