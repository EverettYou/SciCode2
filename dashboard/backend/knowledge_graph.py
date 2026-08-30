"""Weighted wiki graph, communities, insights, and retrieval helpers."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import networkx as nx


STRUCTURAL_PAGE_TYPES = {"collection", "index"}
STRUCTURAL_PAGE_IDS = {"index", "log", "project/overview"}
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]*|[\u3400-\u9fff]+")
DIRECT_LINK_WEIGHT = 8.0
SOURCE_OVERLAP_WEIGHT = 2.0
COMMON_NEIGHBOR_WEIGHT = 1.5
TYPE_AFFINITY_WEIGHT = 0.25
DISPLAY_EDGE_MULTIPLIER = 1.75
EXTRA_DIRECT_EDGES_PER_NODE = 2
BRIDGES_PER_COMMUNITY_PAIR = 1
# Each pass starts with the same five easily distinguishable color families. The
# offset and tonal changes keep later communities distinct without a fixed-size
# palette or random colors that change between refreshes.
COMMUNITY_BASE_HUES = (4, 137, 48, 212, 278)  # red, green, yellow, blue, purple
COMMUNITY_LABEL_STOPWORDS = frozenset({
    "a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "via", "with",
    "analysis", "approach", "based", "construction", "effects", "intrinsically", "study", "using",
})


def _source_key(ref: str) -> str:
    path = str(ref).split("#", 1)[0].rstrip("/")
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] in {"papers", "benchmarks"}:
        return "/".join(parts[:2])
    return path


def _is_structural(page: dict[str, Any]) -> bool:
    return page["page_id"] in STRUCTURAL_PAGE_IDS or page["page_type"] in STRUCTURAL_PAGE_TYPES


def _edge_pair(edge: dict[str, Any]) -> tuple[str, str]:
    return tuple(sorted((edge["source"], edge["target"])))


def _tokens(value: str) -> set[str]:
    return {token.casefold() for token in TOKEN_PATTERN.findall(value)}


def _max_normalized(values: dict[str, float]) -> dict[str, float]:
    maximum = max(values.values(), default=0.0)
    if maximum <= 0:
        return {key: 0.0 for key in values}
    return {key: value / maximum for key, value in values.items()}


def _weighted_pagerank(graph: nx.Graph, iterations: int = 50, damping: float = 0.85) -> dict[str, float]:
    """Compute deterministic weighted PageRank without an optional SciPy dependency."""
    nodes = sorted(graph.nodes)
    if not nodes or graph.number_of_edges() == 0:
        return {node: 0.0 for node in nodes}
    count = len(nodes)
    scores = {node: 1.0 / count for node in nodes}
    strengths = dict(graph.degree(weight="weight"))
    for _ in range(iterations):
        dangling = sum(scores[node] for node in nodes if strengths.get(node, 0.0) <= 0)
        next_scores = {
            node: (1.0 - damping) / count + damping * dangling / count
            for node in nodes
        }
        for source in nodes:
            strength = strengths.get(source, 0.0)
            if strength <= 0:
                continue
            for target, attributes in graph[source].items():
                next_scores[target] += (
                    damping * scores[source] * float(attributes.get("weight", 1.0)) / strength
                )
        scores = next_scores
    return scores


def _importance_scores(
    graph: nx.Graph,
    edges: list[dict[str, Any]],
    weighted_degree: dict[str, float],
) -> dict[str, float]:
    direct_degree = {node: 0.0 for node in graph.nodes}
    for edge in edges:
        if edge["signals"]["direct"]:
            direct_degree[edge["source"]] += 1.0
            direct_degree[edge["target"]] += 1.0
    distance_graph = graph.copy()
    for _, _, attributes in distance_graph.edges(data=True):
        attributes["distance"] = 1.0 / max(float(attributes.get("weight", 1.0)), 1e-9)
    betweenness = nx.betweenness_centrality(
        distance_graph, weight="distance", normalized=True
    ) if graph.number_of_edges() else {node: 0.0 for node in graph.nodes}
    components = {
        "weighted_degree": _max_normalized(weighted_degree),
        "pagerank": _max_normalized(_weighted_pagerank(graph)),
        "betweenness": _max_normalized(betweenness),
        "direct_degree": _max_normalized(direct_degree),
    }
    return {
        node: (
            0.45 * components["weighted_degree"].get(node, 0.0)
            + 0.25 * components["pagerank"].get(node, 0.0)
            + 0.20 * components["betweenness"].get(node, 0.0)
            + 0.10 * components["direct_degree"].get(node, 0.0)
        )
        for node in graph.nodes
    }


def _community_color(community_id: int) -> str:
    """Return a stable, unbounded red/green/yellow/blue/purple color sequence."""
    cycle, family = divmod(community_id, len(COMMUNITY_BASE_HUES))
    variation = 0 if cycle == 0 else ((cycle * 137.508) % 42) - 21
    hue = (COMMUNITY_BASE_HUES[family] + variation) % 360
    saturation = 62 + ((cycle * 17) % 16)
    lightness = 42 + ((cycle * 11) % 14)
    return f"hsl({hue:.1f} {saturation}% {lightness}%)"


def _community_label(
    members: list[str], records: dict[str, dict[str, Any]], weighted_degree: dict[str, float]
) -> str:
    """Summarize a community as a compact, keyword-style category label."""
    topic_counts = Counter(
        topic
        for member in members
        for topic in [*records[member].get("topics", []), *records[member].get("project_topics", [])]
    )
    phrases: Counter[str] = Counter()
    phrase_forms: dict[str, str] = {}
    for member in members:
        title = records[member]["title"]
        words = [word for word in TOKEN_PATTERN.findall(title) if word.casefold() not in COMMUNITY_LABEL_STOPWORDS]
        seen = set()
        for width in (3, 2):
            for start in range(len(words) - width + 1):
                phrase = " ".join(words[start:start + width])
                key = phrase.casefold()
                if key not in seen:
                    phrases[key] += 1
                    phrase_forms.setdefault(key, phrase)
                    seen.add(key)

    recurring = [
        (count * (1.8 + len(key.split()) * .6), phrase_forms[key])
        for key, count in phrases.items() if count >= 2
    ]
    if recurring:
        # Repeated phrases describe the shared scientific subject more precisely
        # than a single central page title.
        return max(recurring, key=lambda item: (item[0], item[1].casefold()))[1]
    if topic_counts:
        ranked_topics = [topic for topic, _ in topic_counts.most_common(2)]
        return " · ".join(ranked_topics)
    top_member = max(members, key=lambda member: (weighted_degree.get(member, 0), records[member]["title"]))
    return records[top_member]["title"]


def _select_display_edges(
    graph: nx.Graph, edges: list[dict[str, Any]], community_by_node: dict[str, int]
) -> list[dict[str, Any]]:
    """Select an explainable sparse graph without collapsing it to a tree.

    The visible view keeps a connectivity backbone, then spends a bounded edge
    budget on direct wikilinks that expose local cycles and inter-community
    bridges. Inferred provenance/topology edges are fallback context only.
    """
    edge_by_pair = {_edge_pair(edge): edge for edge in edges}
    display_pairs: set[tuple[str, str]] = set()
    roles: dict[tuple[str, str], str] = {}
    for component in nx.connected_components(graph):
        tree = nx.maximum_spanning_tree(graph.subgraph(component), weight="weight")
        for source, target in tree.edges():
            pair = tuple(sorted((source, target)))
            display_pairs.add(pair)
            roles[pair] = "backbone"

    budget = min(len(edges), max(len(display_pairs), math.ceil(len(graph) * DISPLAY_EDGE_MULTIPLIER)))
    extra_count: Counter[str] = Counter()

    def rank(edge: dict[str, Any]) -> tuple[float, float, str, str]:
        source, target = edge["source"], edge["target"]
        cross_community = community_by_node[source] != community_by_node[target]
        common_neighbors = min(edge["signals"]["adamic_adar"], 2.0)
        loop_bonus = 2.25 * common_neighbors if not cross_community else 0.0
        bridge_bonus = 3.0 if cross_community else 0.0
        return (edge["weight"] + loop_bonus + bridge_bonus, edge["weight"], source, target)

    def add(edge: dict[str, Any], role: str, *, enforce_node_cap: bool = True) -> bool:
        pair = _edge_pair(edge)
        if pair in display_pairs or len(display_pairs) >= budget:
            return False
        source, target = edge["source"], edge["target"]
        if enforce_node_cap and (
            extra_count[source] >= EXTRA_DIRECT_EDGES_PER_NODE
            or extra_count[target] >= EXTRA_DIRECT_EDGES_PER_NODE
        ):
            return False
        display_pairs.add(pair)
        roles[pair] = role
        extra_count[source] += 1
        extra_count[target] += 1
        return True

    direct_candidates = [edge for edge in edges if edge["signals"]["direct"]]
    # Retain the strongest authored bridge for each linked community pair.
    bridges: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for edge in direct_candidates:
        source_community = community_by_node[edge["source"]]
        target_community = community_by_node[edge["target"]]
        if source_community != target_community:
            bridges[tuple(sorted((source_community, target_community)))].append(edge)
    for candidates in bridges.values():
        for edge in sorted(candidates, key=rank, reverse=True)[:BRIDGES_PER_COMMUNITY_PAIR]:
            add(edge, "bridge", enforce_node_cap=False)

    # Seed every sufficiently connected community with a direct local cycle.
    local_loops: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    for edge in direct_candidates:
        source_community = community_by_node[edge["source"]]
        if source_community == community_by_node[edge["target"]] and edge["signals"]["adamic_adar"] > 0:
            local_loops[source_community].append(edge)
    for candidates in local_loops.values():
        add(sorted(candidates, key=rank, reverse=True)[0], "loop")

    for edge in sorted(direct_candidates, key=rank, reverse=True):
        if len(display_pairs) >= budget:
            break
        role = "bridge" if community_by_node[edge["source"]] != community_by_node[edge["target"]] else "loop"
        add(edge, role)

    # Use inferred links only when authored relationships do not fill the budget.
    for edge in sorted((edge for edge in edges if not edge["signals"]["direct"]), key=rank, reverse=True):
        if len(display_pairs) >= budget:
            break
        add(edge, "inferred")

    selected = []
    for pair in sorted(display_pairs):
        edge = dict(edge_by_pair[pair])
        edge["display_role"] = roles[pair]
        selected.append(edge)
    return selected


def build_knowledge_graph(pages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the semantic graph using direct, provenance, topology, and type signals."""
    semantic_pages = [page for page in pages if not _is_structural(page)]
    records = {page["page_id"]: page for page in semantic_pages}
    page_ids = set(records)

    direct_edges: set[tuple[str, str]] = set()
    direct_neighbors: defaultdict[str, set[str]] = defaultdict(set)
    for page in semantic_pages:
        source = page["page_id"]
        for target in page.get("links", []):
            if target not in page_ids or target == source:
                continue
            edge = tuple(sorted((source, target)))
            direct_edges.add(edge)
            direct_neighbors[source].add(target)
            direct_neighbors[target].add(source)

    source_sets = {
        page_id: {_source_key(ref) for ref in page.get("source_refs", []) if _source_key(ref)}
        for page_id, page in records.items()
    }
    candidates = set(direct_edges)
    source_owners: defaultdict[str, list[str]] = defaultdict(list)
    for page_id, sources in source_sets.items():
        for source in sources:
            source_owners[source].append(page_id)
    # A source cited by many compiled pages is a provenance hub, not evidence that
    # every pair of those pages should be visually adjacent. Keep only small,
    # specific source groups from expanding into cliques.
    for owners in source_owners.values():
        if len(owners) <= 8:
            candidates.update(tuple(sorted(pair)) for pair in combinations(sorted(set(owners)), 2))
    for page_id, neighbors in direct_neighbors.items():
        if len(neighbors) <= 14:
            candidates.update(tuple(sorted(pair)) for pair in combinations(sorted(neighbors), 2))

    edges = []
    for source, target in sorted(candidates):
        shared_sources = source_sets[source] & source_sets[target]
        source_union = source_sets[source] | source_sets[target]
        source_overlap = len(shared_sources) / len(source_union) if source_union else 0.0
        common_neighbors = direct_neighbors[source] & direct_neighbors[target]
        adamic_adar = sum(
            1 / math.log(max(len(direct_neighbors[neighbor]), 2) + 1)
            for neighbor in common_neighbors
        )
        direct = 1.0 if (source, target) in direct_edges else 0.0
        type_affinity = 1.0 if records[source]["page_type"] == records[target]["page_type"] else 0.0
        # Authored wikilinks outrank inferred source/topology similarity.
        weight = (
            DIRECT_LINK_WEIGHT * direct
            + SOURCE_OVERLAP_WEIGHT * source_overlap
            + COMMON_NEIGHBOR_WEIGHT * min(adamic_adar, 2.0)
            + TYPE_AFFINITY_WEIGHT * type_affinity
        )
        if weight < 1.5:
            continue
        signals = {
            "direct": round(direct, 3),
            "source_overlap": round(source_overlap, 3),
            "adamic_adar": round(adamic_adar, 3),
            "type_affinity": round(type_affinity, 3),
        }
        reasons = []
        if direct:
            reasons.append("direct wikilink")
        if shared_sources:
            reasons.append(f"{len(shared_sources)} shared source{'s' if len(shared_sources) != 1 else ''}")
        if common_neighbors:
            reasons.append(f"{len(common_neighbors)} common neighbor{'s' if len(common_neighbors) != 1 else ''}")
        if type_affinity:
            reasons.append(f"same {records[source]['page_type']} type")
        edges.append({
            "source": source,
            "target": target,
            "weight": round(weight, 3),
            "signals": signals,
            "reasons": reasons,
        })

    graph = nx.Graph()
    graph.add_nodes_from(sorted(page_ids))
    graph.add_weighted_edges_from((edge["source"], edge["target"], edge["weight"]) for edge in edges)
    if graph.number_of_edges():
        detected = nx.community.louvain_communities(graph, weight="weight", resolution=1.05, seed=42)
    else:
        detected = [{page_id} for page_id in sorted(page_ids)]
    detected = sorted(detected, key=lambda group: (-len(group), sorted(group)[0]))
    community_by_node = {
        page_id: community_id
        for community_id, group in enumerate(detected)
        for page_id in group
    }
    display_edges = _select_display_edges(graph, edges, community_by_node)

    weighted_degree = dict(graph.degree(weight="weight"))
    importance_scores = _importance_scores(graph, edges, weighted_degree)
    nodes = []
    for page_id in sorted(page_ids):
        page = records[page_id]
        nodes.append({
            "id": page_id,
            "label": page["title"],
            "type": page["page_type"],
            "summary": page.get("summary", ""),
            "community": community_by_node[page_id],
            "degree": graph.degree(page_id),
            "weighted_degree": round(weighted_degree.get(page_id, 0.0), 3),
            "importance_score": round(importance_scores.get(page_id, 0.0), 4),
            "size": round(4.2 + min(8.5, math.sqrt(weighted_degree.get(page_id, 0.0)) * 1.45), 2),
        })

    communities = []
    for community_id, group in enumerate(detected):
        members = sorted(group)
        possible = len(members) * (len(members) - 1) / 2
        internal = graph.subgraph(members).number_of_edges()
        top_nodes = sorted(members, key=lambda node: (-weighted_degree.get(node, 0), records[node]["title"]))[:3]
        communities.append({
            "id": community_id,
            "color": _community_color(community_id),
            "label": _community_label(members, records, weighted_degree) if members else f"Community {community_id + 1}",
            "label_source": "local",
            "node_count": len(members),
            "cohesion": round(internal / possible, 3) if possible else 1.0,
            "top_nodes": top_nodes,
        })

    insights = _graph_insights(nodes, edges, communities)
    fingerprint_source = "|".join(node["id"] for node in nodes) + "::" + "|".join(
        f"{edge['source']}:{edge['target']}:{edge['weight']}" for edge in edges
    )
    return {
        "nodes": nodes,
        "edges": edges,
        "display_edges": display_edges,
        "communities": communities,
        "insights": insights,
        "fingerprint": hashlib.sha256(fingerprint_source.encode()).hexdigest()[:16],
        "model": {
            "signals": {
                "direct": DIRECT_LINK_WEIGHT,
                "source_overlap": SOURCE_OVERLAP_WEIGHT,
                "adamic_adar": COMMON_NEIGHBOR_WEIGHT,
                "type_affinity": TYPE_AFFINITY_WEIGHT,
            },
            "display_policy": {
                "edge_budget_multiplier": DISPLAY_EDGE_MULTIPLIER,
                "extra_direct_edges_per_node": EXTRA_DIRECT_EDGES_PER_NODE,
                "bridges_per_community_pair": BRIDGES_PER_COMMUNITY_PAIR,
                "strategy": "backbone + direct loops + direct bridges",
            },
            "community_detection": "Louvain",
            "label_importance": {
                "weighted_degree": 0.45,
                "pagerank": 0.25,
                "betweenness": 0.20,
                "direct_degree": 0.10,
            },
        },
    }


def _graph_insights(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], communities: list[dict[str, Any]]
) -> dict[str, list[dict[str, Any]]]:
    node_map = {node["id"]: node for node in nodes}
    graph = nx.Graph()
    graph.add_nodes_from(node_map)
    graph.add_weighted_edges_from((edge["source"], edge["target"], edge["weight"]) for edge in edges)

    # A prediction is specifically a relationship not written by an author. It
    # must have provenance or topology evidence; type affinity alone is never an
    # insight. Cross-community predictions rank slightly higher because they can
    # reveal a useful bridge, but same-community missing links remain eligible.
    predictions = []
    for edge in edges:
        signals = edge["signals"]
        if signals["direct"]:
            continue
        source = node_map[edge["source"]]
        target = node_map[edge["target"]]
        semantic_evidence = (
            SOURCE_OVERLAP_WEIGHT * signals["source_overlap"]
            + COMMON_NEIGHBOR_WEIGHT * min(signals["adamic_adar"], 2.0)
        )
        if semantic_evidence <= 0:
            continue
        cross_community = source["community"] != target["community"]
        predictions.append({
            "kind": "predicted-bridge" if cross_community else "predicted-link",
            "title": f"{source['label']} ↔ {target['label']}",
            "description": f"{', '.join(edge['reasons'])}; no authored wikilink",
            "score": round(semantic_evidence + (0.35 if cross_community else 0), 3),
            "node_ids": [source["id"], target["id"]],
        })
    predictions.sort(key=lambda item: (-item["score"], item["title"]))

    # Anomalies are review candidates, not automatic errors. They identify
    # structural exceptions to the graph's normal local organization.
    anomalies = []
    isolated = sorted((node for node in nodes if node["degree"] == 0), key=lambda node: node["label"])
    if isolated:
        anomalies.append({
            "kind": "isolated-nodes",
            "title": f"{len(isolated)} isolated page{'s' if len(isolated) != 1 else ''}",
            "description": ", ".join(node["label"] for node in isolated[:4]),
            "score": 3.0,
            "node_ids": [node["id"] for node in isolated],
        })

    community_map = {community["id"]: community for community in communities}
    cross_edges: defaultdict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        pair = tuple(sorted((node_map[edge["source"]]["community"], node_map[edge["target"]]["community"])))
        if pair[0] != pair[1]:
            cross_edges[pair].append(edge)
    audited_edges: set[tuple[str, str]] = set()
    for community_pair, pair_edges in cross_edges.items():
        if len(pair_edges) != 1 or not pair_edges[0]["signals"]["direct"]:
            continue
        edge = pair_edges[0]
        audited_edges.add(_edge_pair(edge))
        source = node_map[edge["source"]]
        target = node_map[edge["target"]]
        first, second = (community_map[community_id]["label"] for community_id in community_pair)
        support = edge["signals"]["source_overlap"] + min(edge["signals"]["adamic_adar"], 1.0)
        anomalies.append({
            "kind": "fragile-community-bridge",
            "title": f"Single bridge: {source['label']} ↔ {target['label']}",
            "description": f"Only connection between {first} and {second}; review whether the authored link is intentional",
            "score": round(2.5 - min(support, 1.5), 3),
            "node_ids": [source["id"], target["id"]],
        })

    # Authored cross-community edges with no provenance or common-neighbor
    # support are unusual even when another bridge exists between the clusters.
    for edge in edges:
        signals = edge["signals"]
        source = node_map[edge["source"]]
        target = node_map[edge["target"]]
        if (
            not signals["direct"]
            or source["community"] == target["community"]
            or signals["source_overlap"] > 0
            or signals["adamic_adar"] > 0
            or _edge_pair(edge) in audited_edges
        ):
            continue
        anomalies.append({
            "kind": "unsupported-authored-bridge",
            "title": f"Unusual link: {source['label']} ↔ {target['label']}",
            "description": "Authored cross-community link with no shared source or common-neighbor support",
            "score": 2.0,
            "node_ids": [source["id"], target["id"]],
        })

    for node in nodes:
        neighbors = list(graph.neighbors(node["id"]))
        if len(neighbors) < 3:
            continue
        total_weight = sum(graph[node["id"]][neighbor]["weight"] for neighbor in neighbors)
        external_weight = sum(
            graph[node["id"]][neighbor]["weight"]
            for neighbor in neighbors
            if node_map[neighbor]["community"] != node["community"]
        )
        external_ratio = external_weight / total_weight if total_weight else 0
        if external_ratio >= 0.75:
            anomalies.append({
                "kind": "community-outlier",
                "title": f"Community outlier: {node['label']}",
                "description": f"{external_ratio:.0%} of its connection weight points outside its assigned community",
                "score": round(1.0 + external_ratio, 3),
                "node_ids": [node["id"]],
            })
    anomalies.sort(key=lambda item: (-item["score"], item["title"]))
    return {"predicted_connections": predictions[:6], "graph_anomalies": anomalies[:8]}


def retrieve_pages(pages: list[dict[str, Any]], query: str, limit: int = 12) -> list[dict[str, Any]]:
    """Token retrieval with one-hop propagation over the weighted relevance graph."""
    query_tokens = _tokens(query)
    if not query_tokens:
        return []
    graph_payload = build_knowledge_graph(pages)
    nodes = {node["id"]: node for node in graph_payload["nodes"]}
    lexical: dict[str, float] = {}
    for page in pages:
        page_id = page["page_id"]
        title_hits = len(query_tokens & _tokens(page.get("title", "")))
        summary_hits = len(query_tokens & _tokens(page.get("summary", "")))
        topic_hits = len(query_tokens & _tokens(" ".join(map(str, [*page.get("topics", []), *page.get("project_topics", [])]))))
        path_hits = len(query_tokens & _tokens(page_id.replace("/", " ")))
        score = 4 * title_hits + 2 * summary_hits + 1.5 * topic_hits + path_hits
        if score:
            lexical[page_id] = score
    propagated: defaultdict[str, float] = defaultdict(float)
    for edge in graph_payload["edges"]:
        propagated[edge["target"]] += lexical.get(edge["source"], 0) * min(edge["weight"] / 8, 1) * 0.35
        propagated[edge["source"]] += lexical.get(edge["target"], 0) * min(edge["weight"] / 8, 1) * 0.35
    records = {page["page_id"]: page for page in pages}
    ranked = []
    for page_id in set(lexical) | set(propagated):
        if page_id not in records:
            continue
        total = lexical.get(page_id, 0) + propagated.get(page_id, 0)
        ranked.append({
            **{key: records[page_id].get(key) for key in ("page_id", "title", "page_type", "summary", "topics", "project_topics")},
            "score": round(total, 3),
            "token_score": round(lexical.get(page_id, 0), 3),
            "graph_score": round(propagated.get(page_id, 0), 3),
            "community": nodes.get(page_id, {}).get("community"),
        })
    return sorted(ranked, key=lambda item: (-item["score"], item["title"]))[:limit]
