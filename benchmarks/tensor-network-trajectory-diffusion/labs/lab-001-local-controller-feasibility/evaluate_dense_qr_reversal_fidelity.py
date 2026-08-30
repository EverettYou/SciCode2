"""Held-out reversal-fidelity gate for the approved Lab 001 baseline.

This is deliberately limited to the unmodified companion dense-QR ``PolicyModel``
on the frozen one- and two-qubit fixture.  Each requested seed is retrained from
scratch using the declared 128-update budget, then evaluated on the frozen held-out
test records.  It neither introduces a new controller head nor a system with more
than two qubits.
"""

from __future__ import annotations

import argparse
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

from src import BackwardDiffusion, QuantumDiffusionLoss, WeakMeasurement  # noqa: E402
from src.model import PolicyModel  # noqa: E402


CONFIG = {
    1: (2301, 2303, 2305),
    2: (2302, 2304, 2306),
}
UPDATES = 128
BATCH_SIZE = 16
LEARNING_RATE = 1e-3
EPSILON = 0.5


def train_policy(n_qubits: int, seed: int, train: torch.Tensor) -> PolicyModel:
    torch.manual_seed(seed)
    policy = PolicyModel(n_qubits)
    loss_fn = QuantumDiffusionLoss(WeakMeasurement(EPSILON), policy)
    optimizer = torch.optim.Adam(policy.parameters(), lr=LEARNING_RATE)
    for update in range(UPDATES):
        offset = (update * BATCH_SIZE) % len(train)
        optimizer.zero_grad()
        loss_fn(train[offset : offset + BATCH_SIZE]).backward()
        optimizer.step()
    return policy


def final_states_from_records(records: torch.Tensor, wm: WeakMeasurement) -> torch.Tensor:
    """Reconstruct normalized forward final states for fixed measurement records."""
    batch, _, n_qubits = records.shape
    state = torch.zeros(batch, 2**n_qubits, dtype=torch.complex128)
    state[:, 0] = 1.0
    for t in range(records.shape[1]):
        state = torch.einsum("bij,bj->bi", wm.operator(records[:, t, :]), state)
        state = state / state.norm(dim=-1, keepdim=True).clamp_min(1e-12)
    return state


def evaluate(n_qubits: int, seed: int) -> dict[str, object]:
    fixture = LAB / "artifacts" / "dense-splits-v1"
    train = torch.load(fixture / f"n{n_qubits}-train.pt", weights_only=True)
    test = torch.load(fixture / f"n{n_qubits}-test.pt", weights_only=True)
    policy = train_policy(n_qubits, seed, train)
    wm = WeakMeasurement(EPSILON)
    reverse = BackwardDiffusion(wm, policy)
    reverse.state = final_states_from_records(test, wm)
    reverse.forward_trajectory = test
    reverse.trajectory_reversal(test.shape[1])
    target = torch.zeros(2**n_qubits, dtype=torch.complex128)
    target[0] = 1.0
    fidelity = (reverse.state.conj() * target).sum(dim=-1).abs().square()
    return {
        "schema_version": 1,
        "kind": "held_out_dense_qr_reversal_fidelity",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_qubits": n_qubits,
        "seed": seed,
        "updates": UPDATES,
        "batch_size": BATCH_SIZE,
        "optimizer": {"name": "Adam", "lr": LEARNING_RATE},
        "fixture": "dense-splits-v1",
        "split": "test",
        "epsilon": EPSILON,
        "trajectory_length": int(test.shape[1]),
        "reversal_steps": int(test.shape[1] - 1),
        "target": "computational_zero",
        "mean_fidelity": fidelity.mean().item(),
        "sample_std_fidelity": fidelity.std(unbiased=True).item(),
        "minimum_fidelity": fidelity.min().item(),
        "maximum_fidelity": fidelity.max().item(),
        "note": "Held-out companion dense-QR baseline evidence only; not a locality or scaling result.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-qubits", type=int, choices=(1, 2), nargs="+", default=(1, 2))
    args = parser.parse_args()
    torch.set_num_threads(1)
    output = LAB / "results" / "dense-qr-reversal-fidelity-v1"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for n_qubits in args.n_qubits:
        for seed in CONFIG[n_qubits]:
            result = evaluate(n_qubits, seed)
            (output / f"n{n_qubits}-seed{seed}-updates{UPDATES}.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            results.append(result)
            print(json.dumps(result, sort_keys=True))
    summary = {"results": results}
    (output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
