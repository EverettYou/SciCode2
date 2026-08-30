#!/usr/bin/env python3
"""Classify benchmark progress before a supervisor-synthesis decision."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from evidence_digest import benchmark_path, digest


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def classify(benchmark: Path) -> dict:
    state_file = benchmark / ".auto-research" / "state.yml"
    if not state_file.is_file():
        raise ValueError("auto-research state is not initialized")
    state = yaml.safe_load(state_file.read_text(encoding="utf-8")) or {}
    status = state.get("status")
    progress = state.get("progress", {})
    policy = state.get("policy", {})
    current_digest, files = digest(benchmark)
    previous_digest = state.get("cursors", {}).get("last_synthesis_evidence_digest")

    result = {
        "classification": "observation-window",
        "diagnostic_required": False,
        "current_evidence_digest": current_digest,
        "previous_evidence_digest": previous_digest,
        "evidence_file_count": len(files),
        "reasons": [],
    }
    if status != "active":
        result.update(classification="inactive", reasons=[f"loop status is {status!r}"])
        return result
    if previous_digest != current_digest:
        result.update(classification="evidence-changed", reasons=["candidate evidence digest changed"])
        return result
    if progress.get("pending_human_thread_id"):
        result.update(
            classification="awaiting-human",
            reasons=[f"pending thread {progress['pending_human_thread_id']}"],
        )
        return result

    now = datetime.now(timezone.utc)
    heartbeat = parse_timestamp(progress.get("last_lab_heartbeat_at"))
    stale_minutes = int(policy.get("heartbeat_stale_minutes", 30))
    if heartbeat and (now - heartbeat).total_seconds() < stale_minutes * 60:
        result.update(classification="healthy-in-flight", reasons=["active lab heartbeat is fresh"])
        return result

    triggers = []
    if progress.get("consecutive_no_evidence_syntheses", 0) >= int(
        policy.get("diagnostic_after_no_progress_cycles", 3)
    ):
        triggers.append("no-evidence synthesis threshold reached")
    if progress.get("repeated_action_count", 0) >= int(policy.get("repeated_action_limit", 3)):
        triggers.append("same action repeated without progress")
    if progress.get("repeated_failure_count", 0) >= int(policy.get("repeated_failure_limit", 2)):
        triggers.append("same failure repeated")
    if heartbeat and (now - heartbeat).total_seconds() >= stale_minutes * 60:
        triggers.append("active lab heartbeat is stale")

    if triggers:
        result.update(classification="stalled", diagnostic_required=True, reasons=triggers)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmark")
    args = parser.parse_args()
    try:
        result = classify(benchmark_path(args.benchmark))
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"error: {error}") from error
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
