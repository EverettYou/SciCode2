"""Strict reproduction of the repository notebook's N=1 configuration.

Configuration copied from test/2026-03-14.ipynb: eps=0.8, T=30,
1024 trajectories/epoch, 2000 epochs, Adam lr=1e-3, and |0> training state.
The notebook places PolicyModel and tensors on CUDA when available.

The script records both the notebook's stochastic-backward metric and the
separate deterministic trajectory-reversal fidelity to avoid conflating them.
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
from src.operator import PAULI  # noqa: E402

N, EPSILON, T, N_TRAJ, EPOCHS, EVAL_TRAJ = 1, 0.8, 30, 1024, 2000, 2000


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    # Prefer a GPU with unused compute if more than one is visible.
    best_index = 0
    best_free = -1
    for index in range(torch.cuda.device_count()):
        free, _total = torch.cuda.mem_get_info(index)
        # GPU 0 was often occupied by other jobs; still pick the most free device.
        if free > best_free:
            best_free = free
            best_index = index
    return torch.device(f"cuda:{best_index}")


def bloch_vectors(state: torch.Tensor) -> torch.Tensor:
    pauli = PAULI[1:4].to(device=state.device, dtype=state.dtype)
    return torch.einsum("...i,kij,...j->...k", state.conj(), pauli, state).real


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
    stochastic_p0 = float((stochastic.state[:, 0].abs() ** 2).mean())
    stochastic_bloch = bloch_vectors(stochastic.state)
    stochastic_mean_bloch = stochastic_bloch.mean(dim=0)
    paper_style = {
        "paper_style_stochastic_fidelity_to_zero": stochastic_p0,
        "paper_style_mean_bloch_x": float(stochastic_mean_bloch[0]),
        "paper_style_mean_bloch_y": float(stochastic_mean_bloch[1]),
        "paper_style_mean_bloch_z": float(stochastic_mean_bloch[2]),
        "paper_style_mean_polarization": float(torch.linalg.norm(stochastic_mean_bloch)),
    }

    reverse = BackwardDiffusion(wm, policy)
    reverse.state, reverse.forward_trajectory = forward.state.clone(), records
    reverse.trajectory_reversal(T)
    reverse_p0 = float((reverse.state[:, 0].abs() ** 2).mean())
    reverse_bloch = bloch_vectors(reverse.state)
    reverse_mean_bloch = reverse_bloch.mean(dim=0)
    deterministic = {
        "deterministic_recorded_trajectory_reversal_fidelity_to_zero": reverse_p0,
        "deterministic_mean_bloch_z": float(reverse_mean_bloch[2]),
        "deterministic_mean_polarization": float(torch.linalg.norm(reverse_mean_bloch)),
    }
    return {**paper_style, **deterministic}


def environment_record(device: torch.device) -> dict[str, object]:
    gpu_name = torch.cuda.get_device_name(device) if device.type == "cuda" else None
    return {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device": str(device),
        "gpu_name": gpu_name,
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Strict N=1 notebook reproduction")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--seed", type=int, default=7011)
    parser.add_argument("--eval-every", type=int, default=100)
    parser.add_argument("--checkpoint-every", type=int, default=100)
    parser.add_argument("--output-name", type=str, default="n1")
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
    initial = torch.tensor([1.0, 0.0], dtype=torch.complex128, device=device)

    output = LAB / "results" / "strict-repository-reproduction-v1"
    output.mkdir(parents=True, exist_ok=True)
    stem = args.output_name
    env = environment_record(device)
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / f"{stem}-environment.json").write_text(json.dumps({"created_at": started_at, **env, "seed": args.seed, "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": args.epochs, "lr": 1e-3, "dtype_state": "complex128", "policy_param_dtype": str(next(policy.parameters()).dtype)}}, indent=2) + "\n")
    print(json.dumps({"event": "start", "device": str(device), "gpu_name": env["gpu_name"], "seed": args.seed}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        loss = trainer.train_step(trainer.collect(N_TRAJ, T, initial_state=initial))
        epoch_id = epoch + 1
        record: dict[str, object] = {"epoch": epoch_id, "loss": loss, "elapsed_seconds": time.perf_counter() - started}
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            with torch.no_grad():
                record.update(evaluate(policy, wm, initial, device))
        curve.append(record)
        if epoch_id % args.checkpoint_every == 0 or epoch == 0 or epoch_id == args.epochs:
            progress = {
                "epoch": epoch_id,
                "loss": loss,
                "seed": args.seed,
                "device": str(device),
                "elapsed_seconds": record["elapsed_seconds"],
                "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": args.epochs},
                "latest": record,
            }
            (output / f"{stem}-progress.json").write_text(json.dumps(progress) + "\n")
            torch.save(policy.state_dict(), output / f"{stem}-policy-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 10 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": loss}), flush=True)

    result = {
        "kind": "strict_repository_n1_reproduction",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "seed": args.seed,
        "environment": env,
        "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": args.epochs, "lr": 1e-3, "eval_trajectories": EVAL_TRAJ},
        "loss_curve": curve,
        "final": curve[-1],
        "notebook_reference": {
            "source": "papers/liu2025mqdm/repo/test/2026-03-14.ipynb",
            "epoch1_loss": 0.049800,
            "epoch2000_loss": 0.040487,
            "note": "Notebook trains on CUDA and evaluates stochastic BackwardDiffusion.trajectory from random pure states. It does not print a numerical fidelity; Fig-style concentration at |0> is visual. The notebook loss plateaus near 0.040.",
        },
    }
    (output / f"{stem}.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(policy.state_dict(), output / f"{stem}-policy.pt")
    print(json.dumps({"event": "done", "final": curve[-1], "elapsed_seconds": result["elapsed_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
