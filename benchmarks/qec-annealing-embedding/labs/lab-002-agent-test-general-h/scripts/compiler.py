"""Sparse binary parity constraints -> bounded-size XOR-chain QUBO.

No decoding optimization is performed during compilation. Arithmetic in the
proof is exact; this implementation uses finite IEEE doubles and rejects
non-finite coefficients. JSON output contains every variable, including isolates.
"""
from __future__ import annotations
import math
import copy
from fractions import Fraction
from collections import Counter, defaultdict
import networkx as nx


def normalize_rows(rows, n):
    """Canonicalize sparse row supports; repeated coordinates add over GF(2)."""
    out = []
    for row in rows:
        row = list(row)
        if any(int(i) != i for i in row):
            raise ValueError("Column indices must be integers")
        counts = Counter(int(i) for i in row)
        if any(i < 0 or i >= n for i in counts):
            raise ValueError("Column index outside [0,n)")
        out.append(sorted(i for i, count in counts.items() if count % 2))
    return out


def _ratio(x):
    return [x.numerator, x.denominator]


def certify_coefficients(model, exact_linear, exact_quadratic, exact_offset,
                         require_float_fidelity=True):
    """A rational rounding-error certificate for IEEE coefficient output.

    Finite binary64 inputs have exact rational values. Their objective costs
    lie on a rational lattice. Compare the exact lattice/penalty gap with twice
    the total coefficient error. Offsets do not affect ground states.
    """
    weights = [Fraction(w) for w in model["weights"]]
    exact_budget = sum(map(abs,weights), Fraction(0))
    margin = Fraction(model["penalty"])-exact_budget
    if margin <= 0:
        raise ValueError("Penalty does not strictly exceed exact weight L1 norm")
    denominator = max((w.denominator for w in weights),default=1)
    numerator_gcd = math.gcd(*(abs(w.numerator)*(denominator//w.denominator) for w in weights))
    lattice = Fraction(numerator_gcd,denominator) if numerator_gcd else None
    gap = min(margin,lattice) if lattice else margin
    approx_quad={(i,j):Fraction(q) for i,j,q in model["quadratic"]}
    rho = sum((abs(Fraction(a)-b) for a,b in zip(model["linear"],exact_linear)),Fraction(0))
    rho += sum((abs(approx_quad.get(pair,Fraction(0))-exact_quadratic.get(pair,Fraction(0)))
                for pair in set(approx_quad)|set(exact_quadratic)),Fraction(0))
    certified = 2*rho < gap
    model["exact_coefficients"] = {
        "linear": [_ratio(a) for a in exact_linear],
        "quadratic": [[i,j,*_ratio(exact_quadratic[i,j])] for i,j in model["structural_edges"]
                      if exact_quadratic.get((i,j),Fraction(0))],
        "offset": _ratio(exact_offset),
        "interpretation": "authoritative exact rational model for the binary64 input weights and penalty"}
    model["numeric_certificate"] = {
        "float_ground_states_certified": certified,
        "coefficient_error_l1_exact": _ratio(rho),
        "nonoptimal_gap_lower_bound_exact": _ratio(gap),
        "weight_lattice_step_exact": None if lattice is None else _ratio(lattice),
        "exact_penalty_margin": _ratio(margin),
        "offset_error_exact": _ratio(abs(Fraction(model["offset"])-exact_offset)),
        "condition": "2 * coefficient_error_l1 < nonoptimal_gap_lower_bound"}
    if require_float_fidelity and not certified:
        raise ArithmeticError("Floating expansion cannot be certified faithful; use require_float_fidelity=False to obtain authoritative exact rational coefficients")
    return model


def compile_instance(rows, n, syndrome, weights, penalty=None, require_float_fidelity=True):
    """Return faithful sparse QUBO, assuming syndrome lies in image(H).

    penalty must strictly exceed sum(abs(weights)). Set a fixed envelope for
    repeated syndromes/weights to avoid rebuilding the structural coefficients.
    y_i=(z_i+1)/2 is the Ising conversion used by the companion implementation.
    """
    if n < 0 or int(n) != n:
        raise ValueError("n must be a nonnegative integer")
    rows = normalize_rows(rows, n)
    syndrome = list(syndrome)
    if any(s not in (0,1) for s in syndrome):
        raise ValueError("Syndrome entries must be binary")
    syndrome = [int(s) for s in syndrome]
    weights = [float(w) for w in weights]
    if len(rows) != len(syndrome) or len(weights) != n:
        raise ValueError("Dimension mismatch")
    if any(s not in (0, 1) for s in syndrome):
        raise ValueError("Syndrome entries must be binary")
    if not all(math.isfinite(w) for w in weights):
        raise ValueError("Weights must be finite")
    budget = math.fsum(abs(w) for w in weights)
    penalty = float(budget + 1.0 if penalty is None else penalty)
    if not math.isfinite(penalty) or not penalty > budget:
        raise ValueError("Need finite penalty > sum(abs(weights)); supply a larger envelope")
    linear = list(weights)
    exact_linear = list(map(Fraction,weights))
    quadratic = defaultdict(float)
    exact_quadratic = defaultdict(Fraction)
    offset = 0.0
    exact_offset = Fraction(0)
    exact_penalty = Fraction(penalty)
    variables = [{"kind": "error", "column": i} for i in range(n)]
    constraints = []
    structural_edges = set()

    def auxiliary(kind, row, stage):
        variables.append({"kind": kind, "row": row, "stage": stage})
        linear.append(0.0)
        exact_linear.append(Fraction(0))
        return len(linear) - 1

    def square(coeffs, constant, row, kind):
        nonlocal offset,exact_offset
        terms = sorted(coeffs.items())
        for i, a in terms:
            linear[i] += penalty * (a*a + 2*constant*a)
            exact_linear[i] += exact_penalty*(a*a+2*constant*a)
        for p, (i, a) in enumerate(terms):
            for j, b in terms[p+1:]:
                quadratic[i, j] += 2*penalty*a*b
                exact_quadratic[i,j] += 2*exact_penalty*a*b
                structural_edges.add((i, j))
        offset += penalty*constant*constant
        exact_offset += exact_penalty*constant*constant
        constraints.append({"row": row, "kind": kind,
                            "terms": [[i, a] for i, a in terms],
                            "constant": constant})

    for r, (support, s) in enumerate(zip(rows, syndrome)):
        d = len(support)
        if d == 0:
            if s:
                raise ValueError("Empty check has nonzero syndrome (infeasible)")
        elif d == 1:
            square({support[0]: 1}, -s, r, "final")
        else:
            previous = support[0]
            for stage, current in enumerate(support[1:]):
                if stage == d-2:
                    # Exact degree-two parity violation indicator, avoiding the
                    # final carry. Its interaction sign depends on syndrome.
                    sign = 1-2*s
                    linear[previous] += penalty*sign
                    linear[current] += penalty*sign
                    exact_linear[previous] += exact_penalty*sign
                    exact_linear[current] += exact_penalty*sign
                    pair = tuple(sorted((previous, current)))
                    quadratic[pair] -= 2*penalty*sign
                    exact_quadratic[pair] -= 2*exact_penalty*sign
                    structural_edges.add(pair)
                    offset += penalty*s
                    exact_offset += exact_penalty*s
                    constraints.append({"row": r, "kind": "parity",
                                        "inputs": [previous, current], "target": s})
                else:
                    carry = auxiliary("carry", r, stage)
                    parity = auxiliary("prefix", r, stage)
                    square({previous: 1, current: 1, parity: -1, carry: -2}, 0, r, "xor")
                    previous = parity

    quadratic = [[i, j, q] for (i, j), q in sorted(quadratic.items()) if q != 0]
    if not all(math.isfinite(c) for c in linear + [offset] + [q[2] for q in quadratic]):
        raise ValueError("Coefficient overflow")
    model = {"schema": "xor-chain-qubo-v1", "n_original": n, "rows": rows,
            "syndrome": syndrome, "weights": weights, "penalty": penalty,
            "weight_l1": budget, "linear": linear, "quadratic": quadratic,
            "offset": offset, "variables": variables, "constraints": constraints,
            "structural_edges": [list(edge) for edge in sorted(structural_edges)]}
    return certify_coefficients(model,exact_linear,exact_quadratic,exact_offset,require_float_fidelity)


def model_graph(model, structural=False):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(model["linear"])))
    if structural:
        graph.add_edges_from(model["structural_edges"])
    else:
        graph.add_edges_from((i, j) for i, j, q in model["quadratic"] if q)
    return graph


def energy(model, y):
    return (model["offset"] + math.fsum(c*int(y[i]) for i, c in enumerate(model["linear"]))
            + math.fsum(q*int(y[i])*int(y[j]) for i, j, q in model["quadratic"]))


def residual_energy(model, y):
    return (math.fsum(w*int(y[i]) for i, w in enumerate(model["weights"]))
            + model["penalty"]*sum(constraint_violation(c, y)
                                   for c in model["constraints"]))


def constraint_violation(c, y):
    if c["kind"] == "parity":
        return int((int(y[c["inputs"][0]]) ^ int(y[c["inputs"][1]])) != c["target"])
    return (c["constant"] + sum(a*int(y[i]) for i, a in c["terms"]))**2


def feasible(model, e):
    return all(sum(int(e[i]) for i in row) % 2 == s
               for row, s in zip(model["rows"], model["syndrome"]))


def complete_feasible(model, e):
    """Unique zero-penalty auxiliary extension of a feasible error pattern."""
    if len(e) != model["n_original"] or any(int(b) not in (0, 1) for b in e):
        raise ValueError("Error pattern dimension/bits invalid")
    if not feasible(model, e):
        raise ValueError("Error pattern does not match syndrome")
    y = list(map(int, e)) + [0]*(len(model["linear"])-len(e))
    for c in model["constraints"]:
        if c["kind"] == "xor":
            inputs = [i for i, a in c["terms"] if a == 1]
            carry = next(i for i, a in c["terms"] if a == -2)
            parity = next(i for i, a in c["terms"] if a == -1)
            total = sum(y[i] for i in inputs)
            y[carry], y[parity] = total//2, total % 2
    assert all(constraint_violation(c, y) == 0 for c in model["constraints"])
    return y


def update_instance(model, syndrome=None, weights=None, require_float_fidelity=True):
    """Numerical-only update in O(nnz(H)+n+m), including copying the output.

    Only final parity factors depend on syndrome. The preprocessed structural
    envelope survives cancellations/sign changes of actual quadratic terms.
    """
    syndrome = list(model["syndrome"] if syndrome is None else syndrome)
    weights = [float(w) for w in (model["weights"] if weights is None else weights)]
    if len(syndrome) != len(model["rows"]) or any(s not in (0,1) for s in syndrome):
        raise ValueError("Syndrome dimensions/bits invalid")
    syndrome = list(map(int,syndrome))
    if len(weights) != model["n_original"] or not all(math.isfinite(w) for w in weights):
        raise ValueError("Weight dimensions/values invalid")
    budget = math.fsum(abs(w) for w in weights)
    if not model["penalty"] > budget:
        raise ValueError("Updated weights exceed fixed penalty envelope")
    if any(not row and s for row,s in zip(model["rows"],syndrome)):
        raise ValueError("Empty check has nonzero syndrome (infeasible)")
    out = copy.deepcopy(model)
    M = model["penalty"]
    qdict = {(i,j): q for i,j,q in model["quadratic"]}
    exact_linear = [Fraction(*a) for a in model["exact_coefficients"]["linear"]]
    exact_quadratic = {(i,j): Fraction(a,b) for i,j,a,b in model["exact_coefficients"]["quadratic"]}
    exact_offset = Fraction(*model["exact_coefficients"]["offset"])
    exact_M = Fraction(M)
    for i,(old,new) in enumerate(zip(model["weights"],weights)):
        out["linear"][i] += new-old
        exact_linear[i] += Fraction(new)-Fraction(old)
    for c in out["constraints"]:
        r = c["row"]
        delta = syndrome[r]-model["syndrome"][r]
        if not delta or c["kind"] == "xor":
            continue
        out["offset"] += M*delta
        exact_offset += exact_M*delta
        if c["kind"] == "parity":
            a,b = c["inputs"]
            out["linear"][a] -= 2*M*delta
            out["linear"][b] -= 2*M*delta
            exact_linear[a] -= 2*exact_M*delta
            exact_linear[b] -= 2*exact_M*delta
            pair = tuple(sorted((a,b)))
            qdict[pair] = qdict.get(pair,0.0)+4*M*delta
            exact_quadratic[pair] = exact_quadratic.get(pair,Fraction(0))+4*exact_M*delta
            c["target"] = syndrome[r]
        else:
            assert len(c["terms"]) == 1
            a = c["terms"][0][0]
            out["linear"][a] -= 2*M*delta
            exact_linear[a] -= 2*exact_M*delta
            c["constant"] = -syndrome[r]
    out["quadratic"] = [[a,b,qdict[a,b]] for a,b in model["structural_edges"]
                        if qdict.get((a,b),0.0) != 0]
    out["syndrome"],out["weights"],out["weight_l1"] = syndrome,weights,budget
    return certify_coefficients(out,exact_linear,exact_quadratic,exact_offset,require_float_fidelity)
