"""Paper-faithful control-Hamiltonian score matching for two qubits.

Liu et al., arXiv:2508.08799, Sec. III.A.4 and Fig. 4 — not the QR notebooks.

Forward: on-site weak Pauli measurements on every qubit each step
(Eq. sde_multisite). State encoding: 15-dimensional two-qubit Pauli vector z.
Learned object: H_θ(z, t) = Σ_{P ≠ I} h_P(z, t) P, 15 real coefficients.
Score operator, multi-site lift of Eq. (28):
    V = exp[ (Σ_j (−γ/2) (δO^{(j)})² + 2 i H_θ) dt ]
Loss: mean infidelity 1 − |⟨ψ_{t−dt}| V |ψ_t⟩|².

Targets
  bell:        singlet |ψ_B⟩ = (|↑↓⟩ − |↓↑⟩)/√2, Fig. 4(a)
  heisenberg:  thermal ensemble of
               H = J σ1·σ2 + B_x σ_{1x} + B_z σ_{2x},
               J=1, B_x=B_z=0.5, T_H ∈ [0, 0.5], Fig. 4(b)

For a rank-one Bell target, W_1 with trace-distance cost equals the mean
trace distance to |ψ_B⟩.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import torch
import torch.nn as nn

LAB = Path(__file__).resolve().parent
OUTPUT_ROOT = LAB / "results"

GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))  # 300
N_QUBITS = 2
DIM = 4
N_PAULI = 15  # 4^2 − 1
HEISENBERG_J = 1.0
HEISENBERG_BX = 0.5
HEISENBERG_BZ = 0.5
HEISENBERG_TMAX = 0.5


def _pauli_matrices() -> torch.Tensor:
    return torch.tensor(
        [
            [[1.0, 0.0], [0.0, 1.0]],
            [[0.0, 1.0], [1.0, 0.0]],
            [[0.0, -1.0j], [1.0j, 0.0]],
            [[1.0, 0.0], [0.0, -1.0]],
        ],
        dtype=torch.complex128,
    )


def _two_qubit_paulis() -> tuple[torch.Tensor, list[str]]:
    one = _pauli_matrices()
    labels = ["I", "X", "Y", "Z"]
    ops = []
    names = []
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            if i == 0 and j == 0:
                continue
            ops.append(torch.kron(one[i], one[j]))
            names.append(a + b)
    return torch.stack(ops, dim=0), names


TWO_QUBIT_PAULI, PAULI_NAMES = _two_qubit_paulis()
LOCAL_PAULI = _pauli_matrices()[1:]  # X, Y, Z


def embed_local(ops: torch.Tensor, site: int) -> torch.Tensor:
    """ops (B, 2, 2) → (B, 4, 4) as P⊗I or I⊗P."""
    batch = ops.shape[0]
    identity = torch.eye(2, dtype=ops.dtype, device=ops.device).expand(batch, 2, 2)
    left, right = (ops, identity) if site == 0 else (identity, ops)
    return torch.einsum("bij,bkl->bikjl", left, right).reshape(batch, DIM, DIM)


def pauli_vector(state: torch.Tensor) -> torch.Tensor:
    basis = TWO_QUBIT_PAULI.to(device=state.device, dtype=state.dtype)
    return torch.einsum("bi,kij,bj->bk", state.conj(), basis, state).real


def bell_singlet(n_traj: int, device: torch.device) -> torch.Tensor:
    psi = torch.zeros(n_traj, DIM, dtype=torch.complex128, device=device)
    amp = 1.0 / math.sqrt(2.0)
    psi[:, 1] = amp
    psi[:, 2] = -amp
    return psi


def heisenberg_hamiltonian(device: torch.device) -> torch.Tensor:
    basis = {name: op.to(device) for name, op in zip(PAULI_NAMES, TWO_QUBIT_PAULI)}
    return (
        HEISENBERG_J * (basis["XX"] + basis["YY"] + basis["ZZ"])
        + HEISENBERG_BX * basis["XI"]
        + HEISENBERG_BZ * basis["IX"]
    )


def sample_heisenberg_thermal(n_traj: int, device: torch.device) -> torch.Tensor:
    """Max-entropy unraveling of e^{-H/T_H}/Z with T_H ~ Uniform[0, 0.5]."""
    hamiltonian = heisenberg_hamiltonian(device)
    evals, evecs = torch.linalg.eigh(hamiltonian)
    temperatures = torch.rand(n_traj, device=device, dtype=torch.float64) * HEISENBERG_TMAX
    temperatures = temperatures.clamp(min=1e-8)
    logits = -evals[None, :].real / temperatures[:, None]
    logits = logits - logits.max(dim=-1, keepdim=True).values
    weights = torch.exp(logits)
    weights = weights / weights.sum(dim=-1, keepdim=True)
    sqrt_w = weights.sqrt().to(evecs.dtype)
    sqrt_rho = torch.einsum("ij,bj,kj->bik", evecs, sqrt_w, evecs)
    gauss = (
        torch.randn(n_traj, DIM, device=device) + 1j * torch.randn(n_traj, DIM, device=device)
    ).to(torch.complex128)
    psi = torch.einsum("bij,bj->bi", sqrt_rho, gauss)
    return psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


def sample_initial(target: str, n_traj: int, device: torch.device) -> torch.Tensor:
    if target == "bell":
        return bell_singlet(n_traj, device)
    if target == "heisenberg":
        return sample_heisenberg_thermal(n_traj, device)
    raise ValueError(f"unknown target {target}")


class ControlHamiltonian(nn.Module):
    """h_θ(z, t) → R^{15}, H = Σ h_P P."""

    def __init__(self, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(N_PAULI + 1, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, N_PAULI),
        )

    def field(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        inputs = torch.cat([z, t_norm], dim=-1).to(dtype=next(self.net.parameters()).dtype)
        return self.net(inputs)

    def hamiltonian(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        h = self.field(z, t_norm).to(torch.float64)
        basis = TWO_QUBIT_PAULI.to(device=z.device)
        return torch.einsum("ba,aij->bij", h.to(basis.dtype), basis)


def kraus_binary(observable: torch.Tensor, sign: torch.Tensor, gamma: float, dt: float) -> torch.Tensor:
    dim = observable.shape[-1]
    delta_o = sign.to(observable.dtype) * 0.5 * math.sqrt(dt / gamma)
    identity = torch.eye(dim, dtype=observable.dtype, device=observable.device)
    generator = (-gamma * dt) * identity + (2.0 * gamma) * observable * delta_o[:, None, None]
    return (1.0 / math.sqrt(2.0)) * torch.linalg.matrix_exp(generator)


def sample_forward_step(state: torch.Tensor, gamma: float, dt: float) -> tuple[torch.Tensor, torch.Tensor]:
    """Simultaneous on-site weak Pauli measurements, Eq. sde_multisite."""
    batch = state.shape[0]
    device = state.device
    observables = []
    for site in range(N_QUBITS):
        axis = torch.randint(0, 3, (batch,), device=device)
        local = LOCAL_PAULI.to(device=device)[axis]
        observable = embed_local(local, site)
        plus = torch.ones(batch, device=device)
        minus = -plus
        k_plus = kraus_binary(observable, plus, gamma, dt)
        k_minus = kraus_binary(observable, minus, gamma, dt)
        post_plus = torch.einsum("bij,bj->bi", k_plus, state)
        post_minus = torch.einsum("bij,bj->bi", k_minus, state)
        p_plus = (post_plus.abs() ** 2).sum(dim=-1)
        p_minus = (post_minus.abs() ** 2).sum(dim=-1)
        choice = torch.rand(batch, device=device) < (p_plus / (p_plus + p_minus + 1e-12))
        state = torch.where(choice[:, None], post_plus, post_minus)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        observables.append(observable)
    return state, torch.stack(observables, dim=1)


def score_operator(
    hamiltonian: torch.Tensor,
    observables: torch.Tensor,
    state: torch.Tensor,
    gamma: float,
    dt: float,
) -> torch.Tensor:
    """V = exp[(Σ_j (−γ/2) δO_j² + 2i H) dt]."""
    identity = torch.eye(DIM, dtype=observables.dtype, device=observables.device)
    generator = (2.0j) * hamiltonian
    for site in range(observables.shape[1]):
        observable = observables[:, site]
        expectation = torch.einsum("bi,bij,bj->b", state.conj(), observable, state).real
        delta = observable - expectation[:, None, None] * identity
        generator = generator + (-0.5 * gamma) * (delta @ delta)
    return torch.linalg.matrix_exp(generator * dt)


def collect_forward(target: str, n_traj: int, device: torch.device) -> dict[str, torch.Tensor]:
    state = sample_initial(target, n_traj, device)
    states = [state]
    observables = []
    for _ in range(N_STEPS):
        state, obs = sample_forward_step(state, GAMMA, DT)
        states.append(state)
        observables.append(obs)
    stacked = torch.stack(states, dim=1)
    return {
        "states": stacked,
        "z": pauli_vector(stacked.reshape(-1, DIM)).reshape(n_traj, N_STEPS + 1, N_PAULI),
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
        operator = score_operator(hamiltonian, observables[:, step], states[:, step + 1], GAMMA, DT)
        recovered = torch.einsum("bij,bj->bi", operator, states[:, step + 1])
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
        z_now = z_forward[:, step + 1] if z_forward is not None else pauli_vector(state)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        operator = score_operator(hamiltonian, observables[:, step], state, GAMMA, DT)
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    return state


def fidelity_to_target(states: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    overlap = (states.conj() * target).sum(dim=-1)
    return overlap.abs() ** 2


def trace_distance_to_target(states: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (1.0 - fidelity_to_target(states, target)).clamp(min=0.0).sqrt()


def ensemble_w1_trace(states_a: torch.Tensor, states_b: torch.Tensor) -> float:
    """Wasserstein-1 with trace-distance cost via exact assignment (equal sizes)."""
    overlap_sq = torch.einsum("ik,jk->ij", states_a.conj(), states_b).abs() ** 2
    cost = (1.0 - overlap_sq.clamp(0.0, 1.0)).sqrt().detach().cpu().numpy()
    try:
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        return float(cost.diagonal().mean())
    row, col = linear_sum_assignment(cost)
    return float(cost[row, col].mean())


@torch.no_grad()
def evaluate(model: ControlHamiltonian, target: str, device: torch.device, n_eval: int = 256) -> dict[str, float]:
    batch = collect_forward(target, n_eval, device)
    loss = float(infidelity_loss(model, batch).item())
    reversed_oracle = reverse_from_final(model, batch["states"][:, -1], batch["observables"], batch["z"])
    reversed_closed = reverse_from_final(model, batch["states"][:, -1], batch["observables"], None)
    initial = batch["states"][:, 0]
    fid_oracle = float(fidelity_to_target(reversed_oracle, initial).mean())
    fid_closed = float(fidelity_to_target(reversed_closed, initial).mean())
    mean_z = pauli_vector(reversed_closed).mean(dim=0)
    result = {
        "one_step_infidelity": loss,
        "same_record_oracle_z_fidelity": fid_oracle,
        "same_record_closed_loop_z_fidelity": fid_closed,
        "closed_loop_mean_polarization": float(torch.linalg.norm(mean_z)),
    }
    if target == "bell":
        bell = bell_singlet(n_eval, device)
        fid_bell = fidelity_to_target(reversed_closed, bell)
        result["closed_loop_fidelity_to_bell"] = float(fid_bell.mean())
        result["closed_loop_W1_trace_to_bell"] = float(trace_distance_to_target(reversed_closed, bell).mean())
        named = {f"closed_loop_mean_{name}": float(mean_z[i]) for i, name in enumerate(PAULI_NAMES)}
        result.update({k: named[k] for k in ("closed_loop_mean_XX", "closed_loop_mean_YY", "closed_loop_mean_ZZ")})
    result["closed_loop_W1_to_initial_ensemble"] = ensemble_w1_trace(reversed_closed, initial)
    return result


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Paper Fig. 4 control-Hamiltonian trainer")
    parser.add_argument("--target", choices=("bell", "heisenberg"), default="bell")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--eval-every", type=int, default=20)
    parser.add_argument("--eval-traj", type=int, default=256)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--hidden", type=int, default=128)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    output = OUTPUT_ROOT / f"paper-fig4-n2-{args.target}-v1"
    output.mkdir(parents=True, exist_ok=True)
    model = ControlHamiltonian(hidden=args.hidden).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
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
        "n_qubits": N_QUBITS,
        "target": args.target,
        "batch": args.batch,
        "hidden": args.hidden,
        "protocol": "paper-eq-27-28-fig4-simultaneous-onsite",
        "pauli_basis": PAULI_NAMES,
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        batch = collect_forward(args.target, args.batch, device)
        optimizer.zero_grad()
        loss = infidelity_loss(model, batch)
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, args.target, device, n_eval=args.eval_traj))
            (output / "progress.json").write_text(
                json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n"
            )
            torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"paper_control_hamiltonian_n2_{args.target}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": env,
        "loss_curve": curve,
        "final": curve[-1],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), output / "model.pt")
    print(json.dumps({"event": "done", "final": curve[-1]}), flush=True)


if __name__ == "__main__":
    main()
