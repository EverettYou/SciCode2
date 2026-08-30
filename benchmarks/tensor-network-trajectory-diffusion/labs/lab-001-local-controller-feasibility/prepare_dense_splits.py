"""Freeze deterministic N=1,2 trajectory splits for the Lab-001 comparison.

This qualification fixture is intentionally small. It verifies the companion
data path and establishes immutable shared inputs before any controller trains.
The final training budget is declared separately after baseline timing.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import torch


LAB = Path(__file__).resolve().parent
BENCHMARK = LAB.parents[1]
REPOSITORY = BENCHMARK.parents[1]
COMPANION = REPOSITORY / "papers" / "liu2025mqdm" / "repo"
sys.path.insert(0, str(COMPANION))

from src import ForwardDiffusion, WeakMeasurement  # noqa: E402


CONFIG = {
    "schema_version": 1,
    "purpose": "qualification fixture before dense-QR baseline timing",
    "epsilon": 0.5,
    "trajectory_length": 6,
    "counts": {"train": 256, "validation": 64, "test": 64},
    "seeds": {"train": 1701, "validation": 1702, "test": 1703},
    "n_qubits": [1, 2],
    "initial_state": "computational_zero",
    "dtype": "complex128",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def generate(n_qubits: int, count: int, seed: int) -> torch.Tensor:
    torch.manual_seed(seed)
    dimension = 2 ** n_qubits
    initial = torch.zeros(dimension, dtype=torch.complex128)
    initial[0] = 1.0
    forward = ForwardDiffusion(WeakMeasurement(CONFIG["epsilon"]))
    forward.state = initial.unsqueeze(0).expand(count, -1).clone()
    trajectories = forward.trajectory(CONFIG["trajectory_length"]).cpu()
    if trajectories.shape != (count, CONFIG["trajectory_length"], n_qubits):
        raise RuntimeError(f"unexpected trajectory shape: {trajectories.shape}")
    if not torch.all((0 <= trajectories) & (trajectories < 6)):
        raise RuntimeError("measurement token outside 0..5")
    return trajectories


def main() -> None:
    output = LAB / "artifacts" / "dense-splits-v1"
    output.mkdir(parents=True, exist_ok=True)
    (output / "config.json").write_text(
        json.dumps(CONFIG, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    files = []
    for n_qubits in CONFIG["n_qubits"]:
        for split, count in CONFIG["counts"].items():
            path = output / f"n{n_qubits}-{split}.pt"
            torch.save(generate(n_qubits, count, CONFIG["seeds"][split]), path)
            files.append({
                "path": path.name,
                "sha256": sha256(path),
                "n_qubits": n_qubits,
                "split": split,
                "count": count,
            })
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": Path(__file__).name,
        "companion_source": str(COMPANION.relative_to(REPOSITORY)),
        "torch_version": torch.__version__,
        "files": files,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
