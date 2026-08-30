"""Freeze and validate the approved Lab-002 dense N=3 trajectory fixtures.

This stage generates data only. It contains no controller and performs no
optimizer step. Initial states, measurement records, and normalized final
states are stored together so later fidelity evaluation cannot silently assume
the Lab-001 |000> target.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
COMPANION = REPOSITORY / "papers" / "liu2025mqdm" / "repo"
OUTPUT = LAB / "artifacts" / "dense-n3-state-families-v1"
sys.path.insert(0, str(COMPANION))

from src import ForwardDiffusion, WeakMeasurement  # noqa: E402


CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "purpose": "approved Lab-002 dense N=3 state-family fixture",
    "n_qubits": 3,
    "epsilon": 0.5,
    "trajectory_length": 6,
    "dtype": "complex128",
    "counts": {"train": 256, "validation": 64, "test": 64},
    "families": ["product", "weak-local", "w3"],
    "measurement_seeds": {
        "product": {"train": 3201, "validation": 3202, "test": 3203},
        "weak-local": {"train": 3211, "validation": 3212, "test": 3213},
        "w3": {"train": 3221, "validation": 3222, "test": 3223},
    },
    "state_seeds": {
        "product": {"train": 3231, "validation": 3232, "test": 3233},
        "weak-local": {"train": 3241, "validation": 3242, "test": 3243},
    },
    "product_zero_sentinel_index": 0,
    "weak_entangler": "exp(-i * pi/12 * X_j X_{j+1})",
    "weak_active_bonds": [[0, 1], [1, 2]],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def batched_kron(vectors: list[torch.Tensor]) -> torch.Tensor:
    state = vectors[0]
    for vector in vectors[1:]:
        state = torch.einsum("bi,bj->bij", state, vector).reshape(state.shape[0], -1)
    return state


def random_product_states(count: int, seed: int, *, sentinel: bool) -> torch.Tensor:
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    theta = math.pi * torch.rand(count, 3, generator=generator, dtype=torch.float64)
    phi = 2.0 * math.pi * torch.rand(count, 3, generator=generator, dtype=torch.float64)
    vectors = []
    for qubit in range(3):
        half_theta = theta[:, qubit] / 2.0
        half_phi = phi[:, qubit] / 2.0
        vector = torch.stack(
            [
                torch.cos(half_theta) * torch.exp(-1.0j * half_phi),
                torch.sin(half_theta) * torch.exp(1.0j * half_phi),
            ],
            dim=-1,
        ).to(torch.complex128)
        vectors.append(vector)
    states = batched_kron(vectors)
    if sentinel:
        states[CONFIG["product_zero_sentinel_index"]].zero_()
        states[CONFIG["product_zero_sentinel_index"], 0] = 1.0
    return states


def two_qubit_xx_gate() -> torch.Tensor:
    identity = torch.eye(2, dtype=torch.complex128)
    pauli_x = torch.tensor([[0.0, 1.0], [1.0, 0.0]], dtype=torch.complex128)
    xx = torch.kron(pauli_x, pauli_x)
    alpha = math.pi / 12.0
    return math.cos(alpha) * torch.eye(4, dtype=torch.complex128) - 1.0j * math.sin(alpha) * xx


def weak_local_states(count: int, seed: int) -> tuple[torch.Tensor, torch.Tensor]:
    states = random_product_states(count, seed, sentinel=False)
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed + 10_000)
    active_bonds = torch.arange(count, dtype=torch.long) % 2
    active_bonds = active_bonds[torch.randperm(count, generator=generator)]
    gate = two_qubit_xx_gate()
    identity = torch.eye(2, dtype=torch.complex128)
    operators = [torch.kron(gate, identity), torch.kron(identity, gate)]
    transformed = states.clone()
    for bond_index, operator in enumerate(operators):
        mask = active_bonds == bond_index
        transformed[mask] = torch.einsum("ij,bj->bi", operator, states[mask])
    return transformed, active_bonds


def w3_states(count: int) -> torch.Tensor:
    state = torch.zeros(8, dtype=torch.complex128)
    state[[1, 2, 4]] = 1.0 / math.sqrt(3.0)
    return state.unsqueeze(0).expand(count, -1).clone()


def initial_states(family: str, split: str, count: int) -> tuple[torch.Tensor, torch.Tensor]:
    active_bonds = torch.full((count,), -1, dtype=torch.long)
    if family == "product":
        seed = CONFIG["state_seeds"][family][split]
        return random_product_states(count, seed, sentinel=True), active_bonds
    if family == "weak-local":
        seed = CONFIG["state_seeds"][family][split]
        return weak_local_states(count, seed)
    if family == "w3":
        return w3_states(count), active_bonds
    raise ValueError(f"unknown family: {family}")


def generate_fixture(family: str, split: str, count: int) -> dict[str, Any]:
    states, active_bonds = initial_states(family, split, count)
    torch.manual_seed(CONFIG["measurement_seeds"][family][split])
    forward = ForwardDiffusion(WeakMeasurement(CONFIG["epsilon"]))
    forward.state = states.clone()
    trajectories = forward.trajectory(CONFIG["trajectory_length"]).cpu()
    final_states = forward.state.cpu()
    if final_states is None:
        raise RuntimeError("companion ForwardDiffusion did not retain final states")
    sentinel_mask = torch.zeros(count, dtype=torch.bool)
    if family == "product":
        sentinel_mask[CONFIG["product_zero_sentinel_index"]] = True
    return {
        "schema_version": CONFIG["schema_version"],
        "family": family,
        "split": split,
        "initial_states": states.cpu(),
        "trajectories": trajectories,
        "final_states": final_states,
        "active_bonds": active_bonds,
        "sentinel_mask": sentinel_mask,
    }


def schmidt_values(states: torch.Tensor, cut: int) -> torch.Tensor:
    left = 2**cut
    right = 2 ** (CONFIG["n_qubits"] - cut)
    return torch.linalg.svdvals(states.reshape(states.shape[0], left, right))


def validate_fixture(payload: dict[str, Any], expected_family: str, expected_split: str) -> dict[str, Any]:
    count = CONFIG["counts"][expected_split]
    initial = payload["initial_states"]
    trajectories = payload["trajectories"]
    final = payload["final_states"]
    active_bonds = payload["active_bonds"]
    sentinel_mask = payload["sentinel_mask"]
    expected_trajectory_shape = (count, CONFIG["trajectory_length"], CONFIG["n_qubits"])
    if payload["family"] != expected_family or payload["split"] != expected_split:
        raise RuntimeError("fixture metadata mismatch")
    if initial.shape != (count, 8) or final.shape != (count, 8):
        raise RuntimeError(f"unexpected state shape for {expected_family}/{expected_split}")
    if trajectories.shape != expected_trajectory_shape:
        raise RuntimeError(f"unexpected trajectory shape: {trajectories.shape}")
    if initial.dtype != torch.complex128 or final.dtype != torch.complex128:
        raise RuntimeError("state dtype must be complex128")
    if not torch.isfinite(initial).all() or not torch.isfinite(final).all():
        raise RuntimeError("nonfinite state value")
    if not torch.all((0 <= trajectories) & (trajectories < 6)):
        raise RuntimeError("measurement token outside 0..5")
    initial_norm_error = float(((initial.abs() ** 2).sum(dim=-1) - 1.0).abs().max())
    final_norm_error = float(((final.abs() ** 2).sum(dim=-1) - 1.0).abs().max())
    if initial_norm_error > 1e-10 or final_norm_error > 1e-10:
        raise RuntimeError("state normalization tolerance exceeded")

    invariant: dict[str, Any] = {}
    if expected_family == "product":
        second_left = schmidt_values(initial, 1)[:, 1]
        second_right = schmidt_values(initial, 2)[:, 1]
        max_product_schmidt_tail = float(torch.maximum(second_left, second_right).max())
        if max_product_schmidt_tail > 1e-10:
            raise RuntimeError("product family violates rank-one cut invariant")
        if int(sentinel_mask.sum()) != 1 or not torch.equal(
            initial[sentinel_mask][0], w3_states(1)[0].new_tensor([1, 0, 0, 0, 0, 0, 0, 0])
        ):
            raise RuntimeError("product-zero sentinel mismatch")
        invariant["max_product_schmidt_tail"] = max_product_schmidt_tail
        invariant["sentinel_count"] = int(sentinel_mask.sum())
    elif expected_family == "weak-local":
        if int((active_bonds == 0).sum()) != count // 2 or int((active_bonds == 1).sum()) != count // 2:
            raise RuntimeError("weak-local active bonds are not exactly balanced")
        spectator_tails = torch.empty(count, dtype=torch.float64)
        entangled_tails = torch.empty(count, dtype=torch.float64)
        left_values = schmidt_values(initial, 1)
        right_values = schmidt_values(initial, 2)
        bond01 = active_bonds == 0
        bond12 = active_bonds == 1
        spectator_tails[bond01] = right_values[bond01, 1]
        spectator_tails[bond12] = left_values[bond12, 1]
        entangled_tails[bond01] = left_values[bond01, 1]
        entangled_tails[bond12] = right_values[bond12, 1]
        max_spectator_tail = float(spectator_tails.max())
        median_entangled_tail = float(entangled_tails.median())
        if max_spectator_tail > 1e-10 or median_entangled_tail <= 1e-3:
            raise RuntimeError("weak-local Schmidt invariant failed")
        invariant["bond_counts"] = {
            "01": int(bond01.sum()),
            "12": int(bond12.sum()),
        }
        invariant["max_spectator_schmidt_tail"] = max_spectator_tail
        invariant["median_entangled_schmidt_tail"] = median_entangled_tail
    elif expected_family == "w3":
        reference = w3_states(count)
        max_w3_error = float((initial - reference).abs().max())
        min_second_schmidt = float(
            torch.minimum(schmidt_values(initial, 1)[:, 1], schmidt_values(initial, 2)[:, 1]).min()
        )
        if max_w3_error > 1e-12 or min_second_schmidt <= 0.5:
            raise RuntimeError("W3 family invariant failed")
        invariant["max_w3_error"] = max_w3_error
        invariant["min_second_schmidt"] = min_second_schmidt
    else:
        raise ValueError(expected_family)

    return {
        "initial_norm_max_error": initial_norm_error,
        "final_norm_max_error": final_norm_error,
        "token_min": int(trajectories.min()),
        "token_max": int(trajectories.max()),
        **invariant,
    }


def load_and_validate(output: Path) -> dict[str, Any]:
    config_path = output / "config.json"
    manifest_path = output / "manifest.json"
    if not config_path.is_file() or not manifest_path.is_file():
        raise RuntimeError("fixture config or manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["config_sha256"] != sha256(config_path):
        raise RuntimeError("config hash mismatch")
    validations = []
    for entry in manifest["files"]:
        path = output / entry["path"]
        if sha256(path) != entry["sha256"]:
            raise RuntimeError(f"fixture hash mismatch: {path.name}")
        payload = torch.load(path, map_location="cpu", weights_only=False)
        result = validate_fixture(payload, entry["family"], entry["split"])
        validations.append({"path": path.name, **result})
    return {
        "fixture": output.name,
        "files_checked": len(validations),
        "validations": validations,
    }


def generate(output: Path) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise RuntimeError(f"refusing to overwrite immutable fixture: {output}")
    output.mkdir(parents=True, exist_ok=True)
    config_path = output / "config.json"
    config_path.write_text(json.dumps(CONFIG, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    files = []
    for family in CONFIG["families"]:
        for split, count in CONFIG["counts"].items():
            payload = generate_fixture(family, split, count)
            validate_fixture(payload, family, split)
            path = output / f"{family}-{split}.pt"
            torch.save(payload, path)
            files.append(
                {
                    "path": path.name,
                    "sha256": sha256(path),
                    "family": family,
                    "split": split,
                    "count": count,
                    "measurement_seed": CONFIG["measurement_seeds"][family][split],
                    "state_seed": CONFIG.get("state_seeds", {}).get(family, {}).get(split),
                }
            )
    manifest = {
        "schema_version": CONFIG["schema_version"],
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "companion_source": str(COMPANION.relative_to(REPOSITORY)),
        "torch_version": torch.__version__,
        "config_sha256": sha256(config_path),
        "files": files,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return load_and_validate(output)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="validate the immutable fixture without writing")
    args = parser.parse_args()
    result = load_and_validate(OUTPUT) if args.check else generate(OUTPUT)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
