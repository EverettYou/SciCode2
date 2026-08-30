#!/usr/bin/env python3
"""Manage durable state and leases for a SciCode2 auto-research loop."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml


STATUSES = {"paused", "active", "blocked", "complete"}
WORKERS = {"research", "supervisor-synthesis"}
OUTCOMES = {
    "evidence", "progress", "healthy-in-flight", "no-progress", "failure",
    "blocked", "complete",
}


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def benchmark_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    required = ["metadata.yml", "problem", "wiki", "labs", "src", "note"]
    missing = [name for name in required if not (path / name).exists()]
    if missing:
        raise ValueError(f"not a complete benchmark directory; missing: {', '.join(missing)}")
    metadata = yaml.safe_load((path / "metadata.yml").read_text(encoding="utf-8")) or {}
    if metadata.get("benchmark_id") != path.name:
        raise ValueError("metadata.yml benchmark_id must match the directory name")
    return path


def control_path(benchmark: Path) -> Path:
    return benchmark / ".auto-research"


def state_path(benchmark: Path) -> Path:
    return control_path(benchmark) / "state.yml"


def default_state(benchmark: Path, research_minutes: int, synthesis_minutes: int) -> dict:
    now = timestamp()
    return {
        "schema_version": 1,
        "benchmark_id": benchmark.name,
        "status": "paused",
        "created_at": now,
        "updated_at": now,
        "automations": {
            "research": {
                "id": None,
                "name": f"auto-research:{benchmark.name}:research",
                "interval_minutes": research_minutes,
            },
            "supervisor_synthesis": {
                "id": None,
                "name": f"auto-research:{benchmark.name}:supervisor-synthesis",
                "interval_minutes": synthesis_minutes,
            },
        },
        "cursors": {
            "last_reference_ingested": None,
            "last_lab_ingested": None,
            "last_synthesis_evidence_digest": None,
        },
        "progress": {
            "last_supported_evidence_at": None,
            "last_meaningful_progress_at": None,
            "last_lab_heartbeat_at": None,
            "consecutive_no_evidence_syntheses": 0,
            "last_action_signature": None,
            "repeated_action_count": 0,
            "failure_signature": None,
            "repeated_failure_count": 0,
            "active_lab_id": None,
            "active_lab_stage": None,
            "last_steering_decision_at": None,
            "last_direction_change_at": None,
            "pending_human_thread_id": None,
        },
        "policy": {
            "diagnostic_after_no_progress_cycles": 3,
            "repeated_action_limit": 3,
            "repeated_failure_limit": 2,
            "heartbeat_stale_minutes": max(research_minutes * 3, 30),
            "direction_change_cooldown_hours": 6,
            "research_lease_minutes": max(research_minutes - 1, 1),
            "synthesis_lease_minutes": min(max(synthesis_minutes - 5, 5), 55),
        },
        "budgets": {
            "max_active_hours": None,
            "max_lab_runtime_minutes": None,
            "max_consecutive_failures": 3,
        },
        "last_run": {"research": None, "supervisor_synthesis": None},
    }


def atomic_yaml(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def append_event(benchmark: Path, event: dict) -> None:
    path = control_path(benchmark) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


@contextmanager
def state_lock(benchmark: Path):
    root = control_path(benchmark)
    root.mkdir(parents=True, exist_ok=True)
    lock_path = root / ".state.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_state(benchmark: Path) -> dict:
    path = state_path(benchmark)
    if not path.is_file():
        raise ValueError("auto-research state is not initialized")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("benchmark_id") != benchmark.name:
        raise ValueError("invalid auto-research state")
    return data


def save_state(benchmark: Path, state: dict) -> None:
    state["updated_at"] = timestamp()
    atomic_yaml(state_path(benchmark), state)


def initialize(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    with state_lock(benchmark):
        path = state_path(benchmark)
        if path.exists():
            state = load_state(benchmark)
            print(yaml.safe_dump(state, sort_keys=False), end="")
            return
        state = default_state(benchmark, args.research_minutes, args.synthesis_minutes)
        save_state(benchmark, state)
        append_event(benchmark, {
            "timestamp": timestamp(), "actor": "controller", "kind": "initialized",
            "details": {"research_minutes": args.research_minutes,
                        "synthesis_minutes": args.synthesis_minutes},
        })
    print(yaml.safe_dump(state, sort_keys=False), end="")


def show_status(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    state = load_state(benchmark)
    print(json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True))


def transition(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    if args.status not in STATUSES:
        raise ValueError(f"invalid status: {args.status}")
    with state_lock(benchmark):
        state = load_state(benchmark)
        previous = state["status"]
        state["status"] = args.status
        save_state(benchmark, state)
        append_event(benchmark, {
            "timestamp": timestamp(), "actor": args.actor, "kind": "status-transition",
            "details": {"from": previous, "to": args.status, "reason": args.reason},
        })
    print(json.dumps({"from": previous, "to": args.status}))


def set_schedules(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    if args.research_id is None and args.synthesis_id is None:
        raise ValueError("provide at least one schedule ID")
    with state_lock(benchmark):
        state = load_state(benchmark)
        if args.research_id is not None:
            state["automations"]["research"]["id"] = args.research_id or None
        if args.synthesis_id is not None:
            state["automations"]["supervisor_synthesis"]["id"] = args.synthesis_id or None
        save_state(benchmark, state)
        append_event(benchmark, {
            "timestamp": timestamp(), "actor": "controller", "kind": "schedules-reconciled",
            "details": {
                "research_id": state["automations"]["research"]["id"],
                "synthesis_id": state["automations"]["supervisor_synthesis"]["id"],
            },
        })
    print(json.dumps(state["automations"], indent=2, sort_keys=True))


def set_pending_human(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    with state_lock(benchmark):
        state = load_state(benchmark)
        state["progress"]["pending_human_thread_id"] = args.thread_id
        save_state(benchmark, state)
        append_event(benchmark, {
            "timestamp": timestamp(), "actor": "supervisor-synthesis",
            "kind": "human-consultation-updated", "details": {"thread_id": args.thread_id},
        })
    print(json.dumps({"pending_human_thread_id": args.thread_id}))


def record_run(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    if args.worker not in WORKERS or args.outcome not in OUTCOMES:
        raise ValueError("invalid worker or outcome")
    now = timestamp()
    with state_lock(benchmark):
        state = load_state(benchmark)
        progress = state["progress"]
        meaningful = args.outcome in {"evidence", "progress", "complete"}

        if args.action:
            if progress.get("last_action_signature") == args.action:
                progress["repeated_action_count"] += 1
            else:
                progress["last_action_signature"] = args.action
                progress["repeated_action_count"] = 1

        if args.failure_signature:
            if progress.get("failure_signature") == args.failure_signature:
                progress["repeated_failure_count"] += 1
            else:
                progress["failure_signature"] = args.failure_signature
                progress["repeated_failure_count"] = 1
        elif args.outcome != "failure":
            progress["failure_signature"] = None
            progress["repeated_failure_count"] = 0

        if args.worker == "supervisor-synthesis":
            if args.outcome == "evidence":
                progress["consecutive_no_evidence_syntheses"] = 0
            elif args.outcome in {"no-progress", "failure", "blocked"}:
                progress["consecutive_no_evidence_syntheses"] += 1

        if args.outcome == "evidence":
            progress["last_supported_evidence_at"] = now
        if meaningful:
            progress["last_meaningful_progress_at"] = now
            if args.worker == "research":
                progress["repeated_action_count"] = 0
        if args.heartbeat:
            progress["last_lab_heartbeat_at"] = now
        if args.lab_id is not None:
            progress["active_lab_id"] = args.lab_id or None
        if args.lab_stage is not None:
            progress["active_lab_stage"] = args.lab_stage or None
        if args.evidence_digest:
            state["cursors"]["last_synthesis_evidence_digest"] = args.evidence_digest

        key = args.worker.replace("-", "_")
        state["last_run"][key] = {
            "timestamp": now, "outcome": args.outcome, "action": args.action,
            "details": args.details,
        }
        save_state(benchmark, state)
        append_event(benchmark, {
            "timestamp": now, "actor": args.worker, "kind": "run-completed",
            "outcome": args.outcome, "action": args.action,
            "failure_signature": args.failure_signature, "details": args.details,
        })
    print(json.dumps(state["last_run"][key], indent=2, ensure_ascii=False))


def acquire_lease(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    if args.worker not in WORKERS:
        raise ValueError(f"invalid worker: {args.worker}")
    root = control_path(benchmark)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{args.worker}.lock"
    now = datetime.now(timezone.utc)
    token = uuid.uuid4().hex
    lease = {
        "worker": args.worker,
        "token": token,
        "acquired_at": timestamp(),
        "expires_at": (now + timedelta(minutes=args.ttl_minutes)).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "pid": os.getpid(),
    }
    for _ in range(2):
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(lease, handle, sort_keys=True)
                handle.write("\n")
            print(json.dumps(lease, sort_keys=True))
            return
        except FileExistsError:
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                expired = parse_timestamp(existing["expires_at"]) <= now
            except (OSError, ValueError, KeyError, json.JSONDecodeError):
                expired = False
            if not expired:
                raise RuntimeError(f"{args.worker} lease is already active")
            path.unlink(missing_ok=True)
    raise RuntimeError(f"could not acquire {args.worker} lease")


def release_lease(args: argparse.Namespace) -> None:
    benchmark = benchmark_path(args.benchmark)
    path = control_path(benchmark) / f"{args.worker}.lock"
    if not path.is_file():
        print(json.dumps({"released": False, "reason": "absent"}))
        return
    existing = json.loads(path.read_text(encoding="utf-8"))
    if existing.get("token") != args.token:
        raise ValueError("lease token does not match")
    path.unlink()
    print(json.dumps({"released": True, "worker": args.worker}))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    command = sub.add_parser("init")
    command.add_argument("benchmark")
    command.add_argument("--research-minutes", type=int, default=10)
    command.add_argument("--synthesis-minutes", type=int, default=60)
    command.set_defaults(function=initialize)

    command = sub.add_parser("status")
    command.add_argument("benchmark")
    command.set_defaults(function=show_status)

    command = sub.add_parser("transition")
    command.add_argument("benchmark")
    command.add_argument("status", choices=sorted(STATUSES))
    command.add_argument("--actor", default="controller")
    command.add_argument("--reason", default="")
    command.set_defaults(function=transition)

    command = sub.add_parser("set-schedules")
    command.add_argument("benchmark")
    command.add_argument("--research-id")
    command.add_argument("--synthesis-id")
    command.set_defaults(function=set_schedules)

    command = sub.add_parser("set-pending-human")
    command.add_argument("benchmark")
    command.add_argument("thread_id", nargs="?", default=None)
    command.set_defaults(function=set_pending_human)

    command = sub.add_parser("record-run")
    command.add_argument("benchmark")
    command.add_argument("--worker", required=True, choices=sorted(WORKERS))
    command.add_argument("--outcome", required=True, choices=sorted(OUTCOMES))
    command.add_argument("--action")
    command.add_argument("--failure-signature")
    command.add_argument("--evidence-digest")
    command.add_argument("--heartbeat", action="store_true")
    command.add_argument("--lab-id")
    command.add_argument("--lab-stage")
    command.add_argument("--details", default="")
    command.set_defaults(function=record_run)

    command = sub.add_parser("acquire")
    command.add_argument("benchmark")
    command.add_argument("--worker", required=True, choices=sorted(WORKERS))
    command.add_argument("--ttl-minutes", type=int, required=True)
    command.set_defaults(function=acquire_lease)

    command = sub.add_parser("release")
    command.add_argument("benchmark")
    command.add_argument("--worker", required=True, choices=sorted(WORKERS))
    command.add_argument("--token", required=True)
    command.set_defaults(function=release_lease)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.function(args)
    except (OSError, RuntimeError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"error: {error}") from error


if __name__ == "__main__":
    main()
