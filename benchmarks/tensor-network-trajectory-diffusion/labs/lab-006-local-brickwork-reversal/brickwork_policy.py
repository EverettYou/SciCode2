"""Record-conditioned brickwork of local QR gates.

Each reverse step emits a shallow circuit of 2-qubit (or 1-qubit if N=1)
QR-parameterized gates on a 1D brickwork. The full N-qubit map is never a
dense 2^N x 2^N learned matrix. Gates are applied to dense states or to a
Quimb MPS; bond dimensions are recorded per layer.
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
from transformers import LlamaConfig, LlamaModel

from src.model import measurement_sequence_to_tokens
from src.operator import qr_to_unitary


def brickwork_bonds(n_qubits: int, layer: int) -> tuple[tuple[int, int], ...]:
    if n_qubits <= 1:
        return ((0, 0),)
    start = layer % 2
    return tuple((site, site + 1) for site in range(start, n_qubits - 1, 2))


def max_bonds_per_layer(n_qubits: int) -> int:
    if n_qubits <= 1:
        return 1
    return (n_qubits + 1) // 2


def apply_one_qubit_gate(state: torch.Tensor, gate: torch.Tensor, site: int) -> torch.Tensor:
    n_qubits = int(round(math.log2(state.shape[-1])))
    tensor = state.reshape(state.shape[:-1] + (2,) * n_qubits)
    moved = torch.movedim(tensor, -n_qubits + site, -1)
    rest = moved.shape[:-1]
    applied = torch.einsum("...ij,...j->...i", gate, moved.reshape(*rest, 2))
    restored = torch.movedim(applied.reshape(*rest, 2), -1, -n_qubits + site)
    return restored.reshape(*state.shape)


def apply_two_qubit_gate(state: torch.Tensor, gate: torch.Tensor, bond: tuple[int, int]) -> torch.Tensor:
    i, j = bond
    n_qubits = int(round(math.log2(state.shape[-1])))
    tensor = state.reshape(state.shape[:-1] + (2,) * n_qubits)
    moved = torch.movedim(tensor, (-n_qubits + i, -n_qubits + j), (-2, -1))
    rest = moved.shape[:-2]
    applied = torch.einsum("...ij,...j->...i", gate, moved.reshape(*rest, 4))
    restored = torch.movedim(applied.reshape(*rest, 2, 2), (-2, -1), (-n_qubits + i, -n_qubits + j))
    return restored.reshape(*state.shape)


class BrickworkPolicy(nn.Module):
    """Transformer encoder + local QR brickwork head."""

    def __init__(
        self,
        n_qubits: int,
        max_T: int = 64,
        n_layers: int = 4,
        d_model: int = 64,
        n_layer: int = 2,
        n_head: int = 4,
        use_sep: bool = True,
    ):
        super().__init__()
        self.n = n_qubits
        self.n_layers = n_layers
        self.use_sep = use_sep
        self.bonds_per_layer = max_bonds_per_layer(n_qubits)
        self.gate_dim = 2 if n_qubits <= 1 else 4
        self.params_per_gate = 2 * self.gate_dim * self.gate_dim
        vocab_size = 8 if use_sep else 7
        max_seq_len = max_T * (n_qubits + (1 if use_sep else 0))
        config = LlamaConfig(
            vocab_size=vocab_size,
            hidden_size=d_model,
            intermediate_size=4 * d_model,
            num_hidden_layers=n_layer,
            num_attention_heads=n_head,
            max_position_embeddings=max_seq_len,
            pad_token_id=6,
            bos_token_id=None,
            eos_token_id=None,
        )
        self.transformer = LlamaModel(config)
        self.out_proj = nn.Linear(d_model, n_layers * self.bonds_per_layer * self.params_per_gate)

    def _pooled(self, m_future: torch.Tensor) -> torch.Tensor:
        tokens, attn = measurement_sequence_to_tokens(m_future, use_sep=self.use_sep)
        hidden = self.transformer(input_ids=tokens, attention_mask=attn).last_hidden_state
        weights = attn.unsqueeze(-1).to(hidden.dtype)
        return (hidden * weights).sum(dim=1) / weights.sum(dim=1).clamp(min=1.0)

    def gates(self, m_future: torch.Tensor, dtype: torch.dtype | None = None) -> list[list[tuple[tuple[int, int], torch.Tensor]]]:
        pooled = self._pooled(m_future)
        raw = self.out_proj(pooled)
        if dtype is torch.complex128:
            raw = raw.double()
        batch = raw.shape[0]
        raw = raw.view(batch, self.n_layers, self.bonds_per_layer, self.gate_dim * self.gate_dim, 2)
        complex_a = torch.complex(raw[..., 0], raw[..., 1]).view(batch, self.n_layers, self.bonds_per_layer, self.gate_dim, self.gate_dim)
        circuit: list[list[tuple[tuple[int, int], torch.Tensor]]] = []
        for layer in range(self.n_layers):
            bonds = brickwork_bonds(self.n, layer)
            layer_gates: list[tuple[tuple[int, int], torch.Tensor]] = []
            for index, bond in enumerate(bonds):
                unitary = qr_to_unitary(complex_a[:, layer, index])
                layer_gates.append((bond, unitary))
            circuit.append(layer_gates)
        return circuit

    def apply(self, state: torch.Tensor, m_future: torch.Tensor) -> torch.Tensor:
        current = state
        for layer_gates in self.gates(m_future, dtype=state.dtype):
            for bond, unitary in layer_gates:
                if self.n <= 1:
                    current = apply_one_qubit_gate(current, unitary, 0)
                else:
                    current = apply_two_qubit_gate(current, unitary, bond)
        return current
