"""Dense-vs-MPS parity for the paper reverse step V = exp[(−γ/2 δO² + 2i H) dt].

At N=1 the control Hamiltonian is on-site, so the reverse operator is a 2×2
gate. Representing the state as an MPS and applying that gate must match the
dense vector to numerical precision (algorithm correctness, not scaling).

A second backend splits the generator by first-order Trotter
    exp(−γ dt/2 δO²) then exp(2i H dt)
which is the form that generalizes to 1D TDVP/TEBD of a local H(z,t)
(Wu & Nys, PRX Quantum 2026, DOI 10.1103/tggc-8fjx). Trotter error is
measured against the dense matrix exponential, not treated as parity.
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

from train_n1_control_hamiltonian import (  # noqa: E402
    ControlHamiltonian,
    DT,
    GAMMA,
    N_STEPS,
    T_FINAL,
    bloch,
    collect_forward,
    reverse_from_final,
    score_operator,
)

OUTPUT = LAB / "results" / "mps-n1-reverse-parity-v1"
CHECKPOINT = LAB / "results" / "paper-fig2-n1-v1" / "model.pt"


def mps_from_qubit(state: torch.Tensor) -> torch.Tensor:
    """(B, 2) dense one-qubit state → MPS tensor (B, 1, 2, 1)."""
    return state[:, None, :, None]


def mps_to_qubit(tensor: torch.Tensor) -> torch.Tensor:
    return tensor[:, 0, :, 0]


def apply_local_gate(tensor: torch.Tensor, gate: torch.Tensor) -> torch.Tensor:
    """gate (B, 2, 2) on a one-site MPS tensor (B, χ_left, 2, χ_right)."""
    return torch.einsum("bij,bkjl->bkil", gate, tensor)


def reverse_mps_exact_gate(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
) -> torch.Tensor:
    state = final_state.clone()
    n_traj = state.shape[0]
    tensor = mps_from_qubit(state)
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=state.device, dtype=torch.float32)
        psi = mps_to_qubit(tensor)
        psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        z_now = bloch(psi)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        gate = score_operator(hamiltonian, observables[:, step], psi, GAMMA, DT)
        tensor = apply_local_gate(tensor, gate)
        psi = mps_to_qubit(tensor)
        tensor = mps_from_qubit(psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt())
    return mps_to_qubit(tensor)


def reverse_mps_trotter(
    model: ControlHamiltonian,
    final_state: torch.Tensor,
    observables: torch.Tensor,
) -> torch.Tensor:
    """Local backaction then Hamiltonian gate: the TDVP/TEBD split."""
    state = final_state.clone()
    n_traj = state.shape[0]
    identity = torch.eye(2, dtype=state.dtype, device=state.device)
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=state.device, dtype=torch.float32)
        z_now = bloch(state)
        hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        observable = observables[:, step]
        expectation = torch.einsum("bi,bij,bj->b", state.conj(), observable, state).real
        delta = observable - expectation[:, None, None] * identity
        backaction = torch.linalg.matrix_exp((-0.5 * GAMMA * DT) * (delta @ delta))
        evolve = torch.linalg.matrix_exp((2.0j * DT) * hamiltonian)
        gate = evolve @ backaction
        state = torch.einsum("bij,bj->bi", gate, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    return state


@torch.no_grad()
def main() -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.set_device(0)
    torch.manual_seed(2026)
    model = ControlHamiltonian().to(device)
    model.load_state_dict(torch.load(CHECKPOINT, map_location=device, weights_only=True))
    model.eval()
    batch = collect_forward(64, device)
    started = time.perf_counter()
    dense = reverse_from_final(model, batch["states"][:, -1], batch["observables"], None)
    mps_exact = reverse_mps_exact_gate(model, batch["states"][:, -1], batch["observables"])
    mps_trotter = reverse_mps_trotter(model, batch["states"][:, -1], batch["observables"])
    elapsed = time.perf_counter() - started
    initial = batch["states"][:, 0]

    def mean_fidelity(a: torch.Tensor, b: torch.Tensor) -> float:
        return float(((a.conj() * b).sum(dim=-1).abs() ** 2).mean())

    result = {
        "kind": "mps_n1_reverse_parity",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "elapsed_seconds": elapsed,
        "n_traj": 64,
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
