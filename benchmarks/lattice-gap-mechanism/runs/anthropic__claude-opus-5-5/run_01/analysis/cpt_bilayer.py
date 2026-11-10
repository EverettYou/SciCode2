"""
Cluster perturbation theory (CPT) for the bilayer one-orbital model
    H = sum T_ij c+c (in-plane t,t' in each layer; t_perp on rungs) + U sum n_up n_dn
        + J_perp sum_rungs (S1.S2 - n1 n2/4)
Cluster: open-boundary Lx x Ly in-plane block, both layers (2*Lx*Ly sites).
Cluster Green's function G_ab(omega) (spin up) from the band (block) Lanczos method.
CPT:  G(k~,w) = [G_c(w)^-1 - V(k~)]^-1 ; periodized over layer-1 sites (t_perp=0 => G_12=0).
"""
import numpy as np
import numba as nb
from ed_hubbard import spin_basis, _popcount, _hop_table, lanczos
from ed_bilayer import BSector, _hv_bilayer


# ------------------------------------------------------------------ cluster geometry
def cluster_geometry(Lx, Ly):
    pos = np.array([(x, y) for y in range(Ly) for x in range(Lx)])  # rung positions
    return pos


def intra_hopping(pos, t, tp, tperp=0.0):
    M = len(pos)
    T = np.zeros((2 * M, 2 * M))
    for i in range(M):
        for j in range(M):
            d = pos[j] - pos[i]
            if abs(d[0]) + abs(d[1]) == 1:
                amp = -t
            elif abs(d[0]) == 1 and abs(d[1]) == 1:
                amp = -tp
            else:
                continue
            for l in range(2):
                T[j + l * M, i + l * M] += amp
    for i in range(M):
        T[i, i + M] += -tperp
        T[i + M, i] += -tperp
    return T


def inter_hopping(pos, Lx, Ly, t, tp, k):
    """V_ab(k) for layer-diagonal in-plane hopping between cluster at 0 and clusters at R."""
    M = len(pos)
    V = np.zeros((M, M), complex)
    for R in [(Lx * a, Ly * b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0)]:
        R = np.array(R)
        ph = np.exp(1j * (k @ R))
        for i in range(M):
            for j in range(M):
                d = pos[j] + R - pos[i]
                if abs(d[0]) + abs(d[1]) == 1:
                    V[i, j] += -t * ph
                elif abs(d[0]) == 1 and abs(d[1]) == 1:
                    V[i, j] += -tp * ph
    return V  # (M x M), same for both layers


# ------------------------------------------------------------------ creation/annihilation on sites
@nb.njit(parallel=True, cache=True)
def _cdag_site(gs, mu_new, lu_old, nd, site, out):
    nu_new = len(mu_new)
    for a2 in nb.prange(nu_new):
        m2 = mu_new[a2]
        if (m2 >> site) & 1:
            m = m2 ^ (1 << site)
            a = lu_old[m]
            sgn = -1.0 if _popcount(m & ((1 << site) - 1)) % 2 else 1.0
            for b in range(nd):
                out[a2, b] = sgn * gs[a, b]
        else:
            for b in range(nd):
                out[a2, b] = 0.0


@nb.njit(parallel=True, cache=True)
def _c_site(gs, mu_new, lu_old, nd, site, out):
    nu_new = len(mu_new)
    for a2 in nb.prange(nu_new):
        m2 = mu_new[a2]
        if not (m2 >> site) & 1:
            m = m2 | (1 << site)
            a = lu_old[m]
            sgn = -1.0 if _popcount(m & ((1 << site) - 1)) % 2 else 1.0
            for b in range(nd):
                out[a2, b] = sgn * gs[a, b]
        else:
            for b in range(nd):
                out[a2, b] = 0.0


# ------------------------------------------------------------------ band Lanczos
def band_lanczos(sec, block, nsteps=80, reorth=True):
    """block: list of vectors (each sec.shape). Returns (R0, Tmat) with
    <phi_a|(z-H)^-1|phi_b> = [R0^T ((z - Tmat)^-1)_{00} R0]_ab."""
    p = len(block)
    dim = sec.dim
    Phi = np.array([b.ravel() for b in block]).T  # dim x p
    Q, R0 = np.linalg.qr(Phi)
    # drop near-zero directions (shouldn't happen for independent c+_i|0>)
    Qs = [Q]
    Qprev = np.zeros_like(Q)
    Bprev = np.zeros((p, p))
    As, Bs = [], []
    W = np.empty_like(Q)
    out = np.empty(sec.shape)
    for j in range(nsteps):
        for c in range(p):
            sec.hv(Q[:, c].reshape(sec.shape), out)
            W[:, c] = out.ravel()
        W -= Qprev @ Bprev.T
        A = Q.T @ W
        A = 0.5 * (A + A.T)
        W -= Q @ A
        if reorth:
            # partial reorthogonalization against last two blocks (cheap stabilization)
            for Qo in Qs[-3:]:
                W -= Qo @ (Qo.T @ W)
        Qn, B = np.linalg.qr(W)
        As.append(A); Bs.append(B)
        Qprev, Q, Bprev = Q, Qn, B
        Qs.append(Q)
        if len(Qs) > 4:
            Qs.pop(0)
        if np.linalg.norm(B) < 1e-10:
            break
    n = len(As)
    Tm = np.zeros((n * p, n * p))
    for j in range(n):
        Tm[j * p:(j + 1) * p, j * p:(j + 1) * p] = As[j]
        if j + 1 < n:
            Tm[(j + 1) * p:(j + 2) * p, j * p:(j + 1) * p] = Bs[j]
            Tm[j * p:(j + 1) * p, (j + 1) * p:(j + 2) * p] = Bs[j].T
    return R0, Tm


def poles_from_band(R0, Tm, p):
    ev, U = np.linalg.eigh(Tm)
    W0 = U[:p, :]  # p x nT
    Res = np.einsum('am,bm->mab', R0.T @ W0, R0.T @ W0)  # residue matrices
    return ev, Res


class ClusterGF:
    """Spin-up cluster Green's function for sites `sites_list` (indices into 2M sites)."""
    def __init__(self, pos, t, tp, U, J, nup, ndn, tperp=0.0, sites_list=None, nsteps=80, verbose=True):
        self.pos = pos; M = len(pos); self.M = M
        T = intra_hopping(pos, t, tp, tperp)
        self.T = T
        sec0 = BSector(M, nup, ndn, T, U, J)
        rng = np.random.default_rng(7)
        ev, a, b, gs = lanczos(sec0, rng.standard_normal(sec0.shape), maxit=400, want_vec=True, nev=1)
        self.E0 = ev[0]
        self.E1 = ev[1]
        if verbose:
            print(f'cluster M={M} N=({nup},{ndn}) E0={ev[0]:.8f} E1-E0={ev[1]-ev[0]:.4e} dim={sec0.dim}', flush=True)
        if sites_list is None:
            sites_list = list(range(2 * M))
        self.sites = sites_list
        p = len(sites_list)
        # particle part
        secp = BSector(M, nup + 1, ndn, T, U, J)
        blk = []
        for s in sites_list:
            v = np.empty(secp.shape)
            _cdag_site(gs, secp.mu, sec0.lu, sec0.shape[1], s, v)
            blk.append(v)
        R0, Tm = band_lanczos(secp, blk, nsteps=nsteps)
        self.ep, self.Rp = poles_from_band(R0, Tm, p)
        self.ep = self.ep - self.E0
        # hole part
        if nup > 0:
            secm = BSector(M, nup - 1, ndn, T, U, J)
            blk = []
            for s in sites_list:
                v = np.empty(secm.shape)
                _c_site(gs, secm.mu, sec0.lu, sec0.shape[1], s, v)
                blk.append(v)
            R0, Tm = band_lanczos(secm, blk, nsteps=nsteps)
            em, Rm = poles_from_band(R0, Tm, p)
            self.em = self.E0 - em  # hole excitation energies (negative side)
            self.Rm = Rm
        else:
            self.em = np.zeros(0); self.Rm = np.zeros((0, p, p))
        # sum rules
        self.weight_p = np.einsum('maa->a', self.Rp).real
        self.weight_m = np.einsum('maa->a', self.Rm).real
        if verbose:
            print('   particle weights', np.round(self.weight_p, 4), ' hole weights', np.round(self.weight_m, 4), flush=True)
        # gap
        self.mu_plus = self.ep.min() if len(self.ep) else np.nan

    def G(self, z):
        """z: complex scalar (omega measured from 0 of energy differences, i.e. absolute excitation energies)."""
        return (np.einsum('mab,m->ab', self.Rp, 1.0 / (z - self.ep)) +
                np.einsum('mab,m->ab', self.Rm, 1.0 / (z - self.em)))

    def save(self, fn):
        np.savez(fn, ep=self.ep, Rp=self.Rp, em=self.em, Rm=self.Rm, E0=self.E0, E1=self.E1,
                 pos=self.pos, sites=np.array(self.sites))


class CPT:
    def __init__(self, cgf=None, fn=None, Lx=None, Ly=None, t=1.0, tp=0.2):
        if fn is not None:
            d = np.load(fn)
            self.ep, self.Rp, self.em, self.Rm = d['ep'], d['Rp'], d['em'], d['Rm']
            self.pos = d['pos']; self.sites = list(d['sites'])
        else:
            self.ep, self.Rp, self.em, self.Rm = cgf.ep, cgf.Rp, cgf.em, cgf.Rm
            self.pos = cgf.pos; self.sites = cgf.sites
        self.M = len(self.pos)
        self.Lx, self.Ly, self.t, self.tp = Lx, Ly, t, tp
        # only layer-1 sites are used (t_perp=0 => layer-diagonal); sites list must start with 0..M-1
        assert list(self.sites[:self.M]) == list(range(self.M))

    def Gc(self, z):
        M = self.M
        Gp = np.einsum('mab,m->ab', self.Rp[:, :M, :M], 1.0 / (z - self.ep))
        Gm = np.einsum('mab,m->ab', self.Rm[:, :M, :M], 1.0 / (z - self.em))
        return Gp + Gm

    def Gk(self, k, z, Gc_inv=None):
        if Gc_inv is None:
            Gc_inv = np.linalg.inv(self.Gc(z))
        V = inter_hopping(self.pos, self.Lx, self.Ly, self.t, self.tp, np.asarray(k, float))
        Gcpt = np.linalg.inv(Gc_inv - V)
        ph = np.exp(1j * (self.pos @ np.asarray(k, float)))
        return (ph.conj() @ Gcpt @ ph) / self.M
