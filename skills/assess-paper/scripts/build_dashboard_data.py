#!/usr/bin/env python3
"""Build dashboard data from publications, paper metadata, and benchmark metadata."""

import argparse
import json
import sys
from pathlib import Path

import yaml

MAILBOX_SCRIPTS = Path(__file__).resolve().parents[2] / "consult-human" / "scripts"
sys.path.insert(0, str(MAILBOX_SCRIPTS))
from research_mailbox import load_mailbox  # noqa: E402

FEASIBILITY_FIELDS = {
    "workstation_feasible",
    "reference_solution_feasible",
    "non_searchable_extension_possible",
}

parser = argparse.ArgumentParser()
parser.add_argument("--papers-index", default="papers/papers.yml")
parser.add_argument("--papers-root", default="papers")
parser.add_argument("--benchmarks-index", default="benchmarks/benchmarks.yml")
parser.add_argument("--benchmarks-root", default="benchmarks")
parser.add_argument("--output", default="dashboard/frontend/static/generated/data.js")
args = parser.parse_args()


def load_yaml(path):
    return yaml.safe_load(Path(path).read_text())


paper_assessments = {}
for path in sorted(Path(args.papers_root).glob("*/assessment.yml")):
    assessment = load_yaml(path)
    if "potential_pitfalls" not in assessment and "known_pitfalls" in assessment:
        assessment["potential_pitfalls"] = assessment.pop("known_pitfalls")
    for field in FEASIBILITY_FIELDS:
        if assessment.get(field) is True:
            assessment[field] = "yes"
        elif assessment.get(field) is False:
            assessment[field] = "no"
    paper_assessments[assessment["paper_id"]] = assessment

benchmark_records = {}
for path in sorted(Path(args.benchmarks_root).glob("*/metadata.yml")):
    record = load_yaml(path)
    if record:
        benchmark_records[record["benchmark_id"]] = record

benchmark_index = load_yaml(args.benchmarks_index) or []
indexed_benchmark_ids = {entry["benchmark_id"] for entry in benchmark_index}
unindexed_benchmarks = set(benchmark_records) - indexed_benchmark_ids
if unindexed_benchmarks:
    names = ", ".join(sorted(unindexed_benchmarks))
    raise SystemExit(f"Benchmark records missing from {args.benchmarks_index}: {names}")

benchmarks = []
project_root = Path(args.benchmarks_root).resolve().parent
project_threads = load_mailbox(project_root)["threads"]


def latest_active_author(thread):
    return next(
        (message.get("author") for message in reversed(thread.get("messages", []))
         if not message.get("retracted")),
        None,
    )


for entry in benchmark_index:
    benchmark = dict(entry)
    benchmark.update(benchmark_records.get(entry["benchmark_id"], {}))
    threads = [
        item for item in project_threads
        if not item.get("benchmark_ids") or entry["benchmark_id"] in item["benchmark_ids"]
    ]
    benchmark["open_thread_count"] = sum(item.get("status") == "open" for item in threads)
    benchmark["waiting_user_count"] = sum(
        item.get("status") == "open"
        and latest_active_author(item) == "agent"
        for item in threads
    )
    benchmark["waiting_agent_count"] = sum(
        item.get("status") == "open"
        and latest_active_author(item) == "user"
        for item in threads
    )
    benchmarks.append(benchmark)

papers = []
paper_index = load_yaml(args.papers_index) or []
indexed_paper_ids = {publication["id"] for publication in paper_index}
unknown_paper_assessments = set(paper_assessments) - indexed_paper_ids
if unknown_paper_assessments:
    names = ", ".join(sorted(unknown_paper_assessments))
    raise SystemExit(f"Paper assessments missing from {args.papers_index}: {names}")

for publication in paper_index:
    paper_id = publication["id"]
    assessment = paper_assessments.get(paper_id)
    base = {
        "paper_id": paper_id,
        "title": publication.get("title", ""),
        "authors": ", ".join(
            author.get("name", "") for author in publication.get("authors", [])
        ),
        "year": publication.get("year"),
        "type": publication.get("type", ""),
        "venue": publication.get("journal") or publication.get("conference") or "",
        "source_url": publication.get("url") or publication.get("doi") or "",
        "summary": publication.get("abstract", ""),
        "research_area": [],
        "has_assessment": assessment is not None,
    }
    if assessment:
        base.update(assessment)
    if assessment and assessment.get("stage") in {"listed", "fetched", "assessed", "reviewed"}:
        stage = assessment["stage"]
    elif assessment:
        stage = "assessed"
    elif (Path(args.papers_root) / paper_id).is_dir():
        stage = "fetched"
    else:
        stage = "listed"
    base["stage"] = stage
    base["benchmark_ids"] = [
        benchmark["benchmark_id"]
        for benchmark in benchmarks
        if paper_id in benchmark.get("paper_ids", [])
    ]
    papers.append(base)

destination = Path(args.output)
destination.parent.mkdir(parents=True, exist_ok=True)
payload = (
    "window.SCICODE_PAPERS = "
    + json.dumps(papers, ensure_ascii=False, indent=2)
    + ";\nwindow.SCICODE_BENCHMARKS = "
    + json.dumps(benchmarks, ensure_ascii=False, indent=2)
    + ";\n"
)
destination.write_text(payload)
print(
    f"Wrote {len(papers)} papers ({len(paper_assessments)} assessed) and "
    f"{len(benchmarks)} benchmarks to {destination}"
)
