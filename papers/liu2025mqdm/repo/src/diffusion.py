"""Diffusion: ForwardDiffusion, BackwardDiffusion."""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from .operator import WeakMeasurement

if TYPE_CHECKING:
    from .model import PolicyModel


class ForwardDiffusion:
    """Forward diffusion for training data generation.

    Callers should use state, step, and trajectory only. WeakMeasurement is used
    internally; do not call wm.operator() or wm.apply() directly for diffusion workflows.

    After trajectory(T), fd.state holds the final states. No need to recompute
    from measurement sequences.
    """

    def __init__(self, weak_measurement: WeakMeasurement):
        self.weak_measurement = weak_measurement
        self._state: torch.Tensor | None = None

    @property
    def state(self) -> torch.Tensor | None:
        """Current batched state (..., 2^n). Updated in-place by step/trajectory."""
        return self._state

    @state.setter
    def state(self, value: torch.Tensor | None) -> None:
        self._state = value

    def step(self) -> torch.Tensor:
        """Apply one weak measurement step; update state. Return m_seq (..., n)."""
        if self._state is None:
            raise RuntimeError("state must be set before step()")
        post_state, m_seq = self.weak_measurement.apply(self._state)
        self._state = post_state
        return m_seq

    def trajectory(self, T: int) -> torch.Tensor:
        """Run T steps; update state in-place. Return m_seqs (..., T, n). Final states in fd.state."""
        if self._state is None:
            raise RuntimeError("state must be set before trajectory()")
        m_seqs = [self.step() for _ in range(T)]
        return torch.stack(m_seqs, dim=-2)


class BackwardDiffusion:
    """Inference only.

    Each step:
      (1) weak_measurement.apply(state)
      (2) U = policy(m_forward_future)
      (3) state <- U @ post_state

    The policy is conditioned on the recorded forward measurement trajectory.
    """

    def __init__(
        self,
        weak_measurement: WeakMeasurement,
        policy: PolicyModel,
    ):
        self.weak_measurement = weak_measurement
        self.policy = policy
        self._state: torch.Tensor | None = None
        self._forward_trajectory: torch.Tensor | None = None

    @property
    def state(self) -> torch.Tensor | None:
        return self._state

    @state.setter
    def state(self, value: torch.Tensor | None) -> None:
        self._state = value

    @property
    def forward_trajectory(self) -> torch.Tensor | None:
        """Recorded forward measurement trajectory (..., T, n)."""
        return self._forward_trajectory

    @forward_trajectory.setter
    def forward_trajectory(self, value: torch.Tensor | None) -> None:
        self._forward_trajectory = value

    def step(self, t_forward: int, T: int) -> tuple[torch.Tensor, torch.Tensor]:
        """One backward step using forward-time index t_forward (0..T-1).

        Returns (m_back, U) where m_back is the measurement sequence from the
        backward weak measurement and U is the unitary applied.
        """
        if self._state is None:
            raise RuntimeError("state must be set before step()")
        if self._forward_trajectory is None:
            raise RuntimeError("forward_trajectory must be set before step()")
        if not (0 <= t_forward < T):
            raise ValueError(f"t_forward must be in [0, {T-1}], got {t_forward}")

        with torch.no_grad():
            post_state, m_back = self.weak_measurement.apply(self._state)
            m_forward_future = self._forward_trajectory[..., t_forward:, :]
            U = self.policy(m_forward_future, dtype=post_state.dtype)
            recovered = torch.einsum("...ij,...j->...i", U, post_state)
        self._state = recovered
        return m_back, U

    def trajectory(self, T: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Run T backward steps.

        Time index: forward time 0..T-1. Backward step 0 corresponds to forward
        time T-1 (reversing last forward step).

        Returns:
          m_tensor (T, n): backward measurement sequences per step.
          U_tensor (T, dim, dim): unitaries applied at each step.
        """
        if self._state is None:
            raise RuntimeError("state must be set before trajectory()")
        if self._forward_trajectory is None:
            raise RuntimeError("forward_trajectory must be set before trajectory()")

        with torch.no_grad():
            m_seqs, U_seqs = [], []
            for t_back in range(T):
                t_forward = T - 1 - t_back
                m_back, U = self.step(t_forward, T)
                m_seqs.append(m_back)
                U_seqs.append(U)
        return torch.stack(m_seqs, dim=-2), torch.stack(U_seqs, dim=-3)

    def trajectory_reversal(self, T: int) -> torch.Tensor:
        """Run T-1 backward steps without sampling weak measurement (true reversal).

        The loss trains U_t for t=1..T-1 so that U_t K_t K_{t-1} ≈ cI. So U_{T-1}
        applied to s_T gives s_{T-2}, U_{T-2} applied to s_{T-2} gives s_{T-3},
        ... and after T-1 steps we get s_0 = |0⟩. We do *not* apply a U for t=0
        (policy is only trained on m_future at t=1..T-1).
        Updates state in-place. Returns stacked U (..., T-1, dim, dim).
        """
        if self._state is None:
            raise RuntimeError("state must be set before trajectory_reversal()")
        if self._forward_trajectory is None:
            raise RuntimeError("forward_trajectory must be set before trajectory_reversal()")
        steps = max(0, T - 1)
        with torch.no_grad():
            U_seqs = []
            for t_back in range(steps):
                t_forward = T - 1 - t_back  # T-1, T-2, ..., 1 (never 0)
                m_forward_future = self._forward_trajectory[..., t_forward:, :]
                U = self.policy(m_forward_future, dtype=self._state.dtype)
                self._state = torch.einsum("...ij,...j->...i", U, self._state)
                U_seqs.append(U)
        return torch.stack(U_seqs, dim=-3) if U_seqs else torch.empty(*self._state.shape[:-1], 0, self._state.shape[-1], self._state.shape[-1], dtype=self._state.dtype, device=self._state.device)
