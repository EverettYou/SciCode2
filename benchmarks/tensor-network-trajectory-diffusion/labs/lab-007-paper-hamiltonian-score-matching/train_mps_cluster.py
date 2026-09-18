"""N=3 unique cluster, MPS-TDVP reverse, same (z, H) split as the dense run.

Dense already showed: 2-local H + full z + one-step matching restores edge
checks but not bulk ZXZ; the same H with hybrid (one-step + 300-step
closed-loop overlap) restores ZXZ. This script repeats that pair with
1-site TDVP apply instead of an 8×8 matrix exponential.

z is the dense 63-vector (so the net can see ZXZ). H is the 27 two-local
coefficients, unpacked onto on-site / NN bonds and applied by
reverse_tdvp_local. MPS bond dimension is padded to 4, maximal for N=3,
so the 1-site projection is exact.
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
sys.path.insert(0, str(LAB))

from mps_backend import (  # noqa: E402
    BatchMPS,
    N2_BOND,
    mps_from_dense,
    reverse_tdvp_local,
    sample_onsite_kraus,
)
from train_n3_dense_ghz import (  # noqa: E402
    ALL_PAULI,
    CLUSTER_CHECKS,
    CLUSTER_LOGICALS,
    ControlHamiltonian,
    DIM,
    DT,
    GAMMA,
    N_PAULI,
    N_QUBITS,
    N_STEPS,
    PAULI_NAMES,
    T_FINAL,
    cluster_state,
    pauli_vector,
    subset_index,
)

OUTPUT_ROOT = LAB / "results"
XYZ = "XYZ"
CHI_EXACT = 2  # max χ on an N=3 chain; 1-site TDVP is then exact


def unpack_two_local(h_full: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Scatter a 63-dim Pauli field onto (B, 3, 3) onsite and (B, 2, 9) bonds."""
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    batch = h_full.shape[0]
    h_on = h_full.new_zeros(batch, N_QUBITS, 3)
    h_bond = h_full.new_zeros(batch, N_QUBITS - 1, 9)
    for site in range(N_QUBITS):
        for axis, letter in enumerate(XYZ):
            name = ("I" * site) + letter + ("I" * (N_QUBITS - 1 - site))
            h_on[:, site, axis] = h_full[:, lookup[name]]
    for bond in range(N_QUBITS - 1):
        for k, pair in enumerate(N2_BOND):
            name = ("I" * bond) + pair + ("I" * (N_QUBITS - 2 - bond))
            h_bond[:, bond, k] = h_full[:, lookup[name]]
    return h_on, h_bond


def mps_z(mps: BatchMPS, z_index: torch.Tensor) -> torch.Tensor:
    psi = mps.to_dense()
    psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    return pauli_vector(psi, z_index.to(psi.device))


def apply_tdvp(
    model: ControlHamiltonian,
    mps: BatchMPS,
    t_norm: torch.Tensor,
    axes: torch.Tensor,
    z_index: torch.Tensor,
) -> BatchMPS:
    z = mps_z(mps, z_index)
    h_sub = model.field(z, t_norm.to(z.dtype)).to(torch.float64)
    h_full = h_sub.new_zeros(z.shape[0], N_PAULI)
    h_full[:, model.h_index] = h_sub
    h_on, h_bond = unpack_two_local(h_full)
    return reverse_tdvp_local(mps, h_on, h_bond, axes, GAMMA, DT, chi_max=None)


@torch.no_grad()
def collect_forward(n_traj: int, device: torch.device) -> tuple[list[BatchMPS], list[torch.Tensor], torch.Tensor]:
    psi0 = cluster_state(n_traj, device)
    mps = mps_from_dense(psi0, N_QUBITS).normalize()
    states = [mps]
    axes: list[torch.Tensor] = []
    for _ in range(N_STEPS):
        step_axes = []
        for site in range(N_QUBITS):
            mps, axis, _sign = sample_onsite_kraus(mps, site, GAMMA, DT)
            step_axes.append(axis)
        axes.append(torch.stack(step_axes, dim=-1))
        mps = mps.balance()
        states.append(mps)
    return states, axes, psi0


def infidelity_loss(
    model: ControlHamiltonian,
    states: list[BatchMPS],
    axes: list[torch.Tensor],
    z_index: torch.Tensor,
) -> torch.Tensor:
    n_traj = states[0].batch
    device = states[0].device
    total = torch.zeros((), dtype=torch.float32, device=device)
    for step in range(N_STEPS):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        recovered = apply_tdvp(model, states[step + 1], t_norm, axes[step], z_index)
        overlap = recovered.inner(states[step])
        total = total + (1.0 - overlap.abs() ** 2).mean()
    return total / N_STEPS


def closed_loop_infidelity_loss(
    model: ControlHamiltonian,
    final: BatchMPS,
    axes: list[torch.Tensor],
    z_index: torch.Tensor,
    psi0: torch.Tensor,
) -> torch.Tensor:
    mps = final
    n_traj = mps.batch
    device = mps.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        mps = apply_tdvp(model, mps, t_norm, axes[step], z_index)
    recovered = mps.to_dense()
    recovered = recovered / (recovered.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    overlap = (psi0.conj() * recovered).sum(dim=-1)
    return (1.0 - overlap.abs() ** 2).mean()


@torch.no_grad()
def reverse_closed_loop(
    model: ControlHamiltonian,
    final: BatchMPS,
    axes: list[torch.Tensor],
    z_index: torch.Tensor,
) -> BatchMPS:
    mps = final
    n_traj = mps.batch
    device = mps.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        mps = apply_tdvp(model, mps, t_norm, axes[step], z_index)
    return mps


@torch.no_grad()
def evaluate(
    model: ControlHamiltonian,
    device: torch.device,
    z_index: torch.Tensor,
    n_eval: int,
) -> dict[str, float]:
    states, axes, psi0 = collect_forward(n_eval, device)
    loss = float(infidelity_loss(model, states, axes, z_index).item())
    recovered = reverse_closed_loop(model, states[-1], axes, z_index).to_dense()
    recovered = recovered / (recovered.abs() ** 2).sum(dim=-1, keepdim=True).clamp(min=1e-24).sqrt()
    overlap = (psi0.conj() * recovered).sum(dim=-1)
    fid = float((overlap.abs() ** 2).mean())
    z = pauli_vector(recovered)
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    result: dict[str, float] = {
        "one_step_infidelity": loss,
        "same_record_closed_loop_z_fidelity": fid,
        "closed_loop_fidelity_to_cluster": fid,
        "max_bond_dim": states[-1].max_bond_dim(),
    }
    for name in CLUSTER_CHECKS + CLUSTER_LOGICALS:
        values = z[:, lookup[name]]
        result[f"closed_loop_mean_{name}"] = float(values.mean())
        result[f"closed_loop_std_{name}"] = float(values.std(unbiased=False))
    result["bulk_check_ZXZ"] = result["closed_loop_mean_ZXZ"]
    result["edge_check_mean"] = 0.5 * (result["closed_loop_mean_XZI"] + result["closed_loop_mean_IZX"])
    return result


def select_device() -> torch.device:
    if not torch.cuda.is_available():
        return torch.device("cpu")
    return torch.device("cuda:0")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MPS-TDVP N=3 unique cluster")
    parser.add_argument("--loss", choices=("one_step", "closed_loop", "hybrid"), default="one_step")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--eval-traj", type=int, default=32)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--hidden", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--seed", type=int, default=2026)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    z_index = subset_index("full")
    h_index = subset_index("two_local")
    psi = cluster_state(1, device)
    z0 = pauli_vector(psi).squeeze(0)
    lookup = {name: i for i, name in enumerate(PAULI_NAMES)}
    sanity = {name: float(z0[lookup[name]]) for name in CLUSTER_CHECKS}
    print(json.dumps({"event": "sanity", **sanity, "chi_pad": CHI_EXACT}), flush=True)
    if any(abs(sanity[name] - 1.0) > 1e-8 for name in CLUSTER_CHECKS):
        raise RuntimeError(f"cluster sanity failed: {sanity}")

    tag = "zfull-htwo_local-tdvp"
    if args.loss != "one_step":
        tag = f"{tag}-{args.loss.replace('_', '')}"
    output = OUTPUT_ROOT / f"mps-n3-cluster-{tag}-v1"
    output.mkdir(parents=True, exist_ok=True)
    model = ControlHamiltonian(n_z=int(z_index.numel()), h_index=h_index, hidden=args.hidden).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "seed": args.seed,
        "n_qubits": N_QUBITS,
        "target": "cluster",
        "z_mode": "full",
        "h_mode": "two_local",
        "n_z": int(z_index.numel()),
        "n_h": int(h_index.numel()),
        "chi_pad": CHI_EXACT,
        "reverse": "1-site-tdvp",
        "loss": args.loss,
        "batch": args.batch,
        "hidden": args.hidden,
        "protocol": "mps-n3-cluster-tdvp",
        "sanity": sanity,
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
            loss = infidelity_loss(model, states, axes, z_index)
        elif args.loss == "closed_loop":
            loss = closed_loop_infidelity_loss(model, states[-1], axes, z_index, psi0)
        else:
            loss = 0.5 * infidelity_loss(model, states, axes, z_index) + 0.5 * closed_loop_infidelity_loss(
                model, states[-1], axes, z_index, psi0
            )
        loss.backward()
        optimizer.step()
        epoch_id = epoch + 1
        record: dict[str, object] = {
            "epoch": epoch_id,
            "loss": float(loss.item()),
            "elapsed_seconds": time.perf_counter() - started,
        }
        if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
            record.update(evaluate(model, device, z_index, n_eval=args.eval_traj))
            (output / "progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n")
            torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
            print(json.dumps(record), flush=True)
        elif epoch_id % 5 == 0:
            print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
        curve.append(record)

    result = {
        "kind": f"mps_n3_cluster_{tag}",
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
