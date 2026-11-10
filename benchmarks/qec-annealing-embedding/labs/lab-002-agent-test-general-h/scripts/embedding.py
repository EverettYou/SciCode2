"""Checked reusable minor embeddings and coefficient allocation on ideal Zephyr.

No QPU access.  A checked K_capacity minor is a universal *sufficient* template,
not a claim that larger inputs cannot fit. All model vertices include isolates.
Integer logical and target labels are the portable witness format.
"""
from __future__ import annotations

from collections import deque
from fractions import Fraction
import importlib.metadata
import math
import time

import networkx as nx
import minorminer
from minorminer.busclique import find_clique_embedding

try:
    import dwave.graphs as dwave_graphs
    GRAPH_PACKAGE = "dwave-graphs"
    GRAPH_MODULE = "dwave.graphs"
except ImportError:
    import dwave_networkx as dwave_graphs
    GRAPH_PACKAGE = "dwave-networkx"
    GRAPH_MODULE = "dwave_networkx"


def versions():
    names = ["networkx", "numpy", "minorminer", "dimod", GRAPH_PACKAGE, "dwave-system"]
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def _ordered_target_edges(target):
    """Canonical edges in O(g²) for standard integer Zephyr, bounded degree.

    Scanning the full ideal label interval also supports deleted target qubits.
    Other graphs use a generic O(V log V + sum d log d) ordered traversal.
    """
    if target.graph.get("family") == "zephyr" and target.graph.get("labels") == "int":
        g, t = target.graph["rows"], target.graph["tile"]
        nodes = range(4*t*g*(2*g+1))
    else:
        nodes = sorted(target.nodes)
    for q in nodes:
        if q in target:
            for r in sorted(target[q]):
                if q < r:
                    yield q, r


def make_target(g=6, t=4):
    if not isinstance(g, int) or g < 1 or not isinstance(t, int) or t < 1:
        raise ValueError("g and t must be positive integers")
    target = dwave_graphs.zephyr_graph(g, t=t)
    target.graph["trial_generator"] = GRAPH_MODULE + ".zephyr_graph"
    target.graph["trial_generator_version"] = importlib.metadata.version(GRAPH_PACKAGE)
    target.graph["trial_parameters"] = {"g": g, "t": t, "coordinates": False}
    return target


def graph_witness(graph):
    return {"nodes": sorted(graph.nodes),
            "edges": [list(e) for e in sorted(edge_key(u, v) for u, v in graph.edges)],
            "metadata": dict(graph.graph)}


def graph_from_witness(witness):
    graph = nx.Graph()
    graph.graph.update(witness.get("metadata", {}))
    graph.add_nodes_from(witness["nodes"])
    graph.add_edges_from(witness["edges"])
    return graph


def verify_embedding(source, target, embedding):
    """Independent explicit check in O(|E_T|+|V_T|+|E_S|).

    Does not invoke minorminer, dwave.embedding, or trust source edges alone.
    """
    errors = []
    if set(embedding) != set(source):
        errors.append({"kind": "variable_set", "missing": sorted(set(source) - set(embedding)),
                       "extra": sorted(set(embedding) - set(source))})
    owner = {}
    for v in source:
        chain = list(embedding.get(v, []))
        if not chain:
            errors.append({"kind": "empty_chain", "variable": v})
            continue
        if len(set(chain)) != len(chain):
            errors.append({"kind": "duplicate_in_chain", "variable": v})
        known = set(chain) & target.nodes
        unknown = set(chain) - target.nodes
        if unknown:
            errors.append({"kind": "unknown_qubits", "variable": v, "qubits": sorted(unknown)})
        for q in known:
            if q in owner:
                errors.append({"kind": "overlap", "qubit": q, "variables": [owner[q], v]})
            owner[q] = v
        if known:
            reached, queue = {next(iter(known))}, deque([next(iter(known))])
            while queue:
                q = queue.popleft()
                for r in target[q]:
                    if r in known and r not in reached:
                        reached.add(r)
                        queue.append(r)
            if reached != known:
                errors.append({"kind": "disconnected_chain", "variable": v})
    realized = set()
    for q, r in target.edges:
        if q in owner and r in owner and owner[q] != owner[r]:
            realized.add(edge_key(owner[q], owner[r]))
    for u, v in source.edges:
        if u == v:
            errors.append({"kind": "self_loop", "variable": u})
        elif edge_key(u, v) not in realized:
            errors.append({"kind": "missing_coupler", "variables": [u, v]})
    lengths = [len(embedding.get(v, [])) for v in source]
    return {"valid": not errors, "errors": errors, "logical_variables": len(source),
            "logical_edges": source.number_of_edges(), "physical_qubits": len(owner),
            "chain_max": max(lengths, default=0),
            "chain_mean": sum(lengths) / len(lengths) if lengths else 0.0}


def tree_edges(target, chain):
    chain = set(chain)
    if not chain:
        raise ValueError("empty chain")
    root = min(chain)
    seen, queue, edges = {root}, deque([root]), []
    while queue:
        q = queue.popleft()
        for r in sorted(target[q]):
            if r in chain and r not in seen:
                seen.add(r)
                queue.append(r)
                edges.append(edge_key(q, r))
    if seen != chain:
        raise ValueError("disconnected chain")
    return edges


class CliqueTemplate:
    """Precompute one checked clique minor and fixed contacts for every pair.

    For a fixed verified target/template, every graph with N <= capacity is
    guaranteed a valid embedding.  Capacity failure says nothing about whether
    a different embedding fits.  With prune=True, keep the unique minimal
    subtree of the fixed branch tree spanning this input graph's contacts.
    """
    def __init__(self, target, capacity=None, seed=7, engine="tracks"):
        started = time.perf_counter()
        if engine not in ("native", "tracks"):
            raise ValueError("engine must be native or tracks")
        if capacity is None:
            if target.graph.get("family") != "zephyr":
                raise ValueError("an explicit capacity is required for other targets")
            g, t = target.graph["rows"], target.graph["tile"]
            capacity = 16*g+1 if engine == "tracks" and g >= 2 and t == 4 else max(1, 2 * (2 * g - 1) * t)
        self.target = target
        self.capacity = int(capacity)
        self.seed = seed
        if self.capacity < 1:
            raise ValueError("capacity must be positive")
        # use_cache=False avoids unrecorded/persistent application cache state.
        # minorminer 0.2.21's uncached g=1 clique routine stalled in this run.
        # Use the explicit interior K_(2t,2t) matching contraction for this case.
        if target.graph.get("family") == "zephyr" and target.graph.get("rows") == 1:
            t = target.graph["tile"]
            if self.capacity > 2*t:
                raise ValueError("g=1 explicit template capacity exceeded; not infeasibility")
            if target.graph.get("labels") != "int":
                raise ValueError("g=1 explicit template requires integer target labels")
            f = dwave_graphs.zephyr_coordinates(1, t=t).zephyr_to_linear
            self.branches = {2*k+j:(f((0,1,k,j,0)), f((1,1,k,j,0)))
                             for k in range(t) for j in range(2) if 2*k+j<self.capacity}
            self.construction = "explicit interior bipartite matching contraction"
        elif engine == "tracks":
            if (target.graph.get("family") != "zephyr" or target.graph.get("tile") != 4
                    or target.graph.get("labels") != "int"):
                raise ValueError("explicit tracks require integer-labeled Zephyr with t=4")
            g = target.graph["rows"]
            if self.capacity > 16*g+1:
                raise ValueError("explicit track capacity exceeded; not an infeasibility certificate")
            # Boothby, King, Raymond (2021), Section 5.1, descriptors A--E.
            descriptors = [[(0,3,0,0)], [(1,3,0,0)]]
            descriptors += [[(0,w,k,1),(1,w,k,1)] for w in range(1,3) for k in range(4)]
            descriptors += [[(0,0,k,j),(1,1+j,k,0)] for k in range(4) for j in range(2)]
            descriptors += [[(0,1+j,k,0),(1,0,k,j)] for k in range(4) for j in range(2)]
            descriptors += [[(0,w,k,j),(1,w,k,j)] for w in range(3,2*g)
                            for k in range(4) for j in range(2) if w+k+j>3]
            assert len(descriptors) == 16*g+1
            f = dwave_graphs.zephyr_coordinates(g,t=4).zephyr_to_linear
            self.branches = {i:tuple(f((*track,z)) for track in descriptor for z in range(g))
                             for i,descriptor in enumerate(descriptors[:self.capacity])}
            self.construction = "explicit Zephyr track descriptors A-E, Boothby et al. Section 5.1"
        else:
            self.branches = {v: tuple(c) for v, c in find_clique_embedding(
                self.capacity, target, seed=seed, use_cache=False).items()}
            self.construction = "minorminer.busclique.find_clique_embedding"
        complete = nx.complete_graph(self.capacity)
        self.validation = verify_embedding(complete, target, self.branches)
        if not self.validation["valid"]:
            raise ValueError("native template construction failed; not an infeasibility certificate")
        self.trees = {v: tree_edges(target, c) for v, c in self.branches.items()}
        owner = {q: v for v, chain in self.branches.items() for q in chain}
        self.contacts = {}
        for q, r in _ordered_target_edges(target):
            if q in owner and r in owner and owner[q] != owner[r]:
                a, b = owner[q], owner[r]
                pair = edge_key(a, b)
                oriented = (q, r) if a < b else (r, q)
                self.contacts.setdefault(pair, oriented)
        assert len(self.contacts) == self.capacity * (self.capacity - 1) // 2
        self.preprocessing_seconds = time.perf_counter() - started

    def embed(self, source, prune=True):
        nodes = sorted(source.nodes)
        if len(nodes) > self.capacity:
            raise ValueError("template_capacity_exceeded: sufficient regime only; not infeasible")
        index = {v: i for i, v in enumerate(nodes)}
        if not prune:
            return {v: list(self.branches[index[v]]) for v in nodes}
        terminals = {i: set() for i in range(len(nodes))}
        for u, v in source.edges:
            if u == v:
                raise ValueError("quadratic interaction graph cannot contain self loops")
            a, b = sorted((index[u], index[v]))
            q, r = self.contacts[(a, b)]
            terminals[a].add(q)
            terminals[b].add(r)
        result = {}
        for v in nodes:
            i = index[v]
            if not terminals[i]:
                result[v] = [min(self.branches[i])]
                continue
            adjacency = {q: set() for q in self.branches[i]}
            for q, r in self.trees[i]:
                adjacency[q].add(r)
                adjacency[r].add(q)
            leaves = deque(q for q, nbrs in adjacency.items()
                           if len(nbrs) <= 1 and q not in terminals[i])
            while leaves:
                q = leaves.popleft()
                if q not in adjacency:
                    continue
                for r in adjacency[q]:
                    adjacency[r].remove(q)
                    if len(adjacency[r]) <= 1 and r not in terminals[i]:
                        leaves.append(r)
                del adjacency[q]
            result[v] = [q for q in self.branches[i] if q in adjacency]
        return result

    def witness(self):
        return {"capacity": self.capacity, "seed": self.seed,
                "construction": self.construction,
                "branches": {str(v): list(c) for v, c in self.branches.items()},
                "trees": {str(v): [list(e) for e in es] for v, es in self.trees.items()},
                "contacts": [[a, b, q, r] for (a, b), (q, r) in sorted(self.contacts.items())],
                "validation": self.validation, "preprocessing_seconds": self.preprocessing_seconds,
                "use_cache": False}


def find_automatic_embedding(source, target, seed=7, timeout=10.0, tries=10):
    """Generic minorminer reference, followed by isolate placement and checking.

    Counting violations are certified obstructions; exhausted search is heuristic.
    """
    started = time.perf_counter()
    obstructions = []
    if len(source) > len(target):
        obstructions.append("logical node count exceeds target node count")
    if source.number_of_edges() > target.number_of_edges():
        obstructions.append("logical edge count exceeds target edge count")
    if obstructions:
        return {"status": "certified_resource_obstruction", "obstructions": obstructions,
                "embedding": {}, "elapsed_seconds": time.perf_counter() - started}
    active = source.subgraph([v for v in source if source.degree[v] > 0]).copy()
    embedding = minorminer.find_embedding(active, target, random_seed=seed,
                                         timeout=timeout, tries=tries) if active else {}
    if active and not embedding:
        return {"status": "heuristic_failure", "embedding": {},
                "elapsed_seconds": time.perf_counter() - started}
    occupied = {q for chain in embedding.values() for q in chain}
    available = iter(sorted(set(target) - occupied))
    for v in sorted(set(source) - set(active)):
        q = next(available, None)
        if q is None:
            return {"status": "heuristic_failure_isolate_space", "embedding": {},
                    "elapsed_seconds": time.perf_counter() - started}
        embedding[v] = [q]
    validation = verify_embedding(source, target, embedding)
    return {"status": "valid" if validation["valid"] else "invalid_search_output",
            "embedding": embedding, "validation": validation,
            "elapsed_seconds": time.perf_counter() - started,
            "parameters": {"random_seed": seed, "timeout": timeout, "tries": tries}}


def qubo_to_ising(linear, quadratic, offset=0.0):
    """Q(x)=c+sum a_i*x_i+sum b_ij*x_i*x_j, x=(1+z)/2.

    Linear is either a list by ID or a dict; quadratic is a dict {(i,j):b}
    or triples (i,j,b).  Terms are aggregated before exact-zero removal.
    """
    linear = dict(enumerate(linear)) if not isinstance(linear, dict) else dict(linear)
    h = {i: float(a) / 2 for i, a in linear.items()}
    J = {}
    c = float(offset) + sum(float(a) for a in linear.values()) / 2
    items = ((i, j, b) for (i, j), b in quadratic.items()) if isinstance(quadratic, dict) else quadratic
    for i, j, b in items:
        b = float(b)
        h.setdefault(i, 0.0)
        h.setdefault(j, 0.0)
        if i == j:
            h[i] += b / 2
            c += b / 2
        else:
            h[i] += b / 4
            h[j] += b / 4
            c += b / 4
            pair = edge_key(i, j)
            J[pair] = J.get(pair, 0.0) + b / 4
    return h, {pair: b for pair, b in J.items() if b != 0}, c


def interaction_graph(h, J):
    graph = nx.Graph()
    graph.add_nodes_from(h)
    graph.add_edges_from(pair for pair, value in J.items() if value != 0)
    return graph


def _scale_bound(value, bounds):
    lo, hi = map(float, bounds)
    if not lo < 0 < hi:
        raise ValueError("programming intervals must contain zero in their interior")
    if not math.isfinite(value):
        raise ArithmeticError("nonfinite coefficient or coupling sum in floating allocation")
    return hi / value if value > 0 else lo / value if value < 0 else math.inf


def allocate_physical(h, J, offset, target, embedding, chain_margin=1.0,
                      chain_factor=1.0, h_range=(-4.0, 4.0),
                      j_range=(-1.0, 1.0), group_range=(-13.0, 10.0),
                      coupling_groups=None, cap_scale=True):
    """Explicit uniform fields, one contact/logical edge, BFS ferromagnetic trees.

    Raw energy includes an offset such that E_raw(consistent z)=E_logical(z).
    Chain i uses K_i=factor*(|h_i|+sum_j|J_ij|)+margin, factor>=1, margin>0.
    A broken chain has a monochromatic component that can be flipped, removing
    >=one wall. Chain gain >=2*K_i, nonchain loss <=2*load_i, so all physical
    ground states are consistent. Extra scale alpha>0 preserves this property.

    group_range is parametric. The default numbers are illustrative documented
    examples, NOT the properties of a particular device. The group sum is signed.
    """
    if chain_factor < 1 or chain_margin <= 0:
        raise ValueError("ground-state guarantee requires chain_factor>=1 and margin>0")
    source = interaction_graph(h, J)
    validation = verify_embedding(source, target, embedding)
    if not validation["valid"]:
        raise ValueError("invalid minor embedding: " + repr(validation["errors"]))
    owner = {q: i for i, branch in embedding.items() for q in branch}
    contacts = {}
    for q, r in _ordered_target_edges(target):
        if q in owner and r in owner and owner[q] != owner[r]:
            contacts.setdefault(edge_key(owner[q], owner[r]), (q, r))
    raw_h = {q: float(h.get(i, 0.0)) / len(branch)
             for i, branch in embedding.items() for q in branch}
    raw_J, load = {}, {i: abs(float(h.get(i, 0.0))) for i in embedding}
    for (i, j), value in J.items():
        if value == 0:
            continue
        q, r = contacts[edge_key(i, j)]
        raw_J[edge_key(q, r)] = float(value)
        load[i] += abs(value)
        load[j] += abs(value)
    trees, strength = {}, {}
    raw_offset = float(offset)
    for i, branch in embedding.items():
        trees[i] = tree_edges(target, branch)
        strength[i] = chain_factor * load[i] + chain_margin if trees[i] else 0.0
        for edge in trees[i]:
            raw_J[edge] = -strength[i]
            raw_offset += strength[i]
    if coupling_groups is None:
        if target.graph.get("family") == "zephyr" and target.graph.get("tile", 4) != 4:
            raise ValueError("provide explicit coupling_groups for Zephyr tile size other than 4")
        from dwave.system.coupling_groups import coupling_groups as make_groups
        coupling_groups = list(make_groups(target))
    else:
        coupling_groups = [list(group) for group in coupling_groups]
    group_sums = [sum(raw_J.get(edge_key(q, r), 0.0) for q, r in group)
                  for group in coupling_groups]
    candidates = [("cap", 1.0)] if cap_scale else []
    candidates += [("h", min((_scale_bound(v, h_range) for v in raw_h.values()), default=math.inf))]
    candidates += [("J", min((_scale_bound(v, j_range) for v in raw_J.values()), default=math.inf))]
    if group_range is not None:
        candidates += [("coupling_group", min((_scale_bound(v, group_range) for v in group_sums), default=math.inf))]
    active, alpha = min(candidates, key=lambda item: item[1])
    if not math.isfinite(alpha):
        alpha, active = 1.0, "zero_model"
    return {"h_raw": raw_h, "J_raw": raw_J, "offset_raw": raw_offset,
            "h": {q: alpha * v for q, v in raw_h.items()},
            "J": {pair: alpha * v for pair, v in raw_J.items()},
            "offset": alpha * raw_offset, "scale": alpha,
            "scale_limiter": active, "scale_bounds": dict(candidates),
            "logical_offset": float(offset), "chain_strength_raw": strength,
            "chain_load": load, "chain_edges": trees,
            "chain_margin": chain_margin, "chain_factor": chain_factor,
            "ranges": {"h": h_range, "J": j_range, "coupling_group": group_range},
            "group_sums_raw": group_sums, "coupling_groups": coupling_groups,
            "validation": validation,
            "raw_wall_drop_lower_bound": min((2 * (strength[i] - load[i])
                for i in embedding if trees[i]), default=math.inf)}


def physical_witness(program):
    """JSON-compatible coefficient and tree witness; maps become explicit rows."""
    result = {}
    for key, value in program.items():
        if key in ("h_raw", "h"):
            result[key] = [[q, x] for q, x in sorted(value.items())]
        elif key in ("J_raw", "J"):
            result[key] = [[q, r, x] for (q, r), x in sorted(value.items())]
        elif key == "chain_edges":
            result[key] = {str(i): [list(e) for e in edges] for i, edges in value.items()}
        elif key in ("chain_strength_raw", "chain_load"):
            result[key] = {str(i): x for i, x in value.items()}
        elif isinstance(value, float) and not math.isfinite(value):
            result[key] = None
        elif key == "scale_bounds":
            result[key] = {k: x if math.isfinite(x) else None for k, x in value.items()}
        else:
            result[key] = value
    return result


def ising_energy(h, J, offset, spins):
    return offset + sum(v * spins[q] for q, v in h.items()) + sum(
        v * spins[q] * spins[r] for (q, r), v in J.items())


def exact_model_to_ising(model):
    """Authoritative rational conversion; no binary64 expansion occurs here."""
    exact = model["exact_coefficients"]
    h = {i: Fraction(*a)/2 for i, a in enumerate(exact["linear"])}
    J = {}
    c = Fraction(*exact["offset"]) + sum(h.values(), Fraction(0))
    for i, j, num, den in exact["quadratic"]:
        value = Fraction(num, den)
        if i == j:
            h[i] += value/2
            c += value/2
        else:
            h[i] += value/4
            h[j] += value/4
            c += value/4
            pair = edge_key(i, j)
            J[pair] = J.get(pair, Fraction(0)) + value/4
    return h, {pair: value for pair, value in J.items() if value}, c


def _ratio(value):
    return [value.numerator, value.denominator]


def _exact_range_check(program):
    """Check actual binary64 programmed coefficients as rational numbers."""
    violations = []
    for name in ("h", "J"):
        lo, hi = map(Fraction, program["ranges"][name])
        for key, value in program[name].items():
            if not lo <= Fraction(value) <= hi:
                violations.append({"kind": name, "index": key})
    bounds = program["ranges"]["coupling_group"]
    if bounds is not None:
        lo, hi = map(Fraction, bounds)
        for index, group in enumerate(program["coupling_groups"]):
            total = sum((Fraction(program["J"].get(edge_key(q,r),0))
                         for q,r in group), Fraction(0))
            if not lo <= total <= hi:
                violations.append({"kind": "coupling_group", "index": index})
    return {"valid": not violations, "violations": violations,
            "arithmetic": "exact rational values of actual binary64 coefficients"}


def certify_physical_rounding(model, program, embedding, target):
    """Prove actual programmed double ground states belong to exact ground set.

    Exact companion: authoritative logical rationals, uniform branch fields,
    one deterministic contact, actual binary64 K_i and alpha interpreted as
    rationals.  Those are legitimate exact parameter choices. If each K_i>L_i,
    the raw physical nonoptimal gap is at least min(delta_Q,2*min(K_i-L_i)).
    Coefficient L1 error rho bounds every configuration's energy perturbation;
    strict 2*rho < alpha*gap preserves the exact ground-state set inclusion.
    This permits deterministic selection of a subset of exactly tied optima.
    Constant offsets are recorded separately; they cannot change minimizers.
    """
    h, J, c = exact_model_to_ising(model)
    source = interaction_graph(h, J)
    validation = verify_embedding(source, target, embedding)
    if not validation["valid"]:
        return {"float_ground_states_certified": False,
                "reason": "embedding does not realize authoritative exact graph",
                "embedding_validation": validation}
    alpha = Fraction(program["scale"])
    if alpha <= 0:
        return {"float_ground_states_certified": False, "reason": "nonpositive scale"}
    owner = {q:i for i,branch in embedding.items() for q in branch}
    invalid_fields = [q for q in program["h"] if q not in owner or q not in target]
    invalid_couplers = [pair for pair in program["J"]
                        if pair[0] not in owner or pair[1] not in owner
                        or not target.has_edge(*pair)]
    if invalid_fields or invalid_couplers:
        return {"float_ground_states_certified": False,
                "reason": "programmed support is outside the embedded target graph",
                "invalid_fields": invalid_fields, "invalid_couplers": invalid_couplers}
    contacts = {}
    for q,r in _ordered_target_edges(target):
        if q in owner and r in owner and owner[q] != owner[r]:
            contacts.setdefault(edge_key(owner[q],owner[r]), (q,r))
    ideal_h = {q:h[i]/len(branch) for i,branch in embedding.items() for q in branch}
    ideal_J = {}
    loads = {i:abs(value) for i,value in h.items()}
    ideal_offset = c
    for (i,j),value in J.items():
        ideal_J[contacts[(i,j)]] = value
        loads[i] += abs(value)
        loads[j] += abs(value)
    margins = []
    for i,branch in embedding.items():
        tree = tree_edges(target, branch)
        if not tree:
            continue
        K = Fraction(program["chain_strength_raw"][i])
        margins.append(K-loads[i])
        for pair in tree:
            ideal_J[pair] = -K
            ideal_offset += K
    positive_margins = all(margin > 0 for margin in margins)
    delta_Q = Fraction(*model["numeric_certificate"]["nonoptimal_gap_lower_bound_exact"])
    delta_raw = min([delta_Q] + [2*margin for margin in margins])
    delta = alpha*delta_raw
    ideal_h = {q:alpha*value for q,value in ideal_h.items()}
    ideal_J = {pair:alpha*value for pair,value in ideal_J.items()}
    rho = sum((abs(Fraction(program["h"].get(q,0))-ideal_h.get(q,0))
               for q in set(program["h"]) | set(ideal_h)), Fraction(0))
    rho += sum((abs(Fraction(program["J"].get(pair,0))-ideal_J.get(pair,0))
                for pair in set(program["J"]) | set(ideal_J)), Fraction(0))
    ranges = _exact_range_check(program)
    certified = positive_margins and delta > 0 and 2*rho < delta and ranges["valid"]
    return {"float_ground_states_certified": certified,
            "condition": "all exact K_i>L_i, alpha>0, exact hardware ranges hold, and 2*rho<delta_physical",
            "coefficient_error_l1_exact": _ratio(rho),
            "nonoptimal_gap_lower_bound_exact": _ratio(delta),
            "minimum_chain_margin_exact": _ratio(min(margins)) if margins else None,
            "positive_exact_chain_margins": positive_margins,
            "scale_exact": _ratio(alpha),
            "offset_error_exact": _ratio(abs(Fraction(program["offset"])-alpha*ideal_offset)),
            "ranges": ranges,
            "exact_companion": {"h": [[q,*_ratio(v)] for q,v in sorted(ideal_h.items())],
                                "J": [[q,r,*_ratio(v)] for (q,r),v in sorted(ideal_J.items())],
                                "offset": _ratio(alpha*ideal_offset),
                                "interpretation": "logical rational model, actual float chain strengths and scale interpreted exactly"}}


def allocate_physical_exact(model, target, embedding, require_float_fidelity=True, **kwargs):
    """Allocate and certify numeric ground-state fidelity to exact compiler model.

    Rational Ising coefficients are individually rounded only at allocation.
    If rounded hardware sums overshoot a limit, nudge scale toward zero and
    recheck. Failure is explicit; no claim of fidelity for arbitrary ill-scaled
    binary64 inputs is made when the certificate is inconclusive.
    """
    eh, eJ, ec = exact_model_to_ising(model)
    h, J, c = ({i:float(v) for i,v in eh.items()},
               {pair:float(v) for pair,v in eJ.items()}, float(ec))
    if not all(math.isfinite(x) for x in list(h.values())+list(J.values())+[c]):
        raise ArithmeticError("exact coefficient exceeds representable binary64 range")
    program = allocate_physical(h,J,c,target,embedding,**kwargs)
    if not math.isfinite(program["offset"]) or not math.isfinite(program["offset_raw"]):
        raise ArithmeticError("physical offset overflow in floating allocation")
    adjustments = 0
    while not _exact_range_check(program)["valid"] and adjustments < 32:
        alpha = math.nextafter(program["scale"],0.0)
        program["scale"] = alpha
        program["h"] = {q:alpha*v for q,v in program["h_raw"].items()}
        program["J"] = {pair:alpha*v for pair,v in program["J_raw"].items()}
        program["offset"] = alpha*program["offset_raw"]
        adjustments += 1
    program["scale_nextafter_adjustments"] = adjustments
    program["numeric_certificate"] = certify_physical_rounding(model,program,embedding,target)
    if require_float_fidelity and not program["numeric_certificate"]["float_ground_states_certified"]:
        raise ArithmeticError("binary64 physical ground states not certified; inspect with require_float_fidelity=False")
    return program
