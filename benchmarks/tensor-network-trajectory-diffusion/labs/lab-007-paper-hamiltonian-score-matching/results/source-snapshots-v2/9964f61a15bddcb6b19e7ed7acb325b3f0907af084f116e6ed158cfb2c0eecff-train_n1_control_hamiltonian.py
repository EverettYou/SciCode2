"""Paper-faithful control-Hamiltonian score matching for one qubit.

This follows Liu et al., arXiv:2508.08799, Sec. III.A and Figs. 2–3 — not the
repository notebooks.

Forward: randomized single-qubit Pauli weak measurements, Eqs. (1), (19).
State encoding: Bloch / Pauli vector z_t = (⟨X⟩, ⟨Y⟩, ⟨Z⟩), Eq. (6).
Learned object: control field h_θ(z, t) in H = h·σ, Fig. 3.
Score operator, Eq. (28):
    V = exp[ (-γ/2 δO² + 2 i H_θ(z, t)) dt ]
The prefactor 2 on H is the score–flow identity s = 2f − 2v, Eq. (24)–(26).
Loss: mean infidelity 1 − |⟨ψ_{t−dt}| V |ψ_t⟩|², Eq. (27).

The transformer + dense QR policy in papers/liu2025mqdm/repo is a later
exploratory snapshot and is not used here.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.nn as nn

LAB = Path(__file__).resolve().parent
OUTPUT = LAB / "results" / "paper-fig2-n1-v1"

GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))  # 300
NOISE_STD = 0.2  # Fig. 2(a)


PAULI = torch.tensor(
    [
        [[0.0, 1.0], [1.0, 0.0]],
        [[0.0, -1.0j], [1.0j, 0.0]],
        [[1.0, 0.0], [0.0, -1.0]],
    ],
    dtype=torch.complex128,
)


def bloch(state: torch.Tensor) -> torch.Tensor:
    pauli = PAULI.to(device=state.device, dtype=state.dtype)
    return torch.einsum("bi,kij,bj->bk", state.conj(), pauli, state).real


class ControlHamiltonian(nn.Module):
    """h_θ(z, t) → R^3, H = h_x X + h_y Y + h_z Z."""

    def __init__(self, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(4, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 3),
        )

    def field(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        inputs = torch.cat([z, t_norm], dim=-1).to(dtype=next(self.net.parameters()).dtype)
        return self.net(inputs)

    def hamiltonian(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        h = self.field(z, t_norm).to(torch.float64)
        pauli = PAULI.to(device=z.device)
        return torch.einsum("ba,aij->bij", h.to(pauli.dtype), pauli)


def score_operator(
    hamiltonian: torch.Tensor,
    observable: torch.Tensor,
    state: torch.Tensor,
    gamma: float,
    dt: float,
) -> torch.Tensor:
    """V = exp[(-γ/2 δO² + 2i H) dt], Eq. (28)."""
    expectation = torch.einsum("bi,bij,bj->b", state.conj(), observable, state).real
    identity = torch.eye(2, dtype=observable.dtype, device=observable.device)
    delta = observable - expectation[:, None, None] * identity
    delta_sq = delta @ delta
    generator = (-0.5 * gamma) * delta_sq + (2.0j) * hamiltonian
    return torch.linalg.matrix_exp(generator * dt)


def kraus_binary(observable: torch.Tensor, sign: torch.Tensor, gamma: float, dt: float) -> torch.Tensor:
    """Eq. (19): K = 1/√2 exp(-γ dt + 2γ O δo), δo = sign * (1/2)√(dt/γ)."""
    delta_o = sign.to(observable.dtype) * 0.5 * math.sqrt(dt / gamma)
    identity = torch.eye(2, dtype=observable.dtype, device=observable.device)
    generator = (-gamma * dt) * identity + (2.0 * gamma) * observable * delta_o[:, None, None]
    return (1.0 / math.sqrt(2.0)) * torch.linalg.matrix_exp(generator)


def sample_forward_step(state: torch.Tensor, gamma: float, dt: float) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    batch = state.shape[0]
    axis = torch.randint(0, 3, (batch,), device=state.device)
    observable = PAULI.to(device=state.device)[axis]
    plus = torch.ones(batch, device=state.device)
    minus = -plus
    k_plus = kraus_binary(observable, plus, gamma, dt)
    k_minus = kraus_binary(observable, minus, gamma, dt)
    post_plus = torch.einsum("bij,bj->bi", k_plus, state)
    post_minus = torch.einsum("bij,bj->bi", k_minus, state)
    p_plus = (post_plus.abs() ** 2).sum(dim=-1)
    p_minus = (post_minus.abs() ** 2).sum(dim=-1)
    prob = p_plus / (p_plus + p_minus + 1e-12)
    choice = torch.rand(batch, device=state.device) < prob
    post = torch.where(choice[:, None], post_plus, post_minus)
    sign = torch.where(choice, plus, minus)
    post = post / (post.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    return post, observable, sign


def sample_initial_ensemble(n_traj: int, device: torch.device) -> torch.Tensor:
    """Fig. 2(a): |0⟩ plus complex Gaussian noise, then normalize."""
    delta = NOISE_STD * (
        torch.randn(n_traj, 2, device=device) + 1j * torch.randn(n_traj, 2, device=device)
    ).to(torch.complex128)
    psi0 = torch.zeros(n_traj, 2, dtype=torch.complex128, device=device)
    psi0[:, 0] = 1.0
    psi = psi0 + delta
    return psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


def collect_forward(n_traj: int, device: torch.device) -> dict[str, torch.Tensor]:
    state = sample_initial_ensemble(n_traj, device)
    states = [state]
    observables = []
    for _ in range(N_STEPS):
        state, observable, _sign = sample_forward_step(state, GAMMA, DT)
        states.append(state)
        observables.append(observable)
    stacked = torch.stack(states, dim=1)
    return {
        "states": stacked,
        "z": bloch(stacked.reshape(-1, 2)).reshape(n_traj, N_STEPS + 1, 3),
        "observables": torch.stack(observables, dim=1),
    }


def infidelity_loss(model: ControlHamiltonian, batch: dict[str, torch.Tensor]) -> torch.Tensor:
    states = batch["states"]
    z = batch["z"]
    observables = batch["observables"]
    n_traj = states.shape[0]
    total = states.new_zeros((), dtype=torch.float32)
    for step in range(N_STEPS):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=states.device, dtype=z.dtype)
        hamiltonian = model.hamiltonian(z[:, step + 1], t_norm)
        unitary = score_operator(hamiltonian, observables[:, step], states[:, step + 1], GAMMA, DT)
        recovered = torch.einsum("bij,bj->bi", unitary, states[:, step + 1])
        overlap = (states[:, step].conj() * recovered).sum(dim=-1)
        total = total + (1.0 - overlap.abs() ** 2).mean()
    return total / N_STEPS


@torch.no_grad()
def reverse_from_final(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
    z_forward: torch.Tensor | None = None,
) -> torch.Tensor:
    state = final_state.clone()
    n_traj = state.shape[0]
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=state.device, dtype=torch.float32)
        z_now = z_forward[:, step + 1] if z_forward is not None else bloch(state)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        operator = score_operator(hamiltonian, observables[:, step], state, GAMMA, DT)
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    return state


@torch.no_grad()
def evaluate(model: ControlHamiltonian, device: torch.device, n_eval: int = 400) -> dict[str, float]:
    batch = collect_forward(n_eval, device)
    loss = float(infidelity_loss(model, batch).item())
    reversed_oracle_z = reverse_from_final(model, batch["states"][:, -1], batch["observables"], batch["z"])
    reversed_closed = reverse_from_final(model, batch["states"][:, -1], batch["observables"], None)
    initial = batch["states"][:, 0]
    fid_oracle = float(((reversed_oracle_z.conj() * initial).sum(dim=-1).abs() ** 2).mean())
    fid_closed = float(((reversed_closed.conj() * initial).sum(dim=-1).abs() ** 2).mean())
    mean_z = bloch(reversed_closed).mean(dim=0)
    return {
        "one_step_infidelity": loss,
        "same_record_oracle_z_fidelity": fid_oracle,
        "same_record_closed_loop_z_fidelity": fid_closed,
        "closed_loop_mean_bloch_x": float(mean_z[0]),
        "closed_loop_mean_bloch_y": float(mean_z[1]),
        "closed_loop_mean_bloch_z": float(mean_z[2]),
        "closed_loop_mean_polarization": float(torch.linalg.norm(mean_z)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper Fig. 2 control-Hamiltonian trainer")
    parser.add_argument("--epochs", type=int, default=400)
    parser.add_argument("--batch", type=int, default=256)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--eval-every", type=int, default=20)
    parser.add_argument("--lr", type=float, default=1e-3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.set_device(0)
    torch.manual_seed(args.seed)
    model = ControlHamiltonian().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "seed": args.seed,
        "gamma": GAMMA,
        "T": T_FINAL,
        "dt": DT,
        "n_steps": N_STEPS,
        "protocol": "paper-eq-27-28-fig2",
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (OUTPUT / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        batch = collect_forward(args.batch, device)
        optimizer.zero_grad()
        loss = infidelity_loss(model, batch)
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {"epoch": epoch_id, "loss": float(loss.item()), "elapsed_seconds": time.perf_counter() - started}
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, device))
            (OUTPUT / "progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n")
            torch.save(model.state_dict(), OUTPUT / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": "paper_control_hamiltonian_n1",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": env,
        "loss_curve": curve,
        "final": curve[-1],
    }
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), OUTPUT / "model.pt")
    print(json.dumps({"event": "done", "final": curve[-1]}), flush=True)


if __name__ == "__main__":
    main()
