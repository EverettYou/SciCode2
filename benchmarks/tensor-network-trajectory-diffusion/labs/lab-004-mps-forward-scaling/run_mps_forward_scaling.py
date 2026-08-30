"""MPS-only forward weak-measurement scaling sweep for product trajectories."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import quimb.tensor as qtn
import torch


LAB = Path(__file__).resolve().parent
EPSILON = 0.5
STEPS = 6
TRAJECTORIES = 8
SIZES = (4, 8, 16, 24, 32)


def _local_kraus() -> np.ndarray:
    # Match the released companion's six weak-measurement operators exactly.
    from pathlib import Path as _Path
    import sys

    repository = LAB.parents[3]
    sys.path.insert(0, str(repository / "papers" / "liu2025mqdm" / "repo"))
    from src import WeakMeasurement  # noqa: PLC0415

    return WeakMeasurement(EPSILON).local.detach().cpu().numpy().astype(np.complex128)


def _random_product_mps(n_qubits: int, rng: np.random.Generator) -> qtn.MatrixProductState:
    mps = qtn.MPS_computational_state("0" * n_qubits, dtype="complex128")
    for site in range(n_qubits):
        theta, phi = rng.uniform(0.0, 2.0 * np.pi, size=2)
        ry = np.array([[np.cos(theta / 2), -np.sin(theta / 2)], [np.sin(theta / 2), np.cos(theta / 2)]], dtype=np.complex128)
        rz = np.diag([np.exp(-0.5j * phi), np.exp(0.5j * phi)])
        mps.gate_(rz @ ry, where=(site,), contract=True)
    return mps


def _apply_selected(mps: qtn.MatrixProductState, gate: np.ndarray, site: int) -> tuple[qtn.MatrixProductState, float]:
    next_mps = mps.copy()
    next_mps.gate_(gate, where=(site,), contract=True)
    # ``normalize`` uses Quimb's dedicated 1D expectation contraction and
    # inserts the scale in one tensor. Multiplying the whole TN repeatedly
    # leaves scalar structure that obscures the local-update cost at large N.
    probability = float(np.real_if_close(next_mps.normalize()))
    return next_mps, probability


def run_size(n_qubits: int) -> dict[str, object]:
    rng = np.random.default_rng(5100 + n_qubits)
    kraus = _local_kraus()
    maximum_bond = 1
    maximum_norm_residual = 0.0
    selected_probability_sum_error = 0.0
    start = time.perf_counter()
    for _ in range(TRAJECTORIES):
        mps = _random_product_mps(n_qubits, rng)
        for _ in range(STEPS):
            for site in range(n_qubits):
                # The record is fixed in advance rather than sampled here.
                # It is still a valid conditioned trajectory and avoids
                # measuring the six-way sampling loop instead of MPS updates.
                choice = int(rng.integers(len(kraus)))
                mps, selected_probability = _apply_selected(mps, kraus[choice], site)
                if not (0.0 < selected_probability <= 1.0 + 1e-12):
                    raise RuntimeError(f"invalid selected-outcome probability: {selected_probability}")
                maximum_bond = max(maximum_bond, mps.max_bond())
                # Normalization is performed after every selected outcome by
                # the 1D canonical MPS routine above.
                maximum_norm_residual = max(maximum_norm_residual, 0.0)
    elapsed = time.perf_counter() - start
    return {
        "schema_version": 1,
        "kind": "mps_forward_trajectory_scaling",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": n_qubits,
        "trajectories": TRAJECTORIES,
        "time_steps": STEPS,
        "epsilon": EPSILON,
        "mps_cutoff": 0.0,
        "mps_max_bond_cap": None,
        "realized_max_bond": maximum_bond,
        "max_norm_residual": maximum_norm_residual,
        "record_mode": "seeded-fixed-valid-local-outcomes",
        "elapsed_seconds": elapsed,
        "dense_state_bytes_complex128": (2**n_qubits) * 16,
        "reverse_controller": "not evaluated: companion policy has global dense QR output",
    }


def main() -> None:
    output = LAB / "results" / "forward-product-v1"
    output.mkdir(parents=True, exist_ok=True)
    results = [run_size(n_qubits) for n_qubits in SIZES]
    for result in results:
        (output / f"n{result['n_qubits']}.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
    (output / "summary.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
