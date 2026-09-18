"""Dense recorded-trajectory reversal with paper-style infidelity + rollout loss.

Supports N=1 and N=2. Does not use the notebook Frobenius objective
||U K_t K_{t-1}-c I||, which cannot reverse states even with an oracle polar map.
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

from src import BackwardDiffusion, ForwardDiffusion, PolicyModel, WeakMeasurement  # noqa: E402
from src.operator import PAULI  # noqa: E402

EPSILON, T, N_TRAJ, EPOCHS, EVAL_TRAJ, LR = 0.8, 30, 1024, 800, 2000, 1e-3


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


def collect_states(wm: WeakMeasurement, n_traj: int, steps: int, initial: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    forward = ForwardDiffusion(wm)
    state = initial.unsqueeze(0).expand(n_traj, -1).clone()
    forward.state = state
    states = [state.clone()]
    records = []
    for _ in range(steps):
        records.append(forward.step())
        states.append(forward.state.clone())
    return torch.stack(states, dim=1), torch.stack(records, dim=1)


def reverse_from_final(policy: PolicyModel, records: torch.Tensor, final_state: torch.Tensor, steps: int) -> torch.Tensor:
    state = final_state.clone()
    for t in range(steps, 0, -1):
        unitary = policy(records[:, t - 1 :, :], dtype=state.dtype)
        state = torch.einsum("bij,bj->bi", unitary, state)
    return state


def infidelity_loss(policy: PolicyModel, states: torch.Tensor, records: torch.Tensor, steps: int) -> torch.Tensor:
    total = states.new_zeros((), dtype=torch.float32)
    for t in range(1, steps + 1):
        unitary = policy(records[:, t - 1 :, :], dtype=states.dtype)
        recovered = torch.einsum("bij,bj->bi", unitary, states[:, t])
        overlap = (states[:, t - 1].conj() * recovered).sum(dim=-1)
        total = total + (1.0 - (overlap.abs() ** 2)).mean()
    return total / steps


def rollout_infidelity(policy: PolicyModel, states: torch.Tensor, records: torch.Tensor, steps: int) -> torch.Tensor:
    reversed_states = reverse_from_final(policy, records, states[:, -1], steps)
    overlap = (reversed_states.conj() * states[:, 0]).sum(dim=-1)
    return (1.0 - overlap.abs() ** 2).mean().to(torch.float32)


def bloch_polarization_n1(state: torch.Tensor) -> float:
    pauli = PAULI[1:4].to(device=state.device, dtype=state.dtype)
    bloch = torch.einsum("...i,kij,...j->...k", state.conj(), pauli, state).real.mean(dim=0)
    return float(torch.linalg.norm(bloch))


def evaluate(policy: PolicyModel, wm: WeakMeasurement, initial: torch.Tensor, n_qubits: int, steps: int) -> dict[str, float]:
    dim = 2**n_qubits
    states, records = collect_states(wm, EVAL_TRAJ, steps, initial)
    with torch.no_grad():
        reversed_states = reverse_from_final(policy, records, states[:, -1], steps)
        overlap0 = (reversed_states.conj() * initial.unsqueeze(0)).sum(dim=-1)
        deterministic_fidelity = float((overlap0.abs() ** 2).mean())
        population0 = float((reversed_states[:, 0].abs() ** 2).mean())
        one_step = float(infidelity_loss(policy, states, records, steps).item())
        real = torch.randn(EVAL_TRAJ, dim, dtype=torch.float64, device=initial.device)
        imag = torch.randn(EVAL_TRAJ, dim, dtype=torch.float64, device=initial.device)
        random_states = (real + 1j * imag).to(torch.complex128)
        random_states = random_states / (random_states.abs() ** 2).sum(-1, keepdim=True).sqrt()
        stochastic = BackwardDiffusion(wm, policy)
        stochastic.state, stochastic.forward_trajectory = random_states, records
        stochastic.trajectory(steps)
        paper_style = float((stochastic.state[:, 0].abs() ** 2).mean())
    metrics = {
        "eval_one_step_infidelity": one_step,
        "deterministic_same_record_reversal_fidelity_to_initial": deterministic_fidelity,
        "deterministic_population_on_computational_zero": population0,
        "paper_style_stochastic_population_on_computational_zero": paper_style,
    }
    if n_qubits == 1:
        metrics["deterministic_mean_polarization"] = bloch_polarization_n1(reversed_states)
        metrics["paper_style_mean_polarization"] = bloch_polarization_n1(stochastic.state)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Infidelity+rollout dense reversal")
    parser.add_argument("--n-qubits", type=int, default=1)
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--seed", type=int, default=7111)
    parser.add_argument("--eval-every", type=int, default=25)
    parser.add_argument("--output-name", type=str, default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    n_qubits = args.n_qubits
    output_name = args.output_name or f"n{n_qubits}-infidelity"
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(args.seed)

    wm = WeakMeasurement(EPSILON)
    policy = PolicyModel(n_qubits=n_qubits, max_T=T).to(device)
    optimizer = torch.optim.Adam(policy.parameters(), lr=LR)
    initial = torch.zeros(2**n_qubits, dtype=torch.complex128, device=device)
    initial[0] = 1.0
    output = LAB / "results" / "strict-repository-reproduction-v1"
    output.mkdir(parents=True, exist_ok=True)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "seed": args.seed,
        "n_qubits": n_qubits,
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / f"{output_name}-environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        states, records = collect_states(wm, N_TRAJ, T, initial)
        optimizer.zero_grad()
        step_loss = infidelity_loss(policy, states, records, T)
        roll_loss = rollout_infidelity(policy, states, records, T)
        loss = step_loss + roll_loss
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "one_step_infidelity": float(step_loss.item()),
            "rollout_infidelity": float(roll_loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(policy, wm, initial, n_qubits, T))
            (output / f"{output_name}-progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": {"n": n_qubits, "epsilon": EPSILON, "T": T}}) + "\n")
            torch.save(policy.state_dict(), output / f"{output_name}-policy-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 10 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"n{n_qubits}_infidelity_reversal",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": env,
        "config": {"n": n_qubits, "epsilon": EPSILON, "T": T, "trajectories_per_epoch": N_TRAJ, "epochs": args.epochs, "lr": LR, "loss": "one_step_infidelity_plus_rollout"},
        "loss_curve": curve,
        "final": curve[-1],
    }
    (output / f"{output_name}.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(policy.state_dict(), output / f"{output_name}-policy.pt")
    print(json.dumps({"event": "done", "final": curve[-1]}), flush=True)


if __name__ == "__main__":
    main()
