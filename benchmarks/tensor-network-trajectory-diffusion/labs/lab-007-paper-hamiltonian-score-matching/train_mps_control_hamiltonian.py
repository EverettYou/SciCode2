"""Train the paper control Hamiltonian on the MPS loop.

Loop (N=1 and N=2):
  1. Forward: on-site weak Kraus applied as 2×2 MPS gates.
  2. z_t: local Pauli expectations contracted on the MPS (not a dense Bloch).
  3. h_θ(z, t): the same MLP as the dense trainer.
  4. Reverse: TEBD of on-site backaction + on-site H + nearest-neighbor H,
     or the combined 2^N score operator applied as an MPS gate (parity).
  5. Loss: mean infidelity from the MPS overlap ⟨ψ_{t−dt}|V|ψ_t⟩.

At N=2 the Hamiltonian support is already nearest-neighbor (all 15 Paulis
are 1-site or 2-site), so TEBD is exact up to the backaction/H Trotter split.
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
    N2_PAULI_NAMES,
    BatchMPS,
    mps_from_dense,
    reverse_tebd_step,
    sample_onsite_kraus,
)
from train_n1_control_hamiltonian import (  # noqa: E402
    ControlHamiltonian as ControlH1,
    bloch as dense_bloch,
    sample_initial_ensemble as sample_n1,
)
from train_n2_control_hamiltonian import (  # noqa: E402
    ControlHamiltonian as ControlH2,
    bell_singlet,
    pauli_vector as dense_pauli_n2,
    sample_initial as sample_n2,
)

GAMMA = 1.0
T_FINAL = 3.0
DT = 0.01
N_STEPS = int(round(T_FINAL / DT))


@torch.no_grad()
def collect_forward_mps(
    n_qubits: int,
    n_traj: int,
    device: torch.device,
    target: str,
) -> tuple[list[BatchMPS], list[torch.Tensor], torch.Tensor]:
    if n_qubits == 1:
        psi0 = sample_n1(n_traj, device)
    else:
        psi0 = sample_n2(target, n_traj, device)
    mps = mps_from_dense(psi0, n_qubits).normalize()
    states = [mps]
    axes: list[torch.Tensor] = []
    for _ in range(N_STEPS):
        if n_qubits == 1:
            mps, axis, _sign = sample_onsite_kraus(mps, 0, GAMMA, DT)
            axes.append(axis)
        else:
            step_axes = []
            for site in range(n_qubits):
                mps, axis, _sign = sample_onsite_kraus(mps, site, GAMMA, DT)
                step_axes.append(axis)
            axes.append(torch.stack(step_axes, dim=-1))
        states.append(mps)
    return states, axes, psi0


def infidelity_loss(
    model: nn.Module,
    states: list[BatchMPS],
    axes: list[torch.Tensor],
    combined: bool,
) -> torch.Tensor:
    n_traj = states[0].batch
    device = states[0].device
    total = torch.zeros((), dtype=torch.float32, device=device)
    for step in range(N_STEPS):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        z = states[step + 1].pauli_vector()
        h = model.field(z, t_norm).to(torch.float64)
        recovered = reverse_tebd_step(states[step + 1], h, axes[step], GAMMA, DT, combined=combined)
        overlap = recovered.inner(states[step])
        total = total + (1.0 - overlap.abs() ** 2).mean()
    return total / N_STEPS


@torch.no_grad()
def reverse_closed_loop(
    model: nn.Module,
    final: BatchMPS,
    axes: list[torch.Tensor],
    combined: bool,
    store_every: int = 30,
) -> tuple[BatchMPS, list[tuple[int, BatchMPS]]]:
    mps = final
    snapshots = [(N_STEPS, mps)]
    n_traj = mps.batch
    device = mps.device
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n_traj, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        z = mps.pauli_vector()
        h = model.field(z, t_norm).to(torch.float64)
        mps = reverse_tebd_step(mps, h, axes[step], GAMMA, DT, combined=combined)
        if step % store_every == 0 or step == 0:
            snapshots.append((step, mps))
    return mps, snapshots


def mean_fidelity_dense(a: torch.Tensor, b: torch.Tensor) -> float:
    return float(((a.conj() * b).sum(dim=-1).abs() ** 2).mean())


def w1_to_target(states: torch.Tensor, target: torch.Tensor) -> float:
    fid = (states.conj() * target).sum(dim=-1).abs() ** 2
    return float((1.0 - fid.clamp(0, 1)).sqrt().mean())


def ensemble_w1(states_a: torch.Tensor, states_b: torch.Tensor) -> float:
    overlap_sq = torch.einsum("ik,jk->ij", states_a.conj(), states_b).abs() ** 2
    cost = (1.0 - overlap_sq.clamp(0.0, 1.0)).sqrt().cpu().numpy()
    try:
        from scipy.optimize import linear_sum_assignment
    except ImportError:
        return float(cost.diagonal().mean())
    row, col = linear_sum_assignment(cost)
    return float(cost[row, col].mean())


@torch.no_grad()
def evaluate(
    model: nn.Module,
    n_qubits: int,
    target: str,
    device: torch.device,
    combined: bool,
    n_eval: int = 64,
) -> dict[str, float]:
    states, axes, psi0 = collect_forward_mps(n_qubits, n_eval, device, target)
    loss = float(infidelity_loss(model, states, axes, combined).item())
    reversed_mps, snapshots = reverse_closed_loop(model, states[-1], axes, combined)
    recovered = reversed_mps.to_dense()
    recovered = recovered / (recovered.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    fid = mean_fidelity_dense(recovered, psi0)
    curve = []
    for step, snap in reversed(snapshots):
        psi = snap.to_dense()
        psi = psi / (psi.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        t = step * DT
        if n_qubits == 1:
            z = dense_bloch(psi).mean(dim=0)
            curve.append(
                {
                    "t": t,
                    "W1_to_initial": ensemble_w1(psi, psi0),
                    "mean_Z": float(z[2]),
                }
            )
        else:
            bell = bell_singlet(n_eval, device)
            entry = {
                "t": t,
                "W1_to_initial": ensemble_w1(psi, psi0),
                "mean_fidelity_to_initial": mean_fidelity_dense(psi, psi0),
            }
            if target == "bell":
                entry["W1_to_bell"] = w1_to_target(psi, bell)
                entry["fidelity_to_bell"] = mean_fidelity_dense(psi, bell)
            curve.append(entry)
    result = {
        "one_step_infidelity": loss,
        "same_record_closed_loop_z_fidelity": fid,
        "closed_loop_W1_to_initial_ensemble": ensemble_w1(recovered, psi0),
        "w1_curve": curve,
    }
    if n_qubits == 1:
        z = dense_bloch(recovered).mean(dim=0)
        result.update(
            {
                "closed_loop_mean_bloch_x": float(z[0]),
                "closed_loop_mean_bloch_y": float(z[1]),
                "closed_loop_mean_bloch_z": float(z[2]),
            }
        )
    elif target == "bell":
        bell = bell_singlet(n_eval, device)
        result["closed_loop_fidelity_to_bell"] = mean_fidelity_dense(recovered, bell)
        result["closed_loop_W1_trace_to_bell"] = w1_to_target(recovered, bell)
        named = dict(zip(N2_PAULI_NAMES, dense_pauli_n2(recovered).mean(dim=0).tolist()))
        result.update({f"closed_loop_mean_{k}": float(named[k]) for k in ("XX", "YY", "ZZ")})
    return result


def self_test(device: torch.device) -> dict[str, float]:
    """MPS local z and combined reverse must match dense at N=1,2."""
    torch.manual_seed(0)
    psi1 = sample_n1(8, device)
    mps1 = mps_from_dense(psi1, 1).normalize()
    z_err_1 = float((mps1.pauli_vector() - dense_bloch(psi1)).abs().max())
    psi2 = bell_singlet(8, device)
    # mix a little so all Paulis are nonzero after a random 2-site gate
    noise = 0.05 * (
        torch.randn(8, 4, device=device) + 1j * torch.randn(8, 4, device=device)
    ).to(torch.complex128)
    psi2 = psi2 + noise
    psi2 = psi2 / (psi2.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    mps2 = mps_from_dense(psi2, 2).normalize()
    z_err_2 = float((mps2.pauli_vector() - dense_pauli_n2(psi2)).abs().max())
    dens_from_mps = mps2.to_dense()
    dens_from_mps = dens_from_mps / (dens_from_mps.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
    rec_fid = mean_fidelity_dense(dens_from_mps, psi2)
    return {
        "n1_max_z_error": z_err_1,
        "n2_max_z_error": z_err_2,
        "n2_roundtrip_fidelity": rec_fid,
    }


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
    parser = argparse.ArgumentParser(description="MPS-loop control-Hamiltonian trainer")
    parser.add_argument("--n-qubits", type=int, choices=(1, 2), default=1)
    parser.add_argument("--target", choices=("fig2", "bell", "heisenberg"), default="fig2")
    parser.add_argument("--apply", choices=("tebd", "combined"), default="tebd")
    parser.add_argument("--epochs", type=int, default=80)
    parser.add_argument("--batch", type=int, default=64)
    parser.add_argument("--eval-traj", type=int, default=64)
    parser.add_argument("--eval-every", type=int, default=10)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--self-test-only", action="store_true")
    parser.add_argument("--init-dense", type=str, default="", help="optional dense checkpoint to start from")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = select_device()
    if device.type == "cuda":
        torch.cuda.set_device(device)
    torch.manual_seed(args.seed)
    checks = self_test(device)
    print(json.dumps({"event": "self_test", **checks}), flush=True)
    if max(checks["n1_max_z_error"], checks["n2_max_z_error"]) > 1e-10:
        raise SystemExit(f"MPS local-z parity failed: {checks}")
    if args.self_test_only:
        return

    n_qubits = args.n_qubits
    target = "bell" if n_qubits == 2 and args.target == "fig2" else args.target
    combined = args.apply == "combined"
    model: nn.Module = ControlH1().to(device) if n_qubits == 1 else ControlH2().to(device)
    if args.init_dense:
        model.load_state_dict(torch.load(args.init_dense, map_location=device, weights_only=True))
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    output_name = f"mps-n{n_qubits}-{target}-{args.apply}-v1"
    if args.epochs == 0 and args.init_dense:
        output_name = f"mps-n{n_qubits}-{target}-{args.apply}-dense-weights-v1"
    output = LAB / "results" / output_name
    output.mkdir(parents=True, exist_ok=True)
    env = {
        "torch_version": torch.__version__,
        "device": str(device),
        "gpu_name": torch.cuda.get_device_name(device) if device.type == "cuda" else None,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "n_qubits": n_qubits,
        "target": target,
        "apply": args.apply,
        "seed": args.seed,
        "gamma": GAMMA,
        "T": T_FINAL,
        "dt": DT,
        "n_steps": N_STEPS,
        "batch": args.batch,
        "protocol": "mps-local-z-tebd-control-hamiltonian",
        "self_test": checks,
    }
    started = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (output / "environment.json").write_text(json.dumps({"created_at": started_at, **env}, indent=2) + "\n")
    print(json.dumps({"event": "start", **env}), flush=True)

    curve: list[dict[str, object]] = []
    if args.epochs == 0:
        record = {"epoch": 0, "elapsed_seconds": 0.0}
        record.update(evaluate(model, n_qubits, target, device, combined, n_eval=args.eval_traj))
        curve.append(record)
        printable = {k: v for k, v in record.items() if k != "w1_curve"}
        print(json.dumps(printable), flush=True)
        (output / "progress.json").write_text(json.dumps({"epoch": 0, "latest": record, "config": env}) + "\n")
    else:
        for epoch in range(args.epochs):
            states, axes, _psi0 = collect_forward_mps(n_qubits, args.batch, device, target)
            optimizer.zero_grad()
            loss = infidelity_loss(model, states, axes, combined)
            loss.backward()
            optimizer.step()
            epoch_id = epoch + 1
            record: dict[str, object] = {
                "epoch": epoch_id,
                "loss": float(loss.item()),
                "elapsed_seconds": time.perf_counter() - started,
            }
            if epoch_id % args.eval_every == 0 or epoch == 0 or epoch_id == args.epochs:
                record.update(evaluate(model, n_qubits, target, device, combined, n_eval=args.eval_traj))
                (output / "progress.json").write_text(json.dumps({"epoch": epoch_id, "latest": record, "config": env}) + "\n")
                torch.save(model.state_dict(), output / f"model-epoch{epoch_id:04d}.pt")
                printable = {k: v for k, v in record.items() if k != "w1_curve"}
                print(json.dumps(printable), flush=True)
            elif epoch_id % 5 == 0:
                print(json.dumps({"epoch": epoch_id, "loss": record["loss"]}), flush=True)
            curve.append(record)

    result = {
        "kind": f"mps_control_hamiltonian_n{n_qubits}_{target}_{args.apply}",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "started_at": started_at,
        "elapsed_seconds": time.perf_counter() - started,
        "environment": env,
        "loss_curve": curve,
        "final": curve[-1],
    }
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    torch.save(model.state_dict(), output / "model.pt")
    print(json.dumps({"event": "done", "final": {k: v for k, v in curve[-1].items() if k != "w1_curve"}}), flush=True)


if __name__ == "__main__":
    main()
