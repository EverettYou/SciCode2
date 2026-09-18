"""Ancilla-locked cluster on A_L-1-2-3-A_R, MPS-TDVP, 2-local H.

Five-qubit Choi/EPR purification of the N=3 bulk-ZXZ code. Unique pure
state; Haar code-space is not the target. H is 2-local on the extended
chain (51 coefficients). z is every Pauli with support span ≤ 2, so all
five checks are visible. Reverse is 1-site TDVP; χ=4 is exact on 5 qubits.

Metrics are the five checks separately, not a single F. Default loss is
hybrid (one-step + 300-step closed-loop overlap with this ψ0).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import torch
import torch.nn as nn

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from mps_backend import (  # noqa: E402
    BatchMPS,
    N2_BOND,
    PAULI_XYZ,
    embed_operator,
    mps_from_dense,
    reverse_dense_local,
    reverse_tdvp_local,
    sample_onsite_kraus,
)

OUTPUT_ROOT = LAB / "results"
GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))
N_SITES = 5
DIM = 32
CHI_EXACT = 4
LABELS = "IXYZ"
XYZ = "XYZ"

# Sites: 0=A_L, 1, 2, 3, 4=A_R
CHECKS = (
    ("ZAZ1", "ZZIII"),  # 2-local left lock  ⟨Z_AL Z1⟩
    ("XAX1Z2", "XXZII"),  # 3-local left lock ⟨X_AL X1 Z2⟩
    ("ZXZ", "IZXZI"),  # 3-local bulk      ⟨Z1 X2 Z3⟩
    ("Z3ZAR", "IIIZZ"),  # 2-local right lock ⟨Z3 Z_AR⟩
    ("Z2X3XAR", "IIZXX"),  # 3-local right lock ⟨Z2 X3 X_AR⟩
)


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


def _five_qubit_paulis() -> tuple[torch.Tensor, list[str], list[str]]:
    one = _pauli_matrices()
    ops, names, kinds = [], [], []
    for indices in product(range(4), repeat=N_SITES):
        if all(i == 0 for i in indices):
            continue
        op = one[indices[0]]
        for idx in indices[1:]:
            op = torch.kron(op, one[idx])
        name = "".join(LABELS[i] for i in indices)
        sites = [s for s, i in enumerate(indices) if i != 0]
        span = sites[-1] - sites[0]
        if len(sites) == 1:
            kind = "one_body"
        elif len(sites) == 2 and sites[1] - sites[0] == 1:
            kind = "nn_two_body"
        elif span <= 2:
            kind = "radius2"
        else:
            kind = "longer"
        ops.append(op)
        names.append(name)
        kinds.append(kind)
    return torch.stack(ops, dim=0), names, kinds


ALL_PAULI, PAULI_NAMES, PAULI_KINDS = _five_qubit_paulis()
Z_KINDS = frozenset({"one_body", "nn_two_body", "radius2"})
H_KINDS = frozenset({"one_body", "nn_two_body"})
Z_INDEX = torch.tensor([i for i, k in enumerate(PAULI_KINDS) if k in Z_KINDS])
H_INDEX = torch.tensor([i for i, k in enumerate(PAULI_KINDS) if k in H_KINDS])
LOOKUP = {name: i for i, name in enumerate(PAULI_NAMES)}
CHECK_INDEX = torch.tensor([LOOKUP[name] for _, name in CHECKS])


def pauli_vector(state: torch.Tensor, index: torch.Tensor | None = None) -> torch.Tensor:
    basis = ALL_PAULI.to(device=state.device, dtype=state.dtype)
    if index is not None:
        basis = basis[index.to(device=state.device)]
    return torch.einsum("bi,kij,bj->bk", state.conj(), basis, state).real


def ancilla_locked_state(n_traj: int, device: torch.device) -> torch.Tensor:
    """Unique +1 eigenstate of the five generators, via successive projectors."""
    psi = torch.zeros(DIM, dtype=torch.complex128, device=device)
    psi[0] = 1.0
    for _, name in CHECKS:
        gen = ALL_PAULI[LOOKUP[name]].to(device=device)
        psi = 0.5 * (psi + torch.matmul(gen, psi))
    nrm = psi.norm()
    if float(nrm) < 1e-12:
        raise RuntimeError("ancilla-locked projector annihilated |0⟩")
    psi = psi / nrm
    return psi.unsqueeze(0).expand(n_traj, -1).contiguous()


class TwoLocalControl(nn.Module):
    """h_θ(z_radius2, t) → 51 two-local coefficients, unpacked to on-site / NN."""

    def __init__(self, n_z: int, hidden: int = 128):
        super().__init__()
        self.n_h = int(H_INDEX.numel())
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

    def unpack(self, h_sub: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h_full = h_sub.new_zeros(h_sub.shape[0], len(PAULI_NAMES))
        h_full[:, H_INDEX.to(h_sub.device)] = h_sub
        batch = h_sub.shape[0]
        h_on = h_sub.new_zeros(batch, N_SITES, 3)
        h_bond = h_sub.new_zeros(batch, N_SITES - 1, 9)
        for site in range(N_SITES):
            for axis, letter in enumerate(XYZ):
                name = ("I" * site) + letter + ("I" * (N_SITES - 1 - site))
                h_on[:, site, axis] = h_full[:, LOOKUP[name]]
        for bond in range(N_SITES - 1):
            for k, pair in enumerate(N2_BOND):
                name = ("I" * bond) + pair + ("I" * (N_SITES - 2 - bond))
                h_bond[:, bond, k] = h_full[:, LOOKUP[name]]
        return h_on, h_bond


def mps_z(mps: BatchMPS) -> torch.Tensor:
    psi = mps.to_dense()
    psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    return pauli_vector(psi, Z_INDEX)


def apply_tdvp(model: TwoLocalControl, mps: BatchMPS, t_norm: torch.Tensor, axes: torch.Tensor) -> BatchMPS:
    z = mps_z(mps)
    h_sub = model.field(z, t_norm.to(z.dtype)).to(torch.float64)
    h_on, h_bond = model.unpack(h_sub)
    return reverse_tdvp_local(mps, h_on, h_bond, axes, GAMMA, DT, chi_max=None)


@torch.no_grad()
def collect_forward(n_traj: int, device: torch.device) -> tuple[list[BatchMPS], list[torch.Tensor], torch.Tensor]:
    psi0 = ancilla_locked_state(n_traj, device)
    mps = mps_from_dense(psi0, N_SITES).normalize()
    states = [mps]
    axes: list[torch.Tensor] = []
    for _ in range(N_STEPS):
        step_axes = []
        for site in range(N_SITES):
            mps, axis, _sign = sample_onsite_kraus(mps, site, GAMMA, DT)
            step_axes.append(axis)
        axes.append(torch.stack(step_axes, dim=-1))
        mps = mps.balance()
        states.append(mps)
    return states, axes, psi0


def infidelity_loss(
    model: TwoLocalControl,
    states: list[BatchMPS],
    axes: list[torch.Tensor],
) -> torch.Tensor:
    n_traj = states[0].batch
    device = states[0].device
    total = torch.zeros((), dtype=torch.float32, device=device)
    for step in range(N_STEPS):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        psi = states[step + 1].to_dense()
        psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
        recovered = apply_dense(model, psi, t_norm, axes[step])
        target = states[step].to_dense()
        target = target / (target.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
        overlap = (target.conj() * recovered).sum(dim=-1)
        total = total + (1.0 - overlap.abs() ** 2).mean()
    return total / N_STEPS


def dense_site_expects(psi: torch.Tensor, axes: torch.Tensor) -> torch.Tensor:
    xyz = PAULI_XYZ.to(device=psi.device, dtype=psi.dtype)
    cols = []
    for site in range(N_SITES):
        op = embed_operator(xyz[axes[:, site]], site, N_SITES)
        cols.append(torch.einsum("bi,bij,bj->b", psi.conj(), op, psi).real)
    return torch.stack(cols, dim=1)


def apply_dense(model: TwoLocalControl, psi: torch.Tensor, t_norm: torch.Tensor, axes: torch.Tensor) -> torch.Tensor:
    """Exact 32×32 reverse of the same 2-local H. χ=4 TDVP lives on this manifold."""
    z = pauli_vector(psi, Z_INDEX)
    h_sub = model.field(z, t_norm.to(z.dtype)).to(torch.float64)
    h_on, h_bond = model.unpack(h_sub)
    expects = dense_site_expects(psi, axes)
    return reverse_dense_local(psi, h_on, h_bond, axes, expects, GAMMA, DT)


def closed_loop_infidelity_loss(
    model: TwoLocalControl,
    final: BatchMPS,
    axes: list[torch.Tensor],
    psi0: torch.Tensor,
) -> torch.Tensor:
    # 300-step BPTT through MPS QR explodes. At N=5, χ=4 is exact, so the
    # dense 32×32 score operator is the same 2-local reverse with stable grads.
    psi = final.to_dense()
    psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    n_traj = psi.shape[0]
    device = psi.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        psi = apply_dense(model, psi, t_norm, axes[step])
    overlap = (psi0.conj() * psi).sum(dim=-1)
    return (1.0 - overlap.abs() ** 2).mean()


@torch.no_grad()
def reverse_closed_loop(model: TwoLocalControl, final: BatchMPS, axes: list[torch.Tensor]) -> BatchMPS:
    mps = final
    n_traj = mps.batch
    device = mps.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        mps = apply_tdvp(model, mps, t_norm, axes[step])
    return mps


@torch.no_grad()
def evaluate(model: TwoLocalControl, device: torch.device, n_eval: int) -> dict[str, float]:
    states, axes, psi0 = collect_forward(n_eval, device)
    loss = float(infidelity_loss(model, states, axes).item())
    recovered = reverse_closed_loop(model, states[-1], axes).to_dense()
    recovered = recovered / (recovered.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    overlap = (psi0.conj() * recovered).sum(dim=-1)
    z = pauli_vector(recovered)
    result: dict[str, float] = {
        "one_step_infidelity": loss,
        "same_record_closed_loop_fidelity": float((overlap.abs() ** 2).mean()),
        "max_bond_dim": float(states[-1].max_bond_dim()),
    }
    two_local_vals = []
    three_local_vals = []
    for label, name in CHECKS:
        values = z[:, LOOKUP[name]]
        result[f"mean_{label}"] = float(values.mean())
        result[f"std_{label}"] = float(values.std(unbiased=False))
        if label in ("ZAZ1", "Z3ZAR"):
            two_local_vals.append(result[f"mean_{label}"])
        else:
            three_local_vals.append(result[f"mean_{label}"])
    result["two_local_lock_mean"] = float(sum(two_local_vals) / len(two_local_vals))
    result["three_local_check_mean"] = float(sum(three_local_vals) / len(three_local_vals))
    return result


def select_device(force_cpu: bool) -> torch.device:
    if force_cpu:
        return torch.device("cpu")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required; pass --cpu only as an explicit override")
    cvd = os.environ.get("CUDA_VISIBLE_DEVICES")
    if cvd is not None and cvd != "":
        return torch.device("cuda:0")
    if torch.cuda.device_count() >= 2:
        return torch.device("cuda:1")
    return torch.device("cuda:0")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MPS-TDVP ancilla-locked cluster N=3+2")
    parser.add_argument("--loss", choices=("one_step", "closed_loop", "hybrid"), default="hybrid")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--eval-traj", type=int, default=8)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--sanity-only", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device(args.cpu)
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    psi = ancilla_locked_state(1, device)
    z0 = pauli_vector(psi).squeeze(0)
    sanity = {label: float(z0[LOOKUP[name]]) for label, name in CHECKS}
    sanity["n_z"] = int(Z_INDEX.numel())
    sanity["n_h"] = int(H_INDEX.numel())
    sanity["chi_exact"] = CHI_EXACT
    print(json.dumps({"event": "sanity", **sanity}), flush=True)
    if any(abs(sanity[label] - 1.0) > 1e-8 for label, _ in CHECKS):
        raise RuntimeError(f"ancilla-locked sanity failed: {sanity}")
    if args.sanity_only:
        return

    tag = "zradius2-htwo_local-tdvp"
    if args.loss != "one_step":
        tag = f"{tag}-{args.loss.replace('_', '')}"
    output = OUTPUT_ROOT / f"mps-n5-ancilla-cluster-{tag}-v1"
    output.mkdir(parents=True, exist_ok=True)
    model = TwoLocalControl(n_z=int(Z_INDEX.numel()), hidden=args.hidden).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "seed": args.seed,
        "n_qubits": N_SITES,
        "target": "ancilla_locked_cluster",
        "z_mode": "radius2",
        "h_mode": "two_local",
        "n_z": int(Z_INDEX.numel()),
        "n_h": int(H_INDEX.numel()),
        "chi_pad": CHI_EXACT,
        "reverse": "1-site-tdvp",
        "closed_loop_apply": "dense-32-exact-chi4",
        "one_step_apply": "dense-32-exact-chi4",
        "eval_reverse": "1-site-tdvp",
        "loss": args.loss,
        "batch": args.batch,
        "hidden": args.hidden,
        "protocol": "mps-n5-ancilla-cluster-tdvp",
        "checks": [label for label, _ in CHECKS],
        "sanity": {k: v for k, v in sanity.items() if k not in ("n_z", "n_h", "chi_exact")},
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    for epoch in range(args.epochs):
        states, axes, psi0 = collect_forward(args.batch, device)
        optimizer.zero_grad()
        if args.loss == "one_step":
            loss = infidelity_loss(model, states, axes)
        elif args.loss == "closed_loop":
            loss = closed_loop_infidelity_loss(model, states[-1], axes, psi0)
        else:
            loss = 0.5 * infidelity_loss(model, states, axes) + 0.5 * closed_loop_infidelity_loss(
                model, states[-1], axes, psi0
            )
        loss.backward()
        grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        if not torch.isfinite(loss) or not torch.isfinite(grad_norm):
            optimizer.zero_grad(set_to_none=True)
            print(json.dumps({"epoch": epoch + 1, "event": "skip_nonfinite", "loss": float(loss.detach())}), flush=True)
            continue
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, device, n_eval=args.eval_traj))
            (output / "progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n")
            torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"mps_n5_ancilla_cluster_{tag}",
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
