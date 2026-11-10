"""Export only this attempt's exact sessions, preserving original JSONL bytes."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

LAB = Path(__file__).resolve().parents[1]
SOURCES = {
    "root": Path("/Users/home/.codex/sessions/2026/10/07/rollout-2026-10-07T12-55-30-01a117ef-65f7-7d00-997b-03ac38efb6a9.jsonl"),
    "procedural-provenance": Path("/Users/home/.codex/sessions/2026/10/07/rollout-2026-10-07T12-56-57-01a117f0-c688-7cf0-8cf4-773b06cf9f58.jsonl"),
}


def main():
    captured_at = datetime.now(timezone.utc).isoformat()
    exports = []
    usage = {}
    sources = dict(SOURCES)
    declared_sources = LAB / "transcripts" / "session-sources.json"
    if declared_sources.exists():
        for label, source in json.loads(declared_sources.read_text()).items():
            sources[label] = Path(source)
    for label, source in sources.items():
        original = source.read_bytes()
        boundary = original.rfind(b"\n") + 1
        raw = original[:boundary]
        events = [json.loads(line) for line in raw.splitlines()]
        last_turn = max((i for i, e in enumerate(events) if e.get("type") == "turn_context"), default=-1)
        last_complete = max((i for i, e in enumerate(events)
                             if e.get("type") == "event_msg" and e.get("payload", {}).get("type") == "task_complete"), default=-1)
        turn_complete = last_complete > last_turn
        for i, event in enumerate(events):
            payload = event.get("payload", {})
            if event.get("type") == "event_msg" and payload.get("type") == "token_count" and payload.get("info"):
                usage[label] = {"source_line": i + 1, "timestamp": event.get("timestamp"),
                                "reported": payload["info"],
                                "note": "Per-session reported usage; not summed across inherited contexts."}
        target = LAB / "transcripts" / (label + ".jsonl")
        target.write_bytes(raw)
        assert target.read_bytes() == raw
        exports.append({
            "path": str(target.relative_to(LAB)),
            "source_path": str(source),
            "format": "original Codex rollout JSONL",
            "sha256": sha256(raw).hexdigest(),
            "bytes": len(raw),
            "records": len(events),
            "trailing_incomplete_bytes_excluded": len(original) - boundary,
            "last_event_timestamp": events[-1].get("timestamp") if events else None,
            "exported_at": captured_at,
            "event_locator": "one-based JSONL line number; timestamps retained",
            "latest_turn_complete_at_capture": turn_complete,
            "completeness": "Raw records through latest completed turn, including task_complete; future events absent." if turn_complete else "All newline-terminated records present at capture; active turn, later events and final response absent.",
            "inheritance": "Early root history retained" if label == "procedural-provenance" else "fork none; task-specific message only" if label != "root" else None,
        })
    run_path = LAB / "run.json"
    run = json.loads(run_path.read_text())
    run["transcript"] = exports
    run.setdefault("resource_use", {})["reported_session_token_usage"] = usage
    excluded = {"run.json", "manifest.json"}
    run["outputs"] = [
        {"path": str(path.relative_to(LAB)), "sha256": sha256(path.read_bytes()).hexdigest()}
        for path in sorted(LAB.rglob("*"))
        if path.is_file() and str(path.relative_to(LAB)) not in excluded
    ]
    run_path.write_text(json.dumps(run, indent=2) + "\n")
    manifest = {
        "captured_at": captured_at,
        "files": [
            {"path": str(path.relative_to(LAB)), "sha256": sha256(path.read_bytes()).hexdigest()}
            for path in sorted(LAB.rglob("*"))
            if path.is_file() and path.name != "manifest.json"
        ],
    }
    (LAB / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for item in manifest["files"]:
        assert sha256((LAB / item["path"]).read_bytes()).hexdigest() == item["sha256"]
    print(json.dumps({"exports": [{"path": x["path"], "records": x["records"], "sha256": x["sha256"]} for x in exports], "verified_files": len(manifest["files"])}, indent=2))


if __name__ == "__main__":
    main()
