from __future__ import annotations

import unittest

from dashboard.backend.knowledge_graph import _community_color, build_knowledge_graph, retrieve_pages


def page(page_id, title, page_type="concept", links=None, sources=None, summary=""):
    return {
        "page_id": page_id,
        "title": title,
        "page_type": page_type,
        "links": links or [],
        "source_refs": sources or [],
        "summary": summary,
        "topics": [],
    }


class KnowledgeGraphTests(unittest.TestCase):
    def setUp(self):
        self.pages = [
            page("index", "Index", "index", ["alpha", "beta"]),
            page("alpha", "Petz recovery", links=["beta"], sources=["papers/p1/paper.pdf"], summary="Recovery channel"),
            page("beta", "Finite Markov length", "method", links=["gamma"], sources=["papers/p1/paper.pdf"]),
            page("gamma", "Conditional mutual information", links=["alpha"], sources=["papers/p2/paper.pdf"]),
        ]

    def test_weighted_graph_excludes_structural_pages_and_explains_edges(self):
        graph = build_knowledge_graph(self.pages)
        self.assertEqual({node["id"] for node in graph["nodes"]}, {"alpha", "beta", "gamma"})
        edge = next(item for item in graph["edges"] if {item["source"], item["target"]} == {"alpha", "beta"})
        self.assertEqual(edge["signals"]["direct"], 1)
        self.assertGreater(edge["signals"]["source_overlap"], 0)
        self.assertIn("direct wikilink", edge["reasons"])
        self.assertLessEqual(len(graph["display_edges"]), len(graph["edges"]))
        self.assertEqual(graph["model"]["community_detection"], "Louvain")
        self.assertEqual(
            graph["model"]["label_importance"],
            {
                "weighted_degree": 0.45,
                "pagerank": 0.25,
                "betweenness": 0.20,
                "direct_degree": 0.10,
            },
        )
        self.assertTrue(all(0 <= node["importance_score"] <= 1 for node in graph["nodes"]))

    def test_graph_is_deterministic(self):
        first = build_knowledge_graph(self.pages)
        second = build_knowledge_graph(self.pages)
        self.assertEqual(first["fingerprint"], second["fingerprint"])
        self.assertEqual(first["communities"], second["communities"])

    def test_display_preserves_direct_cycle_instead_of_only_a_tree(self):
        pages = [
            page("alpha", "Alpha", links=["beta", "gamma"]),
            page("beta", "Beta", links=["gamma"]),
            page("gamma", "Gamma"),
        ]
        graph = build_knowledge_graph(pages)
        displayed = {frozenset((edge["source"], edge["target"])) for edge in graph["display_edges"]}
        self.assertEqual(
            displayed,
            {frozenset(("alpha", "beta")), frozenset(("alpha", "gamma")), frozenset(("beta", "gamma"))},
        )
        self.assertTrue(all(edge["signals"]["direct"] for edge in graph["display_edges"]))

    def test_display_policy_prioritizes_direct_links(self):
        graph = build_knowledge_graph(self.pages)
        self.assertGreater(graph["model"]["signals"]["direct"], graph["model"]["signals"]["source_overlap"])
        self.assertEqual(graph["model"]["display_policy"]["strategy"], "backbone + direct loops + direct bridges")

    def test_insights_separate_predictions_from_anomalies(self):
        pages = [
            page("alpha", "Alpha", links=["hub"], sources=["papers/shared/paper.pdf"]),
            page("beta", "Beta", links=["hub"], sources=["papers/shared/paper.pdf"]),
            page("hub", "Hub"),
            page("island", "Island"),
        ]
        insights = build_knowledge_graph(pages)["insights"]
        prediction = next(
            item for item in insights["predicted_connections"]
            if set(item["node_ids"]) == {"alpha", "beta"}
        )
        self.assertIn("no authored wikilink", prediction["description"])
        self.assertTrue(any(item["kind"] == "isolated-nodes" for item in insights["graph_anomalies"]))
        self.assertNotIn("surprising_connections", insights)
        self.assertNotIn("knowledge_gaps", insights)

    def test_community_colors_cycle_through_distinct_color_families(self):
        self.assertEqual(
            [_community_color(index) for index in range(5)],
            [
                "hsl(4.0 62% 42%)", "hsl(137.0 62% 42%)", "hsl(48.0 62% 42%)",
                "hsl(212.0 62% 42%)", "hsl(278.0 62% 42%)",
            ],
        )
        self.assertEqual(len({_community_color(index) for index in range(50)}), 50)

    def test_retrieval_combines_token_and_graph_scores(self):
        results = retrieve_pages(self.pages, "Petz recovery")
        self.assertEqual(results[0]["page_id"], "alpha")
        self.assertGreater(results[0]["token_score"], 0)
        self.assertTrue(any(result["graph_score"] > 0 for result in results))


if __name__ == "__main__":
    unittest.main()
