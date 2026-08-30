"""Stage-2 shape and accounting check for the Lab-002 controller contracts.

This check performs zero optimizer steps and does not run the Stage-3 Quimb or
finite-difference numerical gates.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import torch

from dense_block_controller import DenseBlockController, PANELS, SUPPORTS


LAB = Path(__file__).resolve().parent
EXPECTED = {
    ("coefficient", "full"): (128, 1, 8_320),
    ("coefficient", "r2"): (128, 4, 8_320),
    ("coefficient", "r1"): (128, 16, 8_320),
    ("depth-gate", "full"): (768, 6, 49_920),
    ("depth-gate", "r2"): (192, 6, 12_480),
    ("depth-gate", "r1"): (48, 6, 3_120),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    torch.manual_seed(3401)
    torch.set_num_threads(1)
    features = torch.randn(3, 64)
    states = torch.randn(3, 8, dtype=torch.complex128)
    states = states / torch.linalg.vector_norm(states, dim=-1, keepdim=True)
    records = []
    encoder_parameters = None
    for panel in PANELS:
        for support in SUPPORTS:
            controller = DenseBlockController(panel, support)
            counts = controller.contract_counts()
            expected_reals, expected_gates, expected_head_parameters = EXPECTED[(panel, support)]
            assert counts["raw_qr_reals"] == expected_reals, counts
            assert counts["gate_count"] == expected_gates, counts
            assert counts["sequential_depth"] == expected_gates, counts
            assert counts["head_parameters"] == expected_head_parameters, counts
            if encoder_parameters is None:
                encoder_parameters = counts["encoder_parameters"]
            assert counts["encoder_parameters"] == encoder_parameters, counts
            gates = controller.emit_from_features(features, dtype=torch.complex128)
            assert len(gates) == expected_gates
            assert all(gate.unitary.shape[0] == states.shape[0] for gate in gates)
            output = controller.apply(state=states, m_future=torch.zeros(3, 1, 3, dtype=torch.long))
            assert output.shape == states.shape
            assert torch.isfinite(output).all()
            records.append(
                {
                    **counts,
                    "schedule": [list(gate.sites) for gate in gates],
                    "output_shape": list(output.shape),
                }
            )
    coefficient_heads = {
        record["head_parameters"] for record in records if record["panel"] == "coefficient"
    }
    assert coefficient_heads == {8_320}
    depth_gate_counts = {
        record["gate_count"] for record in records if record["panel"] == "depth-gate"
    }
    assert depth_gate_counts == {6}
    result = {
        "schema_version": 1,
        "kind": "lab002_interface_contract_check",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "seed": 3401,
        "optimizer_steps": 0,
        "numerical_gate_status": "not-run",
        "controller_source_sha256": sha256(LAB / "dense_block_controller.py"),
        "records": records,
    }
    output = LAB / "results" / "interface-contract-v1"
    output.mkdir(parents=True, exist_ok=True)
    path = output / "summary.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
