from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "lint_wiki.py"
SPEC = importlib.util.spec_from_file_location("lint_wiki", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ResolverCitationTests(unittest.TestCase):
    def resolver_ids(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "page.md"
            path.write_text(text, encoding="utf-8")
            return MODULE.resolver_citation_ids(path)

    def test_detects_bare_and_backticked_resolver_ids(self) -> None:
        ids = self.resolver_ids(
            "**Sources**: `global:paper:liu2025`; `benchmark:task`; source:registry-item\n"
        )
        self.assertEqual(
            ids,
            ["global:paper:liu2025", "benchmark:task", "source:registry-item"],
        )

    def test_ignores_fenced_documentation_examples(self) -> None:
        ids = self.resolver_ids(
            "```text\n**Sources**: `global:paper-id`; `benchmark:task`\n```\n"
            "[Readable source](../../papers/example/paper.pdf#page=2)\n"
        )
        self.assertEqual(ids, [])

    def test_dashboard_root_route_resolves_to_frontend_page(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            page = root / "wiki" / "papers" / "index.md"
            route = root / "dashboard" / "frontend" / "pages" / "papers.html"
            page.parent.mkdir(parents=True)
            route.parent.mkdir(parents=True)
            page.write_text("", encoding="utf-8")
            route.write_text("<!doctype html>", encoding="utf-8")

            self.assertEqual(
                MODULE.local_link_path(page, "/papers.html", root),
                route,
            )


if __name__ == "__main__":
    unittest.main()
