"""Read saved witnesses without calling solver verification/allocation code."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import random

LAB = Path(__file__).resolve().parents[1]
RESULTS = LAB / "results"
target = json.loads((RESULTS / "target_zephyr_g6.json").read_text())
nodes = set(target["nodes"])
edges = {tuple(sorted(edge)) for edge in target["edges"]}
adjacency = defaultdict(set)
for q, r in edges:
    adjacency[q].add(r)
    adjacency[r].add(q)
rng = random.Random(731007)
checks = []
for path in sorted(RESULTS.glob("witness_*.json")):
    witness = json.loads(path.read_text())
    method = witness["method"]
    name = path.stem.removeprefix("witness_").removesuffix("_" + method)
    model = json.loads((RESULTS / ("model_" + name + ".json")).read_text())
    branches = {int(i): list(branch) for i, branch in witness["embedding"].items()}
    assert set(branches) == set(range(len(model["linear"])))
    owner = {}
    for i, branch in branches.items():
        assert branch and len(set(branch)) == len(branch)
        assert set(branch) <= nodes
        for q in branch:
            assert q not in owner
            owner[q] = i
        reached, pending = {branch[0]}, [branch[0]]
        while pending:
            q = pending.pop()
            for r in adjacency[q] & set(branch) - reached:
                reached.add(r)
                pending.append(r)
        assert reached == set(branch)
    physical_h = dict(witness["h"])
    physical_j = {tuple(sorted((q, r))): value for q, r, value in witness["J"]}
    raw_h = dict(witness["h_raw"])
    raw_j = {tuple(sorted((q, r))): value for q, r, value in witness["J_raw"]}
    assert len(physical_h) == len(witness["h"]) and set(physical_h) == set(owner)
    assert len(physical_j) == len(witness["J"]) and set(physical_j) <= edges
    assert all(q in owner and r in owner for q, r in physical_j)
    alpha = witness["scale"]
    assert alpha > 0
    assert all(math.isclose(physical_h[q], alpha * value, rel_tol=1e-12, abs_tol=1e-12) for q, value in raw_h.items())
    assert all(math.isclose(physical_j[edge], alpha * value, rel_tol=1e-12, abs_tol=1e-12) for edge, value in raw_j.items())
    lo, hi = witness["ranges"]["h"]
    assert all(lo - 1e-12 <= v <= hi + 1e-12 for v in physical_h.values())
    lo, hi = witness["ranges"]["J"]
    assert all(lo - 1e-12 <= v <= hi + 1e-12 for v in physical_j.values())
    lo, hi = witness["ranges"]["coupling_group"]
    for group in target["coupling_groups"]:
        value = math.fsum(physical_j.get(tuple(sorted(edge)), 0) for edge in group)
        assert lo - 1e-12 <= value <= hi + 1e-12
    logical_h = {i: v / 2 for i, v in enumerate(model["linear"])}
    logical_j = {}
    logical_offset = model["offset"] + math.fsum(model["linear"]) / 2
    for i, j, value in model["quadratic"]:
        logical_h[i] += value / 4
        logical_h[j] += value / 4
        logical_j[(i, j)] = value / 4
        logical_offset += value / 4
        assert any(tuple(sorted((q, r))) in edges for q in branches[i] for r in branches[j])
    allocated_h, allocated_j = defaultdict(float), defaultdict(float)
    for q, value in raw_h.items():
        allocated_h[owner[q]] += value
    for (q, r), value in raw_j.items():
        if owner[q] != owner[r]:
            allocated_j[tuple(sorted((owner[q], owner[r])))] += value
    assert all(math.isclose(allocated_h[i], v, abs_tol=1e-9) for i, v in logical_h.items())
    assert set(allocated_j) == set(logical_j)
    assert all(math.isclose(allocated_j[edge], v, abs_tol=1e-9) for edge, v in logical_j.items())
    for i, branch in branches.items():
        chain_edges = witness["chain_edges"][str(i)]
        assert len(chain_edges) == len(branch) - 1
        chain_set = {tuple(sorted(edge)) for edge in chain_edges}
        assert len(chain_set) == len(chain_edges)
        assert chain_set == {edge for edge in raw_j if owner[edge[0]] == owner[edge[1]] == i}
        chain_adj = defaultdict(set)
        for q, r in chain_edges:
            assert q in branch and r in branch and q != r
            chain_adj[q].add(r)
            chain_adj[r].add(q)
        reached, pending = {branch[0]}, [branch[0]]
        while pending:
            for q in chain_adj[pending.pop()] - reached:
                reached.add(q)
                pending.append(q)
        assert reached == set(branch)
        if chain_edges:
            load = abs(logical_h[i]) + sum(abs(v) for (j, k), v in logical_j.items() if i in (j, k))
            strength = witness["chain_strength_raw"][str(i)]
            assert strength > load
            assert all(math.isclose(raw_j[tuple(sorted(edge))], -strength, abs_tol=1e-9) for edge in chain_edges)
    max_error = 0
    for _ in range(32):
        y = [rng.randrange(2) for _ in model["linear"]]
        spins = {q: 2 * y[i] - 1 for q, i in owner.items()}
        qubo_energy = model["offset"] + math.fsum(v * y[i] for i, v in enumerate(model["linear"]))
        qubo_energy += math.fsum(v * y[i] * y[j] for i, j, v in model["quadratic"])
        physical_energy = witness["offset"] + math.fsum(v * spins[q] for q, v in physical_h.items())
        physical_energy += math.fsum(v * spins[q] * spins[r] for (q, r), v in physical_j.items())
        error = abs(physical_energy - alpha * qubo_energy)
        max_error = max(max_error, error)
        assert error < 1e-9
    checks.append({"path": str(path.relative_to(LAB)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "physical_qubits": len(owner), "consistent_states_checked": 32,
                   "max_scaled_energy_error": max_error})
result = {"status": "pass", "role": "independent coordinator review of saved witnesses only",
          "witnesses": len(checks), "seed": 731007, "checks": checks,
          "scope": "Branch validity, actual interactions, coefficient allocation, chain sufficient condition, ranges/group limits, scaled consistent-state energies. No numerical simulation of large physical ground states."}
(RESULTS / "reviewer-witness-check.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "witnesses": len(checks),
                  "consistent_states_checked": 32 * len(checks),
                  "max_scaled_energy_error": max(x["max_scaled_energy_error"] for x in checks)}, indent=2))
