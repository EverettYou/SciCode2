"""Independent exhaustive truth-table/ground-state checks for compiler.py."""
import json
import itertools
import pathlib
import platform
import time
import importlib.metadata as md
from fractions import Fraction
import numpy as np
from compiler import compile_instance, complete_feasible, energy, residual_energy, model_graph, update_instance

LAB = pathlib.Path(__file__).resolve().parents[1]


def audit(model):
    n, N = model["n_original"], len(model["linear"])
    assert N <= 20
    values = np.arange(1 << N, dtype=np.uint64)
    bits = ((values[:, None] >> np.arange(N, dtype=np.uint64)) & 1).astype(np.int8)
    energies = np.full(1 << N, model["offset"])
    energies += bits @ np.asarray(model["linear"])
    for i, j, q in model["quadratic"]:
        energies += q*bits[:, i]*bits[:, j]
    errors = bits[:1 << n, :n]
    feasible = np.ones(1 << n, dtype=bool)
    for row, s in zip(model["rows"], model["syndrome"]):
        feasible &= errors[:, row].sum(axis=1) % 2 == s
    costs = errors @ np.asarray(model["weights"])
    optimum = float(costs[feasible].min())
    tolerance = 1e-9 * max(1, model["penalty"])
    ground_ids = np.flatnonzero(np.abs(energies-energies.min()) <= tolerance)
    ground_projections = ground_ids % (1 << n)
    assert abs(energies.min()-optimum) <= tolerance
    assert np.all(feasible[ground_projections])
    assert np.all(np.abs(costs[ground_projections]-optimum) <= tolerance)
    # Each feasible error has the claimed energy and is explicitly attained.
    for i in np.flatnonzero(feasible):
        y = complete_feasible(model, errors[i])
        assert abs(energy(model, y)-costs[i]) <= tolerance
    # Direct residual-form polynomial identity, independently on all states.
    residual = bits[:, :n] @ np.asarray(model["weights"])
    for c in model["constraints"]:
        if c["kind"] == "parity":
            a, b = c["inputs"]
            residual += model["penalty"]*((bits[:, a] + bits[:, b]) % 2 != c["target"])
        else:
            res = np.full(1 << N, c["constant"], dtype=np.int64)
            for v, a in c["terms"]:
                res += a*bits[:, v]
            residual += model["penalty"]*res**2
    assert np.max(np.abs(residual-energies)) <= tolerance
    ground_patterns = sorted(set(int(x) for x in ground_projections))
    true_ground_patterns = np.flatnonzero(feasible & (np.abs(costs-optimum) <= tolerance)).tolist()
    assert ground_patterns == true_ground_patterns
    return {"n": n, "qubo_variables": N, "states_checked": 1 << N,
            "qubo_edges": model_graph(model).number_of_edges(), "optimum": optimum,
            "feasible_patterns": int(feasible.sum()), "tied_optimal_patterns": len(ground_patterns),
            "max_polynomial_residual": float(np.max(np.abs(residual-energies)))}


def main():
    start = time.perf_counter()
    rng = np.random.default_rng(20261007)
    records = []
    named = [
        ("isolated_and_negative", [[], [0], [1,2]], 4, [0,1,0], [-2., 0., 1.5, -3.]),
        ("redundant_hyperchecks", [[0,1,2], [0,1,2], [0,1], [0,2], []], 4,
         [1,1,0,1,0], [-1., 0., 2., 0.]),
        ("high_degree_row", [[0,1,2,3,4]], 6, [1], [-2., -1., 0., 1., 2., -3.]),
        ("tied_parity", [[0,1]], 2, [1], [0.,0.]),
        ("empty_matrix", [], 3, [], [0., -1., 2.]),
        ("coordinate_cancellation", [[0,0,1,2,2],[1,2]], 3, [1,0], [0.,0.,0.]),
    ]
    for name, rows, n, syndrome, weights in named:
        model = compile_instance(rows,n,syndrome,weights)
        record = audit(model); record["case"] = name; records.append(record)
        (LAB/"results"/f"compiler_{name}.json").write_text(json.dumps(model,indent=2))
    for trial in range(32):
        n=5; m=int(rng.integers(1,5))
        rows=[sorted(rng.choice(n,size=int(rng.integers(0,4)),replace=False).tolist()) for _ in range(m)]
        truth=rng.integers(0,2,size=n)
        syndrome=[int(truth[row].sum()%2) for row in rows]
        weights=rng.integers(-3,4,size=n).astype(float).tolist()
        model=compile_instance(rows,n,syndrome,weights,penalty=30.)
        record=audit(model); record["case"]=f"random_{trial:02d}"; records.append(record)
        newtruth=rng.integers(0,2,size=n)
        newsyndrome=[int(newtruth[row].sum()%2) for row in rows]
        changed=update_instance(model,syndrome=newsyndrome)
        assert model["variables"]==changed["variables"]
        assert model["structural_edges"]==changed["structural_edges"]
        audit(changed)
    # Repeated updates, including float-valued binary syndrome entries, must
    # preserve the exact companion and match fresh compilation.
    chain=compile_instance([[0],[0,1],[0,1,2],[1,2,3,4]],5,[0,0,0,0],[0.]*5,penalty=30.)
    for trial in range(100):
        truth=rng.integers(0,2,size=5)
        s=[float(truth[row].sum()%2) if trial%2 else int(truth[row].sum()%2) for row in chain["rows"]]
        w=(rng.integers(-8,9,size=5)/4).tolist()
        changed=update_instance(chain,s,w)
        fresh=compile_instance(chain["rows"],5,s,w,penalty=30.)
        assert changed["exact_coefficients"]==fresh["exact_coefficients"]
        assert changed["structural_edges"]==fresh["structural_edges"]
        chain=changed
    # A floating residual on an exactly cancelled quadratic term must still
    # enter rho after the exact serialization has omitted that zero term.
    cancelled=compile_instance([[0,1,2],[0,1]],3,[0,0],[0.]*3,penalty=1.)
    assert not any(i==0 and j==1 for i,j,_,_ in cancelled["exact_coefficients"]["quadratic"])
    cancelled["quadratic"].append([0,1,.6])
    corrupt=update_instance(cancelled,require_float_fidelity=False)
    assert not corrupt["numeric_certificate"]["float_ground_states_certified"]
    assert Fraction(*corrupt["numeric_certificate"]["coefficient_error_l1_exact"])==Fraction(.6)
    report={"seed":20261007,"compiler_cases":len(records),"syndrome_update_cases":32,
            "chained_update_cases":100,"exact_zero_rounding_residual_test":True,
            "states_checked_primary":sum(r["states_checked"] for r in records),
            "elapsed_seconds":time.perf_counter()-start,"python":platform.python_version(),
            "versions":{p:md.version(p) for p in ["numpy","networkx","dimod","scipy"]},
            "all_passed":True,"cases":records}
    (LAB/"results"/"compiler_validation.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},indent=2))

if __name__ == "__main__": main()
