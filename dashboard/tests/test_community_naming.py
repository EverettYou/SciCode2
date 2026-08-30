from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from dashboard.backend.community_naming import community_evidence, enrich_community_labels


class FakeResponses:
    def __init__(self, output):
        self.output = output
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(output_text=json.dumps(self.output))


class FakeClient:
    def __init__(self, responses):
        self.responses = responses


def sample_graph():
    return {
        "nodes": [
            {"id": "project/loop", "label": "Research loop", "community": 0, "weighted_degree": 8.0},
            {"id": "project/skills", "label": "Reusable skills", "community": 0, "weighted_degree": 5.0},
        ],
        "communities": [{"id": 0, "label": "Research loop", "label_source": "local"}],
    }


def sample_pages():
    return [
        {
            "page_id": "project/loop", "title": "Research loop", "page_type": "project",
            "summary": "Agents turn compiled knowledge into discriminating experiments.", "topics": [],
            "project_topics": ["Autonomous Research Workflows", "Agentic Research Infrastructure"],
        },
        {
            "page_id": "project/skills", "title": "Reusable skills", "page_type": "project",
            "summary": "Reusable procedures coordinate acquisition, research, and validation.", "topics": [],
            "project_topics": ["Agentic Research Infrastructure"],
        },
    ]


class CommunityNamingTests(unittest.TestCase):
    def test_evidence_keeps_project_topics_separate(self):
        evidence = community_evidence(sample_graph(), sample_pages(), sample_graph()["communities"][0])
        self.assertIn("Scientific topics: none", evidence)
        self.assertIn("Project topics: Agentic Research Infrastructure (2)", evidence)
        self.assertIn("summary=Agents turn compiled knowledge", evidence)

    def test_structured_label_is_cached_by_evidence(self):
        responses = FakeResponses({
            "labels": [{"community_id": 0, "label": "Agentic Research Infrastructure"}],
        })
        with tempfile.TemporaryDirectory() as directory:
            cache_path = Path(directory) / "labels.json"
            graph = sample_graph()
            stats = enrich_community_labels(
                graph, sample_pages(), cache_path=cache_path, api_key="test-key",
                client_factory=lambda **_: FakeClient(responses),
            )
            self.assertEqual(stats, {"cached": 0, "generated": 1, "fallback": 0})
            self.assertEqual(graph["communities"][0]["label"], "Agentic Research Infrastructure")
            self.assertFalse(responses.calls[0]["store"])
            self.assertEqual(responses.calls[0]["text"]["format"]["type"], "json_schema")

            cached_graph = sample_graph()
            cached = enrich_community_labels(
                cached_graph, sample_pages(), cache_path=cache_path, api_key="test-key",
                client_factory=lambda **_: self.fail("cache hit should not create a client"),
            )
            self.assertEqual(cached, {"cached": 1, "generated": 0, "fallback": 0})
            self.assertEqual(cached_graph["communities"][0]["label_source"], "openai-cache")


if __name__ == "__main__":
    unittest.main()
