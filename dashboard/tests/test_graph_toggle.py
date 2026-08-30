from __future__ import annotations

import unittest
from pathlib import Path


APP_JS = Path(__file__).resolve().parents[1] / "frontend" / "static" / "js" / "app.js"
STYLE_CSS = Path(__file__).resolve().parents[1] / "frontend" / "static" / "css" / "style.css"


class GraphToggleTests(unittest.TestCase):
    def test_type_toggle_reuses_community_layout(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        handler_start = source.index("document.querySelectorAll('[data-graph-color]')")
        handler_end = source.index("document.querySelectorAll('[data-graph-action]')", handler_start)
        handler = source[handler_start:handler_end]

        self.assertIn("updateGraphColors()", handler)
        self.assertNotIn("graphLayout(", handler)
        self.assertNotIn("groupBy === 'type'", source)
        self.assertEqual(source.count("knowledgeGraphState.positions = graphLayout("), 1)
        self.assertIn("scicode-graph-layout:v10:community:", source)

    def test_wheel_zoom_uses_bounded_smooth_delta(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        wheel_start = source.index("byId('relation-graph').onwheel")
        wheel_end = source.index("\n  };", wheel_start)
        handler = source[wheel_start:wheel_end]

        self.assertIn("Math.max(-24, Math.min(24, event.deltaY))", handler)
        self.assertIn("Math.exp(wheelDelta * .0015)", handler)
        self.assertNotIn("event.deltaY < 0 ? .9 : 1.1", handler)

    def test_label_density_grows_quadratically_with_zoom(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        density_start = source.index("function graphUpdateLabelDensity")
        density_end = source.index("\n}\n", density_start)
        function = source[density_start:density_end]

        self.assertIn("const linearZoom = 980 / view.width", function)
        self.assertIn("10 * linearZoom * linearZoom", function)
        self.assertIn("Math.min(labels.length", function)
        self.assertIn("view.width <= 260", function)
        self.assertIn("? labels.length", function)
        self.assertIn("data-label-rank", source)
        self.assertIn("graphSpatialLabelRank(graph.nodes, positions)", source)

    def test_label_priority_balances_importance_and_spatial_coverage(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        rank_start = source.index("function graphSpatialLabelRank")
        rank_end = source.index("\n}\n\nfunction renderGraphSvg", rank_start)
        function = source[rank_start:rank_end]

        self.assertIn("node.importance_score ?? node.weighted_degree", function)
        self.assertIn("candidate.nearest", function)
        self.assertIn("Math.pow(importanceTerm, .6)", function)
        self.assertIn("Math.pow(spatialTerm, .4)", function)
        self.assertIn("ranked.set(chosen.node.id, selectedCount)", function)

    def test_labels_wrap_to_three_fixed_width_lines(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        wrap_start = source.index("function graphWrappedLabel")
        wrap_end = source.index("\n}\n\nfunction graphSpatialLabelRank", wrap_start)
        function = source[wrap_start:wrap_end]

        self.assertIn("lineWidth = 24", function)
        self.assertIn("maxLines = 3", function)
        self.assertIn("graphLabelWidth(word)", function)
        self.assertIn("graphTruncateLabelLine", function)
        self.assertIn("lines.slice(0, maxLines)", function)
        self.assertIn("lineWidth - 1)}…", function)
        self.assertIn("<tspan", source)

    def test_graph_supports_bounded_pointer_drag_panning(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")

        self.assertIn("function graphClampViewBox", source)
        self.assertIn("function graphBeginPan", source)
        self.assertIn("event.target.closest('[data-node-id]')", source)
        self.assertIn("function graphMovePan", source)
        self.assertIn("pan.view.x - deltaX", source)
        self.assertIn("function graphEndPan", source)
        self.assertIn("graphTarget.onpointercancel = graphEndPan", source)

    def test_label_outline_scales_with_label_text(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        styles_start = source.index("function graphApplyZoomInvariantStyles")
        styles_end = source.index("\n}\n\nfunction graphUpdateLabelDensity", styles_start)
        function = source[styles_start:styles_end]

        self.assertIn("9.5 * inverseZoom", function)
        self.assertIn("4 * inverseZoom", function)

    def test_graph_edges_have_visible_weight_hierarchy(self) -> None:
        source = APP_JS.read_text(encoding="utf-8")
        styles = STYLE_CSS.read_text(encoding="utf-8")

        self.assertIn("Math.min(1.25, .9 + edge.weight * .07)", source)
        self.assertIn("Math.min(1.55, 1.05 + edge.weight * .055)", source)
        self.assertIn("Math.min(1.35, .95 + edge.weight * .075)", source)
        self.assertIn("const strokeWidth = baseStrokeWidth", source)
        self.assertIn(".knowledge-edge.context.inferred { opacity:.32", styles)
        self.assertIn(".knowledge-edge.selected.inferred { opacity:.52", styles)
        self.assertIn(".knowledge-edge.selected.direct { opacity:.72", styles)
        self.assertIn(".knowledge-edge.selected.bridge { opacity:.82", styles)


if __name__ == "__main__":
    unittest.main()
