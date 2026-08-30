"""Operators: WeakMeasurement and related utilities.
- These are low-level building blocks.
- Module contains a global PAULI tensor.
"""

import math

import torch

PAULI = torch.tensor(
    [
        [[1.0, 0.0], [0.0, 1.0]],
        [[0.0, 1.0], [1.0, 0.0]],
        [[0.0, -1.0j], [1.0j, 0.0]],
        [[1.0, 0.0], [0.0, -1.0]],
    ],
    dtype=torch.complex128,
)  # (4, 2, 2) I, X, Y, Z


def _batched_kron(mats: torch.Tensor) -> torch.Tensor:
    """mats (..., n, 2, 2) -> (..., 2^n, 2^n). Batched Kronecker product via einsum."""
    n = mats.shape[-3]
    out = mats[..., 0, :, :]
    for k in range(1, n):
        next_mat = mats[..., k, :, :]
        out = torch.einsum("...ij,...kl->...ikjl", out, next_mat)
        out = out.reshape(out.shape[:-4] + (out.shape[-4] * out.shape[-3], out.shape[-2] * out.shape[-1]))
    return out


class WeakMeasurement:
    """Low-level weak measurement. Prefer ForwardDiffusion/BackwardDiffusion for experiments."""

    def __init__(self, epsilon: float):
        """epsilon: measurement strength. n inferred from input shapes."""
        self.epsilon = epsilon
        norm = (6 * (1 + epsilon**2)) ** 0.5
        I, P = PAULI[0:1], PAULI[1:4]
        m = torch.arange(6, device=PAULI.device)
        Pm = P[m // 2]
        signs = (1 - 2 * (m % 2)).view(6, 1, 1).to(dtype=PAULI.dtype)
        self.local = (I + signs * epsilon * Pm) / norm

    def operator(self, m_seq: torch.Tensor) -> torch.Tensor:
        """m_seq (..., n) -> (..., 2^n, 2^n). Values in {0..5}."""
        local = self.local.to(m_seq.device)
        mats = local[m_seq]
        return _batched_kron(mats)

    def logprob(self, m_seq: torch.Tensor, state: torch.Tensor) -> torch.Tensor:
        """m_seq (..., N), state (..., 2^N) -> log probs (...,)."""
        K = self.operator(m_seq)
        post = torch.einsum("...ij,...j->...i", K, state)
        prob = (post.abs() ** 2).sum(dim=-1)
        return torch.log(prob + 1e-12)

    def sample(self, state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Sample m_seq and return (m_seq, post_measurement_state).
        state (..., 2^n) -> (m_seq (..., n), post_state (..., 2^n))."""
        local = self.local.to(state.device)
        dim = state.shape[-1]
        n = int(round(math.log2(dim)))
        assert 2**n == dim
        batch_shape = state.shape[:-1]
        current_state = state
        m_seq = torch.empty(*batch_shape, n, dtype=torch.long, device=state.device)
        for q in range(n):
            left, mid, right = 2**q, 2, 2 ** (n - 1 - q)
            s = current_state.reshape(*batch_shape, left, mid, right)
            posts = torch.einsum("mij,...ajr->...mair", local, s).reshape(*batch_shape, 6, dim)
            probs = (posts.abs() ** 2).sum(dim=-1)
            probs = probs / (probs.sum(dim=-1, keepdim=True) + 1e-12)
            probs_flat = probs.reshape(-1, 6)
            idx_flat = torch.multinomial(probs_flat, 1).squeeze(-1)
            idx = idx_flat.reshape(batch_shape) if batch_shape else idx_flat.squeeze(0)
            m_seq[..., q] = idx
            index = idx.unsqueeze(-1).unsqueeze(-1).expand(*idx.shape, 1, dim)
            post_selected = posts.gather(dim=-2, index=index).squeeze(-2)
            norm = (post_selected.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()
            current_state = post_selected / (norm + 1e-12)
        return m_seq, current_state

    def apply(self, state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """End-to-end: sample m, return (post-measurement state, m_seq)."""
        m_seq, post_state = self.sample(state)
        return post_state, m_seq


def qr_to_unitary(A: torch.Tensor) -> torch.Tensor:
    """Return the unitary factor Q from a QR decomposition of A.

    A (..., dim, dim) complex -> Q (..., dim, dim) with Q unitary.
    """
    Q, _ = torch.linalg.qr(A)
    return Q

