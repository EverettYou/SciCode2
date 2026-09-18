"""Translation-shared local Pauli coefficients for the control Hamiltonian.

The network does not emit MPO tensors. It emits, with weights shared across
the chain:

  on-site:  h^{(1)}_j(z_j, t) ∈ R^3
  bond:     h^{(2)}_j(z_j, z_{j+1}, ⟨σ_j σ_{j+1}⟩, t) ∈ R^9

H = Σ_j h^{(1)}_j · σ_j + Σ_j Σ_{αβ} h^{(2)}_{j,αβ} σ_j^α σ_{j+1}^β
is applied by 1-site MPS-TDVP (QR gauge, no SVD). TEBD remains a no-grad
comparator. Parameter count is 3N + 9(N-1) = 12N-9.
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
sys.path.insert(0, str(LAB))

from mps_backend import (  # noqa: E402
    BatchMPS,
    mps_from_dense,
    reverse_dense_local,
    reverse_tdvp_local,
    reverse_tebd_local,
    sample_onsite_kraus,
)
from train_n1_control_hamiltonian import sample_initial_ensemble as sample_n1  # noqa: E402
from train_n2_control_hamiltonian import bell_singlet, ensemble_w1_trace  # noqa: E402

GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))
NOISE_STD = 0.2


class LocalControlHamiltonian(nn.Module):
    """Shared on-site and bond MLPs. Not an MPO parameterization."""

    def __init__(self, hidden: int = 128):
        super().__init__()
        self.onsite = nn.Sequential(
            nn.Linear(22, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 3),
        )
        self.bond = nn.Sequential(
            nn.Linear(16, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 9),
        )

    def coefficients(
        self,
        bloch: torch.Tensor,
        bonds: torch.Tensor | None,
        t_norm: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        batch, n_sites, _ = bloch.shape
        t_site = t_norm[:, None, :].expand(batch, n_sites, 1).to(dtype=bloch.dtype)
        left_bond = bloch.new_zeros(batch, n_sites, 9)
        right_bond = bloch.new_zeros(batch, n_sites, 9)
        if bonds is not None:
            left_bond[:, 1:] = bonds
            right_bond[:, :-1] = bonds
        onsite_in = torch.cat([bloch, left_bond, right_bond, t_site], dim=-1)
        onsite_in = onsite_in.to(dtype=next(self.onsite.parameters()).dtype)
        h_on = self.onsite(onsite_in.reshape(batch * n_sites, 22)).reshape(batch, n_sites, 3).to(torch.float64)
        if n_sites == 1 or bonds is None:
            return h_on, None
        t_bond = t_norm[:, None, :].expand(batch, n_sites - 1, 1)
        bond_in = torch.cat([bloch[:, :-1], bloch[:, 1:], bonds, t_bond], dim=-1)
        bond_in = bond_in.to(dtype=next(self.bond.parameters()).dtype)
        h_bond = self.bond(bond_in.reshape(batch * (n_sites - 1), 16)).reshape(batch, n_sites - 1, 9).to(torch.float64)
        return h_on, h_bond


def sample_product_ensemble(n_qubits: int, n_traj: int, device: torch.device) -> torch.Tensor:
    """Independent N=1-style noisy |0⟩ on each site, then the tensor product.

    Full-Hilbert noise would inject volume-law components a local Hamiltonian
    cannot reverse. This is the Fig. 2 ensemble, one factor per qubit.
    """
    sites = torch.zeros(n_traj, n_qubits, 2, dtype=torch.complex128, device=device)
    sites[:, :, 0] = 1.0
    sites = sites + NOISE_STD * (
        torch.randn(n_traj, n_qubits, 2, device=device) + 1j * torch.randn(n_traj, n_qubits, 2, device=device)
    ).to(torch.complex128)
    sites = sites / (sites.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    psi = sites[:, 0, :]
    for qubit in range(1, n_qubits):
        psi = torch.einsum("bi,bj->bij", psi, sites[:, qubit]).reshape(n_traj, -1)
    return psi


def ghz_state(n_traj: int, n_qubits: int, device: torch.device) -> torch.Tensor:
    """(|0...0⟩ + |1...1⟩)/√2, the N-qubit lift of the Bell target."""
    dim = 2**n_qubits
    psi = torch.zeros(n_traj, dim, dtype=torch.complex128, device=device)
    amp = 1.0 / math.sqrt(2.0)
    psi[:, 0] = amp
    psi[:, -1] = amp
    return psi


def w_state(n_traj: int, n_qubits: int, device: torch.device) -> torch.Tensor:
    """Single-excitation Dicke state, e.g. N=3: (|001⟩+|010⟩+|100⟩)/√3."""
    dim = 2**n_qubits
    psi = torch.zeros(n_traj, dim, dtype=torch.complex128, device=device)
    amp = 1.0 / math.sqrt(n_qubits)
    for site in range(n_qubits):
        psi[:, 1 << (n_qubits - 1 - site)] = amp
    return psi


def sample_initial(n_qubits: int, target: str, n_traj: int, device: torch.device) -> torch.Tensor:
    if n_qubits == 1:
        return sample_n1(n_traj, device)
    if n_qubits == 2 and target == "bell":
        return bell_singlet(n_traj, device)
    if target == "ghz":
        return ghz_state(n_traj, n_qubits, device)
    if target == "w":
        return w_state(n_traj, n_qubits, device)
    return sample_product_ensemble(n_qubits, n_traj, device)


@torch.no_grad()
def collect_forward(
    n_qubits: int,
    n_traj: int,
    device: torch.device,
    target: str,
) -> tuple[list[BatchMPS], list[torch.Tensor], torch.Tensor]:
    psi0 = sample_initial(n_qubits, target, n_traj, device)
    mps = mps_from_dense(psi0, n_qubits).normalize()
    states = [mps]
    axes: list[torch.Tensor] = []
    for _ in range(N_STEPS):
        step_axes = []
        for site in range(n_qubits):
            mps, axis, _sign = sample_onsite_kraus(mps, site, GAMMA, DT)
            step_axes.append(axis)
        axes.append(torch.stack(step_axes, dim=-1))
        mps = mps.balance()
        states.append(mps)
    return states, axes, psi0


def model_step(
    model: LocalControlHamiltonian,
    mps: BatchMPS,
    t_norm: torch.Tensor,
    axes: torch.Tensor,
    chi_max: int | None,
) -> BatchMPS:
    bloch, bonds = mps.local_observables()
    h_on, h_bond = model.coefficients(bloch, bonds, t_norm)
    return reverse_tdvp_local(mps, h_on, h_bond, axes, GAMMA, DT, chi_max=chi_max)


def infidelity_loss(
    model: LocalControlHamiltonian,
    states: list[BatchMPS],
    axes: list[torch.Tensor],
    chi_max: int | None,
) -> torch.Tensor:
    n_traj = states[0].batch
    device = states[0].device
    total = torch.zeros((), dtype=torch.float32, device=device)
    for step in range(N_STEPS):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        recovered = model_step(model, states[step + 1], t_norm, axes[step], chi_max)
        overlap = recovered.inner(states[step])
        total = total + (1.0 - overlap.abs() ** 2).mean()
    return total / N_STEPS


@torch.no_grad()
def reverse_closed_loop(
    model: LocalControlHamiltonian,
    final: BatchMPS,
    axes: list[torch.Tensor],
    chi_max: int | None,
) -> tuple[BatchMPS, int]:
    mps = final
    chi = mps.max_bond_dim()
    n_traj = mps.batch
    device = mps.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        mps = model_step(model, mps, t_norm, axes[step], chi_max)
        chi = max(chi, mps.max_bond_dim())
    return mps, chi


def mean_fidelity(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(((a.conj() * b).sum(dim=-1).abs() ** 2).mean())


@torch.no_grad()
def evaluate(
    model: LocalControlHamiltonian,
    n_qubits: int,
    target: str,
    device: torch.device,
    chi_max: int | None,
    n_eval: int,
) -> dict[str, float]:
    states, axes, psi0 = collect_forward(n_qubits, n_eval, device, target)
    loss = float(infidelity_loss(model, states, axes, chi_max).item())
    reversed_mps, chi = reverse_closed_loop(model, states[-1], axes, chi_max)
    recovered = reversed_mps.to_dense()
    recovered = recovered / (recovered.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    result = {
        "one_step_infidelity": loss,
        "same_record_closed_loop_z_fidelity": mean_fidelity(recovered, psi0),
        "closed_loop_W1_to_initial_ensemble": ensemble_w1_trace(recovered, psi0),
        "max_bond_dim": chi,
        "n_hamiltonian_params": 3 * n_qubits + 9 * max(n_qubits - 1, 0),
    }
    if n_qubits == 2 and target == "bell":
        bell = bell_singlet(n_eval, device)
        result["closed_loop_fidelity_to_bell"] = mean_fidelity(recovered, bell)
    if target == "ghz":
        result["closed_loop_fidelity_to_ghz"] = mean_fidelity(recovered, ghz_state(n_eval, n_qubits, device))
    if target == "w":
        result["closed_loop_fidelity_to_w"] = mean_fidelity(recovered, w_state(n_eval, n_qubits, device))
    return result


def parity_check(n_qubits: int, device: torch.device, chi_max: int | None) -> dict[str, float]:
    """One reverse step: TEBD comparator and 1-site TDVP vs the dense score operator."""
    from mps_backend import PAULI_XYZ

    torch.manual_seed(0)
    psi = sample_product_ensemble(n_qubits, 4, device)
    mps = mps_from_dense(psi, n_qubits).normalize()
    result: dict[str, float | None] = {"n_qubits": n_qubits}
    if n_qubits == 2:
        from train_n2_control_hamiltonian import pauli_vector as dense_n2

        result["n2_z_error"] = float((mps.pauli_vector() - dense_n2(psi)).abs().max())
    h_on = 0.1 * torch.randn(4, n_qubits, 3, device=device, dtype=torch.float64)
    h_bond = None if n_qubits == 1 else 0.1 * torch.randn(4, n_qubits - 1, 9, device=device, dtype=torch.float64)
    axes = torch.randint(0, 3, (4, n_qubits), device=device)
    xyz = PAULI_XYZ.to(device)
    expects = torch.stack([mps.expect_site(site, xyz[axes[:, site]]) for site in range(n_qubits)], dim=1)
    tebd = reverse_tebd_local(mps, h_on, h_bond, axes, GAMMA, DT, chi_max=chi_max).to_dense()
    tebd = tebd / (tebd.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    tdvp = reverse_tdvp_local(mps, h_on, h_bond, axes, GAMMA, DT, chi_max=chi_max).to_dense()
    tdvp = tdvp / (tdvp.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    dense = reverse_dense_local(psi, h_on, h_bond, axes, expects, GAMMA, DT)
    result["tebd_vs_dense_step_fidelity"] = mean_fidelity(tebd, dense)
    result["tdvp_vs_dense_step_fidelity"] = mean_fidelity(tdvp, dense)
    if n_qubits >= 2:
        h_on_g = h_on.detach().clone().requires_grad_(True)
        h_bond_g = h_bond.detach().clone().requires_grad_(True)
        recovered = reverse_tdvp_local(mps, h_on_g, h_bond_g, axes, GAMMA, DT, chi_max=chi_max)
        recovered.to_dense().real.sum().backward()
        grad = h_on_g.grad
        result["tdvp_backward_ok"] = bool(grad is not None and torch.isfinite(grad).all())
    return result


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    best, best_free = 0, -1
    for index in range(torch.cuda.device_count()):
        free, _ = torch.cuda.mem_get_info(index)
        if free > best_free:
            best_free, best = free, index
    return torch.device(f"cuda:{best}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Shared local-term control Hamiltonian")
    parser.add_argument("--n-qubits", type=int, default=2)
    parser.add_argument("--target", choices=("bell", "product", "fig2", "ghz", "w"), default="bell")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch", type=int, default=32)
    parser.add_argument("--eval-traj", type=int, default=32)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--chi-max", type=int, default=16)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--parity-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    target = "fig2" if args.n_qubits == 1 else args.target
    chi_max = None if args.n_qubits <= 2 else args.chi_max
    parity_ns = sorted({n for n in (2, 3, 4, args.n_qubits) if n >= 2})
    parity = {n: parity_check(n, device, None if n <= 2 else args.chi_max) for n in parity_ns}
    print(json.dumps({"event": "parity", "checks": parity}), flush=True)
    if args.parity_only:
        return

    model = LocalControlHamiltonian(hidden=args.hidden).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    output = LAB / "results" / f"local-h-n{args.n_qubits}-{target}-tdvp-v1"
    output.mkdir(parents=True, exist_ok=True)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "n_qubits": args.n_qubits,
        "target": target,
        "chi_max": chi_max,
        "hidden": args.hidden,
        "seed": args.seed,
        "n_hamiltonian_params": 3 * args.n_qubits + 9 * max(args.n_qubits - 1, 0),
        "parameterization": "shared-local-pauli-coefficients",
        "ensemble": "per-site-noisy-zero" if target == "product" else target,
        "parity": parity,
        "protocol": "per-step-infidelity-tdvp",
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **{k: v for k, v in env.items() if k != "parity"}}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        states, axes, _ = collect_forward(args.n_qubits, args.batch, device, target)
        optimizer.zero_grad()
        loss = infidelity_loss(model, states, axes, chi_max)
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, args.n_qubits, target, device, chi_max, args.eval_traj))
            (output / "progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n")
            torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"local_pauli_hamiltonian_n{args.n_qubits}_{target}",
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
