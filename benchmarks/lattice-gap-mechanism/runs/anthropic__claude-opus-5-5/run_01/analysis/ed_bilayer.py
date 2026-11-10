"""
Exact diagonalization of a bilayer one-orbital model on periodic clusters:

H = sum_{ij,l,s} T_ij c^+_{ils} c_{jls}              (in-plane t, t'; same in both layers)
  + t_perp sum_{i,s} (c^+_{i1s} c_{i2s} + h.c.)
  + U sum_{i,l} n_{il,up} n_{il,dn}
  + J_perp sum_i ( S_{i1}.S_{i2} - n_{i1} n_{i2}/4 )

Site index: s = r + l*M  (r = rung 0..M-1, l = 0,1).  Fermion ordering: all up operators first.
The rung term is applied matrix-free:
   diagonal:    -J/2 sum_r ( n_{r1u} n_{r2d} + n_{r1d} n_{r2u} )
   off-diagonal: J/2 sum_r ( S+_{r1} S-_{r2} + h.c. ),  S+_1 S-_2 = -(c+_{1u} c_{2u})(c+_{2d} c_{1d})
"""
import numpy as np
import numba as nb
from ed_hubbard import (make_cluster, spin_basis, _popcount, _hop_table, lanczos,
                        cont_frac_eval)


def bilayer_hopping(sites, reduce, t, tp, tperp=0.0):
    M = len(sites)
    Ns = 2 * M
    T = np.zeros((Ns, Ns))
    nn = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    nnn = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for l in range(2):
        for i, r in enumerate(sites):
            for d in nn:
                T[reduce(r + np.array(d)) + l * M, i + l * M] += -t
            for d in nnn:
                T[reduce(r + np.array(d)) + l * M, i + l * M] += -tp
    for i in range(M):
        T[i, i + M] += -tperp
        T[i + M, i] += -tperp
    assert np.allclose(T, T.T)
    return T


@nb.njit(parallel=True, cache=True)
def _hv_bilayer(V, out, up_ptr, up_idx, up_val, dn_ptr, dn_idx, dn_val,
                mu, md, lu, ld, U, J, M):
    nu, nd = V.shape
    lowmask = (1 << M) - 1
    for a in nb.prange(nu):
        ma = mu[a]
        up1 = ma & lowmask
        up2 = (ma >> M) & lowmask
        for b in range(nd):
            mb = md[b]
            dn1 = mb & lowmask
            dn2 = (mb >> M) & lowmask
            diag = U * _popcount(ma & mb) - 0.5 * J * (_popcount(up1 & dn2) + _popcount(dn1 & up2))
            acc = diag * V[a, b]
            for p in range(dn_ptr[b], dn_ptr[b + 1]):
                acc += dn_val[p] * V[a, dn_idx[p]]
            # rung spin flips (target (a,b) <- source obtained by applying the term)
            if J != 0.0:
                for r in range(M):
                    s1 = r
                    s2 = r + M
                    # term A: S+_1 S-_2 acting on (a,b): needs up at s2 (not s1), dn at s1 (not s2)
                    # term B: S-_1 S+_2 : needs up at s1 (not s2), dn at s2 (not s1)
                    for term in range(2):
                        if term == 0:
                            src_u = s2; dst_u = s1; src_d = s1; dst_d = s2
                        else:
                            src_u = s1; dst_u = s2; src_d = s2; dst_d = s1
                        if ((ma >> src_u) & 1) and not ((ma >> dst_u) & 1) and \
                           ((mb >> src_d) & 1) and not ((mb >> dst_d) & 1):
                            lo = min(s1, s2); hi = max(s1, s2)
                            between = ((1 << hi) - 1) ^ ((1 << (lo + 1)) - 1)
                            su = -1.0 if _popcount(ma & between) % 2 else 1.0
                            sd = -1.0 if _popcount(mb & between) % 2 else 1.0
                            ma2 = (ma ^ (1 << src_u)) | (1 << dst_u)
                            mb2 = (mb ^ (1 << src_d)) | (1 << dst_d)
                            acc += -0.5 * J * su * sd * V[lu[ma2], ld[mb2]]
            out[a, b] = acc
        for p in range(up_ptr[a], up_ptr[a + 1]):
            a2 = up_idx[p]
            val = up_val[p]
            for b in range(nd):
                out[a, b] += val * V[a2, b]


class BSector:
    def __init__(self, M, nup, ndn, T, U, J):
        self.M = M
        self.Ns = Ns = 2 * M
        self.nup, self.ndn, self.U, self.J = nup, ndn, U, J
        self.mu, self.lu = spin_basis(Ns, nup)
        self.md, self.ld = spin_basis(Ns, ndn)
        self.up = _hop_table(self.mu, self.lu, T, Ns)
        self.dn = _hop_table(self.md, self.ld, T, Ns)
        self.shape = (len(self.mu), len(self.md))
        self.dim = self.shape[0] * self.shape[1]

    def hv(self, V, out=None):
        if out is None:
            out = np.empty_like(V)
        _hv_bilayer(V, out, self.up[0], self.up[1], self.up[2], self.dn[0], self.dn[1], self.dn[2],
                    self.mu, self.md, self.lu, self.ld, float(self.U), float(self.J), self.M)
        return out


def ground_state(sec, seed=1, maxit=500, want_vec=True, nev=1):
    rng = np.random.default_rng(seed)
    v0 = rng.standard_normal(sec.shape)
    return lanczos(sec, v0, maxit=maxit, want_vec=want_vec, nev=nev)


if __name__ == '__main__':
    # tests: (1) single rung, t=0: two electrons -> singlet energy -J (U large)
    sites, red, Ks = make_cluster((1, 0), (0, 1))  # 1 rung
    T = np.zeros((2, 2))
    for U, J in [(10.0, 4.0), (0.0, 4.0), (3.0, 5.0)]:
        sec = BSector(1, 1, 1, T, U, J)
        H = np.zeros((sec.dim, sec.dim))
        for i in range(sec.dim):
            e = np.zeros(sec.dim); e[i] = 1
            H[:, i] = sec.hv(e.reshape(sec.shape)).ravel()
        ev = np.linalg.eigvalsh(H)
        print('rung test U,J=', U, J, 'spectrum', np.round(ev, 6), ' expect singlet -J =', -J,
              'triplet 0 (x3?), doublons U')
    # Sz=1 sector (2 up): triplet energy 0
    sec = BSector(1, 2, 0, T, 3.0, 5.0)
    print('Sz=1 dim', sec.dim)
    # (2) U=J=0 free fermions on a 2x2-rung... check vs single-particle
    sites, red, Ks = make_cluster((3, 1), (-1, 3))
    T = bilayer_hopping(sites, red, 1.0, 0.2, 0.3)
    eps = np.linalg.eigvalsh(T)
    sec = BSector(len(sites), 3, 3, T, 0.0, 0.0)
    ev, *_ = ground_state(sec, want_vec=False)
    print('free check', ev[0], 2 * eps[:3].sum())
    # (3) Heisenberg check: large U, J only on rungs, t=0 -> all rungs singlets -> E = -J*M
    T0 = np.zeros_like(T)
    sec = BSector(len(sites), 5, 5, T0, 50.0, 3.0)
    ev, *_ = ground_state(sec, want_vec=False)
    print('rung-singlet product check', ev[0], -3.0 * len(sites))
