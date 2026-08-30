#!/usr/bin/env python3
"""Create, read, and update project research-talk threads."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

import yaml


THREAD_STATUSES = {"open", "closed"}
AUTHORS = {"agent", "user"}
PRIORITIES = {"blocking", "high", "normal", "low"}
CATEGORIES = {
    "checkpoint", "scientific", "scope", "interpretation", "conflict",
    "resource", "lint", "task", "other",
}
MESSAGE_CONTENT_TYPES = {
    "question", "advice", "response", "acknowledgment", "update",
    "decision", "resolution",
}
MESSAGE_OPERATION_TYPES = {"edit", "retraction"}
MESSAGE_TYPES = MESSAGE_CONTENT_TYPES | MESSAGE_OPERATION_TYPES
THREAD_ID_PATTERN = re.compile(r"^T-([0-9]{4,})$")
MESSAGE_ID_PATTERN = re.compile(r"^M-([0-9]{3,})$")
MESSAGE_HEADING = re.compile(
    r"^## (M-[0-9]{3,}) · (agent|user) · ([a-z-]+) · (.+)$",
    re.MULTILINE,
)
MESSAGE_OPERATION = re.compile(
    r"^Target: (M-[0-9]{3,})(?:\n\n([\s\S]*))?$",
)


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def clean_text(value: str, label: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{label} must not be empty")
    return value


def project_path(value: str | Path) -> Path:
    path = Path(value).resolve()
    if not (path / "benchmarks" / "benchmarks.yml").is_file():
        raise ValueError(f"not a SciCode2 project root: {path}")
    return path


def mailbox_path(project: str | Path) -> Path:
    path = project_path(project) / "talk"
    if not (path / "README.md").is_file():
        raise ValueError(f"project talk is not initialized: {path}")
    return path


@contextmanager
def mailbox_lock(root: Path):
    with (root / "README.md").open("r", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def locked_mutation(function):
    @wraps(function)
    def wrapper(project, *args, **kwargs):
        with mailbox_lock(mailbox_path(project)):
            return function(project, *args, **kwargs)
    return wrapper


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug[:72].rstrip("-") or "thread"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise ValueError("thread is missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("thread frontmatter is not closed")
    metadata = yaml.safe_load(text[4:end])
    if not isinstance(metadata, dict):
        raise ValueError("thread frontmatter must be a YAML mapping")
    return metadata, text[end + 5:]


def parse_messages(body: str) -> list[dict]:
    headings = list(MESSAGE_HEADING.finditer(body))
    messages = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(body)
        messages.append({
            "id": heading.group(1),
            "author": heading.group(2),
            "type": heading.group(3),
            "created": heading.group(4).strip(),
            "content": body[heading.end():end].strip(),
        })
    return messages


def parse_thread(path: Path) -> dict:
    metadata, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    return {**metadata, "messages": parse_messages(body), "path": path}


def render_thread(thread: dict) -> str:
    metadata = {
        "id": thread["id"],
        "title": thread["title"],
        "status": thread["status"],
        "priority": thread["priority"],
        "category": thread["category"],
        "created": thread["created"],
        "updated": thread["updated"],
        "context": thread.get("context", ""),
        "benchmark_ids": thread.get("benchmark_ids", []),
        "related": thread.get("related", []),
    }
    frontmatter = yaml.safe_dump(
        metadata, sort_keys=False, allow_unicode=True, width=1000,
    ).strip()
    messages = "\n\n".join(
        f"## {message['id']} · {message['author']} · {message['type']} · {message['created']}\n\n"
        f"{message['content']}"
        for message in thread["messages"]
    )
    return f"---\n{frontmatter}\n---\n\n# {thread['title']}\n\n{messages}\n"


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, suffix=".tmp"
    ) as handle:
        handle.write(content)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def materialize_messages(messages: list[dict]) -> list[dict]:
    """Apply append-only edit/retraction events to user-visible messages."""
    visible = []
    by_id = {}
    for raw in messages:
        message = dict(raw)
        if message.get("type") in MESSAGE_OPERATION_TYPES:
            operation = MESSAGE_OPERATION.fullmatch(str(message.get("content", "")))
            target = by_id.get(operation.group(1)) if operation else None
            if target and target.get("author") == "user":
                if message["type"] == "edit" and not target.get("retracted"):
                    replacement = (operation.group(2) or "").strip()
                    if replacement:
                        target["content"] = replacement
                        target["edited"] = message.get("created", "")
                        target["revision_id"] = message.get("id", "")
                elif message["type"] == "retraction":
                    target["content"] = ""
                    target["retracted"] = True
                    target["retracted_at"] = message.get("created", "")
                    target["revision_id"] = message.get("id", "")
                continue
        visible.append(message)
        by_id[message.get("id")] = message
    return visible


def public_thread(thread: dict) -> dict:
    public = {key: value for key, value in thread.items() if key != "path"}
    public["messages"] = materialize_messages(thread.get("messages", []))
    return public


def load_mailbox(project: str | Path) -> dict[str, list[dict]]:
    threads_root = mailbox_path(project) / "threads"
    threads = []
    if threads_root.is_dir():
        for path in sorted(threads_root.glob("T-*.md")):
            threads.append(public_thread(parse_thread(path)))
    threads.sort(key=lambda item: (item.get("updated", ""), item.get("id", "")), reverse=True)
    return {"threads": threads}


def next_thread_id(threads: list[dict]) -> str:
    numbers = [
        int(match.group(1))
        for item in threads
        if isinstance(item.get("id"), str)
        and (match := THREAD_ID_PATTERN.fullmatch(item["id"]))
    ]
    return f"T-{max(numbers, default=0) + 1:04d}"


def next_message_id(messages: list[dict]) -> str:
    numbers = [
        int(match.group(1))
        for item in messages
        if isinstance(item.get("id"), str)
        and (match := MESSAGE_ID_PATTERN.fullmatch(item["id"]))
    ]
    return f"M-{max(numbers, default=0) + 1:03d}"


def validate_choice(value: str, allowed: set[str], label: str) -> str:
    if value not in allowed:
        raise ValueError(f"invalid {label}: {value}")
    return value


def clean_related(values: list[str] | None) -> list[str]:
    related = []
    for value in values or []:
        value = clean_text(value, "related path")
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"related path must be project-relative: {value}")
        if value not in related:
            related.append(value)
    return related


def clean_context(value: str | None) -> str:
    return (value or "").strip()


def clean_benchmark_ids(project: str | Path, values: list[str] | None) -> list[str]:
    index = yaml.safe_load((project_path(project) / "benchmarks" / "benchmarks.yml").read_text()) or []
    known = {entry.get("benchmark_id") for entry in index if isinstance(entry, dict)}
    benchmark_ids = []
    for value in values or []:
        value = clean_text(value, "benchmark ID")
        if value not in known:
            raise ValueError(f"unknown benchmark ID: {value}")
        if value not in benchmark_ids:
            benchmark_ids.append(value)
    return benchmark_ids


def find_thread(project: str | Path, thread_id: str) -> tuple[Path, dict]:
    if not THREAD_ID_PATTERN.fullmatch(thread_id):
        raise ValueError(f"invalid thread ID: {thread_id}")
    threads_root = mailbox_path(project) / "threads"
    matches = list(threads_root.glob(f"{thread_id}-*.md")) if threads_root.is_dir() else []
    if len(matches) != 1:
        raise ValueError(f"unknown or ambiguous thread: {thread_id}")
    return matches[0], parse_thread(matches[0])


@locked_mutation
def create_thread(
    project: str | Path,
    *,
    title: str,
    author: str,
    message: str,
    message_type: str | None = None,
    priority: str = "normal",
    category: str = "other",
    context: str = "",
    benchmark_ids: list[str] | None = None,
    related: list[str] | None = None,
) -> dict:
    root = mailbox_path(project)
    author = validate_choice(author, AUTHORS, "author")
    priority = validate_choice(priority, PRIORITIES, "priority")
    category = validate_choice(category, CATEGORIES, "category")
    message_type = validate_choice(
        message_type or ("question" if author == "agent" else "advice"),
        MESSAGE_CONTENT_TYPES,
        "message type",
    )
    title = clean_text(title, "title").replace("\n", " ")
    existing = load_mailbox(project)["threads"]
    if any(
        item.get("status") == "open" and str(item.get("title", "")).casefold() == title.casefold()
        for item in existing
    ):
        raise ValueError("an open thread with this title already exists")
    now = timestamp()
    thread_id = next_thread_id(existing)
    thread = {
        "id": thread_id,
        "title": title,
        "status": "open",
        "priority": priority,
        "category": category,
        "created": now,
        "updated": now,
        "context": clean_context(context),
        "benchmark_ids": clean_benchmark_ids(project, benchmark_ids),
        "related": clean_related(related),
        "messages": [{
            "id": "M-001",
            "author": author,
            "type": message_type,
            "created": now,
            "content": clean_text(message, "message"),
        }],
    }
    path = root / "threads" / f"{thread_id}-{slugify(title)}.md"
    atomic_write(path, render_thread(thread))
    return public_thread(thread)


@locked_mutation
def reply_thread(
    project: str | Path,
    thread_id: str,
    *,
    author: str,
    message: str,
    message_type: str = "response",
) -> dict:
    path, thread = find_thread(project, thread_id)
    if thread.get("status") == "closed":
        raise ValueError("closed threads must be reopened before replying")
    author = validate_choice(author, AUTHORS, "author")
    message_type = validate_choice(message_type, MESSAGE_CONTENT_TYPES, "message type")
    now = timestamp()
    thread["messages"].append({
        "id": next_message_id(thread["messages"]),
        "author": author,
        "type": message_type,
        "created": now,
        "content": clean_text(message, "message"),
    })
    thread["updated"] = now
    atomic_write(path, render_thread(thread))
    return public_thread(thread)


@locked_mutation
def revise_user_message(
    project: str | Path,
    thread_id: str,
    message_id: str,
    *,
    author: str,
    action: str,
    message: str = "",
) -> dict:
    path, thread = find_thread(project, thread_id)
    if thread.get("status") == "closed":
        raise ValueError("closed threads must be reopened before changing messages")
    if validate_choice(author, AUTHORS, "author") != "user":
        raise ValueError("only the user may edit or retract user messages")
    action = validate_choice(action, MESSAGE_OPERATION_TYPES, "message action")
    if not MESSAGE_ID_PATTERN.fullmatch(message_id):
        raise ValueError(f"invalid message ID: {message_id}")
    target = next(
        (item for item in materialize_messages(thread["messages"]) if item.get("id") == message_id),
        None,
    )
    if not target or target.get("author") != "user":
        raise ValueError("only an existing user message may be changed")
    if target.get("retracted"):
        raise ValueError("a retracted message cannot be changed again")
    content = f"Target: {message_id}"
    if action == "edit":
        content += f"\n\n{clean_text(message, 'message')}"
    now = timestamp()
    thread["messages"].append({
        "id": next_message_id(thread["messages"]),
        "author": "user",
        "type": action,
        "created": now,
        "content": content,
    })
    thread["updated"] = now
    atomic_write(path, render_thread(thread))
    return public_thread(thread)


@locked_mutation
def transition_thread(
    project: str | Path,
    thread_id: str,
    *,
    author: str,
    status: str,
    message: str,
) -> dict:
    path, thread = find_thread(project, thread_id)
    author = validate_choice(author, AUTHORS, "author")
    status = validate_choice(status, THREAD_STATUSES, "thread status")
    if author != "user":
        raise ValueError("only the user may close or reopen a thread")
    if thread.get("status") == status:
        raise ValueError(f"thread is already {status}")
    now = timestamp()
    thread["messages"].append({
        "id": next_message_id(thread["messages"]),
        "author": author,
        "type": "decision" if status == "closed" else "update",
        "created": now,
        "content": clean_text(message, "message"),
    })
    thread["status"] = status
    thread["updated"] = now
    atomic_write(path, render_thread(thread))
    return public_thread(thread)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    listing = commands.add_parser("list")
    listing.add_argument("project")

    opening = commands.add_parser("open")
    opening.add_argument("project")
    opening.add_argument("--title", required=True)
    opening.add_argument("--author", choices=sorted(AUTHORS), required=True)
    opening.add_argument("--message", required=True)
    opening.add_argument("--type", choices=sorted(MESSAGE_CONTENT_TYPES))
    opening.add_argument("--priority", choices=sorted(PRIORITIES), default="normal")
    opening.add_argument("--category", choices=sorted(CATEGORIES), default="other")
    opening.add_argument("--context", default="")
    opening.add_argument("--benchmark", action="append", dest="benchmark_ids")
    opening.add_argument("--related", nargs="*")

    replying = commands.add_parser("reply")
    replying.add_argument("project")
    replying.add_argument("thread_id")
    replying.add_argument("--author", choices=sorted(AUTHORS), required=True)
    replying.add_argument("--message", required=True)
    replying.add_argument("--type", choices=sorted(MESSAGE_CONTENT_TYPES), default="response")

    editing = commands.add_parser("edit")
    editing.add_argument("project")
    editing.add_argument("thread_id")
    editing.add_argument("message_id")
    editing.add_argument("--author", choices=sorted(AUTHORS), required=True)
    editing.add_argument("--message", required=True)

    retracting = commands.add_parser("retract")
    retracting.add_argument("project")
    retracting.add_argument("thread_id")
    retracting.add_argument("message_id")
    retracting.add_argument("--author", choices=sorted(AUTHORS), required=True)

    transitioning = commands.add_parser("transition")
    transitioning.add_argument("project")
    transitioning.add_argument("thread_id")
    transitioning.add_argument("--author", choices=sorted(AUTHORS), required=True)
    transitioning.add_argument("--status", choices=sorted(THREAD_STATUSES), required=True)
    transitioning.add_argument("--message", required=True)

    args = parser.parse_args()
    if args.command == "list":
        result = load_mailbox(args.project)
    elif args.command == "open":
        result = create_thread(
            args.project, title=args.title, author=args.author, message=args.message,
            message_type=args.type, priority=args.priority,
            category=args.category, context=args.context,
            benchmark_ids=args.benchmark_ids, related=args.related,
        )
    elif args.command == "reply":
        result = reply_thread(
            args.project, args.thread_id, author=args.author, message=args.message,
            message_type=args.type,
        )
    elif args.command in {"edit", "retract"}:
        result = revise_user_message(
            args.project, args.thread_id, args.message_id, author=args.author,
            action="edit" if args.command == "edit" else "retraction",
            message=getattr(args, "message", ""),
        )
    else:
        result = transition_thread(
            args.project, args.thread_id, author=args.author, status=args.status,
            message=args.message,
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        raise SystemExit(str(error)) from error
