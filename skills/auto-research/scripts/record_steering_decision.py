#!/usr/bin/env python3
"""Append a structured supervisor steering decision to a benchmark ledger."""

from __future__ import annotations

import argparse
import fcntl
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from loop_state import benchmark_path, load_state, save_state, state_lock


DIAGNOSES = {
    "technical-block", "scientific-stall", "frontier-exhausted", "scope-decision",
    "looping", "awaiting-analysis",
}
ACTIONS = {
    "unblock", "redesign-lab", "branch", "change-direction", "prune", "consult-human",
    "pause",
}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_yaml(path: Path, data: list) -> None:
    content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark")
    parser.add_argument("--diagnosis", required=True, choices=sorted(DIAGNOSES))
    parser.add_argument("--action", required=True, choices=sorted(ACTIONS))
    parser.add_argument("--summary", required=True)
    parser.add_argument("--recommendation", required=True)
    parser.add_argument("--idea-id", action="append", default=[])
    parser.add_argument("--wiki-path", action="append", default=[])
    parser.add_argument("--lab-path", action="append", default=[])
    parser.add_argument("--alternative", action="append", default=[])
    parser.add_argument("--requires-human", action="store_true")
    parser.add_argument("--thread-id")
    args = parser.parse_args()

    try:
        benchmark = benchmark_path(args.benchmark)
        if args.requires_human and not args.thread_id:
            raise ValueError("--requires-human requires --thread-id")
        for value in args.wiki_path + args.lab_path:
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"evidence path must be benchmark-relative: {value}")

        ledger_path = benchmark / ".auto-research" / "steering-decisions.yml"
        lock_path = benchmark / ".auto-research" / ".steering.lock"
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            decisions = yaml.safe_load(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else []
            if not isinstance(decisions, list):
                raise ValueError("steering decision ledger must be a YAML list")
            decision = {
                "decision_id": f"steer-{len(decisions) + 1:04d}",
                "created_at": timestamp(),
                "diagnosis": args.diagnosis,
                "summary": args.summary,
                "wiki_basis": args.wiki_path,
                "lab_basis": args.lab_path,
                "target_idea_ids": args.idea_id,
                "decision": args.action,
                "recommendation": args.recommendation,
                "alternatives": args.alternative,
                "requires_human": args.requires_human,
                "thread_id": args.thread_id,
            }
            decisions.append(decision)
            atomic_yaml(ledger_path, decisions)

        with state_lock(benchmark):
            state = load_state(benchmark)
            state["progress"]["last_steering_decision_at"] = decision["created_at"]
            if args.action in {"unblock", "redesign-lab", "branch", "change-direction", "prune"}:
                state["progress"]["consecutive_no_evidence_syntheses"] = 0
                state["progress"]["repeated_action_count"] = 0
            if args.action in {"branch", "change-direction", "prune"}:
                state["progress"]["last_direction_change_at"] = decision["created_at"]
            if args.thread_id:
                state["progress"]["pending_human_thread_id"] = args.thread_id
            save_state(benchmark, state)
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"error: {error}") from error

    print(yaml.safe_dump(decision, sort_keys=False, allow_unicode=True), end="")


if __name__ == "__main__":
    main()
