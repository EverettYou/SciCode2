#!/usr/bin/env python3
"""Search arXiv or archive one arXiv paper with provenance metadata."""

import argparse
import hashlib
import json
import os
import re
import shutil
import ssl
import tarfile
import tempfile
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

import certifi

API = "https://export.arxiv.org/api/query"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
PAPER_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ARXIV_ID_PATTERN = re.compile(
    r"^(?:\d{4}\.\d{4,5}(?:v\d+)?|[A-Za-z-]+(?:\.[A-Za-z-]+)?/\d{7}(?:v\d+)?)$"
)
REQUIRED_FILES = ("paper.pdf", "source.tar", "provenance.json")


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "SciCode2-fetch-paper/0.1"})
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(request, timeout=45, context=context) as response:
        return response.read()


def validate_identifiers(arxiv_id, paper_id):
    if not ARXIV_ID_PATTERN.fullmatch(arxiv_id):
        raise ValueError(
            "Invalid arXiv identifier. Use a form such as 2411.03285 or hep-th/9901001."
        )
    if not PAPER_ID_PATTERN.fullmatch(paper_id):
        raise ValueError(
            "Invalid paper ID. Use only letters, digits, periods, underscores, and hyphens."
        )


def search(query, limit):
    params = urllib.parse.urlencode({"search_query": f"all:{query}", "max_results": limit})
    root = ElementTree.fromstring(get(f"{API}?{params}"))
    results = []
    for entry in root.findall("a:entry", ATOM):
        identifier = entry.findtext("a:id", namespaces=ATOM, default="").rsplit("/abs/", 1)[-1]
        results.append({
            "id": identifier,
            "title": " ".join((entry.findtext("a:title", namespaces=ATOM, default="") or "").split()),
            "published": entry.findtext("a:published", namespaces=ATOM),
            "url": entry.findtext("a:id", namespaces=ATOM),
            "abstract": " ".join((entry.findtext("a:summary", namespaces=ATOM, default="") or "").split()),
        })
    print(json.dumps(results, indent=2, ensure_ascii=False))


def download(arxiv_id, output_root, extract_source, paper_id=None):
    paper_id = paper_id or re.sub(r"[^a-zA-Z0-9._-]", "_", arxiv_id)
    validate_identifiers(arxiv_id, paper_id)

    output_root = Path(output_root).resolve()
    folder = output_root / paper_id
    if folder.exists():
        if not folder.is_dir():
            raise FileExistsError(f"Target path is not a directory: {folder}")
        if all((folder / filename).is_file() for filename in REQUIRED_FILES):
            print(folder)
            return
        raise FileExistsError(
            f"Target directory exists but is incomplete: {folder}. Resolve it before retrying."
        )

    staging_root = output_root.parent / ".tmp"
    staging_root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f"fetch-{paper_id}-", dir=staging_root))
    files = {
        "paper.pdf": f"https://arxiv.org/pdf/{arxiv_id}",
        "source.tar": f"https://arxiv.org/src/{arxiv_id}",
    }
    try:
        checksums = {}
        for filename, url in files.items():
            payload = get(url)
            if not payload:
                raise RuntimeError(f"Downloaded an empty file: {url}")
            destination = staging / filename
            destination.write_bytes(payload)
            checksums[filename] = hashlib.sha256(payload).hexdigest()
        if extract_source:
            source_dir = staging / "source"
            source_dir.mkdir()
            with tarfile.open(staging / "source.tar") as archive:
                archive.extractall(source_dir)
        metadata = {
            "arxiv_id": arxiv_id,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
            "urls": {"abstract": f"https://arxiv.org/abs/{arxiv_id}", **files},
            "sha256": checksums,
        }
        (staging / "provenance.json").write_text(json.dumps(metadata, indent=2) + "\n")
        if not all((staging / filename).is_file() for filename in REQUIRED_FILES):
            raise RuntimeError("Staged download is incomplete.")
        if folder.exists():
            raise FileExistsError(f"Target directory was created while downloading: {folder}")
        output_root.mkdir(parents=True, exist_ok=True)
        os.replace(staging, folder)
        staging = None
        print(folder)
    finally:
        if staging is not None:
            shutil.rmtree(staging, ignore_errors=True)


parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)
search_parser = subparsers.add_parser("search")
search_parser.add_argument("query")
search_parser.add_argument("--limit", type=int, default=10)
download_parser = subparsers.add_parser("download")
download_parser.add_argument("arxiv_id")
download_parser.add_argument("--output-root", default="papers")
download_parser.add_argument("--extract-source", action="store_true")
download_parser.add_argument("--paper-id", help="Project-local folder name, such as he2026smgia")
args = parser.parse_args()
if args.command == "search":
    search(args.query, args.limit)
else:
    try:
        download(args.arxiv_id, args.output_root, args.extract_source, args.paper_id)
    except (FileExistsError, RuntimeError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
