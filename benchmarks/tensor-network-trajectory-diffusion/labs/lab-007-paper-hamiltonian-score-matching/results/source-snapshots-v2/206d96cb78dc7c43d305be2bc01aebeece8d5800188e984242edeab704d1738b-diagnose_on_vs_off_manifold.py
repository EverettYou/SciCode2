"""On-manifold vs off-manifold diagnostics for N=3 cluster / GHZ.

Runs on CPU (8x8). Does not claim a new training method; only measures
what the already-trained paper-loss models actually do.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import torch

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from train_n3_dense_ghz import (  # noqa: E402
    ALL_PAULI,
    ControlHamiltonian,
    DIM,
    DT,
    GAMMA,
    N_PAULI,
    N_STEPS,
    PAULI_NAMES,
    T_FINAL,
    collect_forward,
    pauli_vector,
    score_operator,
    subset_index,
)

LOOKUP = {name: i for i, name in enumerate(PAULI_NAMES)}
OUT = LAB / "results" / "diagnostics-on-off-manifold-v1"
CLUSTER_OBS = ("XZI", "ZXZ", "IZX")
GHZ_OBS = ("ZZI", "IZZ", "XXX")


def load_model(path: Path, h_mode: str, device: torch.device) -> ControlHamiltonian:
    z_index = subset_index("full")
    h_index = subset_index(h_mode)
    model = ControlHamiltonian(int(z_index.numel()), h_index, hidden=128).to(device)
    model.load_state_dict(torch.load(path, map_location=device, weights_only=True))
    model.eval()
    return model


def ham_coeffs(model: ControlHamiltonian | None, z: torch.Tensor, t_norm: torch.Tensor) -> torch.Tensor:
    if model is None:
        return z.new_zeros(z.shape[0], N_PAULI)
    h_sub = model.field(z, t_norm).to(torch.float64)
    h_full = h_sub.new_zeros(z.shape[0], N_PAULI)
    h_full[:, model.h_index] = h_sub
    return h_full


def apply_reverse_step(
    model: ControlHamiltonian | None,
    state: torch.Tensor,
    z_for_h: torch.Tensor,
    observables: torch.Tensor,
    t_norm: torch.Tensor,
) -> torch.Tensor:
    if model is None:
        ham = state.new_zeros(state.shape[0], DIM, DIM)
    else:
        ham = model.hamiltonian(z_for_h, t_norm.to(z_for_h.dtype))
    operator = score_operator(ham, observables, state, GAMMA, DT)
    nxt = torch.einsum("bij,bj->bi", operator, state)
    return nxt / (nxt.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


def means(state: torch.Tensor, names: tuple[str, ...]) -> dict[str, float]:
    z = pauli_vector(state)
    return {name: float(z[:, LOOKUP[name]].mean()) for name in names}


@torch.no_grad()
def teacher_forced_one_step(model, batch, steps: list[int], names: tuple[str, ...]) -> dict[str, float]:
    states, z, obs = batch["states"], batch["z"], batch["observables"]
    n = states.shape[0]
    infids = []
    h_rms = []
    corr = {name: [] for name in names}
    for step in steps:
        t_norm = torch.full((n, 1), (step + 1) * DT / T_FINAL, device=states.device, dtype=z.dtype)
        rec = apply_reverse_step(model, states[:, step + 1], z[:, step + 1], obs[:, step], t_norm)
        true = states[:, step]
        ov = (true.conj() * rec).sum(dim=-1)
        infids.append(1.0 - ov.abs() ** 2)
        coeffs = ham_coeffs(model, z[:, step + 1], t_norm)
        h_rms.append(coeffs.pow(2).mean(dim=-1).sqrt())
        z_rec, z_true = pauli_vector(rec), pauli_vector(true)
        for name in names:
            corr[name].append((z_rec[:, LOOKUP[name]] - z_true[:, LOOKUP[name]]).abs())
    out = {
        "infidelity": float(torch.cat(infids).mean()),
        "h_rms": float(torch.cat(h_rms).mean()) if model is not None else 0.0,
    }
    for name in names:
        out[f"abs_d_{name}"] = float(torch.cat(corr[name]).mean())
    return out


@torch.no_grad()
def closed_loop_trace(model, batch, names: tuple[str, ...], every: int = 20) -> dict[str, object]:
    states, obs = batch["states"], batch["observables"]
    n = states.shape[0]
    device = states.device
    state = states[:, -1].clone()
    z_true = pauli_vector(states.reshape(-1, DIM)).reshape(n, N_STEPS + 1, N_PAULI)
    times = []
    fid_to_true = []
    z_l2 = []
    h_rms = []
    series = {name: [] for name in names}
    true_series = {name: [] for name in names}
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        z_now = pauli_vector(state)
        coeffs = ham_coeffs(model, z_now, t_norm.to(z_now.dtype))
        state = apply_reverse_step(model, state, z_now, obs[:, step], t_norm)
        if step % every == 0 or step == 0:
            t = step * DT
            true = states[:, step]
            ov = (true.conj() * state).sum(dim=-1)
            times.append(t)
            fid_to_true.append(float(ov.abs().pow(2).mean()))
            z_l2.append(float((z_now - z_true[:, step + 1]).pow(2).mean().sqrt()))
            h_rms.append(float(coeffs.pow(2).mean().sqrt()) if model is not None else 0.0)
            z_s = pauli_vector(state)
            for name in names:
                series[name].append(float(z_s[:, LOOKUP[name]].mean()))
                true_series[name].append(float(z_true[:, step, LOOKUP[name]].mean()))
    initial = states[:, 0]
    ov0 = (initial.conj() * state).sum(dim=-1)
    return {
        "times": times,
        "fid_to_true_at_t": fid_to_true,
        "z_l2_to_true": z_l2,
        "h_rms": h_rms,
        "closed_loop": series,
        "true_forward": true_series,
        "same_record_F": float(ov0.abs().pow(2).mean()),
        "final_means": means(state, names),
    }


@torch.no_grad()
def h_rms_on_true_vs_closed_loop(model, batch) -> dict[str, float]:
    """||h|| on teacher z versus ||h|| along the model's own reverse."""
    states, z, obs = batch["states"], batch["z"], batch["observables"]
    n = states.shape[0]
    device = states.device
    on_true = []
    off = []
    state = states[:, -1].clone()
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full((n, 1), (step + 1) * DT / T_FINAL, device=device, dtype=torch.float32)
        h_true = ham_coeffs(model, z[:, step + 1], t_norm.to(z.dtype))
        z_now = pauli_vector(state)
        h_now = ham_coeffs(model, z_now, t_norm.to(z_now.dtype))
        on_true.append(h_true.pow(2).mean(dim=-1).sqrt())
        off.append(h_now.pow(2).mean(dim=-1).sqrt())
        state = apply_reverse_step(model, state, z_now, obs[:, step], t_norm)
    return {
        "h_rms_on_true_z": float(torch.cat(on_true).mean()),
        "h_rms_on_closed_loop_z": float(torch.cat(off).mean()),
        "ratio_off_over_on": float(torch.cat(off).mean() / (torch.cat(on_true).mean() + 1e-12)),
    }


def main() -> None:
    device = torch.device("cpu")
    torch.manual_seed(2026)
    OUT.mkdir(parents=True, exist_ok=True)
    z_full = subset_index("full")
    n_traj = 32
    batch_c = collect_forward(n_traj, device, z_full, "cluster")
    batch_g = collect_forward(n_traj, device, z_full, "ghz")
    models = {
        "cluster_onestep": (
            load_model(LAB / "results/dense-n3-cluster-zfull-htwo_local-v1/model.pt", "two_local", device),
            batch_c,
            CLUSTER_OBS,
        ),
        "cluster_hybrid": (
            load_model(LAB / "results/dense-n3-cluster-zfull-htwo_local-hybrid-v1/model.pt", "two_local", device),
            batch_c,
            CLUSTER_OBS,
        ),
        "ghz_A_onestep": (
            load_model(LAB / "results/dense-n3-ghz-zfull-htwo_local-v1/model.pt", "two_local", device),
            batch_g,
            GHZ_OBS,
        ),
        "ghz_C_fullH": (
            load_model(LAB / "results/dense-n3-ghz-zfull-hfull-v1/model.pt", "full", device),
            batch_g,
            GHZ_OBS,
        ),
        "ghz_hybrid": (
            load_model(LAB / "results/dense-n3-ghz-zfull-htwo_local-hybrid-v1/model.pt", "two_local", device),
            batch_g,
            GHZ_OBS,
        ),
    }

    report: dict[str, object] = {"n_traj": n_traj, "device": str(device), "models": {}}
    steps_all = list(range(0, N_STEPS, 10))

    print(json.dumps({"event": "start", "n_traj": n_traj}), flush=True)
    h0_tf_c = teacher_forced_one_step(None, batch_c, steps_all, CLUSTER_OBS)
    h0_cl_c = closed_loop_trace(None, batch_c, CLUSTER_OBS)
    h0_tf_g = teacher_forced_one_step(None, batch_g, steps_all, GHZ_OBS)
    h0_cl_g = closed_loop_trace(None, batch_g, GHZ_OBS)
    report["H0_cluster"] = {"teacher_forced": h0_tf_c, "closed_loop": {k: h0_cl_c[k] for k in ("same_record_F", "final_means")}}
    report["H0_ghz"] = {"teacher_forced": h0_tf_g, "closed_loop": {k: h0_cl_g[k] for k in ("same_record_F", "final_means")}}
    print(json.dumps({"event": "H0_cluster", **h0_tf_c, "closed_F": h0_cl_c["same_record_F"], **h0_cl_c["final_means"]}), flush=True)
    print(json.dumps({"event": "H0_ghz", **h0_tf_g, "closed_F": h0_cl_g["same_record_F"], **h0_cl_g["final_means"]}), flush=True)

    for name, (model, batch, obs_names) in models.items():
        tf = teacher_forced_one_step(model, batch, steps_all, obs_names)
        cl = closed_loop_trace(model, batch, obs_names)
        mag = h_rms_on_true_vs_closed_loop(model, batch)
        entry = {
            "teacher_forced": tf,
            "h_magnitude": mag,
            "closed_loop_F": cl["same_record_F"],
            "closed_loop_final": cl["final_means"],
            "trace": {
                "times": cl["times"],
                "fid_to_true_at_t": cl["fid_to_true_at_t"],
                "z_l2_to_true": cl["z_l2_to_true"],
                "h_rms": cl["h_rms"],
                "closed_loop": cl["closed_loop"],
                "true_forward": cl["true_forward"],
            },
        }
        report["models"][name] = entry
        print(
            json.dumps(
                {
                    "event": name,
                    "tf_infid": tf["infidelity"],
                    "tf_h_rms": tf["h_rms"],
                    **{k: tf[k] for k in tf if k.startswith("abs_d_")},
                    **mag,
                    "closed_F": cl["same_record_F"],
                    **cl["final_means"],
                }
            ),
            flush=True,
        )

    (OUT / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"event": "done", "path": str(OUT / "summary.json")}), flush=True)


if __name__ == "__main__":
    main()
