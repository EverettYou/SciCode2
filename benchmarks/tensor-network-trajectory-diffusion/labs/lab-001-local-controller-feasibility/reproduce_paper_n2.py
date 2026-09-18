"""Same discrete notebook protocol as N=1, extended to N=2.

The 2026-03-14 notebook does not train N=2. This script keeps ε, T, batch,
epochs, optimizer, loss, and both evaluation metrics identical, and only
changes n_qubits=2 with computational |00>.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
sys.path.insert(0, str(REPOSITORY / "papers" / "liu2025mqdm" / "repo"))

from src import BackwardDiffusion, DiffusionTrainer, ForwardDiffusion, PolicyModel, QuantumDiffusionLoss, WeakMeasurement  # noqa: E402

N, EPSILON, T, N_TRAJ, EPOCHS, EVAL_TRAJ = 2, 0.8, 30, 1024, 2000, 2000


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    best_index = 0
    best_free = -1
    for index in range(torch.cuda.device_count()):
        free, _total = torch.cuda.mem_get_info(index)
        if free > best_free:
            best_free = free
            best_index = index
    return torch.device(f"cuda:{best_index}")


def evaluate(policy: PolicyModel, wm: WeakMeasurement, initial: torch.Tensor, device: torch.device) -> dict[str, float]:
    dim = 2**N
    forward = ForwardDiffusion(wm)
    forward.state = initial.unsqueeze(0).expand(EVAL_TRAJ, -1).clone()
    records = forward.trajectory(T)

    real = torch.randn(EVAL_TRAJ, dim, dtype=torch.float64, device=device)
    imag = torch.randn(EVAL_TRAJ, dim, dtype=torch.float64, device=device)
    random_states = (real + 1j * imag).to(torch.complex128)
    random_states = random_states / (random_states.abs() ** 2).sum(-1, keepdim=True).sqrt()
    stochastic = BackwardDiffusion(wm, policy)
    stochastic.state, stochastic.forward_trajectory = random_states, records
    stochastic.trajectory(T)
    stochastic_p00 = float((stochastic.state[:, 0].abs() ** 2).mean())

    reverse = BackwardDiffusion(wm, policy)
    reverse.state, reverse.forward_trajectory = forward.state.clone(), records
    reverse.trajectory_reversal(T)
    deterministic_p00 = float((reverse.state[:, 0].abs() ** 2).mean())
    overlap = (reverse.state.conj() * initial.unsqueeze(0)).sum(dim=-1)
    deterministic_fidelity = float((overlap.abs() ** 2).mean())
    return {
        "paper_style_stochastic_population_on_00": stochastic_p00,
        "deterministic_recorded_trajectory_reversal_population_on_00": deterministic_p00,
        "deterministic_recorded_trajectory_reversal_fidelity_to_00": deterministic_fidelity,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strict N=2 discrete-protocol reproduction")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--seed", type=int, default=8011)
    parser.add_argument("--eval-every", type=int, default=100)
    parser.add_argument("--output-name", type=str, default="n2")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)

    wm = WeakMeasurement(EPSILON)
    forward = ForwardDiffusion(wm)
    policy = PolicyModel(n_qubits=N, max_T=T).to(device)
    loss_fn = QuantumDiffusionLoss(wm, policy).to(device)
    trainer = DiffusionTrainer(forward, policy, loss_fn, lr=1e-3)
    initial = torch.zeros(2**N, dtype=torch.complex128, device=device)
    initial[0] = 1.0

    output = LAB / "results" / "strict-repository-reproduction-v1"
    output.mkdir(parents=True, exist_ok=True)
    env = {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "seed": args.seed,
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / f"{args.output_name}-environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        loss = trainer.train_step(trainer.collect(N_TRAJ, T, initial_state=initial))
        epoch_id = epoch + 1
        record: dict[str, object] = {"epoch": epoch_id, "loss": loss, "elapsed_seconds": time.perf_counter() - started}
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            with torch.no_grad():
                record.update(evaluate(policy, wm, initial, device))
        curve.append(record)
        if epoch_id % 100 == 0 or epoch == 0 or epoch_id == args.epochs:
            (output / f"{args.output_name}-progress.json").write_text(json.dumps({"epoch": epoch_id, "loss": loss, "latest": record, "config": {"n": N, "epsilon": EPSILON, "T": T}}) + "\n")
            torch.save(policy.state_dict(), output / f"{args.output_name}-policy-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 10 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": loss}), flush=True)

    result = {
        "kind": "strict_repository_n2_discrete_protocol",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": env,
        "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": args.epochs, "lr": 1e-3},
        "loss_curve": curve,
        "final": curve[-1],
        "note": "N=2 is not trained in 2026-03-14.ipynb; this is the same discrete QR protocol with |00>.",
    }
    (output / f"{args.output_name}.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(policy.state_dict(), output / f"{args.output_name}-policy.pt")
    print(json.dumps({"event": "done", "final": curve[-1], "elapsed_seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
