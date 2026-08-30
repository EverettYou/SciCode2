"""Bounded, resumable dense-QR qualification run for Lab 001.

This intentionally trains only the unmodified companion ``PolicyModel`` on the
frozen N=1,2 fixture.  It is a baseline checkpoint, not a controller-head
comparison and does not exercise MPS or systems larger than two qubits.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
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


def mean_loss(loss_fn: QuantumDiffusionLoss, data: torch.Tensor, batch_size: int) -> float:
    with torch.no_grad():
        values = [loss_fn(data[start : start + batch_size]).item()
                  for start in range(0, len(data), batch_size)]
    return sum(values) / len(values)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-qubits", type=int, choices=(1, 2), required=True)
    parser.add_argument("--updates", type=int, default=4,
                        help="Fixed number of optimizer updates for this resumable checkpoint.")
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=2301)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    torch.set_num_threads(1)
    fixture = LAB / "artifacts" / "dense-splits-v1"
    train = torch.load(fixture / f"n{args.n_qubits}-train.pt", weights_only=True)
    validation = torch.load(fixture / f"n{args.n_qubits}-validation.pt", weights_only=True)
    test = torch.load(fixture / f"n{args.n_qubits}-test.pt", weights_only=True)
    policy = PolicyModel(args.n_qubits)
    loss_fn = QuantumDiffusionLoss(WeakMeasurement(0.5), policy)
    optimizer = torch.optim.Adam(policy.parameters(), lr=1e-3)

    initial_validation = mean_loss(loss_fn, validation, args.batch_size)
    started = time.perf_counter()
    for update in range(args.updates):
        offset = (update * args.batch_size) % len(train)
        batch = train[offset : offset + args.batch_size]
        optimizer.zero_grad()
        loss = loss_fn(batch)
        loss.backward()
        optimizer.step()
    elapsed_seconds = time.perf_counter() - started
    result = {
        "schema_version": 1,
        "kind": "bounded_dense_qr_qualification_checkpoint",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": args.n_qubits,
        "seed": args.seed,
        "updates": args.updates,
        "batch_size": args.batch_size,
        "optimizer": {"name": "Adam", "lr": 1e-3},
        "model": {"source": "companion-unmodified PolicyModel", "d_model": 64,
                  "n_layer": 2, "n_head": 4, "use_sep": True},
        "fixture": "dense-splits-v1", "epsilon": 0.5, "trajectory_length": 6,
        "initial_validation_loss": initial_validation,
        "final_train_batch_loss": loss.item(),
        "final_validation_loss": mean_loss(loss_fn, validation, args.batch_size),
        "test_loss": mean_loss(loss_fn, test, args.batch_size),
        "elapsed_seconds": elapsed_seconds,
        "note": "A fixed small qualification checkpoint only; not a converged baseline or local-head comparison.",
    }
    output = LAB / "results" / "dense-qr-baseline-v1"
    output.mkdir(parents=True, exist_ok=True)
    path = output / f"n{args.n_qubits}-seed{args.seed}-updates{args.updates}.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
