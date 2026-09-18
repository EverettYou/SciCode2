"""Oracle diagnosis: can any U with U K_t K_{t-1} ~ c I reverse N=1 trajectories?

This does not train a policy. It uses the exact least-squares/polar unitary for
each recorded Kraus pair and reports both the Frobenius residual and the
same-record reversal fidelity under two indexing conventions.
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

from src import ForwardDiffusion, WeakMeasurement  # noqa: E402
from src.operator import qr_to_unitary  # noqa: E402

N, EPSILON, T, N_TRAJ = 1, 0.8, 30, 512


def polar_inverse(matrix: torch.Tensor) -> torch.Tensor:
    """Unitary closest to mapping matrix -> I, i.e. polar factor of matrix^{-1} via QR of matrix.H."""
    return qr_to_unitary(matrix.mH)


def collect_states(wm: WeakMeasurement, n_traj: int, steps: int, initial: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    forward = ForwardDiffusion(wm)
    states = [initial.unsqueeze(0).expand(n_traj, -1).clone()]
    forward.state = states[0].clone()
    records = []
    for _ in range(steps):
        records.append(forward.step())
        states.append(forward.state.clone())
    return torch.stack(states, dim=1), torch.stack(records, dim=1)


def apply_unitaries(states_final: torch.Tensor, unitaries: torch.Tensor, times: list[int]) -> torch.Tensor:
    state = states_final.clone()
    for t in times:
        state = torch.einsum("...ij,...j->...i", unitaries[:, t], state)
    return state


def main() -> None:
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(9101)
    wm = WeakMeasurement(EPSILON)
    initial = torch.tensor([1.0, 0.0], dtype=torch.complex128, device=device)
    states, records = collect_states(wm, N_TRAJ, T, initial)
    kraus = wm.operator(records)
    dim = kraus.shape[-1]
    identity = torch.eye(dim, dtype=kraus.dtype, device=kraus.device)
    products = kraus[:, 1:] @ kraus[:, :-1]
    unitaries = polar_inverse(products)
    # products and unitaries are indexed by t=1..T-1 as [:, t-1]
    padded = torch.zeros(N_TRAJ, T, dim, dim, dtype=unitaries.dtype, device=device)
    padded[:, 1:] = unitaries
    residual = unitaries @ products - (unitaries @ products).diagonal(dim1=-2, dim2=-1).sum(-1).div(dim)[..., None, None] * identity
    frobenius = float((residual.abs() ** 2).mean())

    consecutive = list(range(T - 1, 0, -1))  # companion trajectory_reversal
    skip2 = list(range(T - 1, 0, -2))
    fid_consecutive = float((apply_unitaries(states[:, -1], padded, consecutive)[:, 0].abs() ** 2).mean())
    fid_skip2 = float((apply_unitaries(states[:, -1], padded, skip2)[:, 0].abs() ** 2).mean())

    # Direct two-step infidelity of the oracle map: |<psi_{t-1}| U_t |psi_{t+1}>|^2
    recovered = torch.einsum("btij,btj->bti", unitaries, states[:, 2:])
    overlap = (states[:, :-2].conj() * recovered).sum(dim=-1)
    two_step = float((overlap.abs() ** 2).mean())

    result = {
        "kind": "n1_oracle_kraus_pair_reversal",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "device": str(device),
        "config": {"n": N, "epsilon": EPSILON, "T": T, "n_traj": N_TRAJ},
        "mean_frobenius_residual": frobenius,
        "companion_trajectory_reversal_indexing_fidelity_to_zero": fid_consecutive,
        "skip2_indexing_fidelity_to_zero": fid_skip2,
        "mean_two_step_state_fidelity_U_on_psi_tplus1_to_psi_tminus1": two_step,
        "note": "Oracle U is the polar factor of (K_t K_{t-1}).H. Two-step state fidelity is the quantity the paper-style infidelity loss would maximize.",
    }
    output = LAB / "results" / "strict-repository-reproduction-v1" / "n1-oracle-reversal.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
