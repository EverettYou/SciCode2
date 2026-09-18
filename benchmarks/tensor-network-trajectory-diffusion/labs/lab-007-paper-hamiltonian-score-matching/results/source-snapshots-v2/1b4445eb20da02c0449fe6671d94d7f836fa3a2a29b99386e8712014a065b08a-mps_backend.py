"""Batched 1D MPS: local observables, 1-site TDVP reverse, TEBD comparator.

The reverse engine is 1-site MPS-TDVP (Haegeman): the 1D instance of the
Wu–Nys manifold flow. Gauge is fixed by phase-locked QR, not SVD. TEBD
(Trotter + SVD split) remains a no-grad comparator; it is not trained.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch

PAULI_I = torch.tensor([[1.0, 0.0], [0.0, 1.0]], dtype=torch.complex128)
PAULI_XYZ = torch.tensor(
    [
        [[0.0, 1.0], [1.0, 0.0]],
        [[0.0, -1.0j], [1.0j, 0.0]],
        [[1.0, 0.0], [0.0, -1.0]],
    ],
    dtype=torch.complex128,
)
PAULI_IXYZ = torch.stack([PAULI_I, PAULI_XYZ[0], PAULI_XYZ[1], PAULI_XYZ[2]], dim=0)

# Two-qubit Pauli order matches train_n2_control_hamiltonian.PAULI_NAMES
# IX IY IZ XI XX XY XZ YI YX YY YZ ZI ZX ZY ZZ
N2_PAULI_INDEX = {
    "IX": (0, 1),
    "IY": (0, 2),
    "IZ": (0, 3),
    "XI": (1, 0),
    "XX": (1, 1),
    "XY": (1, 2),
    "XZ": (1, 3),
    "YI": (2, 0),
    "YX": (2, 1),
    "YY": (2, 2),
    "YZ": (2, 3),
    "ZI": (3, 0),
    "ZX": (3, 1),
    "ZY": (3, 2),
    "ZZ": (3, 3),
}
N2_PAULI_NAMES = list(N2_PAULI_INDEX.keys())
N2_SITE0 = {"XI": 0, "YI": 1, "ZI": 2}  # indices in XYZ
N2_SITE1 = {"IX": 0, "IY": 1, "IZ": 2}
N2_BOND = ["XX", "XY", "XZ", "YX", "YY", "YZ", "ZX", "ZY", "ZZ"]


def _xyz(device: torch.device) -> torch.Tensor:
    return PAULI_XYZ.to(device)


def _phase_qr(matrix: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Reduced QR with real-positive R diagonal (unique gauge, AD-safe)."""
    q, r = torch.linalg.qr(matrix, mode="reduced")
    diag = torch.diagonal(r, dim1=-2, dim2=-1)
    phase = torch.where(diag.abs() > 1e-30, diag / diag.abs().clamp(min=1e-30), torch.ones_like(diag))
    return q * phase.unsqueeze(-2), phase.conj().unsqueeze(-1) * r


@dataclass
class BatchMPS:
    tensors: list[torch.Tensor]  # each (batch, χ_left, 2, χ_right)

    @property
    def batch(self) -> int:
        return int(self.tensors[0].shape[0])

    @property
    def n_sites(self) -> int:
        return len(self.tensors)

    @property
    def device(self) -> torch.device:
        return self.tensors[0].device

    @property
    def dtype(self) -> torch.dtype:
        return self.tensors[0].dtype

    def clone(self) -> "BatchMPS":
        return BatchMPS([t.clone() for t in self.tensors])

    def inner(self, other: "BatchMPS | None" = None) -> torch.Tensor:
        """⟨other|self⟩, shape (batch,). other defaults to self."""
        bra = other.tensors if other is not None else self.tensors
        env = torch.ones(self.batch, 1, 1, dtype=self.dtype, device=self.device)
        for ket, br in zip(self.tensors, bra):
            env = torch.einsum("blm,blsr,bmsd->brd", env, ket, br.conj())
        return env[:, 0, 0]

    def normalize(self) -> "BatchMPS":
        nrm = self.inner().real.clamp(min=1e-24).sqrt()
        scaled = self.tensors[0] / nrm[:, None, None, None]
        return BatchMPS([scaled] + [t for t in self.tensors[1:]])

    def balance(self) -> "BatchMPS":
        """Push per-site max-abs toward the right so QR does not overflow."""
        tensors = list(self.tensors)
        for i in range(len(tensors) - 1):
            nrm = tensors[i].abs().amax(dim=(1, 2, 3)).clamp(min=1e-30)
            tensors[i] = tensors[i] / nrm[:, None, None, None]
            tensors[i + 1] = tensors[i + 1] * nrm[:, None, None, None]
        return BatchMPS(tensors).normalize()

    def left_env(self, site: int) -> torch.Tensor:
        env = torch.ones(self.batch, 1, 1, dtype=self.dtype, device=self.device)
        for ket in self.tensors[:site]:
            env = torch.einsum("blm,blsr,bmsd->brd", env, ket, ket.conj())
        return env

    def right_env(self, site: int) -> torch.Tensor:
        env = torch.ones(self.batch, 1, 1, dtype=self.dtype, device=self.device)
        for ket in reversed(self.tensors[site + 1 :]):
            env = torch.einsum("brd,blsr,bmsd->blm", env, ket, ket.conj())
        return env

    def expect_site(self, site: int, pauli: torch.Tensor) -> torch.Tensor:
        """⟨σ⟩ on one site. pauli is (2,2) or (batch,2,2), acting as P|ψ⟩."""
        if pauli.dim() == 2:
            pauli = pauli.expand(self.batch, 2, 2)
        ket = self.tensors[site]
        applied = torch.einsum("bts,blsr->bltr", pauli, ket)
        left = self.left_env(site)
        right = self.right_env(site)
        return torch.einsum("blm,bltr,bmtu,bru->b", left, applied, ket.conj(), right).real

    def expect_bond(self, site: int, pauli_a: torch.Tensor, pauli_b: torch.Tensor) -> torch.Tensor:
        """⟨σ^a_site σ^b_{site+1}⟩."""
        if pauli_a.dim() == 2:
            pauli_a = pauli_a.expand(self.batch, 2, 2)
            pauli_b = pauli_b.expand(self.batch, 2, 2)
        left = self.left_env(site)
        right = self.right_env(site + 1)
        a = self.tensors[site]
        b = self.tensors[site + 1]
        theta = torch.einsum("blsr,brcd->blscd", a, b)
        theta_p = torch.einsum("bts,buc,blscd->bltud", pauli_a, pauli_b, theta)
        return torch.einsum("blm,bltud,bmtup,bdp->b", left, theta_p, theta.conj(), right).real

    def pauli_vector(self) -> torch.Tensor:
        """N=1: Bloch (B,3). N=2: 15-dim vector in N2_PAULI_NAMES order."""
        xyz = _xyz(self.device)
        if self.n_sites == 1:
            return torch.stack([self.expect_site(0, xyz[i]) for i in range(3)], dim=-1)
        if self.n_sites != 2:
            raise NotImplementedError("pauli_vector is implemented for N=1,2")
        cols = []
        for name in N2_PAULI_NAMES:
            a, b = N2_PAULI_INDEX[name]
            if a == 0:
                cols.append(self.expect_site(1, PAULI_IXYZ[b].to(self.device)))
            elif b == 0:
                cols.append(self.expect_site(0, PAULI_IXYZ[a].to(self.device)))
            else:
                cols.append(
                    self.expect_bond(
                        0,
                        PAULI_IXYZ[a].to(self.device),
                        PAULI_IXYZ[b].to(self.device),
                    )
                )
        return torch.stack(cols, dim=-1)

    def apply_site_gate(self, site: int, gate: torch.Tensor) -> "BatchMPS":
        """gate (batch, 2, 2) on one site. Bond dimension unchanged."""
        updated = torch.einsum("bst,bltr->blsr", gate, self.tensors[site])
        tensors = list(self.tensors)
        tensors[site] = updated
        return BatchMPS(tensors)

    def apply_bond_gate(self, site: int, gate: torch.Tensor, chi_max: int | None = None) -> "BatchMPS":
        """gate (batch, 4, 4) on sites (site, site+1), then SVD split. Comparator only."""
        left = self.tensors[site]
        right = self.tensors[site + 1]
        chi_l = left.shape[1]
        chi_r = right.shape[3]
        theta = torch.einsum("blsr,brcd->blscd", left, right)
        theta = theta.reshape(self.batch, chi_l, 4, chi_r)
        theta = torch.einsum("bij,bljr->blir", gate, theta)
        theta = theta.reshape(self.batch, chi_l * 2, 2 * chi_r)
        u, s, vh = torch.linalg.svd(theta, full_matrices=False)
        chi = s.shape[-1] if chi_max is None else min(chi_max, s.shape[-1])
        u, s, vh = u[:, :, :chi], s[:, :chi], vh[:, :chi, :]
        new_left = (u * s[:, None, :]).reshape(self.batch, chi_l, 2, chi)
        new_right = vh.reshape(self.batch, chi, 2, chi_r)
        tensors = list(self.tensors)
        tensors[site] = new_left
        tensors[site + 1] = new_right
        return BatchMPS(tensors)

    def qr_shift_right(self, site: int) -> "BatchMPS":
        """Left-canonicalize `site` and absorb R into `site+1`. SVD-free."""
        a = self.tensors[site]
        q, r = _phase_qr(a.reshape(self.batch, a.shape[1] * 2, a.shape[3]))
        tensors = list(self.tensors)
        tensors[site] = q.reshape(self.batch, a.shape[1], 2, q.shape[-1])
        tensors[site + 1] = torch.einsum("bik,bksd->bisd", r, self.tensors[site + 1])
        return BatchMPS(tensors)

    def qr_shift_left(self, site: int) -> "BatchMPS":
        """Right-canonicalize `site` and absorb L into `site-1`. SVD-free."""
        a = self.tensors[site]
        q, r = _phase_qr(a.reshape(self.batch, a.shape[1], 2 * a.shape[3]).mH)
        tensors = list(self.tensors)
        tensors[site] = q.mH.reshape(self.batch, q.shape[-1], 2, a.shape[3])
        tensors[site - 1] = torch.einsum("blsr,brk->blsk", self.tensors[site - 1], r.mH)
        return BatchMPS(tensors)

    def right_canonical(self) -> "BatchMPS":
        state = self
        for site in range(self.n_sites - 1, 0, -1):
            state = state.qr_shift_left(site)
        return state

    def apply_bond_projected(self, site: int, gate: torch.Tensor) -> "BatchMPS":
        """1-site TDVP: apply a 4×4 gate on (site, site+1) and project onto site.

        Neighbor `site+1` must be right-canonical. Bond dimension is unchanged.
        At maximal χ this is exact; otherwise it is the tangent-space projection.
        """
        left = self.tensors[site]
        right = self.tensors[site + 1]
        chi_l = left.shape[1]
        chi_r = right.shape[3]
        theta = torch.einsum("blsr,brcd->blscd", left, right)
        theta = theta.reshape(self.batch, chi_l, 4, chi_r)
        theta = torch.einsum("bij,bljr->blir", gate, theta)
        theta = theta.reshape(self.batch, chi_l, 2, 2, chi_r)
        updated = torch.einsum("blscd,bmcd->blsm", theta, right.conj())
        tensors = list(self.tensors)
        tensors[site] = updated
        return BatchMPS(tensors)

    def to_dense(self) -> torch.Tensor:
        contracted = self.tensors[0]
        for nxt in self.tensors[1:]:
            contracted = torch.einsum("b...r,brsd->b...sd", contracted, nxt)
        return contracted.reshape(self.batch, -1)

    def max_bond_dim(self) -> int:
        return max(int(t.shape[-1]) for t in self.tensors)

    def local_observables(self) -> tuple[torch.Tensor, torch.Tensor | None]:
        """On-site Bloch (B, N, 3) and nearest-neighbor correlators (B, N-1, 9).

        Bond order is XX,XY,XZ,YX,YY,YZ,ZX,ZY,ZZ.
        """
        xyz = _xyz(self.device)
        bloch = torch.stack(
            [torch.stack([self.expect_site(site, xyz[i]) for i in range(3)], dim=-1) for site in range(self.n_sites)],
            dim=1,
        )
        if self.n_sites == 1:
            return bloch, None
        bonds = []
        for site in range(self.n_sites - 1):
            corr = []
            for name in N2_BOND:
                a, b = N2_PAULI_INDEX[name]
                corr.append(self.expect_bond(site, PAULI_IXYZ[a].to(self.device), PAULI_IXYZ[b].to(self.device)))
            bonds.append(torch.stack(corr, dim=-1))
        return bloch, torch.stack(bonds, dim=1)


def mps_from_dense(state: torch.Tensor, n_sites: int) -> BatchMPS:
    batch = state.shape[0]
    rest = state
    chi_left = 1
    tensors = []
    remaining = n_sites
    for _ in range(n_sites - 1):
        remaining -= 1
        rest = rest.reshape(batch, chi_left * 2, 2**remaining)
        u, s, vh = torch.linalg.svd(rest, full_matrices=False)
        chi = s.shape[-1]
        tensors.append((u * s[:, None, :]).reshape(batch, chi_left, 2, chi))
        chi_left = chi
        rest = vh
    tensors.append(rest.reshape(batch, chi_left, 2, 1))
    return BatchMPS(tensors)


def mps_product(site_states: torch.Tensor) -> BatchMPS:
    """site_states (batch, n_sites, 2) product MPS with χ=1."""
    batch, n_sites, _ = site_states.shape
    tensors = [site_states[:, i, :].reshape(batch, 1, 2, 1) for i in range(n_sites)]
    return BatchMPS(tensors)


def kraus_binary_2x2(pauli: torch.Tensor, sign: torch.Tensor, gamma: float, dt: float) -> torch.Tensor:
    delta_o = sign.to(pauli.dtype) * 0.5 * math.sqrt(dt / gamma)
    identity = torch.eye(2, dtype=pauli.dtype, device=pauli.device)
    generator = (-gamma * dt) * identity + (2.0 * gamma) * pauli * delta_o[:, None, None]
    return (1.0 / math.sqrt(2.0)) * torch.linalg.matrix_exp(generator)


def sample_onsite_kraus(mps: BatchMPS, site: int, gamma: float, dt: float) -> tuple[BatchMPS, torch.Tensor, torch.Tensor]:
    """One on-site weak Pauli measurement. Returns (state, axis, sign)."""
    batch = mps.batch
    device = mps.device
    axis = torch.randint(0, 3, (batch,), device=device)
    pauli = _xyz(device)[axis]
    plus = torch.ones(batch, device=device)
    minus = -plus
    k_plus = kraus_binary_2x2(pauli, plus, gamma, dt)
    k_minus = kraus_binary_2x2(pauli, minus, gamma, dt)
    trial_plus = mps.apply_site_gate(site, k_plus)
    trial_minus = mps.apply_site_gate(site, k_minus)
    p_plus = trial_plus.inner().real.clamp(min=0.0)
    p_minus = trial_minus.inner().real.clamp(min=0.0)
    choice = torch.rand(batch, device=device) < (p_plus / (p_plus + p_minus + 1e-12))
    # Select tensors per-sample without Python looping the batch.
    tensors = []
    for plus_t, minus_t in zip(trial_plus.tensors, trial_minus.tensors):
        picked = torch.where(choice[:, None, None, None], plus_t, minus_t)
        tensors.append(picked)
    sign = torch.where(choice, plus, minus)
    return BatchMPS(tensors).normalize(), axis, sign


def _onsite_hamiltonian(field: torch.Tensor) -> torch.Tensor:
    """field (B, 3) → (B, 2, 2) = h·σ."""
    xyz = _xyz(field.device)
    return torch.einsum("ba,aij->bij", field.to(xyz.dtype), xyz)


def _bond_hamiltonian(field: torch.Tensor) -> torch.Tensor:
    """field (B, 9) in N2_BOND order → (B, 4, 4)."""
    xyz = _xyz(field.device)
    terms = []
    for i, name in enumerate(N2_BOND):
        a, b = N2_PAULI_INDEX[name]
        op = torch.kron(PAULI_IXYZ[a].to(field.device), PAULI_IXYZ[b].to(field.device))
        terms.append(field[:, i].to(op.dtype)[:, None, None] * op)
    return torch.stack(terms, dim=0).sum(dim=0)


def reverse_tebd_step(
    mps: BatchMPS,
    h: torch.Tensor,
    axes: torch.Tensor,
    gamma: float,
    dt: float,
    combined: bool = False,
) -> BatchMPS:
    """One reverse dt. h is (B, 3) for N=1 or (B, 15) for N=2.

    combined=True: build the full 2^N generator and apply as one gate (dense
    parity at N≤2). combined=False: TEBD of on-site backaction, on-site H,
    then the two-site H (the scalable apply).
    """
    if combined:
        return _reverse_combined(mps, h, axes, gamma, dt)
    xyz = _xyz(mps.device)
    identity = torch.eye(2, dtype=mps.dtype, device=mps.device)
    state = mps
    n_meas = 1 if mps.n_sites == 1 else axes.shape[1]
    for site in range(n_meas):
        axis = axes if mps.n_sites == 1 else axes[:, site]
        pauli = xyz[axis]
        expect = state.expect_site(site, pauli)
        delta = pauli - expect[:, None, None] * identity
        backaction = torch.linalg.matrix_exp((-0.5 * gamma * dt) * (delta @ delta))
        state = state.apply_site_gate(site, backaction)
    if mps.n_sites == 1:
        ham = _onsite_hamiltonian(h)
        evolve = torch.linalg.matrix_exp((2.0j * dt) * ham)
        return state.apply_site_gate(0, evolve).normalize()
    h_s0 = torch.stack([h[:, N2_PAULI_NAMES.index(n)] for n in ("XI", "YI", "ZI")], dim=-1)
    h_s1 = torch.stack([h[:, N2_PAULI_NAMES.index(n)] for n in ("IX", "IY", "IZ")], dim=-1)
    h_bond = torch.stack([h[:, N2_PAULI_NAMES.index(n)] for n in N2_BOND], dim=-1)
    state = state.apply_site_gate(0, torch.linalg.matrix_exp((2.0j * dt) * _onsite_hamiltonian(h_s0)))
    state = state.apply_site_gate(1, torch.linalg.matrix_exp((2.0j * dt) * _onsite_hamiltonian(h_s1)))
    bond = torch.linalg.matrix_exp((2.0j * dt) * _bond_hamiltonian(h_bond))
    return state.apply_bond_gate(0, bond).normalize()


def _reverse_combined(mps: BatchMPS, h: torch.Tensor, axes: torch.Tensor, gamma: float, dt: float) -> BatchMPS:
    """Exact 2^N score operator applied as an MPS gate. N=1,2 only."""
    from torch.linalg import matrix_exp

    dim = 2**mps.n_sites
    device = mps.device
    xyz = _xyz(device)
    identity = torch.eye(dim, dtype=mps.dtype, device=device)
    if mps.n_sites == 1:
        ham = _onsite_hamiltonian(h)
        pauli = xyz[axes]
        expect = mps.expect_site(0, pauli)
        delta = pauli - expect[:, None, None] * torch.eye(2, dtype=mps.dtype, device=device)
        generator = (-0.5 * gamma) * (delta @ delta) + (2.0j) * ham
        gate = matrix_exp(generator * dt)
        return mps.apply_site_gate(0, gate).normalize()
    ham = torch.zeros(mps.batch, 4, 4, dtype=mps.dtype, device=device)
    for name, coeff in zip(N2_PAULI_NAMES, h.unbind(dim=-1)):
        a, b = N2_PAULI_INDEX[name]
        op = torch.kron(PAULI_IXYZ[a].to(device), PAULI_IXYZ[b].to(device))
        ham = ham + coeff.to(mps.dtype)[:, None, None] * op
    generator = (2.0j) * ham
    eye2 = torch.eye(2, dtype=mps.dtype, device=device)
    for site in range(2):
        pauli_loc = xyz[axes[:, site]]
        expect = mps.expect_site(site, pauli_loc)
        if site == 0:
            op = torch.einsum("bij,kl->bikjl", pauli_loc, eye2).reshape(mps.batch, 4, 4)
        else:
            op = torch.einsum("ij,bkl->bikjl", eye2, pauli_loc).reshape(mps.batch, 4, 4)
        delta = op - expect[:, None, None] * identity
        generator = generator + (-0.5 * gamma) * (delta @ delta)
    gate = matrix_exp(generator * dt)
    return mps.apply_bond_gate(0, gate).normalize()


def reverse_projected_gate_legacy(
    mps: BatchMPS,
    h_onsite: torch.Tensor,
    h_bond: torch.Tensor | None,
    axes: torch.Tensor,
    gamma: float,
    dt: float,
    chi_max: int | None = None,
) -> BatchMPS:
    """1-site TDVP reverse. χ is frozen; `chi_max` is ignored.

    On-site backaction and on-site H are exact 2×2 gates. Two-site H is the
    Haegeman 1-site projection (QR to move the center), not an SVD split.
    """
    del chi_max
    xyz = _xyz(mps.device)
    identity = torch.eye(2, dtype=mps.dtype, device=mps.device)
    n_sites = mps.n_sites
    axes_n = axes if axes.dim() == 2 else axes[:, None]
    state = mps.balance()
    for site in range(n_sites):
        pauli = xyz[axes_n[:, site]]
        expect = state.expect_site(site, pauli)
        delta = pauli - expect[:, None, None] * identity
        backaction = torch.linalg.matrix_exp((-0.5 * gamma * dt) * (delta @ delta))
        state = state.apply_site_gate(site, backaction)
    for site in range(n_sites):
        evolve = torch.linalg.matrix_exp((2.0j * dt) * _onsite_hamiltonian(h_onsite[:, site]))
        state = state.apply_site_gate(site, evolve)
    if h_bond is not None and n_sites > 1:
        state = state.right_canonical()
        for site in range(n_sites - 1):
            gate = torch.linalg.matrix_exp((2.0j * dt) * _bond_hamiltonian(h_bond[:, site]))
            state = state.apply_bond_projected(site, gate)
            state = state.qr_shift_right(site)
    return state.normalize()


def reverse_tebd_local(
    mps: BatchMPS,
    h_onsite: torch.Tensor,
    h_bond: torch.Tensor | None,
    axes: torch.Tensor,
    gamma: float,
    dt: float,
    chi_max: int | None = None,
) -> BatchMPS:
    """TEBD reverse with on-site (B, N, 3) and bond (B, N-1, 9) coefficients."""
    xyz = _xyz(mps.device)
    identity = torch.eye(2, dtype=mps.dtype, device=mps.device)
    n_sites = mps.n_sites
    axes_n = axes if axes.dim() == 2 else axes[:, None]
    state = mps
    for site in range(n_sites):
        pauli = xyz[axes_n[:, site]]
        expect = state.expect_site(site, pauli)
        delta = pauli - expect[:, None, None] * identity
        backaction = torch.linalg.matrix_exp((-0.5 * gamma * dt) * (delta @ delta))
        state = state.apply_site_gate(site, backaction)
    for site in range(n_sites):
        evolve = torch.linalg.matrix_exp((2.0j * dt) * _onsite_hamiltonian(h_onsite[:, site]))
        state = state.apply_site_gate(site, evolve)
    if h_bond is not None:
        for parity in (0, 1):
            for site in range(parity, n_sites - 1, 2):
                gate = torch.linalg.matrix_exp((2.0j * dt) * _bond_hamiltonian(h_bond[:, site]))
                state = state.apply_bond_gate(site, gate, chi_max=chi_max)
    return state.normalize()


def embed_operator(op: torch.Tensor, start: int, n_sites: int) -> torch.Tensor:
    """Embed a 2^k × 2^k operator on consecutive sites starting at `start`."""
    k = int(round(math.log2(op.shape[-1])))
    left = 2**start
    right = 2 ** (n_sites - start - k)
    eye_l = torch.eye(left, dtype=op.dtype, device=op.device)
    eye_r = torch.eye(right, dtype=op.dtype, device=op.device)
    embedded = torch.einsum("xy,bmj,uv->bxmuyjv", eye_l, op, eye_r)
    dim = 2**n_sites
    return embedded.reshape(op.shape[0], dim, dim)


def reverse_dense_local(
    psi: torch.Tensor,
    h_onsite: torch.Tensor,
    h_bond: torch.Tensor | None,
    axes: torch.Tensor,
    expects: torch.Tensor,
    gamma: float,
    dt: float,
) -> torch.Tensor:
    """Exact 2^N score operator from the same local coefficients. N small only."""
    n_sites = h_onsite.shape[1]
    batch = psi.shape[0]
    dim = 2**n_sites
    device = psi.device
    xyz = _xyz(device)
    identity = torch.eye(dim, dtype=psi.dtype, device=device)
    ham = psi.new_zeros(batch, dim, dim)
    for site in range(n_sites):
        ham = ham + embed_operator(_onsite_hamiltonian(h_onsite[:, site]), site, n_sites)
    if h_bond is not None:
        for site in range(n_sites - 1):
            ham = ham + embed_operator(_bond_hamiltonian(h_bond[:, site]), site, n_sites)
    generator = (2.0j) * ham
    axes_n = axes if axes.dim() == 2 else axes[:, None]
    for site in range(n_sites):
        op = embed_operator(xyz[axes_n[:, site]], site, n_sites)
        delta = op - expects[:, site, None, None] * identity
        generator = generator + (-0.5 * gamma) * (delta @ delta)
    gate = torch.linalg.matrix_exp(generator * dt)
    out = torch.einsum("bij,bj->bi", gate, psi)
    return out / (out.abs() ** 2).sum(dim=-1, keepdim=True).sqrt()


# Projector-splitting TDVP, Haegeman et al., PRB 94, 165116 (2016).
# The legacy projected-gate sweep above is retained ONLY for historical controls.
def local_generator_mpo(mps, h_onsite, h_bond, axes, gamma):
    """Frozen G = 2i H - gamma/2 sum (P-<P>)² as a bond-5 MPO.

    Coefficients and expectations are frozen at the start of the macro step.
    MPO axes are (batch, left, right, physical_out, physical_in).
    """
    xyz = _xyz(mps.device)
    eye = torch.eye(2, device=mps.device, dtype=mps.dtype)
    axes = axes if axes.ndim == 2 else axes[:, None]
    mpo = []
    norm = mps.inner().real
    for i in range(mps.n_sites):
        pauli = xyz[axes[:, i]]
        expect = mps.expect_site(i, pauli) / norm
        delta = pauli - expect[:, None, None] * eye
        onsite = 2j * _onsite_hamiltonian(h_onsite[:, i]) - gamma / 2 * (delta @ delta)
        w = mps.tensors[0].new_zeros(mps.batch, 5, 5, 2, 2)
        w[:, 0, 0] = eye
        w[:, 4, 4] = eye
        w[:, 0, 4] = onsite
        for a in range(3):
            w[:, 0, a + 1] = xyz[a]
            if i > 0 and h_bond is not None:
                w[:, a + 1, 4] = 2j * torch.einsum('ba,aij->bij', h_bond[:, i-1, 3*a:3*a+3].to(mps.dtype), xyz)
        if i == 0:
            w = w[:, :1]
        if i == mps.n_sites - 1:
            w = w[:, :, 4:5]
        mpo.append(w)
    return mpo


def _left_mpo(env, a, w):
    return torch.einsum('bawk,basc,bwvst,bktd->bcvd', env, a.conj(), w, a)


def _right_mpo(env, a, w):
    return torch.einsum('bcvd,basc,bwvst,bktd->bawk', env, a.conj(), w, a)


def _evolve_center(a, left, w, right, dt):
    eff = torch.einsum('bawk,bwvst,bcvd->bascktd', left, w, right)
    dim = a[0].numel()
    gate = torch.linalg.matrix_exp(dt * eff.reshape(a.shape[0], dim, dim))
    return (gate @ a.reshape(a.shape[0], dim, 1)).reshape_as(a)


def _evolve_bond(c, left, right, dt):
    eff = torch.einsum('bawk,bcwd->backd', left, right)
    dim = c[0].numel()
    gate = torch.linalg.matrix_exp(dt * eff.reshape(c.shape[0], dim, dim))
    return (gate @ c.reshape(c.shape[0], dim, 1)).reshape_as(c)


def tdvp_projector_sweep(mps, mpo, dt):
    """First-order left-to-right site-forward / bond-backward sweep.

    Exponentials act only on effective center/bond spaces. Cost depends on
    chi (effective site dimension <= 2 chi²), never directly on 2**N.
    Does not expand bonds. Non-Hermitian frozen generators are supported.
    """
    state = mps.right_canonical()
    tensors = list(state.tensors)
    boundary = tensors[0].new_ones(state.batch, 1, 1, 1)
    right = [None] * (state.n_sites + 1)
    right[-1] = boundary
    for i in range(state.n_sites - 1, -1, -1):
        right[i] = _right_mpo(right[i+1], tensors[i], mpo[i])
    left = boundary
    for i in range(state.n_sites):
        a = _evolve_center(tensors[i], left, mpo[i], right[i+1], dt)
        if i == state.n_sites - 1:
            tensors[i] = a
            break
        q, c = _phase_qr(a.reshape(state.batch, a.shape[1]*2, a.shape[3]))
        tensors[i] = q.reshape(state.batch, a.shape[1], 2, q.shape[-1])
        left = _left_mpo(left, tensors[i], mpo[i])
        c = _evolve_bond(c, left, right[i+1], -dt)
        tensors[i+1] = torch.einsum('bik,bksd->bisd', c, tensors[i+1])
    return BatchMPS(tensors).normalize()


def reverse_tdvp_local(mps, h_onsite, h_bond, axes, gamma, dt,
                       chi_max=None, substeps=1):
    """Projector-splitting TDVP with frozen coefficients per macro step.

    chi_max cannot grow a one-site manifold; explicitly pad/prepare bonds
    before calling if a larger variational space is required.
    """
    if substeps < 1:
        raise ValueError('substeps must be positive')
    if chi_max is not None and mps.max_bond_dim() > chi_max:
        raise ValueError('one-site TDVP cannot enforce a smaller chi_max')
    state = mps.normalize()
    mpo = local_generator_mpo(state, h_onsite, h_bond, axes, gamma)
    for _ in range(substeps):
        state = tdvp_projector_sweep(state, mpo, dt / substeps)
    return state
