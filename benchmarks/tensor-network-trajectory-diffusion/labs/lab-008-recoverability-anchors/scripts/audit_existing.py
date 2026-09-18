"""Audit saved Lab 007 evidence, without claiming to rerun its experiments."""
import hashlib
import json
import math
import statistics
from pathlib import Path


def main():
    lab = Path(__file__).resolve().parents[2] / "lab-007-paper-hamiltonian-score-matching"
    manifest = json.loads((lab / "results/continuation-final-manifest-v2.json").read_text())
    for relative, digest in manifest.items():
        actual = hashlib.sha256((lab / relative).read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"artifact hash changed: {relative}")
    gap = json.loads((lab / "results/tdvp-gap-audit-64-v2/summary.json").read_text())
    for row in gap["parity"]:
        if row["state_error"] > 1e-12 or row["gradient_error"] > 1e-12 or row["fd_error"] > 1e-8:
            raise ValueError("small-system parity gate failed")
    backends = gap["rollout"]["backends"]
    for row in backends.values():
        if len(row["fidelity"]) != 64:
            raise ValueError("wrong paired sample count")
        if abs(statistics.mean(row["fidelity"]) - row["mean_fidelity"]) > 1e-12:
            raise ValueError("saved mean disagrees with trajectories")
    if min(backends["tdvp"]["paired_dense_fidelity"]) < 1 - 1e-8:
        raise ValueError("TDVP/dense final-state parity failed")
    scale = []
    for name in ("shared-cluster-n5-transfer-v2", "shared-cluster-large-transfer-v2"):
        data = json.loads((lab / "results" / name / "summary.json").read_text())
        for row in data["rows"]:
            values = row["fidelity"]
            if not all(math.isfinite(v) and -1e-10 <= v <= 1+1e-10 for v in values):
                raise ValueError("invalid trajectory fidelity")
            if abs(statistics.mean(values) - row["mean_fidelity"]) > 1e-12:
                raise ValueError("saved transfer mean disagrees with trajectories")
            if row.get("chi") == 4 and row["backend"] == "tdvp":
                scale.append(dict(n=row["n"], fidelity=row["mean_fidelity"], samples=len(values)))
    grad = json.loads((lab / "results/tdvp-rollout-gradient-audit-v3/summary.json").read_text())
    for row in grad["rows"]:
        if not (row["passed"] and row["all_gradients_finite"] and row["max_dense_gradient"] > 0):
            raise ValueError("rollout gradient gate failed")
    print(json.dumps(dict(status="saved-artifact-audit-passed", artifact_hashes=len(manifest),
                          paired_fidelity={k:v["mean_fidelity"] for k,v in backends.items()},
                          historical_transfer=scale,
                          scope="Numerical infrastructure evidence; not optimal recovery gold"), indent=2))


if __name__ == "__main__":
    main()
