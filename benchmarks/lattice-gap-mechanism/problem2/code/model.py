"""Bilayer square-lattice t1-t2-J model: geometry and second-quantized term list.

Mode convention (shared by the ED code and the NetKet/VMC code):
    orbital o = layer * n_cell + site,  site = x * Ly + y   (layer in {0,1})
    mode    m = spin_block * n_orb + o,  spin_block 0 = down, 1 = up
This matches NetKet's SpinOrbitalFermions(n_orb, s=1/2) layout.

The Hamiltonian is
    H = -t1 sum_<ij>,l,s (c+_{ils} c_{jls} + h.c.) - t2 sum_<<ij>>,l,s (...)
        + J sum_i S_{i1} . S_{i2}
with S.S = Sz Sz + (S+ S- + S- S+)/2.

A term is (coefficient, ((mode, dagger), ...)) in operator order: the tuple
    ((m1, 1), (m2, 0))  means  c+_{m1} c_{m2}.
"""
from __future__ import annotations

import numpy as np

T1_DEFAULT = 1.0
T2_DEFAULT = 0.2


class Lattice:
    """Lx x Ly bilayer with boundary condition codes per direction:
    'p' periodic, 'a' antiperiodic, 'o' open."""

    def __init__(self, Lx: int, Ly: int, bc: str = "pp"):
        assert len(bc) == 2 and all(c in "pao" for c in bc)
        self.Lx, self.Ly, self.bc = Lx, Ly, bc
        self.n_cell = Lx * Ly
        self.n_orb = 2 * self.n_cell
        self.n_modes = 2 * self.n_orb
        self.nn_bonds, self.nnn_bonds = self._bonds()

    # --- indexing -------------------------------------------------------
    def site(self, x: int, y: int) -> int:
        return (x % self.Lx) * self.Ly + (y % self.Ly)

    def xy(self, s: int) -> tuple[int, int]:
        return s // self.Ly, s % self.Ly

    def orb(self, layer: int, site: int) -> int:
        return layer * self.n_cell + site

    def mode(self, layer: int, site: int, spin_up: int) -> int:
        return (1 if spin_up else 0) * self.n_orb + self.orb(layer, site)

    # --- bonds ----------------------------------------------------------
    def _wrap(self, x: int, y: int):
        """Return (site, phase) for displaced coordinates, or None if the bond
        leaves an open boundary. Phase is -1 for each antiperiodic crossing."""
        phase = 1.0
        for coord, Lc, c in ((x, self.Lx, self.bc[0]), (y, self.Ly, self.bc[1])):
            if coord < 0 or coord >= Lc:
                if c == "o":
                    return None
                if c == "a":
                    phase *= -1.0
        return self.site(x, y), phase

    def _bonds(self):
        nn, nnn = [], []
        seen = set()
        for x in range(self.Lx):
            for y in range(self.Ly):
                i = self.site(x, y)
                for (dx, dy, lst) in ((1, 0, nn), (0, 1, nn), (1, 1, nnn), (1, -1, nnn)):
                    r = self._wrap(x + dx, y + dy)
                    if r is None:
                        continue
                    j, ph = r
                    if j == i:
                        continue  # L=1 degenerate direction
                    key = (min(i, j), max(i, j), dx, dy)
                    if key in seen:
                        continue
                    seen.add(key)
                    lst.append((i, j, ph))
        return nn, nnn

    # --- momenta --------------------------------------------------------
    def kpoints(self):
        """Allowed momenta for the given boundary conditions (open -> None)."""
        ks = []
        shifts = []
        for Lc, c in ((self.Lx, self.bc[0]), (self.Ly, self.bc[1])):
            if c == "o":
                return None
            shifts.append(0.0 if c == "p" else np.pi / Lc)
        for nx in range(self.Lx):
            for ny in range(self.Ly):
                ks.append((2 * np.pi * nx / self.Lx + shifts[0], 2 * np.pi * ny / self.Ly + shifts[1]))
        return np.array(ks)

    def positions(self):
        return np.array([self.xy(s) for s in range(self.n_cell)], dtype=float)


def dispersion(kx, ky, t1=T1_DEFAULT, t2=T2_DEFAULT):
    return -2.0 * t1 * (np.cos(kx) + np.cos(ky)) - 4.0 * t2 * np.cos(kx) * np.cos(ky)


def free_energy_sector(lat: Lattice, n_per_flavor, t1=T1_DEFAULT, t2=T2_DEFAULT):
    """Exact J=0 ground energy with n_per_flavor = dict {(layer, spin_up): N}.
    Returns (energy, shell_gap_info). Works for periodic/antiperiodic BCs."""
    ks = lat.kpoints()
    if ks is None:
        # open boundaries: diagonalize the single-layer hopping matrix
        h = hopping_matrix_single_layer(lat, t1, t2)
        eps = np.linalg.eigvalsh(h)
    else:
        eps = np.sort(dispersion(ks[:, 0], ks[:, 1], t1, t2))
    e = 0.0
    info = {}
    for key, n in n_per_flavor.items():
        e += eps[:n].sum()
        if 0 < n < len(eps):
            info[key] = (float(eps[n - 1]), float(eps[n]))
    return e, info


def hopping_matrix_single_layer(lat: Lattice, t1=T1_DEFAULT, t2=T2_DEFAULT):
    h = np.zeros((lat.n_cell, lat.n_cell))
    for (i, j, ph) in lat.nn_bonds:
        h[i, j] += -t1 * ph
        h[j, i] += -t1 * ph
    for (i, j, ph) in lat.nnn_bonds:
        h[i, j] += -t2 * ph
        h[j, i] += -t2 * ph
    return h


def hamiltonian_terms(lat: Lattice, J: float, t1=T1_DEFAULT, t2=T2_DEFAULT):
    """Return list of (coef, ops) terms for H."""
    terms = []
    for (bonds, t) in ((lat.nn_bonds, t1), (lat.nnn_bonds, t2)):
        if t == 0.0:
            continue
        for (i, j, ph) in bonds:
            for layer in (0, 1):
                for s in (0, 1):
                    a, b = lat.mode(layer, i, s), lat.mode(layer, j, s)
                    terms.append((-t * ph, ((a, 1), (b, 0))))
                    terms.append((-t * ph, ((b, 1), (a, 0))))
    if J != 0.0:
        for i in range(lat.n_cell):
            u1, d1 = lat.mode(0, i, 1), lat.mode(0, i, 0)
            u2, d2 = lat.mode(1, i, 1), lat.mode(1, i, 0)
            # Sz Sz = (n1u - n1d)(n2u - n2d)/4
            for (p, sp) in ((u1, 1.0), (d1, -1.0)):
                for (q, sq) in ((u2, 1.0), (d2, -1.0)):
                    terms.append((0.25 * J * sp * sq, ((p, 1), (p, 0), (q, 1), (q, 0))))
            # (S+_1 S-_2 + S-_1 S+_2)/2 ; S+ = c+_u c_d
            terms.append((0.5 * J, ((u1, 1), (d1, 0), (d2, 1), (u2, 0))))
            terms.append((0.5 * J, ((d1, 1), (u1, 0), (u2, 1), (d2, 0))))
    return terms


# ---------------------------------------------------------------------------
# Observable term lists
# ---------------------------------------------------------------------------
def spin_ops(lat: Lattice, layer: int, site: int):
    """Terms for Sx, Sy (as i*Sy -> we return S+ and S-), Sz of one orbital."""
    u, d = lat.mode(layer, site, 1), lat.mode(layer, site, 0)
    sz = [(0.5, ((u, 1), (u, 0))), (-0.5, ((d, 1), (d, 0)))]
    sp = [(1.0, ((u, 1), (d, 0)))]
    sm = [(1.0, ((d, 1), (u, 0)))]
    return sz, sp, sm


def spin_corr_terms(lat: Lattice, l1: int, i: int, l2: int, j: int):
    """S_{i l1} . S_{j l2} as a term list (works for i==j, l1==l2 too)."""
    terms = []
    u1, d1 = lat.mode(l1, i, 1), lat.mode(l1, i, 0)
    u2, d2 = lat.mode(l2, j, 1), lat.mode(l2, j, 0)
    for (p, sp) in ((u1, 1.0), (d1, -1.0)):
        for (q, sq) in ((u2, 1.0), (d2, -1.0)):
            terms.append((0.25 * sp * sq, ((p, 1), (p, 0), (q, 1), (q, 0))))
    terms.append((0.5, ((u1, 1), (d1, 0), (d2, 1), (u2, 0))))
    terms.append((0.5, ((d1, 1), (u1, 0), (u2, 1), (d2, 0))))
    return terms


def density_corr_terms(lat: Lattice, l1, i, l2, j):
    terms = []
    for s1 in (0, 1):
        for s2 in (0, 1):
            p, q = lat.mode(l1, i, s1), lat.mode(l2, j, s2)
            terms.append((1.0, ((p, 1), (p, 0), (q, 1), (q, 0))))
    return terms


def hop_terms(lat: Lattice, layer: int, spin_up: int, i: int, j: int):
    """c+_{i} c_{j} for the given flavor."""
    return [(1.0, ((lat.mode(layer, i, spin_up), 1), (lat.mode(layer, j, spin_up), 0)))]


def interlayer_pair_terms(lat: Lattice, i: int, j: int):
    """Delta+_i Delta_j with Delta_i = (c_{i1u} c_{i2d} - c_{i1d} c_{i2u})/sqrt2
    (rung singlet pair). Delta+_i = (c+_{i2d} c+_{i1u} - c+_{i2u} c+_{i1d})/sqrt2."""
    terms = []
    a_u1, a_d1, a_u2, a_d2 = (lat.mode(0, i, 1), lat.mode(0, i, 0), lat.mode(1, i, 1), lat.mode(1, i, 0))
    b_u1, b_d1, b_u2, b_d2 = (lat.mode(0, j, 1), lat.mode(0, j, 0), lat.mode(1, j, 1), lat.mode(1, j, 0))
    creators = [(1.0, ((a_d2, 1), (a_u1, 1))), (-1.0, ((a_u2, 1), (a_d1, 1)))]
    annihil = [(1.0, ((b_u1, 0), (b_d2, 0))), (-1.0, ((b_d1, 0), (b_u2, 0)))]
    for (c1, o1) in creators:
        for (c2, o2) in annihil:
            terms.append((0.5 * c1 * c2, o1 + o2))
    return terms


def intralayer_dwave_pair_terms(lat: Lattice, layer: int, i: int, j: int):
    """d-wave singlet pair on bonds around i and j within one layer:
    Delta^d_i = sum_delta f(delta) (c_{i u} c_{i+delta d} - c_{i d} c_{i+delta u})/sqrt2,
    f = +1 for x-bonds, -1 for y-bonds. Returns Delta^d+_i Delta^d_j terms."""
    def nbrs(s):
        x, y = lat.xy(s)
        out = []
        for (dx, dy, f) in ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, -1.0), (0, -1, -1.0)):
            r = lat._wrap(x + dx, y + dy)
            if r is None:
                continue
            out.append((r[0], f * r[1]))
        return out

    terms = []
    for (ia, fa) in nbrs(i):
        for (jb, fb) in nbrs(j):
            # Delta+_{i,ia} = (c+_{ia d} c+_{i u} - c+_{ia u} c+_{i d})/sqrt2
            cre = [(1.0, ((lat.mode(layer, ia, 0), 1), (lat.mode(layer, i, 1), 1))),
                   (-1.0, ((lat.mode(layer, ia, 1), 1), (lat.mode(layer, i, 0), 1)))]
            ann = [(1.0, ((lat.mode(layer, j, 1), 0), (lat.mode(layer, jb, 0), 0))),
                   (-1.0, ((lat.mode(layer, j, 0), 0), (lat.mode(layer, jb, 1), 0)))]
            for (c1, o1) in cre:
                for (c2, o2) in ann:
                    terms.append((0.5 * fa * fb * c1 * c2, o1 + o2))
    return terms


def filling_to_counts(lat: Lattice, nu: float):
    """Electrons per layer per spin for filling nu (per layer, per spin, per site)."""
    n = nu * lat.n_cell
    if abs(n - round(n)) > 1e-9:
        raise ValueError(f"filling {nu} not commensurate with {lat.n_cell} sites")
    return int(round(n))
