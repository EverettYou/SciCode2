"""Record ⟨ZXZ⟩, ⟨XZI⟩, ⟨ZII⟩ along forward T∈[0,3] and closed-loop reverse.

Starts from the unique open-boundary cluster and from a Z1-polarized copy
(I+Z1)|cluster⟩ so the edge magnetization is visible. Reverse uses the
learned H_θ(z_t, t) on the *current* state (closed-loop), not teacher-forced
forward z. Writes a compact JSON the canvas embeds.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))

from train_n3_dense_ghz import (  # noqa: E402
    ALL_PAULI,
    DIM,
    DT,
    GAMMA,
    N_STEPS,
    PAULI_NAMES,
    T_FINAL,
    ControlHamiltonian,
    cluster_state,
    pauli_vector,
    sample_forward_step,
    score_operator,
    subset_index,
)

OBS = ("ZXZ", "XZI", "IZX", "ZII", "IIZ")
STRIDE = 10  # 0.10 in t; 31 samples from 0 to 3
OUTPUT = LAB / "results" / "cluster-stabilizer-curves-v1.json"

MODELS = [
    {
        "id": "two_local_onestep",
        "label": "2-local H, one-step",
        "h_mode": "two_local",
        "path": LAB / "results" / "dense-n3-cluster-zfull-htwo_local-v1" / "model.pt",
    },
    {
        "id": "two_local_hybrid",
        "label": "2-local H, closed-loop",
        "h_mode": "two_local",
        "path": LAB / "results" / "dense-n3-cluster-zfull-htwo_local-hybrid-v1" / "model.pt",
    },
    {
        "id": "three_local_onestep",
        "label": "3-local H, one-step",
        "h_mode": "full",
        "path": LAB / "results" / "dense-n3-cluster-zfull-hfull-v1" / "model.pt",
    },
    {
        "id": "three_local_hybrid",
        "label": "3-local H, closed-loop",
        "h_mode": "full",
        "path": LAB / "results" / "dense-n3-cluster-zfull-hfull-hybrid-v1" / "model.pt",
    },
]


def lookup() -> dict[str, int]:
    return {name: i for i, name in enumerate(PAULI_NAMES)}


def polarized_cluster_state(n_traj: int, device: torch.device) -> torch.Tensor:
    """(I + Z1)|cluster⟩ / norm. Makes ⟨ZII⟩ = +1; XZI anticommutes so it drops."""
    psi = cluster_state(1, device)[0]
    z1 = ALL_PAULI[lookup()["ZII"]].to(device=device, dtype=psi.dtype)
    psi = psi + torch.matmul(z1, psi)
    psi = psi / psi.norm()
    return psi.unsqueeze(0).expand(n_traj, -1).contiguous()


def collect_forward_from(initial: torch.Tensor) -> dict[str, torch.Tensor]:
    state = initial.clone()
    states = [state]
    observables = []
    for _ in range(N_STEPS):
        state, obs = sample_forward_step(state, GAMMA, DT)
        states.append(state)
        observables.append(obs)
    stacked = torch.stack(states, dim=1)
    return {
        "states": stacked,
        "observables": torch.stack(observables, dim=1),
    }


@torch.no_grad()
def named_curve(states: torch.Tensor) -> dict[str, list[float]]:
    """states (B, T+1, 8) → mean Pauli vs time, downsampled."""
    n_traj, n_t, _ = states.shape
    z = pauli_vector(states.reshape(-1, DIM)).reshape(n_traj, n_t, -1)
    idx = lookup()
    times = list(range(0, n_t, STRIDE))
    if times[-1] != n_t - 1:
        times.append(n_t - 1)
    out: dict[str, list[float]] = {}
    for name in OBS:
        out[name] = [round(float(z[:, t, idx[name]].mean()), 4) for t in times]
    return out


@torch.no_grad()
def reverse_path(
    model: ControlHamiltonian | None,
    final_state: torch.Tensor,
    observables: torch.Tensor,
    z_index: torch.Tensor,
) -> torch.Tensor:
    state = final_state.clone()
    n_traj = state.shape[0]
    z_index = z_index.to(state.device)
    path = [state.clone()]
    zero_h = torch.zeros(n_traj, DIM, DIM, dtype=state.dtype, device=state.device)
    for step in range(N_STEPS - 1, -1, -1):
        t_norm = torch.full(
            (n_traj, 1),
            (step + 1) * DT / T_FINAL,
            device=state.device,
            dtype=torch.float32,
        )
        if model is None:
            hamiltonian = zero_h
        else:
            z_now = pauli_vector(state, z_index)
            hamiltonian = model.hamiltonian(z_now, t_norm.to(z_now.dtype))
        operator = score_operator(hamiltonian, observables[:, step], state, GAMMA, DT)
        state = torch.einsum("bij,bj->bi", operator, state)
        state = state / (state.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
        path.append(state.clone())
    # path[0] = t=T … path[-1] = t=0. Flip to match forward time.
    return torch.stack(path[::-1], dim=1)


def load_model(spec: dict, device: torch.device) -> ControlHamiltonian:
    z_index = subset_index("full")
    h_index = subset_index(spec["h_mode"])
    model = ControlHamiltonian(n_z=int(z_index.numel()), h_index=h_index, hidden=128).to(device)
    state = torch.load(spec["path"], map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


def initial_means(psi: torch.Tensor) -> dict[str, float]:
    z = pauli_vector(psi[:1])
    idx = lookup()
    return {name: float(z[0, idx[name]]) for name in OBS}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-traj", type=int, default=32)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    device = torch.device("cpu")
    torch.manual_seed(args.seed)
    z_index = subset_index("full")

    unique = cluster_state(args.n_traj, device)
    polarized = polarized_cluster_state(args.n_traj, device)
    print(
        json.dumps(
            {
                "event": "initials",
                "unique": initial_means(unique),
                "polarized": initial_means(polarized),
            }
        ),
        flush=True,
    )

    ensembles = {
        "unique_cluster": collect_forward_from(unique),
        "polarized_Z1": collect_forward_from(polarized),
    }

    t_labels = [f"{k * STRIDE * DT:.1f}" for k in range((N_STEPS // STRIDE) + 1)]
    if t_labels[-1] != f"{T_FINAL:.1f}":
        t_labels.append(f"{T_FINAL:.1f}")

    payload: dict = {
        "protocol": {
            "T": T_FINAL,
            "dt": DT,
            "gamma": GAMMA,
            "n_steps": N_STEPS,
            "n_traj": args.n_traj,
            "seed": args.seed,
            "stride": STRIDE,
            "t": t_labels,
            "note": (
                "Forward: paper unraveling, local Pauli jumps. "
                "Reverse: closed-loop score operator with learned H(z_now, t). "
                "polarized_Z1 = (I+Z1)|cluster⟩ / norm."
            ),
        },
        "forward": {},
        "reverse": {},
        "models_loaded": [],
        "models_missing": [],
    }

    for name, batch in ensembles.items():
        payload["forward"][name] = named_curve(batch["states"])

    reverse_specs = [{"id": "H0", "label": "H = 0", "model": None}]
    for spec in MODELS:
        if not spec["path"].exists():
            payload["models_missing"].append({"id": spec["id"], "path": str(spec["path"])})
            print(json.dumps({"event": "missing", "id": spec["id"]}), flush=True)
            continue
        model = load_model(spec, device)
        reverse_specs.append({"id": spec["id"], "label": spec["label"], "model": model})
        payload["models_loaded"].append(spec["id"])
        print(json.dumps({"event": "loaded", "id": spec["id"]}), flush=True)

    for ens_name, batch in ensembles.items():
        payload["reverse"][ens_name] = {}
        for spec in reverse_specs:
            print(json.dumps({"event": "reverse", "ensemble": ens_name, "id": spec["id"]}), flush=True)
            path = reverse_path(spec["model"], batch["states"][:, -1], batch["observables"], z_index)
            payload["reverse"][ens_name][spec["id"]] = {
                "label": spec["label"],
                **named_curve(path),
            }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({"event": "done", "out": str(args.out), "loaded": payload["models_loaded"], "missing": payload["models_missing"]}), flush=True)


if __name__ == "__main__":
    main()
