"""Exact diagonalization of the bilayer t1-t2-J model in a fixed
(N_layer1, N_layer2, N_up, N_down) sector, using bit-string states and
the Jordan-Wigner convention |n> = prod_{m ascending} (c+_m)^{n_m} |0>.

Used only on small clusters (<= 24 modes) as a reference for the VMC.
"""
from __future__ import annotations

import itertools
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from model import Lattice

_POP8 = np.array([bin(i).count("1") for i in range(256)], dtype=np.int64)


def popcount(x: np.ndarray) -> np.ndarray:
    x = x.astype(np.uint64)
    out = np.zeros(x.shape, dtype=np.int64)
    for k in range(8):
        out += _POP8[((x >> np.uint64(8 * k)) & np.uint64(0xFF)).astype(np.int64)]
    return out


def _subsets(n, k):
    """All k-subsets of range(n) as bitmasks (uint64)."""
    out = []
    for c in itertools.combinations(range(n), k):
        m = 0
        for b in c:
            m |= 1 << b
        out.append(m)
    return np.array(out, dtype=np.uint64)


class Sector:
    """Basis for fixed N1 (layer 0), N2 (layer 1), Nup, Ndn."""

    def __init__(self, lat: Lattice, N1: int, N2: int, Nup: int, Ndn: int):
        self.lat = lat
        nc = lat.n_cell
        states = []
        # flavors: (layer, spin): bit offset = mode(layer, 0, spin)
        for n1u in range(0, nc + 1):
            n1d = N1 - n1u
            n2u = Nup - n1u
            n2d = N2 - n2u
            if min(n1d, n2u, n2d) < 0 or max(n1d, n2u, n2d) > nc:
                continue
            if n1d + n2d != Ndn:
                continue
            blocks = []
            for (layer, s, n) in ((0, 1, n1u), (0, 0, n1d), (1, 1, n2u), (1, 0, n2d)):
                off = lat.mode(layer, 0, s)
                blocks.append(_subsets(nc, n) << np.uint64(off))
            # cartesian product via broadcasting
            tot = blocks[0]
            for b in blocks[1:]:
                tot = (tot[:, None] | b[None, :]).ravel()
            states.append(tot)
        self.states = np.sort(np.concatenate(states)) if states else np.zeros(0, dtype=np.uint64)
        self.dim = len(self.states)

    def index(self, st: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(self.states, st)
        idx = np.minimum(idx, self.dim - 1)
        ok = self.states[idx] == st
        return idx, ok


def apply_term(states: np.ndarray, ops) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Apply an operator string (leftmost op applied last) to bit states.
    Returns (new_states, sign, valid)."""
    st = states.copy()
    sign = np.ones(len(states), dtype=np.int64)
    valid = np.ones(len(states), dtype=bool)
    for (m, dag) in reversed(ops):
        bit = np.uint64(1) << np.uint64(m)
        occ = (st & bit) != 0
        if dag:
            valid &= ~occ
        else:
            valid &= occ
        below = st & (bit - np.uint64(1))
        sign *= np.where(popcount(below) % 2 == 0, 1, -1)
        st = st ^ bit
    return st, sign, valid


def build_operator(sec_out: Sector, sec_in: Sector, terms) -> sp.csr_matrix:
    """Sparse matrix of sum_t coef_t * ops_t mapping sec_in -> sec_out."""
    rows, cols, vals = [], [], []
    for (coef, ops) in terms:
        new, sign, valid = apply_term(sec_in.states, ops)
        idx, ok = sec_out.index(new[valid])
        ok_all = ok
        cols.append(np.nonzero(valid)[0][ok_all])
        rows.append(idx[ok_all])
        vals.append(coef * sign[valid][ok_all])
    if not rows:
        return sp.csr_matrix((sec_out.dim, sec_in.dim))
    rows = np.concatenate(rows)
    cols = np.concatenate(cols)
    vals = np.concatenate(vals).astype(float)
    return sp.csr_matrix((vals, (rows, cols)), shape=(sec_out.dim, sec_in.dim))


def ground_state(H: sp.csr_matrix, k: int = 1, tol=1e-10):
    if H.shape[0] <= 400:
        w, v = np.linalg.eigh(H.toarray())
        return w[:k], v[:, :k]
    w, v = spla.eigsh(H, k=max(k, 2), which="SA", tol=tol)
    order = np.argsort(w)
    return w[order][:k], v[:, order][:, :k]


def expect(sec: Sector, psi: np.ndarray, terms) -> float:
    O = build_operator(sec, sec, terms)
    return float(psi.conj() @ (O @ psi))


def lanczos_spectral(H: sp.csr_matrix, E0: float, phi: np.ndarray, omegas, eta: float,
                     n_lanczos: int = 200, sign: int = +1):
    """Spectral function  -1/pi Im <phi| (w + i eta - sign*(H - E0))^{-1} |phi>
    for sign=+1 (particle/excitation side); for sign=-1 (hole side)
    uses (w + i eta + (H - E0))^{-1}. Lanczos continued fraction."""
    norm2 = float(np.vdot(phi, phi).real)
    if norm2 < 1e-14:
        return np.zeros(len(omegas))
    v = phi / np.sqrt(norm2)
    a, b = [], []
    v_prev = np.zeros_like(v)
    beta = 0.0
    n_l = min(n_lanczos, H.shape[0])
    for it in range(n_l):
        w = H @ v - beta * v_prev
        alpha = float(np.vdot(v, w).real)
        w = w - alpha * v
        a.append(alpha)
        beta = float(np.linalg.norm(w))
        if beta < 1e-12:
            break
        b.append(beta)
        v_prev, v = v, w / beta
    a = np.array(a)
    b = np.array(b)
    out = np.zeros(len(omegas))
    for iw, om in enumerate(omegas):
        z = om + 1j * eta
        # continued fraction from the bottom: G = 1/(z - sign*(a0-E0) - b0^2/(z - sign*(a1-E0) - ...))
        g = 0.0 + 0.0j
        for n in range(len(a) - 1, -1, -1):
            denom = z - sign * (a[n] - E0) - (b[n] ** 2 * g if n < len(b) else 0.0)
            g = 1.0 / denom
        out[iw] = -norm2 * g.imag / np.pi
    return out
