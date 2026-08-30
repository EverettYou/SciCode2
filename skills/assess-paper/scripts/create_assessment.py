#!/usr/bin/env python3
"""Create starter paper assessment metadata from the publication YAML file."""

import argparse
from pathlib import Path
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("paper_id")
parser.add_argument("--papers-index", default="papers/papers.yml")
parser.add_argument("--output-root", default="papers")
args = parser.parse_args()

publications = yaml.safe_load(Path(args.papers_index).read_text())
entry = next((item for item in publications if item.get("id") == args.paper_id), None)
if entry is None:
    raise SystemExit(f"Publication not found: {args.paper_id}")

authors = ", ".join(author.get("name", "") for author in entry.get("authors", []))
card = {
    "paper_id": entry["id"],
    "title": entry.get("title", ""),
    "authors": authors,
    "year": entry.get("year"),
    "source_url": entry.get("url", ""),
    "research_area": [],
    "summary": entry.get("abstract", "").strip(),
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
    "ai_assessment": "Starter assessment generated from publication metadata; review the full text before marking it reviewed.",
    "stage": "assessed",
}
destination = Path(args.output_root) / args.paper_id / "assessment.yml"
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(yaml.safe_dump(card, sort_keys=False, allow_unicode=True, width=100))
print(destination)
