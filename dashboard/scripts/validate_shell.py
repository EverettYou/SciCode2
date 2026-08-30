#!/usr/bin/env python3
"""Verify every dashboard page mounts the shared client-side shell."""

from __future__ import annotations

from pathlib import Path


DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = DASHBOARD_ROOT / "frontend" / "pages"
STATIC_ROOT = DASHBOARD_ROOT / "frontend" / "static"
HEADER_MOUNT = '<div id="site-header"></div>'
SHELL_SCRIPT_PREFIX = 'src="../static/js/site-shell.js'


def main() -> None:
    pages = sorted(PAGES_ROOT.glob("*.html"))
    for page_path in pages:
        source = page_path.read_text(encoding="utf-8")
        if source.count(HEADER_MOUNT) != 1:
            raise SystemExit(f"{page_path.name} must contain one shared-header mount")
        if source.count(SHELL_SCRIPT_PREFIX) != 1:
            raise SystemExit(f"{page_path.name} must load the shared site shell")
        if source.count('src="../static/js/redirect-to-dashboard.js"') != 1:
            raise SystemExit(f"{page_path.name} must use the shared local-file redirect")
        if '<header class="site-header">' in source:
            raise SystemExit(f"{page_path.name} contains a page-local site header")

    if not (STATIC_ROOT / "js" / "site-shell.js").is_file():
        raise SystemExit("missing shared site shell")
    print(f"Validated shared dashboard shell for {len(pages)} pages")


if __name__ == "__main__":
    main()
