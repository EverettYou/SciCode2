from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from dashboard import server


class FakeCatalogSearch:
    def __init__(self) -> None:
        self.calls = []

    def search(self, query, **kwargs):
        self.calls.append((query, kwargs))
        return {"query": query, "results": [], **kwargs}


class FakeWikiSearch:
    def __init__(self) -> None:
        self.calls = []

    def search(self, query, **kwargs):
        self.calls.append((query, kwargs))
        return {
            "query": query,
            "scope": "wiki",
            "mode": "hybrid",
            "complex_query": False,
            "results": [{
                "search_id": "wiki:global:project/example",
                "entity_type": "wiki",
                "entity_id": "project/example",
                "target": {"kind": "wiki", "page_id": "project/example", "scope": "global"},
                "title": "Example",
                "stage": "active",
                "score": 0.02,
                "match_type": "conceptual",
            }],
        }


class CatalogSearchApiTests(unittest.TestCase):
    def test_benchmark_catalog_is_derived_from_canonical_index(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            benchmarks_root = Path(directory)
            (benchmarks_root / "alpha-benchmark" / "wiki").mkdir(parents=True)
            (benchmarks_root / "alpha-benchmark" / "wiki" / "index.md").write_text("# Alpha")
            entries = {
                "alpha-benchmark": {"benchmark_id": "alpha-benchmark", "title": "Alpha benchmark"},
                "beta-benchmark": {"benchmark_id": "beta-benchmark", "title": "Beta benchmark"},
            }
            with patch.object(server, "BENCHMARKS_ROOT", benchmarks_root), patch.object(
                server, "benchmark_index", return_value=entries
            ):
                rendered = server.benchmark_catalog_markdown()

        self.assertIn("**Alpha benchmark**", rendered)
        self.assertIn("/wiki.html?scope=benchmark%3Aalpha-benchmark&page=index", rendered)
        self.assertIn("/benchmark.html?id=alpha-benchmark", rendered)
        self.assertIn("**Beta benchmark**", rendered)
        self.assertIn("(wiki unavailable)", rendered)
        self.assertIn("/benchmark.html?id=beta-benchmark", rendered)

    def test_wiki_fallback_distinguishes_token_hits_from_graph_relations(self) -> None:
        records = [
            {
                "page_id": "alpha", "title": "Petz recovery", "page_type": "concept",
                "status": "active", "summary": "Recovery channel", "topics": [],
                "project_topics": [], "source_refs": [], "links": ["beta"],
            },
            {
                "page_id": "beta", "title": "Finite Markov length", "page_type": "method",
                "status": "active", "summary": "", "topics": [], "project_topics": [],
                "source_refs": [], "links": [],
            },
        ]

        results = server.wiki_fallback_results(records, "Petz recovery", "global", 10)
        by_id = {item["entity_id"]: item for item in results}

        self.assertEqual(by_id["alpha"]["match_type"], "keyword-semantic")
        self.assertEqual(by_id["beta"]["match_type"], "conceptual")
        self.assertGreater(by_id["beta"]["semantic_score"], 0)

    def test_wiki_navigation_kind_is_shared_across_catalog_shapes(self) -> None:
        self.assertEqual(server.wiki_navigation_kind("index", "reference"), "catalog")
        self.assertEqual(server.wiki_navigation_kind("papers/index", "reference"), "catalog")
        self.assertEqual(server.wiki_navigation_kind("benchmarks", "collection"), "catalog")
        self.assertEqual(server.wiki_navigation_kind("concepts/example", "concept"), "page")

    def test_wiki_search_ids_include_scope(self) -> None:
        self.assertEqual(
            server.wiki_search_id("global", "thesis"),
            "wiki:global:thesis",
        )
        self.assertEqual(
            server.wiki_search_id("benchmark:example-benchmark", "thesis"),
            "wiki:benchmark:example-benchmark:thesis",
        )

    def test_semantic_search_requires_explicit_opt_in(self) -> None:
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENAI_CATALOG_SEARCH_ENABLED", None)
            with self.assertRaises(HTTPException) as raised:
                server.search_catalog("quantum recovery")
        self.assertEqual(raised.exception.status_code, 503)

    def test_enabled_route_passes_validated_parameters(self) -> None:
        fake = FakeCatalogSearch()
        with patch.dict(os.environ, {"OPENAI_CATALOG_SEARCH_ENABLED": "true"}), patch.object(
            server, "CATALOG_SEARCH", fake
        ):
            result = server.search_catalog(
                "  workstation   recovery  ",
                scope="papers",
                stage="reviewed",
                limit=12,
                refine=True,
            )
        self.assertEqual(result["query"], "workstation recovery")
        self.assertEqual(fake.calls[0][1]["stage"], "reviewed")
        self.assertTrue(fake.calls[0][1]["refine"])

    def test_wiki_search_uses_semantic_documents_when_enabled(self) -> None:
        fake = FakeWikiSearch()
        with patch.dict(os.environ, {"OPENAI_CATALOG_SEARCH_ENABLED": "true"}), patch.object(
            server, "WIKI_SEARCH", fake
        ):
            result = server.search_wiki("quality generation", limit=8, refine=True)
        self.assertEqual(result["scope"], "global")
        self.assertEqual(result["results"][0]["entity_id"], "project/example")
        self.assertEqual(result["results"][0]["target"]["page_id"], "project/example")
        server.SearchResponsePayload.model_validate(result)
        self.assertEqual(fake.calls[0][1]["scope"], "wiki")
        self.assertTrue(fake.calls[0][1]["refine"])
        self.assertTrue(fake.calls[0][1]["documents"])


if __name__ == "__main__":
    unittest.main()
