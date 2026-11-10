"""
Exact diagonalization of the single-band t-t'-U Hubbard model on periodic square-lattice clusters.

H = sum_{ij,s} T_ij c^+_{is} c_{js} + U sum_i n_{i,up} n_{i,dn}
with T_ij = -t (nearest neighbours), -t' (next-nearest neighbours).

Fermion ordering: all up operators (ascending site) to the left of all down operators.
State index = a*nd + b with a = up-configuration index, b = down-configuration index.
H.v is applied matrix-free in the Kronecker-sum form  T_up (x) 1 + 1 (x) T_dn + U D.
"""
import numpy as np
import numba as nb
from math import comb

# ----------------------------------------------------------------------------- cluster
def make_cluster(a1, a2):
    """Periodic cluster spanned by integer vectors a1, a2 on the square lattice.
    Returns site coordinates (Ns,2), a function to reduce coordinates to site index,
    and the list of allowed cluster momenta K (Ns,2)."""
    a1 = np.array(a1); a2 = np.array(a2)
    Ns = abs(a1[0] * a2[1] - a1[1] * a2[0])
    # reciprocal vectors b1, b2 with a_i . b_j = 2 pi delta_ij
    A = np.array([a1, a2], float)
    B = 2 * np.pi * np.linalg.inv(A).T
    # enumerate sites: lattice points in the parallelogram
    sites = []
    rng = range(-30, 31)
    for x in rng:
        for y in rng:
            f = np.linalg.solve(A.T, np.array([x, y], float))
            if np.all(f >= -1e-9) and np.all(f < 1 - 1e-9):
                sites.append((x, y))
    sites = np.array(sites)
    assert len(sites) == Ns, (len(sites), Ns)

    def reduce(r):
        f = np.linalg.solve(A.T, np.array(r, float))
        f = f - np.floor(f + 1e-9)
        rr = np.rint(A.T @ f).astype(int)
        idx = np.where((sites[:, 0] == rr[0]) & (sites[:, 1] == rr[1]))[0]
        assert len(idx) == 1
        return idx[0]

    # momenta: K = m1 b1/?... use K such that exp(i K.a1)=exp(i K.a2)=1 -> K = n1 b1 + n2 b2 with
    # integer n's; enumerate Ns inequivalent ones by brute force in the first BZ
    Ks = []
    for n1 in range(-Ns, Ns + 1):
        for n2 in range(-Ns, Ns + 1):
            K = n1 * B[0] + n2 * B[1]
            Kr = (K + np.pi) % (2 * np.pi) - np.pi
            if not any(np.allclose(Kr, k2) for k2 in Ks):
                Ks.append(Kr)
    Ks = np.array(Ks)
    assert len(Ks) == Ns
    return sites, reduce, Ks


def hopping_matrix(sites, reduce, t, tp, tpp=0.0):
    Ns = len(sites)
    T = np.zeros((Ns, Ns))
    nn = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    nnn = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    n3 = [(2, 0), (-2, 0), (0, 2), (0, -2)]
    for i, r in enumerate(sites):
        for d in nn:
            T[reduce(r + np.array(d)), i] += -t
        for d in nnn:
            T[reduce(r + np.array(d)), i] += -tp
        if tpp != 0.0:
            for d in n3:
                T[reduce(r + np.array(d)), i] += -tpp
    assert np.allclose(T, T.T)
    return T

# ----------------------------------------------------------------------------- basis
def spin_basis(Ns, n):
    masks = np.array([m for m in range(1 << Ns) if bin(m).count('1') == n], dtype=np.int64)
    lookup = -np.ones(1 << Ns, dtype=np.int64)
    lookup[masks] = np.arange(len(masks))
    return masks, lookup


@nb.njit(cache=True)
def _popcount(x):
    c = 0
    while x:
        x &= x - 1
        c += 1
    return c


@nb.njit(cache=True)
def _hop_table(masks, lookup, T, Ns):
    n = len(masks)
    # count first
    cnt = np.zeros(n + 1, dtype=np.int64)
    for s in range(n):
        m = masks[s]
        c = 0
        for i in range(Ns):
            for j in range(Ns):
                if i != j and T[i, j] != 0.0:
                    if (m >> j) & 1 and not (m >> i) & 1:
                        c += 1
        cnt[s + 1] = c
    ptr = np.cumsum(cnt)
    idx = np.empty(ptr[-1], dtype=np.int64)
    val = np.empty(ptr[-1], dtype=np.float64)
    for s in range(n):
        m = masks[s]
        p = ptr[s]
        for i in range(Ns):
            for j in range(Ns):
                if i != j and T[i, j] != 0.0:
                    if (m >> j) & 1 and not (m >> i) & 1:
                        lo = min(i, j); hi = max(i, j)
                        between = ((1 << hi) - 1) ^ ((1 << (lo + 1)) - 1)
                        sgn = -1.0 if _popcount(m & between) % 2 else 1.0
                        m2 = (m ^ (1 << j)) | (1 << i)
                        idx[p] = lookup[m2]
                        val[p] = T[i, j] * sgn
                        p += 1
    return ptr, idx, val


@nb.njit(parallel=True, cache=True)
def _hv(V, out, up_ptr, up_idx, up_val, dn_ptr, dn_idx, dn_val, dblocc, U):
    nu, nd = V.shape
    for a in nb.prange(nu):
        for b in range(nd):
            acc = U * dblocc[a, b] * V[a, b]
            for p in range(dn_ptr[b], dn_ptr[b + 1]):
                acc += dn_val[p] * V[a, dn_idx[p]]
            out[a, b] = acc
        for p in range(up_ptr[a], up_ptr[a + 1]):
            a2 = up_idx[p]
            val = up_val[p]
            for b in range(nd):
                out[a, b] += val * V[a2, b]


@nb.njit(parallel=True, cache=True)
def _dblocc(mu, md):
    nu = len(mu); nd = len(md)
    D = np.empty((nu, nd), dtype=np.int8)
    for a in nb.prange(nu):
        for b in range(nd):
            D[a, b] = _popcount(mu[a] & md[b])
    return D


class Sector:
    def __init__(self, Ns, nup, ndn, T, U):
        self.Ns, self.nup, self.ndn, self.U = Ns, nup, ndn, U
        self.mu, self.lu = spin_basis(Ns, nup)
        self.md, self.ld = spin_basis(Ns, ndn)
        self.up = _hop_table(self.mu, self.lu, T, Ns)
        self.dn = _hop_table(self.md, self.ld, T, Ns)
        self.D = _dblocc(self.mu, self.md)
        self.shape = (len(self.mu), len(self.md))
        self.dim = self.shape[0] * self.shape[1]

    def hv(self, V, out=None):
        if out is None:
            out = np.empty_like(V)
        _hv(V, out, self.up[0], self.up[1], self.up[2], self.dn[0], self.dn[1], self.dn[2],
            self.D, float(self.U))
        return out

# ----------------------------------------------------------------------------- Lanczos
def lanczos(sec, v0, maxit=300, tol=1e-10, want_vec=False, verbose=False, nev=1):
    """Plain Lanczos. Returns (evals, alphas, betas[, ground-state vector])."""
    v = v0 / np.sqrt(np.vdot(v0, v0).real)
    vprev = np.zeros_like(v)
    alphas, betas = [], []
    beta = 0.0
    w = np.empty_like(v)
    E_old = None
    for it in range(maxit):
        sec.hv(v, w)
        alpha = np.vdot(v, w).real
        w -= alpha * v + beta * vprev
        alphas.append(alpha)
        beta = np.sqrt(np.vdot(w, w).real)
        if it >= 2:
            Tm = np.diag(alphas) + np.diag(betas, 1) + np.diag(betas, -1)
            ev = np.linalg.eigvalsh(Tm)
            E = ev[:nev]
            if E_old is not None and np.all(np.abs(E - E_old) < tol) and it > 20:
                break
            E_old = E
        if beta < 1e-12:
            break
        betas.append(beta)
        vprev, v = v, w / beta
        w = np.empty_like(v)
    alphas = np.array(alphas); betas = np.array(betas[:len(alphas) - 1])
    Tm = np.diag(alphas) + np.diag(betas, 1) + np.diag(betas, -1)
    ev, evec = np.linalg.eigh(Tm)
    if verbose:
        print(f'   Lanczos {len(alphas)} its, E0={ev[0]:.10f}')
    if not want_vec:
        return ev, alphas, betas
    # second pass to build ground-state vector
    c = evec[:, 0]
    v = v0 / np.sqrt(np.vdot(v0, v0).real)
    vprev = np.zeros_like(v)
    gs = c[0] * v
    w = np.empty_like(v)
    for it in range(len(alphas) - 1):
        sec.hv(v, w)
        w -= alphas[it] * v + (betas[it - 1] if it > 0 else 0.0) * vprev
        vprev, v = v, w / betas[it]
        w = np.empty_like(v)
        gs += c[it + 1] * v
    gs /= np.sqrt(np.vdot(gs, gs).real)
    return ev, alphas, betas, gs


def ground_state(sec, seed=1, maxit=400, want_vec=True, verbose=False, nev=1):
    rng = np.random.default_rng(seed)
    v0 = rng.standard_normal(sec.shape)
    return lanczos(sec, v0, maxit=maxit, want_vec=want_vec, verbose=verbose, nev=nev)

# ----------------------------------------------------------------------------- creation ops
@nb.njit(parallel=True, cache=True)
def _apply_cdag_up(gs, mu, md, lu_new, nd, phase, Ns, out):
    """out = sum_j phase_j c^+_{j,up} gs   (gs in sector (nup,ndn); out in (nup+1, ndn))"""
    nu = len(mu)
    for a in nb.prange(nu):
        m = mu[a]
        for j in range(Ns):
            if not (m >> j) & 1:
                sgn = -1.0 if _popcount(m & ((1 << j) - 1)) % 2 else 1.0
                a2 = lu_new[m | (1 << j)]
                ph = phase[j] * sgn
                for b in range(nd):
                    out[a2, b] += ph * gs[a, b]


@nb.njit(parallel=True, cache=True)
def _apply_c_up(gs, mu_new, md, lu_old, nd, phase, Ns, out):
    """out = sum_j phase_j c_{j,up} gs  ; loop over target states to avoid races"""
    nu_new = len(mu_new)
    for a2 in nb.prange(nu_new):
        m2 = mu_new[a2]
        for j in range(Ns):
            if not (m2 >> j) & 1:
                m = m2 | (1 << j)
                sgn = -1.0 if _popcount(m & ((1 << j) - 1)) % 2 else 1.0
                a = lu_old[m]
                ph = phase[j] * sgn
                for b in range(nd):
                    out[a2, b] += ph * gs[a, b]


def apply_cdag_k(sec, sec_p, gs, K, sites):
    """c^+_{K,up} |gs> = 1/sqrt(Ns) sum_j e^{i K.r_j} c^+_{j up} |gs>"""
    Ns = sec.Ns
    phase = np.exp(1j * (sites @ K)) / np.sqrt(Ns)
    out = np.zeros(sec_p.shape, dtype=np.complex128)
    # race-free version: loop over target configurations
    _apply_cdag_up_safe(gs.astype(np.complex128), sec_p.mu, sec.lu, sec.shape[1], phase, Ns, out)
    return out


@nb.njit(parallel=True, cache=True)
def _apply_cdag_up_safe(gs, mu_new, lu_old, nd, phase, Ns, out):
    nu_new = len(mu_new)
    for a2 in nb.prange(nu_new):
        m2 = mu_new[a2]
        for j in range(Ns):
            if (m2 >> j) & 1:
                m = m2 ^ (1 << j)
                a = lu_old[m]
                sgn = -1.0 if _popcount(m & ((1 << j) - 1)) % 2 else 1.0
                ph = phase[j] * sgn
                for b in range(nd):
                    out[a2, b] += ph * gs[a, b]


def apply_c_k(sec, sec_m, gs, K, sites):
    """c_{K,up} |gs> = 1/sqrt(Ns) sum_j e^{-i K.r_j} c_{j up} |gs>"""
    Ns = sec.Ns
    phase = np.exp(-1j * (sites @ K)) / np.sqrt(Ns)
    out = np.zeros(sec_m.shape, dtype=np.complex128)
    _apply_c_up(gs.astype(np.complex128), sec_m.mu, sec.md, sec.lu, sec.shape[1], phase, Ns, out)
    return out


def cont_frac_coeffs(sec, phi, maxit=200):
    norm2 = np.vdot(phi, phi).real
    ev, a, b = lanczos(sec, phi, maxit=maxit, tol=1e-13)
    return norm2, a, b


def cont_frac_eval(z, norm2, a, b, sign=+1, E0=0.0):
    """Particle: G = norm2/(z - (a0-E0) - b1^2/(z - (a1-E0) - ...))   (sign=+1)
       Hole:     G = norm2/(z + (a0-E0) - b1^2/(z + (a1-E0) - ...))   (sign=-1)"""
    n = len(a)
    g = np.zeros_like(z)
    for i in range(n - 1, -1, -1):
        bb = b[i] ** 2 if i < len(b) else 0.0
        if i == n - 1:
            g = z - sign * (a[i] - E0)
        else:
            g = z - sign * (a[i] - E0) - b[i] ** 2 / g
    return norm2 / g


if __name__ == '__main__':
    # self-tests
    # 1) U=0: ground state = filled Fermi sea
    sites, red, Ks = make_cluster((4, 0), (0, 4))
    T = hopping_matrix(sites, red, 1.0, 0.2)
    eps = np.linalg.eigvalsh(T)
    for (nu_, nd_) in [(3, 3), (5, 5)]:
        sec = Sector(16, nu_, nd_, T, 0.0)
        ev, *_ = ground_state(sec, want_vec=False)
        print('U=0 check', nu_, nd_, ev[0], eps[:nu_].sum() + eps[:nd_].sum())
    # 2) two-site Hubbard: E0 = U/2 - sqrt(U^2/4 + 4 t^2)
    T2 = np.array([[0, -1.0], [-1.0, 0]])
    for U in [4.0, -4.0]:
        sec = Sector(2, 1, 1, T2, U)
        ev, *_ = ground_state(sec, want_vec=False)
        print('2-site check U=', U, ev[0], U / 2 - np.sqrt(U ** 2 / 4 + 4))
