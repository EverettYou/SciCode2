"""Exact small-system execution parity between dense trajectories and MPS.

The MPS backend receives fixed measurement records: it never resamples an
outcome. This makes every local Born probability and every normalized update
directly comparable with the companion dense implementation.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import quimb.tensor as qtn
import torch


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
sys.path.insert(0, str(REPOSITORY / "papers" / "liu2025mqdm" / "repo"))

from src import ForwardDiffusion, WeakMeasurement  # noqa: E402
from src.model import PolicyModel  # noqa: E402


EPSILON = 0.5
T = 6
TRAJECTORIES = 8
TOLERANCE = 1e-10


def _dense_vector(mps: qtn.MatrixProductState) -> np.ndarray:
    return np.asarray(mps.to_dense()).reshape(-1)


def _mps_from_dense(state: torch.Tensor) -> qtn.MatrixProductState:
    n_qubits = state.numel().bit_length() - 1
    vector = state.detach().cpu().numpy().astype(np.complex128, copy=False)
    return qtn.MatrixProductState.from_dense(vector, dims=[2] * n_qubits)


def _normalized_gate(mps: qtn.MatrixProductState, gate: np.ndarray, where: tuple[int, ...]) -> tuple[qtn.MatrixProductState, float]:
    trial = mps.copy()
    trial.gate_(gate, where=where, contract=True)
    # Quimb returns the vector norm, while a selected Born probability is its
    # square. Keeping this explicit makes the comparison independent of the
    # normalization convention used by the tensor backend.
    probability = float(abs(trial.norm()) ** 2)
    if probability <= 0.0:
        raise RuntimeError(f"nonpositive selected-outcome probability: {probability}")
    trial.normalize()
    return trial, probability


def _dense_local_step(state: torch.Tensor, gate: torch.Tensor, site: int) -> tuple[torch.Tensor, float]:
    n_qubits = state.numel().bit_length() - 1
    shape = (2,) * n_qubits
    tensor = state.reshape(shape)
    moved = tensor.movedim(site, 0).reshape(2, -1)
    post = (gate @ moved).reshape((2,) + shape[:site] + shape[site + 1 :]).movedim(0, site).reshape(-1)
    probability = float((post.abs() ** 2).sum().item())
    return post / probability**0.5, probability


def _fixture(n_qubits: int) -> tuple[torch.Tensor, torch.Tensor, str]:
    if n_qubits in (1, 2):
        records = torch.load(
            BENCHMARK / "labs" / "lab-001-local-controller-feasibility" / "artifacts" / "dense-splits-v1" / f"n{n_qubits}-validation.pt",
            weights_only=True,
        )[:TRAJECTORIES]
        initial = torch.zeros(TRAJECTORIES, 2**n_qubits, dtype=torch.complex128)
        initial[:, 0] = 1.0
        return initial, records, "dense-splits-v1"
    payload = torch.load(
        BENCHMARK / "labs" / "lab-002-dense-bounded-support-isolation" / "artifacts" / "dense-n3-state-families-v1" / "weak-local-validation.pt",
        weights_only=True,
    )
    return payload["initial_states"][:TRAJECTORIES], payload["trajectories"][:TRAJECTORIES], "dense-n3-state-families-v1/weak-local"


def run(n_qubits: int) -> dict[str, object]:
    torch.manual_seed(4300 + n_qubits)
    torch.set_num_threads(1)
    initial, records, fixture = _fixture(n_qubits)
    policy = PolicyModel(n_qubits).double().eval()
    wm = WeakMeasurement(EPSILON)
    local = wm.local.detach().cpu().numpy().astype(np.complex128)

    max_probability_error = 0.0
    max_forward_state_error = 0.0
    max_reverse_state_error = 0.0
    max_final_infidelity = 0.0
    trajectories_checked = 0

    for i in range(TRAJECTORIES):
        dense = initial[i].clone()
        mps = _mps_from_dense(dense)
        for step in range(T):
            for site, token in enumerate(records[i, step].tolist()):
                dense, dense_probability = _dense_local_step(dense, wm.local[token], site)
                mps, mps_probability = _normalized_gate(mps, local[token], (site,))
                max_probability_error = max(max_probability_error, abs(dense_probability - mps_probability))
                max_forward_state_error = max(max_forward_state_error, float(np.max(np.abs(dense.detach().cpu().numpy() - _dense_vector(mps)))))

        dense_final = dense.clone()
        mps_reverse = mps
        for t_forward in range(T - 1, 0, -1):
            future = records[i : i + 1, t_forward:, :]
            with torch.no_grad():
                unitary = policy(future, dtype=torch.complex128)[0]
            dense = unitary @ dense
            mps_reverse, _ = _normalized_gate(mps_reverse, unitary.detach().cpu().numpy(), tuple(range(n_qubits)))
            max_reverse_state_error = max(max_reverse_state_error, float(np.max(np.abs(dense.detach().cpu().numpy() - _dense_vector(mps_reverse)))))
        fidelity = abs(np.vdot(initial[i].detach().cpu().numpy(), _dense_vector(mps_reverse))) ** 2
        max_final_infidelity = max(max_final_infidelity, float(1.0 - fidelity))
        # Guard that the forward path did not accidentally compare an unrelated fixture.
        if not torch.isfinite(dense_final).all():
            raise RuntimeError("nonfinite dense forward state")
        trajectories_checked += 1

    result: dict[str, object] = {
        "schema_version": 1,
        "kind": "mps_dense_execution_parity",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": n_qubits,
        "epsilon": EPSILON,
        "time_steps": T,
        "trajectories_checked": trajectories_checked,
        "fixture": fixture,
        "mps_cutoff": 0.0,
        "mps_max_bond": None,
        "policy": "frozen-random-companion-dense-qr",
        "max_selected_probability_abs_error": max_probability_error,
        "max_forward_state_abs_error": max_forward_state_error,
        "max_reverse_state_abs_error": max_reverse_state_error,
        "max_final_reverse_infidelity": max_final_infidelity,
        "tolerance": TOLERANCE,
    }
    assert max_probability_error <= TOLERANCE, result
    assert max_forward_state_error <= TOLERANCE, result
    assert max_reverse_state_error <= TOLERANCE, result
    return result


def main() -> None:
    output = LAB / "results" / "mps-dense-execution-parity-v1"
    output.mkdir(parents=True, exist_ok=True)
    for n_qubits in (1, 2, 3):
        result = run(n_qubits)
        path = output / f"n{n_qubits}.json"
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
