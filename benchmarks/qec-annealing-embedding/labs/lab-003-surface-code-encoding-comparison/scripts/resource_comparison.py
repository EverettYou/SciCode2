#!/usr/bin/env python3
"""Compare the two surface-code encodings on the same ideal Zephyr graph.

No QPU submission.  Both source graphs use generic minorminer with identical
parameters.  Saved graph/chain/coefficient witnesses are independently audited
without relying on minorminer's or the imported allocator's validity flag.
"""
from __future__ import annotations

import argparse
from collections import deque
from fractions import Fraction
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import platform
import statistics
import time

import networkx as nx
import numpy as np

LAB = Path(__file__).resolve().parents[1]
OLD = LAB.parent / "lab-002-agent-test-general-h" / "scripts"
spec = importlib.util.spec_from_file_location("prior_embedding", OLD / "embedding.py")
embedding_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(embedding_lib)


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n")


def edge(a, b):
    return tuple(sorted((int(a), int(b))))


def audit_chains(source, target, chains):
    """Own BFS/disjointness/contact checker, independent of imported code."""
    errors = []
    owners = {}
    if set(chains) != set(source):
        errors.append("logical vertex set mismatch")
    for i in source:
        chain = list(chains.get(i, []))
        if not chain or len(chain) != len(set(chain)):
            errors.append(f"empty or repeated branch {i}")
            continue
        members = set(chain)
        if not members <= set(target):
            errors.append(f"non-target qubit in branch {i}")
            continue
        for q in members:
            if q in owners:
                errors.append(f"overlap {q}")
            owners[q] = i
        found, queue = {chain[0]}, deque([chain[0]])
        while queue:
            q = queue.popleft()
            for r in target[q]:
                if r in members and r not in found:
                    found.add(r)
                    queue.append(r)
        if found != members:
            errors.append(f"disconnected branch {i}")
    contacts = {edge(owners[q], owners[r]) for q, r in target.edges
                if q in owners and r in owners and owners[q] != owners[r]}
    missing = {edge(i, j) for i, j in source.edges} - contacts
    if missing:
        errors.append(f"missing logical contacts {sorted(missing)}")
    sizes = [len(chains.get(i, [])) for i in source]
    return {"valid": not errors, "errors": errors, "physical_qubits": len(owners),
            "chain_max": max(sizes, default=0),
            "chain_mean": statistics.mean(sizes) if sizes else 0,
            "singletons": sum(x == 1 for x in sizes)}


def audit_program(h, J, offset, source, target, chains, program, seed=193):
    """Check exact raw allocation, float ranges, rounding bound and energies.

    Unit input weights and integer penalties imply a >=1 gap from an exact
    encoded ground energy to any non-ground logical energy.  Both direct
    penalties are ground-faithful (see THEORY.md); dual energies are integral
    error weights. K=load+1 gives broken
    chains a >=2 raw descent. Thus 2*rho<alpha certifies programmed floating
    ground states remain exact physical/logical ground states.
    """
    F = Fraction
    errors = []
    owner = {q: i for i, chain in chains.items() for q in chain}
    raw_h, raw_J = program["h_raw"], program["J_raw"]
    if set(raw_h) != set(owner):
        errors.append("physical field support mismatch")
    ideal_h = {q: F(h[i]) / len(chain) for i, chain in chains.items() for q in chain}
    aggregate = {}
    ideal_J = {}
    chain_offset = F(0)
    exact_load = {i: abs(F(h[i])) for i in h}
    for (i, j), value in J.items():
        exact_load[i] += abs(F(value))
        exact_load[j] += abs(F(value))
    for (q, r), value in raw_J.items():
        if not target.has_edge(q, r) or q not in owner or r not in owner:
            errors.append("coupler outside occupied target")
            continue
        i, j = owner[q], owner[r]
        if i != j:
            aggregate[edge(i, j)] = aggregate.get(edge(i, j), F(0)) + F(value)
            ideal_J[edge(q, r)] = F(value)
    if {k: v for k, v in aggregate.items() if v} != {k: F(v) for k, v in J.items() if v}:
        errors.append("logical coupling sums mismatch")
    for i, chain in chains.items():
        trees = [edge(*e) for e in program["chain_edges"][i]]
        tree = nx.Graph()
        tree.add_nodes_from(chain)
        tree.add_edges_from(trees)
        if not nx.is_tree(tree):
            errors.append(f"chain {i} is not a tree")
        K = F(program["chain_strength_raw"][i])
        if len(chain) > 1 and K != exact_load[i] + 1:
            errors.append(f"chain load prescription mismatch {i}")
        for pair in trees:
            if F(raw_J.get(pair, 0)) != -K:
                errors.append(f"chain coupling mismatch {pair}")
            ideal_J[pair] = -K
            chain_offset += K
    if set(ideal_J) != set(raw_J):
        errors.append("unaccounted physical coupler")
    if F(program["offset_raw"]) != F(offset) + chain_offset:
        errors.append("raw constant mismatch")

    alpha = F(program["scale"])
    rho = sum((abs(F(program["h"].get(q, 0)) - alpha * ideal_h.get(q, 0))
               for q in set(program["h"]) | set(ideal_h)), F(0))
    rho += sum((abs(F(program["J"].get(k, 0)) - alpha * ideal_J.get(k, 0))
                for k in set(program["J"]) | set(ideal_J)), F(0))
    ranges_ok = all(F(program["ranges"]["h"][0]) <= F(v) <= F(program["ranges"]["h"][1])
                    for v in program["h"].values())
    ranges_ok &= all(F(program["ranges"]["J"][0]) <= F(v) <= F(program["ranges"]["J"][1])
                     for v in program["J"].values())
    for group in program["coupling_groups"]:
        total = sum((F(program["J"].get(edge(q, r), 0)) for q, r in group), F(0))
        ranges_ok &= F(program["ranges"]["coupling_group"][0]) <= total <= F(program["ranges"]["coupling_group"][1])
    if not ranges_ok:
        errors.append("exact hardware range violation")
    float_cert = 2 * rho < alpha
    if not float_cert:
        errors.append("rounding ground-state certificate failed")

    rng = np.random.default_rng(seed)
    max_raw_error, max_scaled_error = 0.0, 0.0
    for _ in range(16):
        z = {i: int(rng.choice([-1, 1])) for i in h}
        zp = {q: z[i] for i, chain in chains.items() for q in chain}
        logical = offset + math.fsum(h[i] * z[i] for i in h) + math.fsum(v * z[i] * z[j] for (i, j), v in J.items())
        physical = program["offset_raw"] + math.fsum(v * zp[q] for q, v in raw_h.items()) + math.fsum(v * zp[q] * zp[r] for (q, r), v in raw_J.items())
        scaled = program["offset"] + math.fsum(v * zp[q] for q, v in program["h"].items()) + math.fsum(v * zp[q] * zp[r] for (q, r), v in program["J"].items())
        max_raw_error = max(max_raw_error, abs(physical - logical))
        max_scaled_error = max(max_scaled_error, abs(scaled - program["scale"] * logical))
        if not math.isclose(physical, logical, rel_tol=1e-12, abs_tol=1e-9):
            errors.append("sampled raw consistent-state energy mismatch")
        if not math.isclose(scaled, program["scale"] * logical, rel_tol=1e-12, abs_tol=1e-11):
            errors.append("sampled scaled consistent-state energy mismatch")
    return {"valid": not errors, "errors": errors,
            "float_ground_states_certified": float_cert,
            "coefficient_l1_error_exact": [rho.numerator, rho.denominator],
            "coefficient_l1_error": float(rho), "raw_nonoptimal_gap_lower_bound": 1,
            "scaled_nonoptimal_gap_lower_bound": float(alpha - 2 * rho),
            "exact_ranges_valid": bool(ranges_ok), "sampled_consistent_states": 16,
            "max_raw_energy_error": max_raw_error, "max_scaled_energy_error": max_scaled_error}


def rounded_range_fix(program):
    """Move uniform scale down only if an exact binary64 range test requires it."""
    steps = 0
    while not embedding_lib._exact_range_check(program)["valid"]:
        if steps == 32:
            raise ArithmeticError("range adjustment failed")
        program["scale"] = math.nextafter(program["scale"], 0.0)
        for key in ("h", "J"):
            program[key] = {q: program["scale"] * v for q, v in program[key + "_raw"].items()}
        program["offset"] = program["scale"] * program["offset_raw"]
        steps += 1
    program["range_nextafter_steps"] = steps


def ising_json(h, J, offset):
    return {"h": [[i, value] for i, value in sorted(h.items())],
            "J": [[i, j, value] for (i, j), value in sorted(J.items())],
            "offset": offset}


def decode_program(witness, shared_groups=None):
    result = dict(witness)
    if "coupling_groups" not in result:
        if witness.get("coupling_groups_reference") != "resource_target.json#coupling_groups" or shared_groups is None:
            raise ValueError("Missing shared coupling groups")
        result["coupling_groups"] = shared_groups
    for key in ("h", "h_raw"):
        result[key] = {int(q): v for q, v in witness[key]}
    for key in ("J", "J_raw"):
        result[key] = {edge(q, r): v for q, r, v in witness[key]}
    for key in ("chain_strength_raw", "chain_load", "chain_edges"):
        result[key] = {int(i): v for i, v in witness[key].items()}
    return result


def verify_saved(output):
    """Read witnesses back; recompute checks without live model/embedding state."""
    t = json.loads((output / "resource_target.json").read_text())
    target = nx.Graph()
    target.add_nodes_from(t["nodes"])
    target.add_edges_from(t["edges"])
    records = []
    for path in sorted(output.glob("resource_witness_*.json")):
        witness = json.loads(path.read_text())
        source = nx.Graph()
        source.add_nodes_from(witness["source"]["nodes"])
        source.add_edges_from(witness["source"]["edges"])
        chains = {int(i): v for i, v in witness["embedding"].items()}
        checks = audit_chains(source, target, chains)
        programs = []
        for entry in witness["programs"]:
            logical = entry["logical"]
            h = {int(i): v for i, v in logical["h"]}
            J = {edge(i, j): v for i, j, v in logical["J"]}
            programs.append({"variant": entry["variant"], **audit_program(
                h, J, logical["offset"], source, target, chains,
                decode_program(entry["physical"], t.get("coupling_groups")))})
        records.append({"file": path.name, "embedding": checks, "programs": programs})
    valid = all(r["embedding"]["valid"] and all(p["valid"] for p in r["programs"]) for r in records)
    result = {"valid": valid, "witnesses": len(records),
              "programs": sum(len(r["programs"]) for r in records),
              "records": records}
    save(output / "resource_saved_validation.json", result)
    if not valid:
        raise AssertionError("Saved-witness validation failed")
    return result


def run(args):
    from models import make_patch, direct_model, dual_model, interaction_graph, repair_radius

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    target = embedding_lib.make_target(g=6, t=4)
    from dwave.system.coupling_groups import coupling_groups
    target_witness = embedding_lib.graph_witness(target)
    target_witness["coupling_groups"] = list(coupling_groups(target))
    save(output / "resource_target.json", target_witness)
    versions = embedding_lib.versions()
    versions["python"] = platform.python_version()
    request = {"sizes": args.sizes, "seeds": args.seeds, "timeout_seconds": args.timeout,
               "tries": args.tries, "target": "ideal Zephyr Z_(6,4), integer labels, no defects",
               "target_nodes": len(target), "target_edges": target.number_of_edges(),
               "weights": "all ones", "syndrome_rule": "Bernoulli(0.1) errors from NumPy default_rng(3100+d); first bit forced 1",
               "encodings": ["direct_global Lambda=n+1", "direct_local Lambda=repair_radius+1", "dual ell=0,1"],
               "placement": "same generic minorminer parameters for direct/dual structural graphs",
               "physical_fields": "uniform over branch",
               "physical_logical_couplers": "one lexicographic contact per logical edge",
               "chain_strength": "|h_i|+sum_j|J_ij|+1 on BFS tree; singleton 0",
               "h_range": [-1, 1], "J_range": [-1, 1], "coupling_group_range": [-13, 10],
               "range_status": "illustrative common constraints, not a live-device property export",
               "scale": "largest positive uniform scale permitted; common minimum across dual classes; no cap at 1",
               "QPU_access": False, "versions": versions,
               "imported_allocator_sha256": hashlib.sha256((OLD / "embedding.py").read_bytes()).hexdigest(),
               "models_sha256": hashlib.sha256((LAB / "scripts" / "models.py").read_bytes()).hexdigest()}
    save(output / "resource_request.json", request)
    records, inputs = [], []
    started = time.perf_counter()
    for d in args.sizes:
        patch = make_patch(d)
        weights = np.ones(patch["n"])
        sampled = (np.random.default_rng(3100+d).random(patch["n"]) < .1).astype(np.uint8)
        sampled[0] = 1
        syndrome = (patch["H"] @ sampled) % 2
        R = repair_radius(patch, weights)
        models = {
            "direct_global": direct_model(patch, syndrome, weights, penalty=patch["n"]+1),
            "direct_local": direct_model(patch, syndrome, weights, penalty=R+1),
            "dual_0": dual_model(patch, syndrome, weights, ell=0),
            "dual_1": dual_model(patch, syndrome, weights, ell=1),
        }
        inputs.append({"d": d, "n_error": patch["n"], "checks": len(patch["H"]),
                       "stabilizers": patch["B"].shape[1], "repair_radius": R,
                       "weights": weights.tolist(), "syndrome": syndrome.tolist(),
                       "H_rows": patch["rows"], "B_rows": [np.flatnonzero(row).tolist() for row in patch["B"]],
                       "logical_operator": patch["L"].tolist(), "models": models})
        for encoding, variants in (("direct", ["direct_global", "direct_local"]), ("dual", ["dual_0", "dual_1"])):
            source = interaction_graph(models[variants[0]], structural=True)
            assert all(set(interaction_graph(models[v], structural=True).edges) == set(source.edges) for v in variants)
            for seed in args.seeds:
                result = embedding_lib.find_automatic_embedding(source, target, seed=seed, timeout=args.timeout, tries=args.tries)
                record = {"d": d, "encoding": encoding, "seed": seed, "status": result["status"],
                          "logical_variables": len(source), "logical_edges": source.number_of_edges(),
                          "search_seconds": result["elapsed_seconds"], "programs": []}
                if result["status"] == "valid":
                    chains = result["embedding"]
                    record.update(audit_chains(source, target, chains))
                    if not record["valid"]:
                        raise AssertionError(record)
                    programs = []
                    allocation_started = time.perf_counter()
                    for variant in variants:
                        m = models[variant]
                        h = dict(enumerate(m["h"]))
                        J = {edge(i, j): v for i, j, v in m["J"]}
                        physical = embedding_lib.allocate_physical(
                            h, J, m["offset"], target, chains, chain_margin=1,
                            h_range=(-1,1), j_range=(-1,1), group_range=(-13,10), cap_scale=False)
                        rounded_range_fix(physical)
                        programs.append((variant, h, J, m["offset"], physical))
                    if encoding == "dual":
                        common = min(p[4]["scale"] for p in programs)
                        for _, _, _, _, physical in programs:
                            physical["unshared_scale"] = physical["scale"]
                            physical["scale"] = common
                            for key in ("h", "J"):
                                physical[key] = {q: common*v for q, v in physical[key+"_raw"].items()}
                            physical["offset"] = common*physical["offset_raw"]
                            rounded_range_fix(physical)
                        # Rounded range steps may differ. Share the final safe minimum again.
                        common = min(p[4]["scale"] for p in programs)
                        for _, _, _, _, physical in programs:
                            physical["scale"] = common
                            for key in ("h", "J"):
                                physical[key] = {q: common*v for q, v in physical[key+"_raw"].items()}
                            physical["offset"] = common*physical["offset_raw"]
                    record["allocation_seconds"] = time.perf_counter()-allocation_started
                    witness = {"d": d, "encoding": encoding, "seed": seed,
                               "source": embedding_lib.graph_witness(source),
                               "target_reference": "resource_target.json",
                               "embedding": {str(i): list(map(int, chain)) for i, chain in sorted(chains.items())},
                               "programs": []}
                    for variant, h, J, offset, physical in programs:
                        audit = audit_program(h, J, offset, source, target, chains, physical)
                        if not audit["valid"]:
                            raise AssertionError(audit)
                        record["programs"].append({"variant": variant, "scale": physical["scale"],
                            "limiter": physical["scale_limiter"],
                            "chain_strength_max_raw": max(physical["chain_strength_raw"].values(), default=0),
                            "coefficient_max_logical": max([abs(v) for v in h.values()]+[abs(v) for v in J.values()], default=0),
                            "validation": audit})
                        physical_witness = embedding_lib.physical_witness(physical)
                        del physical_witness["coupling_groups"]
                        physical_witness["coupling_groups_reference"] = "resource_target.json#coupling_groups"
                        witness["programs"].append({"variant": variant,
                            "logical": ising_json(h, J, offset), "physical": physical_witness})
                    path = output / f"resource_witness_d{d}_{encoding}_seed{seed}.json"
                    save(path, witness)
                    if d == 2 and seed == 11:
                        compact = {k: witness[k] for k in ["d", "encoding", "embedding", "source"]}
                        compact["programs"] = [{"variant": x["variant"], "logical": x["logical"],
                            "physical": {k: x["physical"][k] for k in
                                ["h", "J", "offset", "scale", "chain_edges", "chain_strength_raw"]}}
                            for x in witness["programs"]]
                        save(output / f"resource_compact_d2_{encoding}_seed11.json", compact)
                    record["witness"] = path.name
                records.append(record)
                save(output / "resource_runs.json", records)
                print(json.dumps({k: record.get(k) for k in ["d", "encoding", "seed", "status", "physical_qubits", "chain_max", "search_seconds"]}), flush=True)
        save(output / "resource_inputs.json", inputs)
    grouped = []
    for d in args.sizes:
        row = {"d": d, "n_error": next(x["n_error"] for x in inputs if x["d"]==d)}
        for encoding in ("direct", "dual"):
            subset = [r for r in records if r["d"]==d and r["encoding"]==encoding]
            ok = [r for r in subset if r["status"]=="valid"]
            summary = {"successes": len(ok), "attempts": len(subset),
                       "logical_variables": subset[0]["logical_variables"], "logical_edges": subset[0]["logical_edges"],
                       "median_search_seconds_all_attempts": statistics.median(r["search_seconds"] for r in subset)}
            if ok:
                summary.update({"physical_qubits_range": [min(r["physical_qubits"] for r in ok), max(r["physical_qubits"] for r in ok)],
                                "physical_qubits_median": statistics.median(r["physical_qubits"] for r in ok),
                                "max_chain_range": [min(r["chain_max"] for r in ok), max(r["chain_max"] for r in ok)],
                                "scales": {v: [min(p["scale"] for r in ok for p in r["programs"] if p["variant"]==v),
                                               max(p["scale"] for r in ok for p in r["programs"] if p["variant"]==v)]
                                           for v in {p["variant"] for r in ok for p in r["programs"]}}})
            row[encoding] = summary
        if row["direct"]["successes"] and row["dual"]["successes"]:
            row["median_qubit_ratio_direct_to_one_dual_class"] = row["direct"]["physical_qubits_median"] / row["dual"]["physical_qubits_median"]
            row["dual_two_parallel_nominal_qubits"] = 2*row["dual"]["physical_qubits_median"]
        grouped.append(row)
    validation = verify_saved(output)
    summary = {"elapsed_seconds": time.perf_counter()-started, "cases": grouped,
               "saved_validation": {k: validation[k] for k in ["valid", "witnesses", "programs"]},
               "interpretation": "Two dual logical classes require two separate anneals. Sequential runs reuse one embedding; twice the qubit count is only a lower accounting estimate for parallel independent placement, which is not constructed here. Search failure does not prove non-embeddability. No speed/success-probability/QPU claims."}
    save(output / "resource_summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", nargs="+", type=int, default=[2,3,5,7,9])
    parser.add_argument("--seeds", nargs="+", type=int, default=[11,29,47])
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--tries", type=int, default=4)
    parser.add_argument("--output", default=str(LAB / "results"))
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        print(json.dumps({k: v for k, v in verify_saved(Path(args.output)).items() if k != "records"}, indent=2))
    else:
        run(args)
