"""Model: PolicyModel, QuantumDiffusionLoss, DiffusionTrainer."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import torch
import torch.nn as nn
from transformers import LlamaConfig, LlamaModel

from .operator import WeakMeasurement, qr_to_unitary

if TYPE_CHECKING:
    from .diffusion import ForwardDiffusion


PAD_TOKEN_ID = 6
SEP_TOKEN_ID = 7  # used only if use_sep=True


def measurement_sequence_to_tokens(
    m_future: torch.Tensor,
    use_sep: bool = True,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Convert measurement sequences to token ids and attention mask.

    m_future (..., L, n) with values in {0..5}.
    Returns (tokens, attention_mask) each of shape (B, S), where
    B is the flattened batch and S is the sequence length (no padding needed
    here because all items in the batch share the same L).
    """
    assert m_future.dtype in (torch.int64, torch.int32, torch.int16, torch.uint8)
    *batch_dims, L, n = m_future.shape
    B = int(math.prod(batch_dims)) if batch_dims else 1
    device = m_future.device
    m_flat = m_future.reshape(B, L, n)
    if use_sep:
        # tokens per time step: n measurement outcomes + 1 SEP
        tokens = torch.empty(B, L, n + 1, dtype=torch.long, device=device)
        tokens[..., :n] = m_flat
        tokens[..., n] = SEP_TOKEN_ID
        tokens = tokens.reshape(B, (n + 1) * L)
    else:
        tokens = m_flat.reshape(B, L * n)
    attention_mask = torch.ones_like(tokens, dtype=torch.long, device=device)
    return tokens, attention_mask


class PolicyModel(nn.Module):
    """Transformer-based policy conditioned on full future measurement trajectory.

    Input: m_future (..., L, n) with values in {0..5}.
    Output: U (..., dim, dim) where dim = 2^n, obtained via QR(A).
    """

    def __init__(
        self,
        n_qubits: int,
        max_T: int = 64,
        use_sep: bool = True,
        d_model: int = 64,
        n_layer: int = 2,
        n_head: int = 4,
        intermediate_size: int | None = None,
    ):
        super().__init__()
        assert d_model % n_head == 0, "d_model must be divisible by n_head"
        self.n = n_qubits
        self.use_sep = use_sep
        self.dim = 2**n_qubits
        vocab_size = 8 if use_sep else 7  # 0..5 + PAD + optional SEP
        if intermediate_size is None:
            intermediate_size = 4 * d_model
        max_seq_len = max_T * (n_qubits + (1 if use_sep else 0))

        config = LlamaConfig(
            vocab_size=vocab_size,
            hidden_size=d_model,
            intermediate_size=intermediate_size,
            num_hidden_layers=n_layer,
            num_attention_heads=n_head,
            max_position_embeddings=max_seq_len,
            pad_token_id=PAD_TOKEN_ID,
            bos_token_id=None,
            eos_token_id=None,
        )
        self.transformer = LlamaModel(config)
        self.out_proj = nn.Linear(d_model, 2 * self.dim * self.dim)

    def forward(
        self,
        m_future: torch.Tensor,
        attention_mask: torch.Tensor | None = None,
        dtype: torch.dtype | None = None,
    ) -> torch.Tensor:
        """m_future (..., L, n) -> U (..., dim, dim) complex unitary.

        dtype: If None, U is complex64 (from float32 head). If torch.complex128,
        the head output is cast to float64 and U is computed in complex128 for
        compatibility with quantum state/operators (Kraus, etc.).
        """
        assert m_future.shape[-1] == self.n, f"Expected last dim {self.n}, got {m_future.shape[-1]}"
        tokens, base_mask = measurement_sequence_to_tokens(m_future, use_sep=self.use_sep)
        if attention_mask is not None:
            attn = base_mask & attention_mask.to(base_mask.dtype)
        else:
            attn = base_mask

        outputs = self.transformer(input_ids=tokens, attention_mask=attn)
        hidden = outputs.last_hidden_state  # (B, S, d_model)

        attn_float = attn.unsqueeze(-1).to(hidden.dtype)
        hidden_sum = (hidden * attn_float).sum(dim=1)
        lengths = attn_float.sum(dim=1).clamp(min=1.0)
        pooled = hidden_sum / lengths

        A_flat = self.out_proj(pooled)  # (B_flat, 2*dim^2) float32
        B_flat = A_flat.shape[0]
        if dtype is torch.complex128:
            A_flat = A_flat.double()
        A_flat = A_flat.view(B_flat, self.dim * self.dim, 2)
        A_complex = torch.complex(A_flat[..., 0], A_flat[..., 1]).view(B_flat, self.dim, self.dim)
        U = qr_to_unitary(A_complex)

        *batch_dims, L, _ = m_future.shape
        if batch_dims:
            U = U.view(*batch_dims, self.dim, self.dim)
        return U


class QuantumDiffusionLoss(nn.Module):
    """Compute loss from trajectories using WeakMeasurement and PolicyModel.

    Policy is conditioned on the full future measurement trajectory for each pair.
    """

    def __init__(
        self,
        weak_measurement: WeakMeasurement,
        policy: PolicyModel,
    ):
        super().__init__()
        self.weak_measurement = weak_measurement
        self.policy = policy

    def forward(self, trajectories: torch.Tensor) -> torch.Tensor:
        """trajectories (..., T, n): measurement sequences. T time steps, n qubits.

        For each forward-time index t=1..T-1, the policy sees the future slice
        m^(t), m^(t+1), ..., m^(T-1) and predicts U_t. The loss is the mean over
        all (t, ...) of ||U_t K_t K_{t-1} - c I||_F^2 with trace normalization.
        """
        T = trajectories.shape[-2]
        if T < 2:
            return torch.tensor(0.0, device=next(self.policy.parameters()).device)
        m_all = trajectories
        K_all = self.weak_measurement.operator(m_all)
        dim = K_all.shape[-1]
        I = torch.eye(dim, dtype=K_all.dtype, device=K_all.device)

        # Flatten batch dims for convenience
        batch_shape = trajectories.shape[:-2]
        B = int(math.prod(batch_shape)) if batch_shape else 1
        m_all_flat = m_all.reshape(B, T, -1)  # (B, T, n)
        K_all_flat = K_all.reshape(B, T, dim, dim)

        total_loss = torch.zeros((), dtype=torch.float64, device=m_all.device)
        count = 0

        for t in range(1, T):
            # K_t and K_{t-1} for this time index
            K_t = K_all_flat[:, t, :, :]
            K_prev = K_all_flat[:, t - 1, :, :]
            m_future = m_all_flat[:, t:, :]  # (B, T-t, n)

            U = self.policy(m_future, dtype=K_all.dtype)  # match Kraus dtype (complex128)
            M = U @ K_t @ K_prev
            tr_M = M.diagonal(dim1=-2, dim2=-1).sum(dim=-1)
            c = tr_M / dim  # (B,)
            diff = M - c.view(B, 1, 1) * I
            total_loss = total_loss + (diff.abs() ** 2).sum(dtype=torch.float64)
            count += B

        if count == 0:
            return torch.tensor(0.0, device=m_all.device)
        return (total_loss / count).to(torch.float32)


class DiffusionTrainer:
    """Collect trajectories; train policy via QuantumDiffusionLoss."""

    def __init__(
        self,
        forward: ForwardDiffusion,
        policy: PolicyModel,
        loss_fn: QuantumDiffusionLoss,
        lr: float = 1e-3,
    ):
        self.forward = forward
        self.policy = policy
        self.loss_fn = loss_fn
        self.optimizer = torch.optim.Adam(policy.parameters(), lr=lr)

    def collect(
        self,
        n_traj: int,
        T: int,
        initial_state: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Run batched forward diffusion. Returns trajectories (n_traj, T, n).
        initial_state: (dim,) or (n_traj, dim); single state broadcast to n_traj.
        If None, sample random pure states."""
        dim = 2**self.policy.n
        device = next(self.policy.parameters()).device
        if initial_state is not None:
            s = initial_state
            if s.ndim == 1:
                states = s.unsqueeze(0).expand(n_traj, -1).clone()
            else:
                assert s.shape[0] == n_traj, f"initial_state.shape[0]={s.shape[0]} != n_traj"
                states = s
        else:
            states = torch.randn(n_traj, dim, dtype=torch.complex128, device=device)
            states = states / (states.abs()**2).sum(-1, keepdim=True).sqrt()
        states = states.to(device)
        self.forward.state = states
        return self.forward.trajectory(T)

    def train_step(self, batch: torch.Tensor) -> float:
        """batch from collect(); loss = loss_fn(batch); backward; return loss."""
        self.optimizer.zero_grad()
        loss = self.loss_fn(batch)
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def train(self, n_epochs: int, n_traj_per_epoch: int = 10, T: int = 5) -> None:
        """Full training loop."""
        for epoch in range(n_epochs):
            batch = self.collect(n_traj_per_epoch, T)
            loss = self.train_step(batch)
            if (epoch + 1) % 10 == 0 or epoch == 0:
                print(f"Epoch {epoch+1}/{n_epochs} loss={loss:.6f}")
