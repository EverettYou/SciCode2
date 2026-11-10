#!/usr/bin/env python3
"""Polynomial pause certificate and exponential small-system validation.

No quantum eigensolver is used by pause_certificate. The remaining functions
provide independent numerical checks of the analytic theorem and example.
Energy conventions are H=sum c(1-ZZ)+D-Gamma sum X, hbar=1.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
import sys
import time
from collections.abc import Hashable, Mapping, Sequence
from fractions import Fraction
from pathlib import Path

import networkx as nx
import numpy as np
import scipy
from scipy.linalg import eigh, expm, solve_sylvester


def _as_binary64_fraction(value, label):
    """Interpret a finite input as its actual binary64 value, exactly."""
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return Fraction.from_float(value)


def _float_directed(value, upward):
    """Round a Fraction outward; None represents an unrepresentable infinity.

    Finite returned values obey the requested inequality even for subnormals.
    Certificate probability bounds are clipped rationally first, so they never
    use the None case. Display-only unbounded energy statistics may use None.
    """
    try:
        result = float(value)
    except OverflowError:
        result = math.inf if value > 0 else -math.inf
    if math.isinf(result):
        if (result > 0 and not upward) or (result < 0 and upward):
            return math.copysign(sys.float_info.max, result)
        return None
    represented = Fraction.from_float(result)
    if upward and represented < value:
        result = math.nextafter(result, math.inf)
    elif not upward and represented > value:
        result = math.nextafter(result, -math.inf)
    return result if math.isfinite(result) else None


def _sqrt_dyadic_upper(value, bits=128):
    """Exact dyadic upper bound on sqrt(value), with bits significant bits."""
    if value < 0:
        raise ValueError("negative square root")
    if value == 0:
        return Fraction(0)
    numerator, denominator = value.numerator, value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        exponent -= numerator < (denominator << exponent)
    else:
        exponent -= (numerator << -exponent) < denominator
    shift = bits - 1 - exponent // 2
    if shift >= 0:
        scaled_numerator, scaled_denominator = numerator << (2*shift), denominator
    else:
        scaled_numerator, scaled_denominator = numerator, denominator << (-2*shift)
    root = math.isqrt(scaled_numerator // scaled_denominator)
    if root*root*scaled_denominator < scaled_numerator:
        root += 1
    if shift >= 0:
        return Fraction(root, 1 << shift)
    return Fraction(root << -shift)


def _exp_rational_upper(x, degree=24):
    """Proved upper bound: Taylor polynomial plus a geometric tail, 0<=x<1."""
    if not 0 <= x < 1:
        raise ValueError("exponential bound requires 0 <= x < 1")
    term = total = Fraction(1)
    for k in range(1, degree+1):
        term *= x / k
        total += term
    first_omitted = term * x / (degree+1)
    tail_upper = first_omitted / (1 - x / (degree+2))
    return total + tail_upper


def pause_certificate(
    branches: Sequence[Sequence[Hashable]],
    chain_edges: Sequence[tuple[Hashable, Hashable, float]],
    fields: Mapping[Hashable, float],
    problem_edges: Sequence[tuple[Hashable, Hashable, float]],
    gamma: float,
    duration: float,
) -> dict:
    """Certify a constant-Hamiltonian hold, using already scaled energies.

    Each chain edge's third entry is positive c in c(1-ZZ). Problem fields
    and edges are energies in D, not unscaled programmed h and J. The result
    concerns events depending only on nonsingleton logical variables and
    initial states supported on consistent branches. Invalid inputs raise;
    failure of the theorem's sufficient condition returns 'inconclusive'.
    Binary64 inputs are interpreted exactly as rationals. Returned error bounds
    are rounded upward. Tree cuts are exact; cyclic-branch cuts use a certified
    minimum-edge lower bound instead of a floating-point min-cut computation.
    """
    if not math.isfinite(gamma) or gamma < 0:
        raise ValueError("gamma must be finite and nonnegative")
    if not math.isfinite(duration) or duration < 0:
        raise ValueError("duration must be finite and nonnegative")
    gamma_q = _as_binary64_fraction(gamma, "gamma")
    duration_q = _as_binary64_fraction(duration, "duration")
    owners = {}
    graphs = []
    for i, branch in enumerate(branches):
        if not branch:
            raise ValueError("empty branch")
        graph = nx.Graph()
        for q in branch:
            if q in owners:
                raise ValueError("branches must be disjoint, without repeats")
            owners[q] = i
            graph.add_node(q)
        graphs.append(graph)
    if not branches:
        raise ValueError("at least one branch is required")
    for q, r, c in chain_edges:
        if q == r or q not in owners or r not in owners:
            raise ValueError("invalid chain endpoint")
        if owners[q] != owners[r] or not math.isfinite(c) or c <= 0:
            raise ValueError("chain must be internal with positive finite weight")
        graph = graphs[owners[q]]
        if graph.has_edge(q, r):
            raise ValueError("duplicate chain edge; aggregate it explicitly")
        graph.add_edge(q, r, weight=_as_binary64_fraction(c, "chain weight"))
    for q, h in fields.items():
        if q not in owners or not math.isfinite(h):
            raise ValueError("invalid field")
    seen_problem = set()
    for q, r, j in problem_edges:
        if q == r or q not in owners or r not in owners:
            raise ValueError("invalid problem endpoint")
        if owners[q] == owners[r] or not math.isfinite(j):
            raise ValueError("problem edge must connect distinct branches")
        key = frozenset((q, r))
        if key in seen_problem:
            raise ValueError("duplicate problem edge; aggregate it explicitly")
        seen_problem.add(key)
    cuts_q = []
    exact_cuts = []
    methods = []
    for graph in graphs:
        if not nx.is_connected(graph):
            raise ValueError("disconnected branch")
        if graph.number_of_nodes() == 1:
            continue
        lower_cut = min(d["weight"] for _, _, d in graph.edges(data=True))
        cuts_q.append(lower_cut)
        is_tree = graph.number_of_edges() == graph.number_of_nodes()-1
        exact_cuts.append(_float_directed(lower_cut, False) if is_tree else None)
        methods.append("tree-min-edge-exact" if is_tree else
                       "connected-graph-min-edge-lower-bound")
    sizes = [len(branch) for branch in branches]
    n = sum(sizes)
    n1 = sizes.count(1)
    n2 = sizes.count(2)
    m = n - n1
    radius_q = sum((abs(_as_binary64_fraction(h, "field")) for h in fields.values()), Fraction())
    radius_q += sum((abs(_as_binary64_fraction(j, "problem coupling"))
                     for _, _, j in problem_edges), Fraction())
    base = {
        "physical_qubits": n,
        "logical_variables": len(branches),
        "singleton_branches": n1,
        "size_two_branches": n2,
        "nonsingleton_physical_qubits": m,
        "R": _float_directed(radius_q, True),
        "Gamma": float(gamma_q),
        "duration": float(duration_q),
        "cut_methods": methods,
        "branch_minimum_cuts": exact_cuts,
        "branch_cut_lower_bounds": [_float_directed(c, False) for c in cuts_q],
        "frozen_logical_variables": [i for i, size in enumerate(sizes) if size > 1],
        "required_initial_support": "all branches internally consistent",
        "numeric_certification": "exact-binary64-rational-with-upward-error-bounds",
        "sqrt_bound_significant_bits": 128,
        "exp_taylor_degree": 24,
    }
    if not cuts_q or gamma_q == 0:
        return {
            **base,
            "status": "exact",
            "Delta": None if not cuts_q else _float_directed(2 * min(cuts_q), False),
            "g": None,
            "rational_g_witness": None,
            "b": 0.0,
            "state_vector_error_bound": 0.0,
            "event_probability_change_bound": 0.0,
            "initially_zero_event_probability_bound": 0.0,
            "chain_leakage_probability_bound": 0.0,
            "reason": "P is the full space" if not cuts_q else "zero driver",
        }
    delta_q = 2 * min(cuts_q)
    gap_q = delta_q - 2 * radius_q - gamma_q * (n + n1)
    offdiag_squared_q = gamma_q**2 * (m + 2*n2)
    offdiag_upper_q = _sqrt_dyadic_upper(offdiag_squared_q)
    base.update(
        Delta=_float_directed(delta_q, False),
        g=_float_directed(gap_q, False),
        b=_float_directed(offdiag_upper_q, True),
        rational_g_witness={"numerator": str(gap_q.numerator),
                            "denominator": str(gap_q.denominator)},
    )
    if gap_q <= 0:
        return {**base, "status": "inconclusive", "reason": "g <= 0"}
    s_upper_q = offdiag_upper_q / gap_q
    if 2*s_upper_q >= 1:
        return {
            **base, "status": "valid-but-vacuous",
            "reason": "2*s_upper >= 1; return universal bounds without exponential",
            "s": _float_directed(s_upper_q, True),
            "unclipped_epsilon": None,
            "state_vector_error_bound": 2.0,
            "event_probability_change_bound": 1.0,
            "initially_zero_event_probability_bound": 1.0,
            "chain_leakage_probability_bound": 1.0,
        }
    exp_upper_q = _exp_rational_upper(2*s_upper_q)
    raw_q = 2*s_upper_q + duration_q*(offdiag_squared_q/gap_q)*exp_upper_q
    squared_q = raw_q**2
    return {
        **base,
        "status": "certified" if raw_q < 1 else "valid-but-vacuous",
        "s": _float_directed(s_upper_q, True),
        "unclipped_epsilon": _float_directed(raw_q, True),
        "state_vector_error_bound": _float_directed(min(Fraction(2), raw_q), True),
        "event_probability_change_bound": _float_directed(min(Fraction(1), raw_q), True),
        "initially_zero_event_probability_bound": _float_directed(min(Fraction(1), squared_q), True),
        "chain_leakage_probability_bound": _float_directed(min(Fraction(1), squared_q), True),
    }


def physical_matrix(n, chains, fields, edges, gamma):
    """Independent dense construction in little-endian computational order."""
    states = np.arange(1 << n)
    z = 1 - 2 * ((states[:, None] >> np.arange(n)) & 1)
    diagonal = np.zeros(len(states), dtype=float)
    for q, r, c in chains:
        diagonal += c * (1 - z[:, q] * z[:, r])
    for q, h in fields.items():
        diagonal += h * z[:, q]
    for q, r, j in edges:
        diagonal += j * z[:, q] * z[:, r]
    hamiltonian = np.diag(diagonal)
    for q in range(n):
        hamiltonian[states, states ^ (1 << q)] -= gamma
    return hamiltonian


def consistent_indices(n, branches):
    return np.asarray([
        state for state in range(1 << n)
        if all(len({(state >> q) & 1 for q in branch}) == 1 for branch in branches)
    ], dtype=int)


def unitary_from_eigenpairs(values, vectors, duration):
    return (vectors * np.exp(-1j * values * duration)) @ vectors.conj().T


def validate_one(branches, chains, fields, edges, gamma, durations):
    """Check each independently constructed matrix and the uniform norm claim."""
    n = sum(map(len, branches))
    h = physical_matrix(n, chains, fields, edges, gamma)
    p = consistent_indices(n, branches)
    q = np.setdiff1d(np.arange(1 << n), p)
    a = h[np.ix_(p, p)]
    d = h[np.ix_(q, q)]
    block_b = h[np.ix_(q, p)]
    cert = pause_certificate(branches, chains, fields, edges, gamma, max(durations))
    if cert["status"] == "inconclusive":
        raise AssertionError("validation parameters unexpectedly inconclusive")
    actual_b = float(np.linalg.norm(block_b, 2))
    np.testing.assert_allclose(actual_b, cert["b"], atol=1e-11, rtol=1e-10)
    actual_gap = float(eigh(d, eigvals_only=True)[0] - eigh(a, eigvals_only=True)[-1])
    assert actual_gap + 1e-10 >= cert["g"]

    # Independently solve the Sylvester equation and check the BCH remainder.
    y = solve_sylvester(d, -a, block_b)
    np.testing.assert_allclose(d @ y - y @ a, block_b, atol=1e-10)
    s_matrix = np.zeros_like(h)
    s_matrix[np.ix_(q, p)] = y
    s_matrix[np.ix_(p, q)] = -y.T
    h0 = h.copy()
    h0[np.ix_(p, q)] = 0
    h0[np.ix_(q, p)] = 0
    es = expm(s_matrix)
    residual = es @ h @ es.T - h0
    s_bound = cert["b"] / cert["g"]
    residual_bound = cert["b"]**2 / cert["g"] * math.exp(2 * s_bound)
    actual_residual = float(np.linalg.norm(residual, 2))
    assert actual_residual <= residual_bound + 1e-10
    assert np.linalg.norm(y, 2) <= s_bound + 1e-10

    ev, vec = eigh(h)
    av, avec = eigh(a)
    rows = []
    for duration in durations:
        result = pause_certificate(branches, chains, fields, edges, gamma, duration)
        u = unitary_from_eigenpairs(ev, vec, duration)
        ua = unitary_from_eigenpairs(av, avec, duration)
        ideal = np.zeros((1 << n, len(p)), dtype=complex)
        ideal[p, :] = ua
        actual_error = float(np.linalg.norm(u[:, p] - ideal, 2))
        actual_leakage = float(np.linalg.norm(u[np.ix_(q, p)], 2)**2)
        assert actual_error <= result["state_vector_error_bound"] + 1e-9
        assert actual_leakage <= result["chain_leakage_probability_bound"] + 1e-9
        rows.append({
            "duration": duration,
            "state_vector_error": actual_error,
            "state_vector_error_bound": result["state_vector_error_bound"],
            "leakage_probability_worst_initial_state": actual_leakage,
            "leakage_probability_bound": result["chain_leakage_probability_bound"],
        })
    return {
        "branch_sizes": list(map(len, branches)),
        "N": n,
        "actual_block_gap": actual_gap,
        "certified_block_gap": cert["g"],
        "actual_offdiagonal_norm": actual_b,
        "certified_offdiagonal_norm": cert["b"],
        "conjugation_residual_norm": actual_residual,
        "conjugation_residual_bound": residual_bound,
        "dynamics": rows,
    }


def random_checks(seed=20261007, count=24):
    rng = np.random.default_rng(seed)
    patterns = [[2], [3], [4], [1, 2], [2, 2], [1, 2, 3], [3, 3], [2, 3]]
    rows = []
    for trial in range(count):
        pattern = patterns[trial % len(patterns)]
        branches = []
        offset = 0
        for size in pattern:
            branches.append(list(range(offset, offset + size)))
            offset += size
        chains = []
        for branch in branches:
            for index in range(1, len(branch)):
                parent = branch[int(rng.integers(index))]
                chains.append((parent, branch[index], float(rng.uniform(0.8, 1.3))))
            if len(branch) > 2 and trial % 3 == 0:
                present = {frozenset((q, r)) for q, r, _ in chains}
                for q, r in itertools.combinations(branch, 2):
                    if frozenset((q, r)) not in present:
                        chains.append((q, r, float(rng.uniform(0.4, 0.8))))
        fields = {q: float(rng.uniform(-0.012, 0.012)) for q in range(offset)}
        edges = [
            (int(rng.choice(left)), int(rng.choice(right)), float(rng.uniform(-0.02, 0.02)))
            for left, right in itertools.combinations(branches, 2)
        ]
        gamma = float(rng.uniform(0.004, 0.018))
        rows.append(validate_one(branches, chains, fields, edges, gamma, [0, 1, 10, 40]))
    # Explicit edge conditions and invalid-input checks.
    assert pause_certificate([[0]], [], {0: 1.0}, [], 0.2, 3)["status"] == "exact"
    assert pause_certificate([[0, 1]], [(0, 1, 1)], {}, [], 0, 3)["status"] == "exact"
    assert pause_certificate([[0, 1]], [(0, 1, 1)], {0: 2.0}, [], 0.2, 3)["status"] == "inconclusive"
    return {"seed": seed, "count": count, "checks_passed": True, "cases": rows}


def numeric_bound_checks():
    """Exact edge tests for outward conversion and boundary classification."""
    tiny = math.nextafter(0.0, 1.0)
    q_tiny = Fraction.from_float(tiny)
    rational_cases = [
        Fraction(0), Fraction(1, 3), Fraction(-1, 3),
        q_tiny/3, -q_tiny/3,
        Fraction.from_float(sys.float_info.max)*2,
        -Fraction.from_float(sys.float_info.max)*2,
        Fraction(1)+Fraction(1, 1 << 54),
    ]
    for value in rational_cases:
        above = _float_directed(value, True)
        below = _float_directed(value, False)
        assert above is None or Fraction.from_float(above) >= value
        assert below is None or Fraction.from_float(below) <= value
    sqrt_cases = [
        Fraction(0), Fraction(2), Fraction(1, 3), q_tiny**2,
        q_tiny**2*8, Fraction.from_float(sys.float_info.max)**2*8,
    ]
    for value in sqrt_cases:
        upper = _sqrt_dyadic_upper(value)
        assert upper*upper >= value
        if value:
            # A 128-significant-bit ceiling has relative error < 2^-126.
            assert upper*upper <= value*(1+Fraction(1, 1 << 126))
    for x in [Fraction(0), Fraction(1, 10000), Fraction(1, 2),
              Fraction(999999, 1000000)]:
        assert _exp_rational_upper(x, 24) >= _exp_rational_upper(x, 40)

    chain = [(0, 1, 1.0)]
    at = pause_certificate([[0, 1]], chain, {0: 0.75}, [], 0.25, 1)
    below = pause_certificate([[0, 1]], chain,
                              {0: math.nextafter(0.75, 0.0)}, [], 0.25, 1)
    above = pause_certificate([[0, 1]], chain,
                              {0: math.nextafter(0.75, 1.0)}, [], 0.25, 1)
    assert at["status"] == above["status"] == "inconclusive"
    assert below["status"] == "valid-but-vacuous"
    assert at["rational_g_witness"]["numerator"] == "0"

    # Rounded accumulation gives a spuriously positive gap for these inputs.
    cancellation_fields = {0: 0.99, 1: 1e-17}
    rounded_gap = 2 - 2*math.fsum(cancellation_fields.values()) - 0.02
    assert rounded_gap > 0
    cancellation = pause_certificate([[0, 1]], chain, cancellation_fields, [], 0.01, 1)
    assert cancellation["status"] == "inconclusive"
    assert int(cancellation["rational_g_witness"]["numerator"]) < 0

    subnormal = pause_certificate([[0, 1]], chain, {}, [], tiny, 1)
    assert subnormal["status"] == "certified"
    assert subnormal["initially_zero_event_probability_bound"] == tiny
    extreme = pause_certificate([[0, 1]], [(0, 1, sys.float_info.max)], {}, [], 0.125, 1)
    assert extreme["status"] == "certified"
    overflowing_radius = pause_certificate(
        [[0, 1]], [(0, 1, sys.float_info.max)],
        {0: sys.float_info.max, 1: sys.float_info.max}, [], 0.125, 1)
    assert overflowing_radius["status"] == "inconclusive"
    assert overflowing_radius["R"] is None
    cycle = pause_certificate([[0, 1, 2]],
                              [(0, 1, 1.0), (1, 2, 1.0), (2, 0, 1.0)],
                              {}, [], 0.01, 1)
    assert cycle["Delta"] == 2.0
    assert cycle["branch_minimum_cuts"] == [None]
    assert cycle["cut_methods"] == ["connected-graph-min-edge-lower-bound"]
    return {
        "checks_passed": True,
        "directed_rounding_cases": len(rational_cases),
        "sqrt_enclosure_cases": len(sqrt_cases),
        "exp_tail_comparison_cases": 4,
        "gap_boundary_statuses": {"exact_zero": at["status"],
                                  "positive_neighbor": below["status"],
                                  "negative_neighbor": above["status"]},
        "cancellation_rounded_gap": rounded_gap,
        "cancellation_exact_gap_witness": cancellation["rational_g_witness"],
        "cancellation_status": cancellation["status"],
        "subnormal_positive_probability_upper": subnormal["initially_zero_event_probability_bound"],
        "extreme_magnitude_status": extreme["status"],
        "overflowing_radius_status": overflowing_radius["status"],
        "cyclic_cut_method": cycle["cut_methods"][0],
    }


def decoding_comparison():
    gamma, j, k = 0.02, 0.0001, 1.0
    duration = math.pi / (2 * math.sqrt(j*j + 4*gamma*gamma))
    native = physical_matrix(2, [], {}, [(0, 1, j)], gamma)
    encoded = physical_matrix(4, [(0, 1, k), (2, 3, k)], {}, [(1, 2, j)], gamma)
    # Match compiler convention e=(z+1)/2; logical e=00 is all z=-1.
    native_psi = expm(-1j * duration * native)[:, 3]
    encoded_psi = expm(-1j * duration * encoded)[:, 15]
    native_correct_psi = expm(-1j * duration * native)[:, 1]
    encoded_correct_psi = expm(-1j * duration * encoded)[:, 3]
    native_success = float(np.abs(native_psi[[1, 2]]) @ np.abs(native_psi[[1, 2]]))
    encoded_success = float(np.abs(encoded_psi[[3, 12]]) @ np.abs(encoded_psi[[3, 12]]))
    reps = [state for state in range(16) if ((state >> 0) & 1) != ((state >> 2) & 1)]
    decoded_success = float(np.sum(np.abs(encoded_psi[reps])**2))
    native_retention = float(np.sum(np.abs(native_correct_psi[[1, 2]])**2))
    encoded_retention = float(np.sum(np.abs(encoded_correct_psi[[3, 12]])**2))
    formula = 2*gamma*gamma / (j*j + 4*gamma*gamma)
    np.testing.assert_allclose(native_success, formula, atol=1e-12)
    cert = pause_certificate([[0, 1], [2, 3]], [(0, 1, k), (2, 3, k)], {}, [(1, 2, j)], gamma, duration)
    assert encoded_success <= cert["initially_zero_event_probability_bound"]
    assert decoded_success <= cert["initially_zero_event_probability_bound"]
    assert native_success > cert["initially_zero_event_probability_bound"]
    retention_lower = _float_directed(
        Fraction(1)-Fraction.from_float(cert["initially_zero_event_probability_bound"]), False)
    np.testing.assert_allclose(native_retention, 1-formula, atol=1e-12)
    assert encoded_retention >= retention_lower
    assert retention_lower > native_retention
    return {
        "decoding_H": [[1, 1]],
        "syndrome": [1],
        "weights": [0, 0],
        "tied_optima": [[0, 1], [1, 0]],
        "target_path_edges": [[0, 1], [1, 2], [2, 3]],
        "native_branches_on_target": [[1], [2]],
        "encoded_branches_on_target": [[0, 1], [2, 3]],
        "Gamma": gamma,
        "physical_problem_J": j,
        "physical_chain_K": k,
        "duration": duration,
        "initial_logical_state": [0, 0],
        "native_success_exact_formula": formula,
        "native_success_matrix": native_success,
        "encoded_consistent_ground_success_matrix": encoded_success,
        "encoded_representative_decode_success_matrix": decoded_success,
        "encoded_success_upper_certificate": cert["initially_zero_event_probability_bound"],
        "strict_comparison_proved_without_encoded_simulation": True,
        "retention_from_optimal_logical_state_01": {
            "native_success_exact_formula": 1-formula,
            "native_success_matrix": native_retention,
            "encoded_consistent_ground_success_matrix": encoded_retention,
            "encoded_success_lower_certificate": retention_lower,
            "ordering_reverses_when_initial_state_changes": True,
        },
        "certificate": cert,
        "programming_model": {
            "field_abs_cap": 1,
            "coupler_abs_cap": 1,
            "node_absolute_group_cap": 2,
            "max_actual_node_absolute_coupling_sum": k+j,
            "normalization": "B=2, A=0.04, physical coefficients as stated",
        },
        "scope": "closed-system constant hold, conditional on encoded initial state; common problem-energy scale",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--random-count", type=int, default=24)
    args = parser.parse_args()
    start = time.perf_counter()
    result = {
        "comparison": decoding_comparison(),
        "random_validation": random_checks(count=args.random_count),
        "numeric_bound_validation": numeric_bound_checks(),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "networkx": nx.__version__,
        },
    }
    result["elapsed_seconds"] = time.perf_counter() - start
    encoded = json.dumps(result, indent=2, allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n")
        print(json.dumps({
            "output": str(args.output),
            "comparison": result["comparison"],
            "random_checks_passed": result["random_validation"]["checks_passed"],
            "random_count": result["random_validation"]["count"],
            "numeric_bound_checks_passed": result["numeric_bound_validation"]["checks_passed"],
            "elapsed_seconds": result["elapsed_seconds"],
        }, indent=2))
    else:
        print(encoded)


if __name__ == "__main__":
    main()
