"""Independent small-instance expanded-QUBO versus constrained enumeration."""
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB / "scripts"))
from compiler import compile_instance

cases = [
    ([], 0, [], []),
    ([[], [], [0]], 3, [0, 0, 1], [0, -2, 1]),
    ([[0, 1, 2], [0, 1, 2]], 3, [1, 1], [-1, 0, 2]),
    ([[0, 1, 2, 3]], 4, [0], [1, -1, 0, 2]),
    ([[0, 0, 1, 2, 2], [2, 1, 0]], 3, [1, 0], [-3, 2, 0]),
]
rng = random.Random(102007)
for _ in range(45):
    n, m = rng.randint(1, 4), rng.randint(0, 3)
    rows = [[i for i in range(n) if rng.random() < 0.45] for _ in range(m)]
    hidden = [rng.randrange(2) for _ in range(n)]
    syndrome = [sum(hidden[i] for i in row) % 2 for row in rows]
    weights = [rng.choice([-2, -0.5, 0, 1, 3]) for _ in range(n)]
    cases.append((rows, n, syndrome, weights))

assignments, checks = 0, []
for case_id, (rows, n, syndrome, weights) in enumerate(cases):
    qubo = compile_instance(rows, n, syndrome, weights)
    size = len(qubo["linear"])
    assert size <= 16
    optimum = min(
        sum(weights[i] * e[i] for i in range(n))
        for e in itertools.product((0, 1), repeat=n)
        if all(sum(e[i] for i in row) % 2 == s for row, s in zip(rows, syndrome))
    )
    ground, projections = float("inf"), []
    for y in itertools.product((0, 1), repeat=size):
        value = qubo["offset"] + sum(a * b for a, b in zip(qubo["linear"], y))
        value += sum(v * y[i] * y[j] for i, j, v in qubo["quadratic"])
        assignments += 1
        if value < ground - 1e-8:
            ground, projections = value, [y[:n]]
        elif abs(value - ground) < 1e-8:
            projections.append(y[:n])
    assert abs(ground - optimum) < 1e-8, (case_id, ground, optimum)
    for e in projections:
        assert all(sum(e[i] for i in row) % 2 == s for row, s in zip(rows, syndrome))
        assert abs(sum(weights[i] * e[i] for i in range(n)) - optimum) < 1e-8
    checks.append({"case": case_id, "original_variables": n,
                   "quadratic_variables": size, "optimum": optimum,
                   "ground_states": len(projections)})

result = {
    "status": "pass", "role": "independent coordinator check; no author reference used",
    "seed": 102007, "compiler_sha256": hashlib.sha256((LAB / "scripts/compiler.py").read_bytes()).hexdigest(),
    "cases": len(cases), "assignments_enumerated": assignments, "checks": checks,
    "scope": "Direct expanded-QUBO enumeration versus original constrained optimum. Finite integer/half-integer fixtures; no arbitrary floating-point fidelity claim.",
}
(LAB / "results/reviewer-compiler-check.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({k: v for k, v in result.items() if k != "checks"}, indent=2))
