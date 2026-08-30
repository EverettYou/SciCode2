from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml
import numpy as np

from dashboard.backend.catalog_search import (
    CatalogVectorIndex,
    CatalogSearch,
    build_catalog_documents,
    hybrid_relevance_score,
    is_complex_query,
    lexical_score,
)
from scripts.llm import EmbeddingResult


class FakeEmbeddings:
    def __init__(self) -> None:
        self.settings = SimpleNamespace(model="fake-embedding")
        self.calls: list[list[str]] = []

    def embed(self, texts, *, task):
        self.calls.append(list(texts))
        vectors = []
        for text in texts:
            lowered = text.casefold()
            if "recovery" in lowered or "petz" in lowered:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return EmbeddingResult(vectors=vectors, model=self.settings.model)


class FakeCatalogSearch(CatalogSearch):
    def __init__(self, project_root: Path, embeddings: FakeEmbeddings) -> None:
        super().__init__(project_root)
        self.embeddings = embeddings

    def _dimensions(self) -> int:
        return 2

    def _embedding_runtime(self):
        return self.embeddings


class CatalogSearchTests(unittest.TestCase):
    def make_project(self, root: Path) -> None:
        (root / "papers").mkdir()
        (root / "benchmarks").mkdir()
        publications = [
            {
                "id": "petz2026",
                "title": "Local quantum recovery",
                "authors": [{"name": "A. Researcher"}],
                "year": 2026,
                "abstract": "Petz recovery and conditional mutual information.",
            },
            {
                "id": "flow2025",
                "title": "Neural renormalization flows",
                "authors": [{"name": "B. Researcher"}],
                "year": 2025,
                "abstract": "Flow models for statistical field theory.",
            },
        ]
        (root / "papers" / "papers.yml").write_text(
            yaml.safe_dump(publications, sort_keys=False), encoding="utf-8"
        )
        (root / "benchmarks" / "benchmarks.yml").write_text("[]\n", encoding="utf-8")

    def test_complex_query_detection_requires_constraints(self) -> None:
        self.assertTrue(is_complex_query("workstation feasible papers about quantum recovery"))
        self.assertFalse(is_complex_query("quantum recovery"))

    def test_exact_id_gets_strong_lexical_score(self) -> None:
        score, reason = lexical_score(
            "petz2026",
            {"entity_id": "petz2026", "title": "Local recovery", "text": "recovery"},
        )
        self.assertEqual(score, 20.0)
        self.assertIn("Exact", reason)

    def test_incidental_long_query_overlap_is_labeled_conceptual(self) -> None:
        score, reason = lexical_score(
            "fermions become massive without symmetry breaking",
            {
                "entity_id": "paper/example",
                "title": "A fermion model",
                "text": "A fermion model with unrelated numerical diagnostics.",
            },
        )
        self.assertLess(score, 1.5)
        self.assertEqual(reason, "Conceptually related")

    def test_conceptual_result_can_outrank_a_weak_keyword_hit(self) -> None:
        conceptual = hybrid_relevance_score(
            0.0, 0.90, semantic_floor=0.68, top_similarity=0.90
        )
        weak_keyword = hybrid_relevance_score(
            4.5, 0.80, semantic_floor=0.68, top_similarity=0.90
        )
        self.assertGreater(conceptual, weak_keyword)

    def test_strong_title_match_can_outrank_a_nearby_concept(self) -> None:
        conceptual = hybrid_relevance_score(
            0.0, 0.90, semantic_floor=0.68, top_similarity=0.90
        )
        strong_title = hybrid_relevance_score(
            10.5, 0.84, semantic_floor=0.68, top_similarity=0.90
        )
        self.assertGreater(strong_title, conceptual)

    def test_exact_title_is_protected_as_navigational_intent(self) -> None:
        exact = hybrid_relevance_score(
            20.0, 0.65, semantic_floor=0.68, top_similarity=0.90
        )
        conceptual = hybrid_relevance_score(
            0.0, 0.90, semantic_floor=0.68, top_similarity=0.90
        )
        self.assertGreater(exact, conceptual)

    def test_hybrid_ranking_interleaves_match_types_by_relevance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            search = FakeCatalogSearch(Path(directory), FakeEmbeddings())
            documents = [
                {
                    "search_id": "wiki:conceptual",
                    "entity_type": "wiki",
                    "entity_id": "conceptual",
                    "target": {"kind": "wiki", "page_id": "conceptual", "scope": "global"},
                    "title": "Interaction-enabled fermion gapping",
                    "stage": "active",
                    "text": "A mechanism that removes fermionic excitations without symmetry breaking.",
                },
                {
                    "search_id": "wiki:weak-keyword",
                    "entity_type": "wiki",
                    "entity_id": "weak-keyword",
                    "target": {"kind": "wiki", "page_id": "weak-keyword", "scope": "global"},
                    "title": "Mass inventory notes",
                    "stage": "active",
                    "text": "A generation counter used by the data pipeline.",
                },
            ]
            vectors = np.asarray([[0.90, 0.0], [0.80, 0.0]], dtype=np.float32)
            index = CatalogVectorIndex(
                vectors=vectors,
                row_by_key={"wiki:conceptual": 0, "wiki:weak-keyword": 1},
            )

            results = search._hybrid_results(
                "mass generation", documents, index, [1.0, 0.0], limit=10
            )

            self.assertEqual([item["entity_id"] for item in results], [
                "conceptual", "weak-keyword",
            ])
            self.assertEqual(results[0]["match_type"], "conceptual")
            self.assertEqual(results[1]["match_type"], "keyword-semantic")

    def test_hybrid_search_builds_index_and_reuses_query_embedding(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            embeddings = FakeEmbeddings()
            search = FakeCatalogSearch(root, embeddings)
            query = "workstation feasible papers about quantum recovery"

            first = search.search(query, scope="papers")
            second = search.search(query, scope="papers")

            self.assertEqual(first["results"][0]["entity_id"], "petz2026")
            self.assertEqual(first["results"][0]["search_id"], "paper:petz2026")
            self.assertEqual(
                first["results"][0]["target"],
                {"kind": "paper", "paper_id": "petz2026"},
            )
            self.assertEqual(first["results"][0]["match_type"], "keyword-semantic")
            self.assertTrue(first["complex_query"])
            self.assertEqual(second["results"][0]["entity_id"], "petz2026")
            self.assertEqual(len(embeddings.calls), 2)  # document batch, then one cached query
            self.assertTrue((root / ".tmp" / "catalog-search-metadata.json").is_file())
            self.assertTrue((root / ".tmp" / "catalog-search-vectors.npy").is_file())

    def test_paper_and_benchmark_scopes_share_hybrid_ranking(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            embeddings = FakeEmbeddings()
            search = FakeCatalogSearch(root, embeddings)
            documents = [
                {
                    "search_id": "paper:recovery-paper",
                    "entity_type": "paper",
                    "entity_id": "recovery-paper",
                    "target": {"kind": "paper", "paper_id": "recovery-paper"},
                    "title": "Local recovery channels",
                    "stage": "reviewed",
                    "linked": False,
                    "text": "Petz recovery for quantum states.",
                    "compact": "Petz recovery for quantum states.",
                },
                {
                    "search_id": "benchmark:recovery-task",
                    "entity_type": "benchmark",
                    "entity_id": "recovery-task",
                    "target": {"kind": "benchmark", "benchmark_id": "recovery-task"},
                    "title": "Recovery-map reconstruction",
                    "stage": "problem-opened",
                    "linked": False,
                    "text": "Reconstruct a Petz recovery map.",
                    "compact": "Reconstruct a Petz recovery map.",
                },
            ]

            paper_results = search.search(
                "quantum recovery", scope="papers", documents=documents
            )["results"]
            benchmark_results = search.search(
                "quantum recovery", scope="benchmarks", documents=documents
            )["results"]

            self.assertEqual(paper_results[0]["search_id"], "paper:recovery-paper")
            self.assertEqual(benchmark_results[0]["search_id"], "benchmark:recovery-task")
            self.assertIn("semantic_score", paper_results[0])
            self.assertIn("lexical_score", benchmark_results[0])

    def test_duplicate_source_ids_receive_stable_internal_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            publications = yaml.safe_load((root / "papers" / "papers.yml").read_text())
            publications.append({
                **publications[0],
                "title": "A distinct paper with a colliding source id",
                "abstract": "A different scientific record.",
            })
            (root / "papers" / "papers.yml").write_text(
                yaml.safe_dump(publications, sort_keys=False), encoding="utf-8"
            )

            first = build_catalog_documents(root)
            second = build_catalog_documents(root)
            first_keys = [document["search_id"] for document in first]

            self.assertEqual(first_keys, [document["search_id"] for document in second])
            self.assertEqual(len(first_keys), len(set(first_keys)))

    def test_legacy_json_migrates_without_deleting_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_project(root)
            documents = build_catalog_documents(root)
            legacy_entries = {}
            for document, vector in zip(documents, ([1.0, 0.0], [0.0, 1.0])):
                legacy_entries[document["search_id"]] = {
                    "fingerprint": hashlib.sha256(document["text"].encode()).hexdigest(),
                    "vector": vector,
                }
            legacy_path = root / ".tmp" / "catalog-search-index.json"
            legacy_path.parent.mkdir()
            legacy_path.write_text(json.dumps({
                "version": 1,
                "model": "fake-embedding",
                "dimensions": 2,
                "entries": legacy_entries,
            }))

            search = FakeCatalogSearch(root, FakeEmbeddings())
            metadata, index = search._load_index("fake-embedding", 2)

            self.assertTrue(legacy_path.exists())
            self.assertTrue(search.metadata_path.exists())
            self.assertTrue(search.vectors_path.exists())
            self.assertEqual(metadata["version"], 2)
            for key, entry in legacy_entries.items():
                np.testing.assert_allclose(
                    index.vectors[index.row_by_key[key]], entry["vector"]
                )


if __name__ == "__main__":
    unittest.main()
