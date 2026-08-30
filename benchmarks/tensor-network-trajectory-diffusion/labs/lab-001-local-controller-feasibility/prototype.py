"""Dense Phase-1 controller heads for the Liu et al. companion interface.

This prototype intentionally supports only one and two qubits. It keeps the
companion contract ``forward(m_future, dtype) -> U`` so its loss and trajectory
code can be reused without modification. Quimb parity belongs in the pinned
Lab-001 environment, not in this dependency-light interface smoke test.
"""

from __future__ import annotations

import itertools
import math

import torch
from torch import nn
from transformers import LlamaConfig, LlamaModel


PAD_TOKEN_ID = 6
SEP_TOKEN_ID = 7


def measurement_sequence_to_tokens(
    m_future: torch.Tensor, use_sep: bool = True
) -> tuple[torch.Tensor, torch.Tensor]:
    """Match the companion model's separator-token convention."""
    *batch_dims, length, n_qubits = m_future.shape
    batch = int(math.prod(batch_dims)) if batch_dims else 1
    flat = m_future.reshape(batch, length, n_qubits)
    if use_sep:
        tokens = torch.empty(batch, length, n_qubits + 1, dtype=torch.long, device=m_future.device)
        tokens[..., :n_qubits] = flat
        tokens[..., n_qubits] = SEP_TOKEN_ID
        tokens = tokens.reshape(batch, length * (n_qubits + 1))
    else:
        tokens = flat.reshape(batch, length * n_qubits)
    return tokens, torch.ones_like(tokens, dtype=torch.long)


class FutureRecordEncoder(nn.Module):
    """The companion future-record transformer with the output head removed."""

    def __init__(self, n_qubits: int, max_T: int = 64, d_model: int = 64,
                 n_layer: int = 2, n_head: int = 4, use_sep: bool = True,
                 intermediate_size: int | None = None):
        super().__init__()
        self.n_qubits = n_qubits
        self.d_model = d_model
        self.use_sep = use_sep
        if intermediate_size is None:
            intermediate_size = 4 * d_model
        config = LlamaConfig(
            vocab_size=8 if use_sep else 7,
            hidden_size=d_model,
            intermediate_size=intermediate_size,
            num_hidden_layers=n_layer,
            num_attention_heads=n_head,
            max_position_embeddings=max_T * (n_qubits + (1 if use_sep else 0)),
            pad_token_id=PAD_TOKEN_ID,
            bos_token_id=None,
            eos_token_id=None,
        )
        self.transformer = LlamaModel(config)

    def forward(self, m_future: torch.Tensor,
                attention_mask: torch.Tensor | None = None) -> torch.Tensor:
        if m_future.shape[-1] != self.n_qubits:
            raise ValueError(f"expected {self.n_qubits} qubits, got {m_future.shape[-1]}")
        tokens, base_mask = measurement_sequence_to_tokens(m_future, use_sep=self.use_sep)
        mask = base_mask if attention_mask is None else base_mask & attention_mask.to(base_mask.dtype)
        hidden = self.transformer(input_ids=tokens, attention_mask=mask).last_hidden_state
        weights = mask.unsqueeze(-1).to(hidden.dtype)
        return (hidden * weights).sum(dim=1) / weights.sum(dim=1).clamp(min=1.0)


class DenseQRHead(nn.Module):
    """The companion dense complex-matrix plus QR output head, isolated verbatim."""

    def __init__(self, d_model: int, n_qubits: int):
        super().__init__()
        self.dim = 2 ** n_qubits
        self.out_proj = nn.Linear(d_model, 2 * self.dim * self.dim)

    def forward(self, features: torch.Tensor, dtype: torch.dtype | None = None) -> torch.Tensor:
        values = self.out_proj(features)
        if dtype is torch.complex128:
            values = values.double()
        matrix = values.view(values.shape[0], self.dim * self.dim, 2)
        complex_matrix = torch.complex(matrix[..., 0], matrix[..., 1]).view(
            values.shape[0], self.dim, self.dim
        )
        q, _ = torch.linalg.qr(complex_matrix)
        return q


class RefactoredQRPolicy(nn.Module):
    """Companion policy factored at the encoder/head seam for exact regression tests."""

    def __init__(self, n_qubits: int, max_T: int = 64, use_sep: bool = True,
                 d_model: int = 64, n_layer: int = 2, n_head: int = 4,
                 intermediate_size: int | None = None):
        super().__init__()
        self.n = n_qubits
        self.dim = 2 ** n_qubits
        self.encoder = FutureRecordEncoder(
            n_qubits, max_T, d_model, n_layer, n_head, use_sep, intermediate_size
        )
        self.head = DenseQRHead(d_model, n_qubits)

    @classmethod
    def from_companion(cls, policy: nn.Module) -> "RefactoredQRPolicy":
        """Copy a companion ``PolicyModel`` without changing its parameter values."""
        config = policy.transformer.config
        refactored = cls(
            policy.n, config.max_position_embeddings // (policy.n + int(policy.use_sep)),
            policy.use_sep, config.hidden_size, config.num_hidden_layers,
            config.num_attention_heads, config.intermediate_size,
        )
        refactored.encoder.transformer.load_state_dict(policy.transformer.state_dict())
        refactored.head.out_proj.load_state_dict(policy.out_proj.state_dict())
        return refactored

    def forward(self, m_future: torch.Tensor, attention_mask=None,
                dtype: torch.dtype | None = None) -> torch.Tensor:
        unitary = self.head(self.encoder(m_future, attention_mask), dtype)
        return unitary.reshape(*m_future.shape[:-2], self.dim, self.dim)


def _paulis(dtype: torch.dtype, device: torch.device) -> tuple[torch.Tensor, ...]:
    matrices = (
        [[1, 0], [0, 1]],
        [[0, 1], [1, 0]],
        [[0, -1j], [1j, 0]],
        [[1, 0], [0, -1]],
    )
    return tuple(torch.tensor(x, dtype=dtype, device=device) for x in matrices)


def _rotation(pauli: torch.Tensor, angle: torch.Tensor) -> torch.Tensor:
    """Return exp(-i angle P) for P^2=I, batched over angle."""
    identity = torch.eye(pauli.shape[0], dtype=pauli.dtype, device=pauli.device)
    return torch.cos(angle)[..., None, None] * identity - 1j * torch.sin(angle)[..., None, None] * pauli


def _pauli_basis(n_qubits: int, dtype: torch.dtype, device: torch.device) -> list[torch.Tensor]:
    pauli = _paulis(dtype, device)
    return [
        torch.kron(pauli[a], pauli[b]) if n_qubits == 2 else pauli[a]
        for a, b in (itertools.product(range(4), repeat=2) if n_qubits == 2 else ((a, 0) for a in range(4)))
        if not (a == 0 and b == 0)
    ]


class LocalHamiltonianHead(nn.Module):
    """Predict local Pauli terms and compile them into a symmetric product formula."""

    def __init__(self, d_model: int, n_qubits: int, trotter_steps: int = 1):
        super().__init__()
        if n_qubits not in (1, 2):
            raise ValueError("Phase-1 prototype supports only one or two qubits")
        self.n_qubits = n_qubits
        self.trotter_steps = trotter_steps
        self.n_terms = 3 if n_qubits == 1 else 15
        self.out_proj = nn.Linear(d_model, self.n_terms)

    def forward(self, features: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
        real_dtype = torch.float64 if dtype == torch.complex128 else torch.float32
        angles = self.out_proj(features).to(real_dtype)
        basis = _pauli_basis(self.n_qubits, dtype, features.device)
        dim = 2 ** self.n_qubits
        unitary = torch.eye(dim, dtype=dtype, device=features.device).expand(features.shape[0], dim, dim).clone()
        scale = 0.5 / self.trotter_steps
        ordered = list(enumerate(basis))
        for _ in range(self.trotter_steps):
            for index, pauli in ordered + ordered[::-1]:
                unitary = _rotation(pauli, scale * angles[:, index]) @ unitary
        return unitary


class LocalGateHead(nn.Module):
    """Predict Euler rotations and an XX/YY/ZZ nearest-neighbor entangler."""

    def __init__(self, d_model: int, n_qubits: int, depth: int = 1):
        super().__init__()
        if n_qubits not in (1, 2):
            raise ValueError("Phase-1 prototype supports only one or two qubits")
        self.n_qubits = n_qubits
        self.depth = depth
        self.params_per_layer = 3 if n_qubits == 1 else 9
        self.out_proj = nn.Linear(d_model, depth * self.params_per_layer)

    def forward(self, features: torch.Tensor, dtype: torch.dtype) -> torch.Tensor:
        real_dtype = torch.float64 if dtype == torch.complex128 else torch.float32
        angles = self.out_proj(features).to(real_dtype).reshape(features.shape[0], self.depth, -1)
        pauli = _paulis(dtype, features.device)
        dim = 2 ** self.n_qubits
        unitary = torch.eye(dim, dtype=dtype, device=features.device).expand(features.shape[0], dim, dim).clone()
        for layer in range(self.depth):
            cursor = 0
            for qubit in range(self.n_qubits):
                local = torch.eye(2, dtype=dtype, device=features.device).expand(features.shape[0], 2, 2).clone()
                for axis in (3, 2, 3):
                    local = _rotation(pauli[axis], 0.5 * angles[:, layer, cursor]) @ local
                    cursor += 1
                if self.n_qubits == 1:
                    embedded = local
                elif qubit == 0:
                    embedded = torch.einsum("bij,kl->bikjl", local, pauli[0]).reshape(-1, 4, 4)
                else:
                    embedded = torch.einsum("ij,bkl->bikjl", pauli[0], local).reshape(-1, 4, 4)
                unitary = embedded @ unitary
            if self.n_qubits == 2:
                for axis in (1, 2, 3):
                    unitary = _rotation(torch.kron(pauli[axis], pauli[axis]), 0.5 * angles[:, layer, cursor]) @ unitary
                    cursor += 1
        return unitary


class CircuitPolicy(nn.Module):
    """Compose the fixed companion-style encoder with an interchangeable local head."""

    def __init__(self, n_qubits: int, family: str, max_T: int = 64,
                 d_model: int = 64, n_layer: int = 2, n_head: int = 4, depth: int = 1):
        super().__init__()
        self.n = n_qubits
        self.encoder = FutureRecordEncoder(n_qubits, max_T, d_model, n_layer, n_head)
        if family == "hamiltonian":
            self.head = LocalHamiltonianHead(d_model, n_qubits, trotter_steps=depth)
        elif family == "gates":
            self.head = LocalGateHead(d_model, n_qubits, depth=depth)
        else:
            raise ValueError("family must be 'hamiltonian' or 'gates'")

    def forward(self, m_future: torch.Tensor, attention_mask=None,
                dtype: torch.dtype | None = None) -> torch.Tensor:
        del attention_mask
        dtype = torch.complex64 if dtype is None else dtype
        unitary = self.head(self.encoder(m_future), dtype)
        return unitary.reshape(*m_future.shape[:-2], 2 ** self.n, 2 ** self.n)
