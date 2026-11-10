"""Phase stiffness (Drude/superfluid weight) of the bilayer model from twisted boundary conditions:
in-plane hopping along displacement d acquires exp(i A.d) with A = (alpha, 0) (same in both layers).
D = (1/M) d^2 E0 / d alpha^2  (M = number of rungs), evaluated by finite differences.
For a paired state the response is carried by charge-2e rung pairs; in the rung-singlet insulator D ~ 0."""
import numpy as np, sys, time
import numba as nb
from ed_hubbard import make_cluster, spin_basis, _popcount, lanczos
from ed_bilayer import _hv_bilayer


def bilayer_hopping_twist(sites, reduce, t, tp, alpha):
    M = len(sites); Ns = 2 * M
    T = np.zeros((Ns, Ns), complex)
    nn = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    nnn = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for l in range(2):
        for i, r in enumerate(sites):
            for d, amp in [(d, -t) for d in nn] + [(d, -tp) for d in nnn]:
                j = reduce(r + np.array(d))
                # c+_j c_i : electron hops from i to j along d -> phase exp(i alpha d_x)
                T[j + l * M, i + l * M] += amp * np.exp(1j * alpha * d[0])
    assert np.allclose(T, T.conj().T)
    return T


@nb.njit(cache=True)
def _hop_table_c(masks, lookup, T, Ns):
    n = len(masks)
    cnt = np.zeros(n + 1, dtype=np.int64)
    for s in range(n):
        m = masks[s]; c = 0
        for i in range(Ns):
            for j in range(Ns):
                if i != j and T[i, j] != 0:
                    if (m >> j) & 1 and not (m >> i) & 1:
                        c += 1
        cnt[s + 1] = c
    ptr = np.cumsum(cnt)
    idx = np.empty(ptr[-1], dtype=np.int64)
    val = np.empty(ptr[-1], dtype=np.complex128)
    for s in range(n):
        m = masks[s]; p = ptr[s]
        for i in range(Ns):
            for j in range(Ns):
                if i != j and T[i, j] != 0:
                    if (m >> j) & 1 and not (m >> i) & 1:
                        lo = min(i, j); hi = max(i, j)
                        between = ((1 << hi) - 1) ^ ((1 << (lo + 1)) - 1)
                        sgn = -1.0 if _popcount(m & between) % 2 else 1.0
                        m2 = (m ^ (1 << j)) | (1 << i)
                        # row = source s, entry gives <target|H|source>; _hv uses out[b] += val*V[idx]
                        # so we need <b|H|b'> with b'=idx: store the conjugate-transposed element
                        idx[p] = lookup[m2]
                        val[p] = np.conj(T[i, j]) * sgn
                        p += 1
    return ptr, idx, val


class CSector:
    def __init__(self, M, nup, ndn, T, U, J):
        self.M = M; Ns = 2 * M
        self.U, self.J = U, J
        self.mu, self.lu = spin_basis(Ns, nup)
        self.md, self.ld = spin_basis(Ns, ndn)
        self.up = _hop_table_c(self.mu, self.lu, T, Ns)
        self.dn = _hop_table_c(self.md, self.ld, T, Ns)
        self.shape = (len(self.mu), len(self.md)); self.dim = self.shape[0] * self.shape[1]

    def hv(self, V, out=None):
        if out is None:
            out = np.empty_like(V)
        _hv_bilayer(V, out, self.up[0], self.up[1], self.up[2], self.dn[0], self.dn[1], self.dn[2],
                    self.mu, self.md, self.lu, self.ld, float(self.U), float(self.J), self.M)
        return out


def E0(M, nup, ndn, sites, red, U, J, alpha, tp=0.2):
    T = bilayer_hopping_twist(sites, red, 1.0, tp, alpha)
    sec = CSector(M, nup, ndn, T, U, J)
    rng = np.random.default_rng(11)
    v0 = rng.standard_normal(sec.shape) + 1j * rng.standard_normal(sec.shape)
    ev, *_ = lanczos(sec, v0, maxit=500, tol=1e-12)
    return ev[0]


if __name__ == '__main__':
    U = float(sys.argv[1]); J = float(sys.argv[2]); Nlist = eval(sys.argv[3])
    sites, red, Ks = make_cluster((2, 2), (-2, 2)); M = len(sites)
    h = 0.15
    for N in Nlist:
        n2 = N // 2
        t0 = time.time()
        e = [E0(M, n2, n2, sites, red, U, J, a) for a in (0.0, h, 2 * h)]
        D = (e[2] - 2 * e[1] + e[0]) / h ** 2 / M  # forward 2nd difference (E even in alpha => fine)
        Dc = 2 * (e[1] - e[0]) / h ** 2 / M
        print(f'RESULT U={U} J={J} N={N} nu={N/(4*M):.4f}: E0={e[0]:.6f} D(2nd diff)={D:.4f} D(curv)={Dc:.4f} ({time.time()-t0:.0f}s)', flush=True)
