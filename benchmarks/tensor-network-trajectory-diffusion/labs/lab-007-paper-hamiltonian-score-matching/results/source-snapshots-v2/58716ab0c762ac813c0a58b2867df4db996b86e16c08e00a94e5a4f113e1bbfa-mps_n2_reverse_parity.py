"""N=2 dense-vs-MPS parity of the paper reverse operator.

The two-qubit state is an MPS with physical dimension 2. The reverse step
V = exp[(Σ_j −γ/2 δO_j² + 2i H) dt] is a 4×4 gate on the only bond.
Applying it as a two-site MPS gate must match the dense vector reverse.

A Trotter backend applies on-site backaction then the two-site Hamiltonian
gate, which is the N=2 instance of 1D TEBD/TDVP used at larger N.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import torch

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from train_n2_control_hamiltonian import (  # noqa: E402
    ControlHamiltonian,
    DIM,
    DT,
    GAMMA,
    N_STEPS,
    T_FINAL,
    collect_forward,
    pauli_vector,
    reverse_from_final,
    score_operator,
)

OUTPUT = LAB / "results" / "mps-n2-bell-reverse-parity-v1"
CHECKPOINT = LAB / "results" / "paper-fig4-n2-bell-v1" / "model.pt"


def mps_from_dense(state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """(B, 4) → two MPS tensors (B, 1, 2, χ), (B, χ, 2, 1) with χ=2."""
    batch = state.shape[0]
    reshaped = state.reshape(batch, 2, 2)
    u, s, vh = torch.linalg.svd(reshaped, full_matrices=True)
    chi = s.shape[-1]
    left = (u * s[:, None, :]).reshape(batch, 1, 2, chi)
    right = vh.reshape(batch, chi, 2, 1)
    return left, right


def mps_to_dense(left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
    return torch.einsum("baij,bjkc->baikc", left, right).reshape(left.shape[0], DIM)


def apply_two_site_gate(left: torch.Tensor, right: torch.Tensor, gate: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """gate (B, 4, 4) on a two-site MPS; restore χ=2 by SVD."""
    theta = torch.einsum("baij,bjkc->baikc", left, right).reshape(left.shape[0], 4)
    theta = torch.einsum("bij,bj->bi", gate, theta).reshape(left.shape[0], 2, 2)
    u, s, vh = torch.linalg.svd(theta, full_matrices=True)
    chi = s.shape[-1]
    new_left = (u * s[:, None, :]).reshape(left.shape[0], 1, 2, chi)
    new_right = vh.reshape(left.shape[0], chi, 2, 1)
    return new_left, new_right


@torch.no_grad()
def reverse_mps_exact(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
) -> torch.Tensor:
    left, right = mps_from_dense(final_state)
    n_traj = final_state.shape[0]
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=final_state.device, dtype=torch.float32)
        psi = mps_to_dense(left, right)
        psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        z_now = pauli_vector(psi)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        gate = score_operator(hamiltonian, observables[:, step], psi, GAMMA, DT)
        left, right = apply_two_site_gate(left, right, gate)
    psi = mps_to_dense(left, right)
    return psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


@torch.no_grad()
def reverse_mps_trotter(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
) -> torch.Tensor:
    identity = torch.eye(DIM, dtype=final_state.dtype, device=final_state.device)
    left, right = mps_from_dense(final_state)
    n_traj = final_state.shape[0]
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=final_state.device, dtype=torch.float32)
        psi = mps_to_dense(left, right)
        psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        z_now = pauli_vector(psi)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        generator_back = psi.new_zeros(n_traj, DIM, DIM)
        obs_step = observables[:, step]
        for site in range(obs_step.shape[1]):
            observable = obs_step[:, site]
            expectation = torch.einsum("bi,bij,bj->b", psi.conj(), observable, psi).real
            delta = observable - expectation[:, None, None] * identity
            generator_back = generator_back + (-0.5 * GAMMA) * (delta @ delta)
        backaction = torch.linalg.matrix_exp(generator_back * DT)
        evolve = torch.linalg.matrix_exp((2.0j * DT) * hamiltonian)
        left, right = apply_two_site_gate(left, right, evolve @ backaction)
    psi = mps_to_dense(left, right)
    return psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


def mean_fidelity(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(((a.conj() * b).sum(dim=-1).abs() ** 2).mean())


@torch.no_grad()
def main() -> None:
    device = torch.device("cpu")
    torch.manual_seed(2026)
    model = ControlHamiltonian().to(device)
    model.load_state_dict(torch.load(CHECKPOINT, map_location=device, weights_only=True))
    model.eval()
    batch = collect_forward("bell", 32, device)
    started = time.perf_counter()
    dense = reverse_from_final(model, batch["states"][:, -1], batch["observables"], None)
    mps_exact = reverse_mps_exact(model, batch["states"][:, -1], batch["observables"])
    mps_trotter = reverse_mps_trotter(model, batch["states"][:, -1], batch["observables"])
    elapsed = time.perf_counter() - started
    initial = batch["states"][:, 0]
    result = {
        "kind": "mps_n2_bell_reverse_parity",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": elapsed,
        "n_traj": 32,
        "checkpoint": str(CHECKPOINT),
        "dense_closed_loop_fidelity": mean_fidelity(dense, initial),
        "mps_exact_gate_fidelity": mean_fidelity(mps_exact, initial),
        "mps_trotter_fidelity": mean_fidelity(mps_trotter, initial),
        "dense_vs_mps_exact_state_fidelity": mean_fidelity(dense, mps_exact),
        "dense_vs_mps_trotter_state_fidelity": mean_fidelity(dense, mps_trotter),
        "max_abs_dense_minus_mps_exact": float((dense - mps_exact).abs().max()),
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
