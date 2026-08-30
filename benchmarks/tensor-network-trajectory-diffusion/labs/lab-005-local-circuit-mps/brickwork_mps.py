"""Dense/MPS parity and entanglement sweep for local QR brickwork circuits."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import quimb.tensor as qtn


LAB = Path(__file__).resolve().parent
LAYERS = 6
TOLERANCE = 1e-10


def brickwork_bonds(n: int, layer: int) -> tuple[tuple[int, int], ...]:
    start = layer % 2
    return tuple((site, site + 1) for site in range(start, n - 1, 2))


def gate(seed: int, layer: int, bond: tuple[int, int]) -> np.ndarray:
    """Generic QR gate; same parameters are shared across equal bond parity."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, layer, bond[0] % 2]))
    raw = rng.normal(size=(4, 4)) + 1j * rng.normal(size=(4, 4))
    unitary, upper = np.linalg.qr(raw)
    diagonal = np.diag(upper)
    return unitary * (diagonal / np.abs(diagonal))[None, :]


def apply_dense(state: np.ndarray, unitary: np.ndarray, bond: tuple[int, int]) -> np.ndarray:
    n = int(np.log2(state.size))
    tensor = state.reshape((2,) * n)
    moved = np.moveaxis(tensor, bond, (0, 1)).reshape(4, -1)
    updated = (unitary @ moved).reshape((2, 2) + (2,) * (n - 2))
    return np.moveaxis(updated, (0, 1), bond).reshape(-1)


def apply_mps(mps: qtn.MatrixProductState, unitary: np.ndarray, bond: tuple[int, int]) -> qtn.MatrixProductState:
    mps.gate_(unitary, where=bond, contract="split-gate", cutoff=0.0, max_bond=None)
    return mps


def parity_n3() -> dict[str, object]:
    rng = np.random.default_rng(6103)
    dense = rng.normal(size=8) + 1j * rng.normal(size=8)
    dense /= np.linalg.norm(dense)
    mps = qtn.MatrixProductState.from_dense(dense, dims=[2, 2, 2])
    maximum_error = 0.0
    maximum_bond = mps.max_bond()
    for layer in range(LAYERS):
        for bond in brickwork_bonds(3, layer):
            unitary = gate(6200, layer, bond)
            dense = apply_dense(dense, unitary, bond)
            apply_mps(mps, unitary, bond)
            maximum_error = max(maximum_error, float(np.max(np.abs(dense - np.asarray(mps.to_dense()).reshape(-1)))))
            maximum_bond = max(maximum_bond, mps.max_bond())
    result = {"kind": "local_qr_circuit_dense_mps_parity", "n_qubits": 3, "layers": LAYERS, "max_state_abs_error": maximum_error, "realized_max_bond": maximum_bond, "tolerance": TOLERANCE}
    assert maximum_error <= TOLERANCE, result
    return result


def sweep(n: int) -> dict[str, object]:
    mps = qtn.MPS_computational_state("0" * n, dtype="complex128")
    started = time.perf_counter()
    maximum_bond = 1
    for layer in range(LAYERS):
        for bond in brickwork_bonds(n, layer):
            apply_mps(mps, gate(6200, layer, bond), bond)
            maximum_bond = max(maximum_bond, mps.max_bond())
    return {"kind": "local_qr_circuit_mps_sweep", "n_qubits": n, "layers": LAYERS, "realized_max_bond": maximum_bond, "elapsed_seconds": time.perf_counter() - started, "dense_state_bytes_complex128": 16 * 2**n}


def main() -> None:
    output = LAB / "results" / "brickwork-v1"
    output.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "parity_n3": parity_n3(), "large_n": [sweep(n) for n in (4, 8, 16, 24)]}
    (output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
