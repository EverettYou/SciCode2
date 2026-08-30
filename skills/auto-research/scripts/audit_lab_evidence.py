#!/usr/bin/env python3
"""Run deterministic prechecks before treating a completed lab as evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REQUIRED_SECTIONS = {
    "methods": ("methods and execution", "methods"),
    "findings": ("findings", "results"),
    "limitations": ("analysis and limitations", "limitations"),
    "search_decision": ("search decision",),
    "wiki_handoff": ("wiki ingest handoff", "wiki-ingest handoff"),
}
PROSPECTIVE_MARKERS = (
    "no experiment has been run",
    "populate this section only",
    "pending execution",
    "findings pending",
)
ARTIFACT_REFERENCE = re.compile(r"(?:results|figures)/[^\s)`]+", re.IGNORECASE)


def heading_sections(text: str) -> dict[str, str]:
    headings = list(re.finditer(r"^##+\s+(.+?)\s*$", text, re.MULTILINE))
    sections = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[heading.group(1).strip().casefold()] = text[heading.end():end].strip()
    return sections


def audit(report: Path) -> dict:
    if not report.is_file() or report.name != "REPORT.md":
        raise ValueError("expected a lab REPORT.md path")
    text = report.read_text(encoding="utf-8")
    lowered = text.casefold()
    errors = []
    warnings = []
    if not re.search(r"^\s*-?\s*status:\s*completed\s*$", text, re.IGNORECASE | re.MULTILINE):
        errors.append("report status is not completed")

    sections = heading_sections(text)
    matched = {}
    for label, aliases in REQUIRED_SECTIONS.items():
        match = next((name for name in sections if any(alias in name for alias in aliases)), None)
        if not match:
            errors.append(f"missing required section: {label}")
            continue
        matched[label] = sections[match]
        if not sections[match].strip():
            errors.append(f"empty required section: {label}")

    findings = matched.get("findings", "").casefold()
    for marker in PROSPECTIVE_MARKERS:
        if marker in findings:
            errors.append(f"findings still contain prospective marker: {marker}")

    references = sorted(set(ARTIFACT_REFERENCE.findall(text)))
    existing = []
    missing = []
    for reference in references:
        normalized = reference.rstrip(".,;:")
        if (report.parent / normalized).exists():
            existing.append(normalized)
        else:
            missing.append(normalized)
    if missing:
        errors.extend(f"cited artifact does not exist: {path}" for path in missing)
    if not references:
        warnings.append("report cites no results/ or figures/ artifact; confirm this is appropriate")
    if not re.search(r"\b(command|configuration|config|seed|environment|revision|commit)\b", lowered):
        warnings.append("report does not visibly record reproducibility metadata")

    return {
        "report": str(report),
        "passes_deterministic_checks": not errors,
        "errors": errors,
        "warnings": warnings,
        "existing_artifacts": existing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report")
    args = parser.parse_args()
    try:
        result = audit(Path(args.report).resolve())
    except (OSError, ValueError) as error:
        raise SystemExit(f"error: {error}") from error
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    if not result["passes_deterministic_checks"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
