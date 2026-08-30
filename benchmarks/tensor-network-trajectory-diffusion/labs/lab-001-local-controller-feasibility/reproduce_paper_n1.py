"""Strict reproduction of the repository notebook's N=1 configuration.

Configuration copied from test/2026-03-14.ipynb: eps=0.8, T=30,
1024 trajectories/epoch, 2000 epochs, Adam lr=1e-3, and |0> training state.
The script records both the notebook's stochastic-backward metric and the
separate deterministic trajectory-reversal fidelity to avoid conflating them.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch

LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
sys.path.insert(0, str(REPOSITORY / "papers" / "liu2025mqdm" / "repo"))

from src import BackwardDiffusion, DiffusionTrainer, ForwardDiffusion, PolicyModel, QuantumDiffusionLoss, WeakMeasurement  # noqa: E402

N, EPSILON, T, N_TRAJ, EPOCHS, EVAL_TRAJ = 1, 0.8, 30, 1024, 2000, 2000


def main() -> None:
    torch.manual_seed(7011)
    # Use PyTorch's default CPU thread pool. Metal/MPS is unavailable in this
    # runtime, and the repository notebook does not impose a single-core cap.
    wm = WeakMeasurement(EPSILON)
    forward = ForwardDiffusion(wm)
    policy = PolicyModel(n_qubits=N, max_T=T)
    trainer = DiffusionTrainer(forward, policy, QuantumDiffusionLoss(wm, policy), lr=1e-3)
    initial = torch.tensor([1.0, 0.0], dtype=torch.complex128)
    output = LAB / "results" / "strict-repository-reproduction-v1"
    output.mkdir(parents=True, exist_ok=True)
    curve = []
    for epoch in range(EPOCHS):
        loss = trainer.train_step(trainer.collect(N_TRAJ, T, initial_state=initial))
        if (epoch + 1) % 100 == 0 or epoch == 0:
            curve.append({"epoch": epoch + 1, "loss": loss})
            (output / "n1-progress.json").write_text(json.dumps({"epoch": epoch + 1, "loss": loss, "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": EPOCHS}}) + "\n")
            print(json.dumps(curve[-1]), flush=True)

    # Exact paper-style stochastic backward path.
    forward.state = initial.unsqueeze(0).expand(EVAL_TRAJ, -1).clone()
    records = forward.trajectory(T)
    random = torch.randn(EVAL_TRAJ, 2, dtype=torch.complex128)
    random /= torch.linalg.vector_norm(random, dim=-1, keepdim=True)
    backward = BackwardDiffusion(wm, policy)
    backward.state, backward.forward_trajectory = random, records
    backward.trajectory(T)
    paper_style_fidelity_to_zero = float((backward.state[:, 0].abs() ** 2).mean())

    # True recorded-trajectory reversal, evaluated separately.
    final = forward.state.clone()
    reverse = BackwardDiffusion(wm, policy)
    reverse.state, reverse.forward_trajectory = final, records
    reverse.trajectory_reversal(T)
    deterministic_fidelity_to_zero = float((reverse.state[:, 0].abs() ** 2).mean())
    result = {"kind": "strict_repository_n1_reproduction", "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "config": {"n": N, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": EPOCHS, "lr": 1e-3}, "loss_curve": curve, "paper_style_stochastic_fidelity_to_zero": paper_style_fidelity_to_zero, "deterministic_recorded_trajectory_reversal_fidelity_to_zero": deterministic_fidelity_to_zero}
    (output / "n1.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(policy.state_dict(), output / "n1-policy.pt")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
