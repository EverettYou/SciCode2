"""Regression gate for extracting the companion dense-QR policy encoder.

This is limited to the approved N=1,2 dense-vector Lab 001 boundary. It copies
the companion weights into the factored policy and checks exact output, loss,
and parameter-gradient agreement on the frozen qualification fixture.
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


def max_abs(left: torch.Tensor, right: torch.Tensor) -> float:
    return (left - right).abs().max().item()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-qubits", type=int, choices=(1, 2), required=True)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--seed", type=int, default=2400)
    args = parser.parse_args()

    torch.manual_seed(args.seed + args.n_qubits)
    torch.set_num_threads(1)
    original = PolicyModel(args.n_qubits)
    refactored = prototype.RefactoredQRPolicy.from_companion(original)
    fixture = LAB / "artifacts" / "dense-splits-v1"
    trajectories = torch.load(
        fixture / f"n{args.n_qubits}-validation.pt", weights_only=True
    )[:args.batch_size]
    records = trajectories[:, 1:, :]

    original_unitary = original(records, dtype=torch.complex128)
    refactored_unitary = refactored(records, dtype=torch.complex128)
    original_loss = QuantumDiffusionLoss(WeakMeasurement(0.5), original)(trajectories)
    refactored_loss = QuantumDiffusionLoss(WeakMeasurement(0.5), refactored)(trajectories)
    original_loss.backward()
    refactored_loss.backward()
    original_grads = dict(original.named_parameters())
    refactored_grads = dict(refactored.named_parameters())
    name_pairs = (
        ("out_proj.weight", "head.out_proj.weight"),
        ("out_proj.bias", "head.out_proj.bias"),
        *[(f"transformer.{name}", f"encoder.transformer.{name}")
          for name in original.transformer.state_dict().keys()
          if name.endswith("weight") or name.endswith("bias")],
    )
    gradient_error = max(
        max_abs(original_grads[left].grad, refactored_grads[right].grad)
        for left, right in name_pairs
    )
    result = {
        "schema_version": 1,
        "kind": "dense_qr_encoder_refactor_regression",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": args.n_qubits,
        "seed": args.seed + args.n_qubits,
        "fixture": "dense-splits-v1",
        "trajectory_batch_size": args.batch_size,
        "unitary_max_abs_error": max_abs(original_unitary, refactored_unitary),
        "loss_abs_error": abs((original_loss - refactored_loss).item()),
        "gradient_max_abs_error": gradient_error,
        "tolerance": 1e-10,
    }
    assert result["unitary_max_abs_error"] < result["tolerance"], result
    assert result["loss_abs_error"] < result["tolerance"], result
    assert result["gradient_max_abs_error"] < result["tolerance"], result
    output = LAB / "results" / "dense-qr-refactor-v1"
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"n{args.n_qubits}-seed{result['seed']}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
