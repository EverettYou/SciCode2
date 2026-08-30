"""Integration checkpoint for local heads on the frozen companion encoder.

This Lab 001 check does not optimize a controller. It copies only the
companion transformer into each local policy, runs the unchanged companion
reverse loss on frozen validation trajectories, and verifies output unitarity
and finite gradients through both the shared encoder and replacement head.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
COMPANION = REPOSITORY / "papers" / "liu2025mqdm" / "repo"
sys.path.insert(0, str(COMPANION))

from src import QuantumDiffusionLoss, WeakMeasurement  # noqa: E402
from src.model import PolicyModel  # noqa: E402

spec = importlib.util.spec_from_file_location("lab001_prototype", LAB / "prototype.py")
prototype = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(prototype)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-qubits", type=int, choices=(1, 2), required=True)
    parser.add_argument("--family", choices=("hamiltonian", "gates"), required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2500)
    args = parser.parse_args()

    torch.manual_seed(args.seed + args.n_qubits)
    torch.set_num_threads(1)
    companion = PolicyModel(args.n_qubits)
    policy = prototype.CircuitPolicy(args.n_qubits, args.family)
    policy.encoder.transformer.load_state_dict(companion.transformer.state_dict())
    fixture = LAB / "artifacts" / "dense-splits-v1"
    trajectories = torch.load(
        fixture / f"n{args.n_qubits}-validation.pt", weights_only=True
    )[:args.batch_size]
    records = trajectories[:, 1:, :]
    unitary = policy(records, dtype=torch.complex128)
    dim = 2 ** args.n_qubits
    identity = torch.eye(dim, dtype=unitary.dtype).expand_as(unitary)
    residual = (unitary.mH @ unitary - identity).abs().max().item()
    loss = QuantumDiffusionLoss(WeakMeasurement(0.5), policy)(trajectories)
    loss.backward()
    gradients = [parameter.grad for parameter in policy.parameters()]
    result = {
        "schema_version": 1,
        "kind": "local_head_encoder_integration_smoke",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": args.n_qubits,
        "family": args.family,
        "seed": args.seed + args.n_qubits,
        "fixture": "dense-splits-v1",
        "trajectory_batch_size": args.batch_size,
        "encoder": "companion-transformer-state-dict-copy",
        "optimization_steps": 0,
        "reverse_loss": loss.item(),
        "unitary_max_residual": residual,
        "all_parameter_gradients_finite": all(
            gradient is not None and torch.isfinite(gradient).all().item()
            for gradient in gradients
        ),
        "head_gradient_l1": sum(
            parameter.grad.abs().sum().item() for parameter in policy.head.parameters()
        ),
        "encoder_gradient_l1": sum(
            parameter.grad.abs().sum().item() for parameter in policy.encoder.parameters()
        ),
    }
    assert result["unitary_max_residual"] < 1e-10, result
    assert result["all_parameter_gradients_finite"], result
    assert result["head_gradient_l1"] > 0.0, result
    assert result["encoder_gradient_l1"] > 0.0, result
    output = LAB / "results" / "local-head-encoder-smoke-v1"
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"n{args.n_qubits}-{args.family}-seed{result['seed']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
