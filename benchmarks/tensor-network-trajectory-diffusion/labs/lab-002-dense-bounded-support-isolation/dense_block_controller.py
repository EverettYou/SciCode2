"""Dense N=3 block-controller contracts for Lab 002.

The module implements only the reviewed full/R2/R1 schedules. It reuses the
qualified Lab-001 future-record encoder and exposes block gates instead of
silently materializing a global unitary for the bounded-support controllers.
"""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path

import torch
from torch import nn


LAB = Path(__file__).resolve().parent
LAB001_PROTOTYPE = LAB.parent / "lab-001-local-controller-feasibility" / "prototype.py"
_spec = importlib.util.spec_from_file_location("lab001_controller_prototype", LAB001_PROTOTYPE)
_prototype = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_prototype)
FutureRecordEncoder = _prototype.FutureRecordEncoder


PANELS = ("coefficient", "depth-gate")
SUPPORTS = ("full", "r2", "r1")


def _schedules() -> dict[tuple[str, str], tuple[tuple[int, ...], ...]]:
    mirror_six = ((0,), (1,), (2,), (2,), (1,), (0,))
    return {
        ("coefficient", "full"): ((0, 1, 2),),
        ("coefficient", "r2"): ((0, 1), (1, 2), (0, 1), (1, 2)),
        ("coefficient", "r1"): mirror_six + mirror_six + ((0,), (1,), (2,), (1,)),
        ("depth-gate", "full"): ((0, 1, 2),) * 6,
        ("depth-gate", "r2"): ((0, 1), (1, 2)) * 3,
        ("depth-gate", "r1"): mirror_six,
    }


SCHEDULES = _schedules()


@dataclass(frozen=True)
class BlockGate:
    sites: tuple[int, ...]
    unitary: torch.Tensor


def raw_reals_for_sites(sites: tuple[int, ...]) -> int:
    dimension = 2 ** len(sites)
    return 2 * dimension * dimension


def apply_contiguous_gate(
    state: torch.Tensor, unitary: torch.Tensor, sites: tuple[int, ...]
) -> torch.Tensor:
    """Apply one batched contiguous gate to dense three-qubit states."""
    if state.shape[-1] != 8:
        raise ValueError(f"expected dense N=3 state dimension 8, got {state.shape[-1]}")
    batch_shape = state.shape[:-1]
    flat_state = state.reshape(-1, 8)
    dimension = 2 ** len(sites)
    flat_unitary = unitary.reshape(-1, dimension, dimension)
    if flat_unitary.shape[0] != flat_state.shape[0]:
        raise ValueError("state and gate batch shapes differ")
    tensor = flat_state.reshape(-1, 2, 2, 2)
    if sites == (0,):
        tensor = torch.einsum("bij,bjkl->bikl", flat_unitary, tensor)
    elif sites == (1,):
        tensor = torch.einsum("bij,bajk->baik", flat_unitary, tensor)
    elif sites == (2,):
        tensor = torch.einsum("bij,bakj->baki", flat_unitary, tensor)
    elif sites == (0, 1):
        reshaped = tensor.reshape(-1, 4, 2)
        tensor = torch.einsum("bij,bjk->bik", flat_unitary, reshaped).reshape(-1, 2, 2, 2)
    elif sites == (1, 2):
        reshaped = tensor.reshape(-1, 2, 4)
        tensor = torch.einsum("bij,baj->bai", flat_unitary, reshaped).reshape(-1, 2, 2, 2)
    elif sites == (0, 1, 2):
        return torch.einsum("bij,bj->bi", flat_unitary, flat_state).reshape(*batch_shape, 8)
    else:
        raise ValueError(f"sites must be a declared contiguous N=3 block, got {sites}")
    return tensor.reshape(*batch_shape, 8)


def apply_block_schedule(state: torch.Tensor, gates: list[BlockGate]) -> torch.Tensor:
    result = state
    for gate in gates:
        result = apply_contiguous_gate(result, gate.unitary, gate.sites)
    return result


class DenseBlockController(nn.Module):
    """Qualified encoder plus one reviewed N=3 QR block schedule."""

    def __init__(
        self,
        panel: str,
        support: str,
        *,
        d_model: int = 64,
        max_T: int = 64,
        n_layer: int = 2,
        n_head: int = 4,
    ) -> None:
        super().__init__()
        if panel not in PANELS or support not in SUPPORTS:
            raise ValueError(f"unknown panel/support: {panel}/{support}")
        self.n = 3
        self.panel = panel
        self.support = support
        self.schedule = SCHEDULES[(panel, support)]
        self.encoder = FutureRecordEncoder(
            n_qubits=3,
            max_T=max_T,
            d_model=d_model,
            n_layer=n_layer,
            n_head=n_head,
        )
        self.out_features = sum(raw_reals_for_sites(sites) for sites in self.schedule)
        self.out_proj = nn.Linear(d_model, self.out_features)

    def encode(self, m_future: torch.Tensor) -> torch.Tensor:
        return self.encoder(m_future)

    def emit_from_features(
        self, features: torch.Tensor, dtype: torch.dtype = torch.complex128
    ) -> list[BlockGate]:
        values = self.out_proj(features)
        if dtype is torch.complex128:
            values = values.double()
        elif dtype is not torch.complex64:
            raise ValueError("dtype must be complex64 or complex128")
        gates: list[BlockGate] = []
        cursor = 0
        for sites in self.schedule:
            dimension = 2 ** len(sites)
            width = 2 * dimension * dimension
            raw = values[:, cursor : cursor + width].reshape(values.shape[0], dimension * dimension, 2)
            matrix = torch.complex(raw[..., 0], raw[..., 1]).reshape(-1, dimension, dimension)
            unitary, _ = torch.linalg.qr(matrix)
            gates.append(BlockGate(sites=sites, unitary=unitary))
            cursor += width
        if cursor != self.out_features:
            raise RuntimeError("QR output cursor mismatch")
        return gates

    def emit_block_gates(
        self, m_future: torch.Tensor, dtype: torch.dtype = torch.complex128
    ) -> list[BlockGate]:
        return self.emit_from_features(self.encode(m_future), dtype=dtype)

    def apply(
        self,
        state: torch.Tensor,
        m_future: torch.Tensor,
        dtype: torch.dtype = torch.complex128,
    ) -> torch.Tensor:
        return apply_block_schedule(state, self.emit_block_gates(m_future, dtype=dtype))

    def contract_counts(self) -> dict[str, int | str]:
        head_parameters = sum(parameter.numel() for parameter in self.out_proj.parameters())
        encoder_parameters = sum(parameter.numel() for parameter in self.encoder.parameters())
        return {
            "panel": self.panel,
            "support": self.support,
            "raw_qr_reals": self.out_features,
            "gate_count": len(self.schedule),
            "sequential_depth": len(self.schedule),
            "head_parameters": head_parameters,
            "encoder_parameters": encoder_parameters,
            "total_parameters": head_parameters + encoder_parameters,
        }

