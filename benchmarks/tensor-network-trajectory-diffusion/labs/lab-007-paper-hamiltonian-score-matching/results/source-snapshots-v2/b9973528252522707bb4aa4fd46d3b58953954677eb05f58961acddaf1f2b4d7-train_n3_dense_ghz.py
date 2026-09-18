"""Dense N=3 GHZ ceiling and see-vs-do ablations.

N=2 Bell recovered at F≈0.97 with the full 15-dimensional Pauli vector and
the full 15-coefficient H. Local 2-local H on N=3 GHZ stalled at F≈0.42.
This script lifts the N=2 dense trainer to N=3 (dim 8, 63 Paulis) and
splits the two bottlenecks:

  C  --z-mode full      --h-mode full       ceiling: can see XXX and apply it
  A  --z-mode full      --h-mode two_local  see, but H is 2-local
  B  --z-mode local     --h-mode full       3-body H, but z is Bloch+NN only

`local` z / `two_local` H = 1-body + nearest-neighbor 2-body (27 terms),
the same support as the MPS shared-local ansatz. Protocol otherwise matches
train_n2_control_hamiltonian.py: T=3, γ=1, dt=0.01, per-step infidelity,
closed-loop reverse from current z.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import torch
import torch.nn as nn

LAB = Path(__file__).resolve().parent
OUTPUT_ROOT = LAB / "results"

GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))
N_QUBITS = 3
DIM = 8
N_PAULI = 63  # 4^3 − 1
LABELS = "IXYZ"


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


def _three_qubit_paulis() -> tuple[torch.Tensor, list[str], list[str]]:
    one = _pauli_matrices()
    ops = []
    names = []
    kinds = []
    for indices in product(range(4), repeat=N_QUBITS):
        if all(i == 0 for i in indices):
            continue
        op = one[indices[0]]
        for idx in indices[1:]:
            op = torch.kron(op, one[idx])
        name = "".join(LABELS[i] for i in indices)
        sites = [s for s, i in enumerate(indices) if i != 0]
        if len(sites) == 1:
            kind = "one_body"
        elif len(sites) == 2 and sites[1] - sites[0] == 1:
            kind = "nn_two_body"
        elif len(sites) == 2:
            kind = "nnn_two_body"
        else:
            kind = "three_body"
        ops.append(op)
        names.append(name)
        kinds.append(kind)
    return torch.stack(ops, dim=0), names, kinds


ALL_PAULI, PAULI_NAMES, PAULI_KINDS = _three_qubit_paulis()
LOCAL_PAULI = _pauli_matrices()[1:]
LOCAL_KINDS = frozenset({"one_body", "nn_two_body"})
GHZ_STABILIZERS = ("XXX", "YYX", "YXY", "XYY", "ZZI", "ZIZ", "IZZ")
CLUSTER_CHECKS = ("XZI", "ZXZ", "IZX")
CLUSTER_LOGICALS = ("ZII", "IIZ", "XII", "IIX")
REPETITION_CHECKS = ("ZZI", "IZZ", "ZIZ")
REPETITION_LOGICALS = ("XXX", "ZII")


def subset_index(mode: str) -> torch.Tensor:
    if mode in ("full",):
        return torch.arange(N_PAULI)
    if mode in ("local", "two_local"):
        return torch.tensor([i for i, kind in enumerate(PAULI_KINDS) if kind in LOCAL_KINDS])
    raise ValueError(f"unknown Pauli subset {mode}")


def embed_local(ops: torch.Tensor, site: int) -> torch.Tensor:
    """ops (B, 2, 2) → (B, 8, 8) acting on `site` (site 0 = kron leftmost / MSB)."""
    batch = ops.shape[0]
    identity = torch.eye(2, dtype=ops.dtype, device=ops.device).expand(batch, 2, 2)
    embedded = ops if site == 0 else identity
    for other in range(1, N_QUBITS):
        factor = ops if other == site else identity
        embedded = torch.einsum("bij,bkl->bikjl", embedded, factor).reshape(batch, embedded.shape[1] * 2, -1)
    return embedded


def pauli_vector(state: torch.Tensor, index: torch.Tensor | None = None) -> torch.Tensor:
    basis = ALL_PAULI.to(device=state.device, dtype=state.dtype)
    if index is not None:
        basis = basis[index.to(device=state.device)]
    return torch.einsum("bi,kij,bj->bk", state.conj(), basis, state).real


def ghz_state(n_traj: int, device: torch.device) -> torch.Tensor:
    psi = torch.zeros(n_traj, DIM, dtype=torch.complex128, device=device)
    amp = 1.0 / math.sqrt(2.0)
    psi[:, 0] = amp
    psi[:, -1] = amp
    return psi


def cluster_state(n_traj: int, device: torch.device) -> torch.Tensor:
    """Open-boundary 1D cluster: CZ on every bond applied to |+⟩^⊗3."""
    amp = 1.0 / math.sqrt(DIM)
    psi = torch.full((DIM,), amp, dtype=torch.complex128, device=device)
    for bond in range(N_QUBITS - 1):
        shift_left = N_QUBITS - 1 - bond
        shift_right = N_QUBITS - 2 - bond
        for basis in range(DIM):
            if ((basis >> shift_left) & 1) and ((basis >> shift_right) & 1):
                psi[basis] *= -1
    return psi.unsqueeze(0).expand(n_traj, -1).contiguous()


def cluster_code_state(n_traj: int, device: torch.device) -> torch.Tensor:
    """Gaussian unraveling of the bulk-ZXZ code space (4-fold, edges free)."""
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    projector = 0.5 * (
        torch.eye(DIM, dtype=torch.complex128, device=device) + ALL_PAULI[lookup["ZXZ"]].to(device)
    )
    gauss = (
        torch.randn(n_traj, DIM, device=device) + 1j * torch.randn(n_traj, DIM, device=device)
    ).to(torch.complex128)
    psi = torch.einsum("ij,bj->bi", projector, gauss)
    return psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


def sample_initial(target: str, n_traj: int, device: torch.device) -> torch.Tensor:
    if target == "ghz":
        return ghz_state(n_traj, device)
    if target == "cluster":
        return cluster_state(n_traj, device)
    if target == "cluster_code":
        return cluster_code_state(n_traj, device)
    raise ValueError(f"unknown target {target}")


class ControlHamiltonian(nn.Module):
    """h_θ(z_subset, t) → coefficients on the H subset, scattered into su(8)."""

    def __init__(self, n_z: int, h_index: torch.Tensor, hidden: int = 128):
        super().__init__()
        self.n_h = int(h_index.numel())
        self.register_buffer("h_index", h_index.long())
        self.net = nn.Sequential(
            nn.Linear(n_z + 1, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, self.n_h),
        )

    def field(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        inputs = torch.cat([z, t_norm], dim=-1).to(dtype=next(self.net.parameters()).dtype)
        return self.net(inputs)

    def hamiltonian(self, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
        h_sub = self.field(z, t_norm).to(torch.float64)
        h_full = h_sub.new_zeros(z.shape[0], N_PAULI)
        h_full[:, self.h_index] = h_sub
        basis = ALL_PAULI.to(device=z.device)
        return torch.einsum("ba,aij->bij", h_full.to(basis.dtype), basis)


def kraus_binary(observable: torch.Tensor, sign: torch.Tensor, gamma: float, dt: float) -> torch.Tensor:
    dim = observable.shape[-1]
    delta_o = sign.to(observable.dtype) * 0.5 * math.sqrt(dt / gamma)
    identity = torch.eye(dim, dtype=observable.dtype, device=observable.device)
    generator = (-gamma * dt) * identity + (2.0 * gamma) * observable * delta_o[:, None, None]
    return (1.0 / math.sqrt(2.0)) * torch.linalg.matrix_exp(generator)


def sample_forward_step(state: torch.Tensor, gamma: float, dt: float) -> tuple[torch.Tensor, torch.Tensor]:
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
    identity = torch.eye(DIM, dtype=observables.dtype, device=observables.device)
    generator = (2.0j) * hamiltonian
    for site in range(observables.shape[1]):
        observable = observables[:, site]
        expectation = torch.einsum("bi,bij,bj->b", state.conj(), observable, state).real
        delta = observable - expectation[:, None, None] * identity
        generator = generator + (-0.5 * gamma) * (delta @ delta)
    return torch.linalg.matrix_exp(generator * dt)


def collect_forward(
    n_traj: int,
    device: torch.device,
    z_index: torch.Tensor,
    target: str,
) -> dict[str, torch.Tensor]:
    state = sample_initial(target, n_traj, device)
    states = [state]
    observables = []
    for _ in range(N_STEPS):
        state, obs = sample_forward_step(state, GAMMA, DT)
        states.append(state)
        observables.append(obs)
    stacked = torch.stack(states, dim=1)
    z_index = z_index.to(device)
    return {
        "states": stacked,
        "z": pauli_vector(stacked.reshape(-1, DIM), z_index).reshape(n_traj, N_STEPS + 1, z_index.numel()),
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


def closed_loop_infidelity_loss(
    model: ControlHamiltonian,
    batch: dict[str, torch.Tensor],
    z_index: torch.Tensor,
) -> torch.Tensor:
    """Endpoint infidelity after the full 300-step reverse.

    Unlike teacher-forced one-step matching, this rewards any 2-local schedule
    that returns to GHZ, including a slow entangling path.
    """
    state = batch["states"][:, -1]
    target = batch["states"][:, 0]
    observables = batch["observables"]
    n_traj = state.shape[0]
    z_index = z_index.to(state.device)
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=state.device, dtype=torch.float32)
        z_now = pauli_vector(state, z_index)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        operator = score_operator(hamiltonian, observables[:, step], state, GAMMA, DT)
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    overlap = (target.conj() * state).sum(dim=-1)
    return (1.0 - overlap.abs() ** 2).mean()


@torch.no_grad()
def reverse_from_final(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
    z_index: torch.Tensor,
    z_forward: torch.Tensor | None = None,
) -> torch.Tensor:
    state = final_state.clone()
    n_traj = state.shape[0]
    z_index = z_index.to(state.device)
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=state.device, dtype=torch.float32)
        z_now = z_forward[:, step + 1] if z_forward is not None else pauli_vector(state, z_index)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        operator = score_operator(hamiltonian, observables[:, step], state, GAMMA, DT)
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    return state


def fidelity_to_target(states: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return (states.conj() * target).sum(dim=-1).abs() ** 2


def ensemble_w1_trace(states_a: torch.Tensor, states_b: torch.Tensor) -> float:
    overlap_sq = torch.einsum("ik,jk->ij", states_a.conj(), states_b).abs() ** 2
    cost = (1.0 - overlap_sq.clamp(0.0, 1.0)).sqrt().detach().cpu().numpy()
    try:
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        return float(cost.diagonal().mean())
    row, col = linear_sum_assignment(cost)
    return float(cost[row, col].mean())


@torch.no_grad()
def named_means(states: torch.Tensor, names: tuple[str, ...]) -> dict[str, float]:
    z = pauli_vector(states)
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    out: dict[str, float] = {}
    for name in names:
        values = z[:, lookup[name]]
        out[f"closed_loop_mean_{name}"] = float(values.mean())
        out[f"closed_loop_std_{name}"] = float(values.std(unbiased=False))
    return out


@torch.no_grad()
def evaluate(
    model: ControlHamiltonian,
    device: torch.device,
    z_index: torch.Tensor,
    n_eval: int,
    target: str,
) -> dict[str, float]:
    batch = collect_forward(n_eval, device, z_index, target)
    loss = float(infidelity_loss(model, batch).item())
    reversed_oracle = reverse_from_final(model, batch["states"][:, -1], batch["observables"], z_index, batch["z"])
    reversed_closed = reverse_from_final(model, batch["states"][:, -1], batch["observables"], z_index, None)
    initial = batch["states"][:, 0]
    fid_closed = float(fidelity_to_target(reversed_closed, initial).mean())
    result = {
        "one_step_infidelity": loss,
        "same_record_oracle_z_fidelity": float(fidelity_to_target(reversed_oracle, initial).mean()),
        "same_record_closed_loop_z_fidelity": fid_closed,
        "closed_loop_W1_to_initial_ensemble": ensemble_w1_trace(reversed_closed, initial),
    }
    if target == "ghz":
        ghz = ghz_state(n_eval, device)
        result["closed_loop_fidelity_to_ghz"] = float(fidelity_to_target(reversed_closed, ghz).mean())
        result.update(named_means(reversed_closed, GHZ_STABILIZERS))
        result["repetition_check_mean"] = 0.5 * (result["closed_loop_mean_ZZI"] + result["closed_loop_mean_IZZ"])
    else:
        cluster = cluster_state(n_eval, device)
        result["closed_loop_fidelity_to_cluster"] = float(fidelity_to_target(reversed_closed, cluster).mean())
        result.update(named_means(reversed_closed, CLUSTER_CHECKS + CLUSTER_LOGICALS))
        result["bulk_check_ZXZ"] = result["closed_loop_mean_ZXZ"]
        result["edge_check_mean"] = 0.5 * (result["closed_loop_mean_XZI"] + result["closed_loop_mean_IZX"])
    return result


def target_sanity(device: torch.device, target: str) -> dict[str, float]:
    psi = sample_initial(target, 8, device)
    z = pauli_vector(psi)
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    report = {
        "n_pauli": N_PAULI,
        "n_local": int(subset_index("local").numel()),
        "target": target,
    }
    if target == "ghz":
        report.update(
            {
                "ghz_XXX": float(z[0, lookup["XXX"]]),
                "ghz_ZZI": float(z[0, lookup["ZZI"]]),
                "ghz_XXI": float(z[0, lookup["XXI"]]),
            }
        )
    else:
        report.update(
            {
                "mean_XZI": float(z[:, lookup["XZI"]].mean()),
                "mean_ZXZ": float(z[:, lookup["ZXZ"]].mean()),
                "mean_IZX": float(z[:, lookup["IZX"]].mean()),
                "mean_ZII": float(z[:, lookup["ZII"]].mean()),
                "std_ZII": float(z[:, lookup["ZII"]].std(unbiased=False)),
            }
        )
    return report


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
    parser = argparse.ArgumentParser(description="Dense N=3 local-stabilizer / GHZ trainer")
    parser.add_argument("--target", choices=("ghz", "cluster", "cluster_code"), default="ghz")
    parser.add_argument("--z-mode", choices=("full", "local"), default="full")
    parser.add_argument("--h-mode", choices=("full", "two_local"), default="full")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--eval-traj", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument(
        "--loss",
        choices=("one_step", "closed_loop", "hybrid"),
        default="one_step",
        help="one_step: teacher-forced score matching; closed_loop: 300-step endpoint F; hybrid: mean of both",
    )
    parser.add_argument("--sanity-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    z_index = subset_index(args.z_mode)
    h_index = subset_index(args.h_mode)
    sanity = target_sanity(device, args.target)
    print(json.dumps({"event": "sanity", **sanity}), flush=True)
    if args.sanity_only:
        return
    if args.target == "ghz" and (
        abs(sanity["ghz_XXX"] - 1.0) > 1e-12 or abs(sanity["ghz_XXI"]) > 1e-12
    ):
        raise RuntimeError(f"GHZ Pauli sanity failed: {sanity}")
    if args.target == "cluster" and (
        abs(sanity["mean_ZXZ"] - 1.0) > 1e-8
        or abs(sanity["mean_XZI"] - 1.0) > 1e-8
        or abs(sanity["mean_IZX"] - 1.0) > 1e-8
    ):
        raise RuntimeError(f"cluster stabilizer sanity failed: {sanity}")
    if args.target == "cluster_code" and abs(sanity["mean_ZXZ"] - 1.0) > 1e-6:
        raise RuntimeError(f"cluster_code bulk check sanity failed: {sanity}")

    tag = f"z{args.z_mode}-h{args.h_mode}"
    if args.loss != "one_step":
        tag = f"{tag}-{args.loss.replace('_', '')}"
    output = OUTPUT_ROOT / f"dense-n3-{args.target}-{tag}-v1"
    output.mkdir(parents=True, exist_ok=True)
    model = ControlHamiltonian(n_z=int(z_index.numel()), h_index=h_index, hidden=args.hidden).to(device)
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
        "z_mode": args.z_mode,
        "h_mode": args.h_mode,
        "n_z": int(z_index.numel()),
        "n_h": int(h_index.numel()),
        "batch": args.batch,
        "hidden": args.hidden,
        "loss": args.loss,
        "protocol": "dense-n3-local-stabilizer",
        "z_paulis": [PAULI_NAMES[i] for i in z_index.tolist()],
        "h_paulis": [PAULI_NAMES[i] for i in h_index.tolist()],
        "sanity": sanity,
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    slim_env = {k: v for k, v in env.items() if k not in ("z_paulis", "h_paulis")}
    (output / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **slim_env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        batch = collect_forward(args.batch, device, z_index, args.target)
        optimizer.zero_grad()
        if args.loss == "one_step":
            loss = infidelity_loss(model, batch)
        elif args.loss == "closed_loop":
            loss = closed_loop_infidelity_loss(model, batch, z_index)
        else:
            loss = 0.5 * infidelity_loss(model, batch) + 0.5 * closed_loop_infidelity_loss(model, batch, z_index)
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, device, z_index, n_eval=args.eval_traj, target=args.target))
            (output / "progress.json").write_text(
                json.dumps({"epoch": epoch_id, "latest": record, "config": slim_env}) + "\n"
            )
            torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"dense_n3_{args.target}_{tag}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": slim_env,
        "loss_curve": curve,
        "final": curve[-1],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), output / "model.pt")
    print(json.dumps({"event": "done", "final": curve[-1]}), flush=True)


if __name__ == "__main__":
    main()
