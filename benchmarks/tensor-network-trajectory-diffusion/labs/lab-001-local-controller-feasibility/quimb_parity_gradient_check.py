"""Phase-1 Quimb exact-circuit and finite-difference gate for local heads.

This script is deliberately limited to the approved dense N=1,2 controller
comparison.  It uses the frozen validation fixture, performs no optimization,
and checks one differentiable reverse-loss coordinate per local head.
"""

from __future__ import annotations

import importlib.util
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

from src import QuantumDiffusionLoss, WeakMeasurement  # noqa: E402
from src.model import PolicyModel  # noqa: E402

spec = importlib.util.spec_from_file_location("lab001_prototype", LAB / "prototype.py")
prototype = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(prototype)


def _quimb_unitary(head: torch.nn.Module, features: torch.Tensor, dtype: torch.dtype) -> np.ndarray:
    """Rebuild the head's ordered primitive gates using Quimb raw gates."""
    values = head.out_proj(features).detach().cpu().double().numpy()[0]
    n = head.n_qubits
    circuit = qtn.Circuit(n, gate_contract=False)
    pauli = [
        np.array([[1, 0], [0, 1]], dtype=np.complex128),
        np.array([[0, 1], [1, 0]], dtype=np.complex128),
        np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.array([[1, 0], [0, -1]], dtype=np.complex128),
    ]

    def rotation(matrix: np.ndarray, angle: float) -> np.ndarray:
        return np.cos(angle) * np.eye(matrix.shape[0]) - 1j * np.sin(angle) * matrix

    if isinstance(head, prototype.LocalHamiltonianHead):
        basis = [
            np.kron(pauli[a], pauli[b]) if n == 2 else pauli[a]
            for a, b in ((a, b) for a in range(4) for b in range(4))
            if (n == 2 and (a != 0 or b != 0)) or (n == 1 and b == 0 and a != 0)
        ]
        ordered = list(enumerate(basis))
        for _ in range(head.trotter_steps):
            for index, matrix in ordered + ordered[::-1]:
                circuit.apply_gate(rotation(matrix, 0.5 * values[index] / head.trotter_steps), *range(n))
    else:
        angles = values.reshape(head.depth, -1)
        for layer in range(head.depth):
            cursor = 0
            for qubit in range(n):
                local = np.eye(2, dtype=np.complex128)
                for axis in (3, 2, 3):
                    local = rotation(pauli[axis], 0.5 * angles[layer, cursor]) @ local
                    cursor += 1
                circuit.apply_gate(local, qubit)
            if n == 2:
                for axis in (1, 2, 3):
                    circuit.apply_gate(rotation(np.kron(pauli[axis], pauli[axis]), 0.5 * angles[layer, cursor]), 0, 1)
                    cursor += 1
    return np.asarray(circuit.get_uni().to_dense())


def _mps_state(head: torch.nn.Module, features: torch.Tensor) -> np.ndarray:
    """Apply the same raw gates to |0...0> with no truncation at N=2."""
    # A raw gate circuit gives a direct, no-truncation CircuitMPS smoke path.
    unitary = _quimb_unitary(head, features, torch.complex128)
    circuit = qtn.CircuitMPS(2, max_bond=None, cutoff=0.0, gate_contract=False)
    circuit.apply_gate(unitary, 0, 1)
    return np.asarray(circuit.psi.to_dense()).reshape(-1)


def _loss(policy: torch.nn.Module, trajectories: torch.Tensor) -> torch.Tensor:
    return QuantumDiffusionLoss(WeakMeasurement(0.5), policy)(trajectories)


def run(n_qubits: int, family: str, seed: int, epsilon: float) -> dict[str, object]:
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    companion = PolicyModel(n_qubits)
    policy = prototype.CircuitPolicy(n_qubits, family)
    policy.encoder.transformer.load_state_dict(companion.transformer.state_dict())
    trajectories = torch.load(
        LAB / "artifacts" / "dense-splits-v1" / f"n{n_qubits}-validation.pt",
        weights_only=True,
    )[:2]
    records = trajectories[:1, 1:, :]
    features = policy.encoder(records)
    dense = policy.head(features, torch.complex128)[0].detach().cpu().numpy()
    quimb = _quimb_unitary(policy.head, features, torch.complex128)
    parity_error = float(np.max(np.abs(dense - quimb)))

    policy.zero_grad(set_to_none=True)
    loss = _loss(policy, trajectories)
    loss.backward()
    parameter = policy.head.out_proj.weight
    index = (0, 0)
    analytic = float(parameter.grad[index].item())
    with torch.no_grad():
        original = float(parameter[index].item())
        parameter[index] = original + epsilon
    plus = float(_loss(policy, trajectories).item())
    with torch.no_grad():
        parameter[index] = original - epsilon
    minus = float(_loss(policy, trajectories).item())
    with torch.no_grad():
        parameter[index] = original
    finite_difference = (plus - minus) / (2.0 * epsilon)
    gradient_error = abs(analytic - finite_difference)
    result: dict[str, object] = {
        "schema_version": 1,
        "kind": "local_head_quimb_parity_gradient_check",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": n_qubits,
        "family": family,
        "seed": seed,
        "fixture": "dense-splits-v1",
        "optimization_steps": 0,
        "quimb_version": "1.11.2",
        "dense_quimb_unitary_max_abs_error": parity_error,
        "finite_difference_epsilon": epsilon,
        "analytic_gradient": analytic,
        "central_finite_difference_gradient": finite_difference,
        "gradient_abs_error": gradient_error,
    }
    if n_qubits == 2:
        torch_state = dense @ np.array([1, 0, 0, 0], dtype=np.complex128)
        result["circuit_mps_state_max_abs_error"] = float(np.max(np.abs(torch_state - _mps_state(policy.head, features))))
    assert parity_error < 1e-10, result
    assert gradient_error < 2e-5, result
    if n_qubits == 2:
        assert result["circuit_mps_state_max_abs_error"] < 1e-10, result
    return result


def main() -> None:
    output = LAB / "results" / "local-head-quimb-parity-v1"
    output.mkdir(parents=True, exist_ok=True)
    for n_qubits in (1, 2):
        for family in ("hamiltonian", "gates"):
            # The companion loss is effectively float32 internally, so this
            # step avoids cancellation while remaining in the local regime.
            result = run(n_qubits, family, seed=2600 + n_qubits, epsilon=3e-4)
            path = output / f"n{n_qubits}-{family}-seed{result['seed']}.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
