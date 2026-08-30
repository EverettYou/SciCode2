"""Zero-optimizer numerical gate for all six Lab-002 controller contracts."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import quimb
import quimb.tensor as qtn
import torch

from dense_block_controller import (
    DenseBlockController,
    PANELS,
    SUPPORTS,
    apply_block_schedule,
)


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
COMPANION = REPOSITORY / "papers" / "liu2025mqdm" / "repo"
sys.path.insert(0, str(COMPANION))

from src.model import PolicyModel, measurement_sequence_to_tokens  # noqa: E402


FIXTURE = LAB / "artifacts" / "dense-n3-state-families-v1"
UNITARY_TOLERANCE = 1e-10
PARITY_TOLERANCE = 1e-10
GRADIENT_ABS_TOLERANCE = 5e-5
GRADIENT_REL_TOLERANCE = 1e-3
FINITE_DIFFERENCE_EPSILON = 3e-4


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def companion_features(policy: PolicyModel, records: torch.Tensor) -> torch.Tensor:
    tokens, mask = measurement_sequence_to_tokens(records, use_sep=policy.use_sep)
    hidden = policy.transformer(input_ids=tokens, attention_mask=mask).last_hidden_state
    weights = mask.unsqueeze(-1).to(hidden.dtype)
    return (hidden * weights).sum(dim=1) / weights.sum(dim=1).clamp(min=1.0)


def one_step_fidelity_loss(
    controller: DenseBlockController,
    features: torch.Tensor,
    final_states: torch.Tensor,
    initial_states: torch.Tensor,
) -> torch.Tensor:
    gates = controller.emit_from_features(features, dtype=torch.complex128)
    recovered = apply_block_schedule(final_states, gates)
    overlap = torch.einsum("bi,bi->b", initial_states.conj(), recovered)
    return 1.0 - (overlap.abs() ** 2).mean()


def quimb_schedule_state(gates, initial_state: torch.Tensor) -> np.ndarray:
    circuit = qtn.Circuit(3, gate_contract=False)
    for gate in gates:
        matrix = gate.unitary[0].detach().cpu().numpy()
        circuit.apply_gate(matrix, *gate.sites)
    unitary = np.asarray(circuit.get_uni().to_dense())
    return unitary @ initial_state[0].detach().cpu().numpy()


def run_contract(
    panel: str,
    support: str,
    seed: int,
    features: torch.Tensor,
    initial_states: torch.Tensor,
    final_states: torch.Tensor,
) -> dict[str, object]:
    torch.manual_seed(seed)
    controller = DenseBlockController(panel, support)
    gates = controller.emit_from_features(features, dtype=torch.complex128)
    identity_errors = []
    for gate in gates:
        dimension = gate.unitary.shape[-1]
        identity = torch.eye(dimension, dtype=torch.complex128)
        residual = gate.unitary.conj().transpose(-2, -1) @ gate.unitary - identity
        identity_errors.append(float(residual.abs().max().detach()))
    dense_state = apply_block_schedule(final_states, gates)
    quimb_state = quimb_schedule_state(gates, final_states)
    parity_error = float(np.max(np.abs(dense_state[0].detach().cpu().numpy() - quimb_state)))

    controller.zero_grad(set_to_none=True)
    loss = one_step_fidelity_loss(controller, features, final_states, initial_states)
    loss.backward()
    parameter = controller.out_proj.weight
    coordinate = (0, 0)
    analytic = float(parameter.grad[coordinate])
    with torch.no_grad():
        original = float(parameter[coordinate])
        parameter[coordinate] = original + FINITE_DIFFERENCE_EPSILON
    plus = float(one_step_fidelity_loss(controller, features, final_states, initial_states))
    with torch.no_grad():
        parameter[coordinate] = original - FINITE_DIFFERENCE_EPSILON
    minus = float(one_step_fidelity_loss(controller, features, final_states, initial_states))
    with torch.no_grad():
        parameter[coordinate] = original
    finite_difference = (plus - minus) / (2.0 * FINITE_DIFFERENCE_EPSILON)
    gradient_abs_error = abs(analytic - finite_difference)
    gradient_scale = max(abs(analytic), abs(finite_difference), 1e-12)
    gradient_relative_error = gradient_abs_error / gradient_scale
    gradient_pass = (
        gradient_abs_error <= GRADIENT_ABS_TOLERANCE
        or gradient_relative_error <= GRADIENT_REL_TOLERANCE
    )
    result: dict[str, object] = {
        **controller.contract_counts(),
        "seed": seed,
        "batch_size": int(features.shape[0]),
        "optimizer_steps": 0,
        "unitarity_max_abs_error": max(identity_errors),
        "dense_quimb_state_max_abs_error": parity_error,
        "gradient_coordinate": list(coordinate),
        "finite_difference_epsilon": FINITE_DIFFERENCE_EPSILON,
        "analytic_gradient": analytic,
        "central_finite_difference_gradient": finite_difference,
        "gradient_abs_error": gradient_abs_error,
        "gradient_relative_error": gradient_relative_error,
        "gradient_pass": gradient_pass,
        "one_step_fidelity_loss": float(loss.detach()),
    }
    assert result["unitarity_max_abs_error"] <= UNITARY_TOLERANCE, result
    assert result["dense_quimb_state_max_abs_error"] <= PARITY_TOLERANCE, result
    assert gradient_pass, result
    return result


def main() -> None:
    torch.set_num_threads(1)
    payload = torch.load(FIXTURE / "product-validation.pt", map_location="cpu", weights_only=False)
    trajectories = payload["trajectories"][:2]
    records = trajectories[:, 1:, :]
    initial_states = payload["initial_states"][:2]
    final_states = payload["final_states"][:2]

    torch.manual_seed(3500)
    companion = PolicyModel(3)
    parity_controller = DenseBlockController("coefficient", "full")
    parity_controller.encoder.transformer.load_state_dict(companion.transformer.state_dict())
    reference_features = companion_features(companion, records)
    copied_features = parity_controller.encode(records)
    encoder_error = float((reference_features - copied_features).abs().max().detach())
    assert encoder_error <= 1e-10, encoder_error
    features = reference_features.detach()

    records_out = []
    index = 0
    for panel in PANELS:
        for support in SUPPORTS:
            records_out.append(
                run_contract(
                    panel,
                    support,
                    3501 + index,
                    features,
                    initial_states,
                    final_states,
                )
            )
            index += 1
    result = {
        "schema_version": 1,
        "kind": "lab002_zero_optimizer_numerical_gate",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fixture": "dense-n3-state-families-v1/product-validation.pt[:2]",
        "fixture_manifest_sha256": sha256(FIXTURE / "manifest.json"),
        "controller_source_sha256": sha256(LAB / "dense_block_controller.py"),
        "torch_version": torch.__version__,
        "quimb_version": quimb.__version__,
        "optimizer_steps": 0,
        "encoder_copy_max_abs_error": encoder_error,
        "tolerances": {
            "unitarity_max_abs_error": UNITARY_TOLERANCE,
            "dense_quimb_state_max_abs_error": PARITY_TOLERANCE,
            "gradient_abs_error": GRADIENT_ABS_TOLERANCE,
            "gradient_relative_error": GRADIENT_REL_TOLERANCE,
        },
        "records": records_out,
    }
    output = LAB / "results" / "numerical-gate-v1"
    output.mkdir(parents=True, exist_ok=True)
    path = output / "summary.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
