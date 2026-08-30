"""Run one bounded Lab-002 teacher-forced controller cell.

Each command executes exactly one family/panel/support/seed cell, saves a
checkpoint and a reloadable result even on budget failure, and never evaluates
the frozen test split. The one-step examples follow the companion adjacent-
Kraus objective: U_t maps the normalized state after K_t K_{t-1} back to the
state before that pair while conditioning on m[t:].
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import resource
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch

from dense_block_controller import DenseBlockController, PANELS, SUPPORTS


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
COMPANION = REPOSITORY / "papers" / "liu2025mqdm" / "repo"
sys.path.insert(0, str(COMPANION))

from src import WeakMeasurement  # noqa: E402
from src.model import PolicyModel  # noqa: E402


FIXTURE = LAB / "artifacts" / "dense-n3-state-families-v1"
FAMILIES = ("product", "weak-local", "w3")
APPROVED_SEEDS = (3301, 3303, 3305, 3307, 3309)
LEARNING_RATE = 1e-3
BATCH_SIZE = 16
DEFAULT_UPDATES = 128
WALL_TIME_CAP_SECONDS = 480.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_split(family: str, split: str) -> dict[str, Any]:
    return torch.load(FIXTURE / f"{family}-{split}.pt", map_location="cpu", weights_only=False)


def reconstruct_state_history(payload: dict[str, Any], weak: WeakMeasurement) -> torch.Tensor:
    trajectories = payload["trajectories"]
    state = payload["initial_states"]
    history = [state]
    for time_index in range(trajectories.shape[1]):
        operator = weak.operator(trajectories[:, time_index, :])
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / torch.linalg.vector_norm(state, dim=-1, keepdim=True)
        history.append(state)
    stacked = torch.stack(history, dim=1)
    final_error = float((stacked[:, -1] - payload["final_states"]).abs().max())
    if final_error > 1e-10:
        raise RuntimeError(f"reconstructed final-state mismatch: {final_error}")
    return stacked


def teacher_forced_loss(
    controller: DenseBlockController,
    trajectories: torch.Tensor,
    history: torch.Tensor,
    indices: torch.Tensor,
) -> torch.Tensor:
    time_losses = []
    for time_index in range(1, trajectories.shape[1]):
        source = history[indices, time_index + 1]
        target = history[indices, time_index - 1]
        records = trajectories[indices, time_index:, :]
        recovered = controller.apply(source, records, dtype=torch.complex128)
        overlap = torch.einsum("bi,bi->b", target.conj(), recovered)
        time_losses.append(1.0 - (overlap.abs() ** 2).mean())
    return torch.stack(time_losses).mean()


@torch.no_grad()
def evaluate(
    controller: DenseBlockController,
    trajectories: torch.Tensor,
    history: torch.Tensor,
) -> dict[str, Any]:
    per_time = []
    for time_index in range(1, trajectories.shape[1]):
        source = history[:, time_index + 1]
        target = history[:, time_index - 1]
        records = trajectories[:, time_index:, :]
        recovered = controller.apply(source, records, dtype=torch.complex128)
        overlap = torch.einsum("bi,bi->b", target.conj(), recovered)
        per_time.append(overlap.abs() ** 2)
    matrix = torch.stack(per_time, dim=1)
    per_trajectory = matrix.mean(dim=1)
    return {
        "mean_fidelity": float(per_trajectory.mean()),
        "mean_infidelity": float(1.0 - per_trajectory.mean()),
        "per_time_mean_fidelity": [float(value) for value in matrix.mean(dim=0)],
        "per_trajectory_fidelity": [float(value) for value in per_trajectory],
    }


def gradient_norm(controller: DenseBlockController) -> float:
    squared = 0.0
    for parameter in controller.parameters():
        if parameter.grad is not None:
            squared += float((parameter.grad.detach().double() ** 2).sum())
    return math.sqrt(squared)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", choices=FAMILIES, required=True)
    parser.add_argument("--panel", choices=PANELS, required=True)
    parser.add_argument("--support", choices=SUPPORTS, required=True)
    parser.add_argument("--seed", type=int, choices=APPROVED_SEEDS, required=True)
    parser.add_argument("--updates", type=int, default=DEFAULT_UPDATES)
    args = parser.parse_args()
    if args.updates != DEFAULT_UPDATES:
        raise ValueError(f"reviewed comparison requires exactly {DEFAULT_UPDATES} updates")

    torch.set_num_threads(1)
    weak = WeakMeasurement(0.5)
    train_payload = load_split(args.family, "train")
    validation_payload = load_split(args.family, "validation")
    train_history = reconstruct_state_history(train_payload, weak)
    validation_history = reconstruct_state_history(validation_payload, weak)

    torch.manual_seed(args.seed)
    companion = PolicyModel(3)
    torch.manual_seed(args.seed + 10_000)
    controller = DenseBlockController(args.panel, args.support)
    controller.encoder.transformer.load_state_dict(companion.transformer.state_dict())
    optimizer = torch.optim.Adam(controller.parameters(), lr=LEARNING_RATE)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(args.seed + 20_000)
    training_curve = []
    status = "completed"
    started = time.monotonic()
    completed_updates = 0
    for update in range(args.updates):
        if time.monotonic() - started >= WALL_TIME_CAP_SECONDS:
            status = "budget-failed"
            break
        indices = torch.randint(
            0,
            train_payload["trajectories"].shape[0],
            (BATCH_SIZE,),
            generator=generator,
        )
        optimizer.zero_grad(set_to_none=True)
        loss = teacher_forced_loss(
            controller,
            train_payload["trajectories"],
            train_history,
            indices,
        )
        loss.backward()
        norm = gradient_norm(controller)
        if not math.isfinite(float(loss.detach())) or not math.isfinite(norm):
            status = "numerical-failed"
            break
        optimizer.step()
        completed_updates = update + 1
        training_curve.append(
            {
                "update": completed_updates,
                "loss": float(loss.detach()),
                "gradient_norm": norm,
                "elapsed_seconds": time.monotonic() - started,
            }
        )

    elapsed = time.monotonic() - started
    validation = evaluate(
        controller,
        validation_payload["trajectories"],
        validation_history,
    )
    output = (
        LAB
        / "results"
        / "one-step-v1"
        / args.family
        / args.panel
        / args.support
    )
    output.mkdir(parents=True, exist_ok=True)
    checkpoint_path = output / f"seed-{args.seed}.pt"
    torch.save(
        {
            "schema_version": 1,
            "family": args.family,
            "panel": args.panel,
            "support": args.support,
            "seed": args.seed,
            "completed_updates": completed_updates,
            "controller_state_dict": controller.state_dict(),
        },
        checkpoint_path,
    )
    result = {
        "schema_version": 1,
        "kind": "lab002_teacher_forced_one_step_cell",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": status,
        "family": args.family,
        "panel": args.panel,
        "support": args.support,
        "seed": args.seed,
        "fixture": "dense-n3-state-families-v1",
        "fixture_manifest_sha256": sha256(FIXTURE / "manifest.json"),
        "controller_source_sha256": sha256(LAB / "dense_block_controller.py"),
        "training_source_sha256": sha256(Path(__file__)),
        "checkpoint": checkpoint_path.name,
        "checkpoint_sha256": sha256(checkpoint_path),
        "test_evaluated": False,
        "optimizer": "Adam",
        "learning_rate": LEARNING_RATE,
        "batch_size": BATCH_SIZE,
        "requested_updates": args.updates,
        "completed_updates": completed_updates,
        "wall_time_cap_seconds": WALL_TIME_CAP_SECONDS,
        "elapsed_seconds": elapsed,
        "resource_ru_maxrss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "platform": platform.platform(),
        "torch_version": torch.__version__,
        "counts": controller.contract_counts(),
        "training_curve": training_curve,
        "validation": validation,
    }
    result_path = output / f"seed-{args.seed}.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "training_curve"}, indent=2, sort_keys=True))
    if status != "completed" or completed_updates != args.updates:
        raise RuntimeError(f"cell did not complete reviewed budget: {status}, {completed_updates}/{args.updates}")


if __name__ == "__main__":
    main()
