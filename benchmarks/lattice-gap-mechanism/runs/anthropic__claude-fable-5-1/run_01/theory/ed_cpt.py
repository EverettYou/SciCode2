"""Exact diagonalization (Lanczos) of small Hubbard clusters + cluster perturbation theory (CPT).
Hamiltonian: H = -sum_{<ij>} t (c+_i c_j + h.c.) - sum_{<<ij>>} t' (c+_i c_j + h.c.) + U sum_i n_iup n_idn  (open cluster)
Used for: (i) charge gap vs spin gap for U = +12 and U = -12 (sign test),
          (ii) CPT A(k,w) at half filling and zeros of Re G(k, mu_midgap) (Luttinger surface).
"""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spla, itertools, time, sys

def popcount(x):
    x = np.asarray(x, dtype=np.int64)
    c = np.zeros_like(x)
    for i in range(64):
        c += (x >> i) & 1
    return c

class Cluster:
    def __init__(self, Lx, Ly, t=1.0, tp=0.196, U=12.0):
        self.Lx, self.Ly, self.Nc = Lx, Ly, Lx*Ly
        self.t, self.tp, self.U = t, tp, U
        self.pos = np.array([(x, y) for y in range(Ly) for x in range(Lx)], dtype=float)   # site index = x + Lx*y
        # intra-cluster hoppings (open boundary)
        self.hops = []   # (i, j, amplitude) with amplitude = -t or -t'
        for i in range(self.Nc):
            for j in range(i+1, self.Nc):
                d = self.pos[j]-self.pos[i]
                if np.allclose(np.abs(d), [1,0]) or np.allclose(np.abs(d), [0,1]): self.hops.append((i,j,-t))
                elif np.allclose(np.abs(d), [1,1]): self.hops.append((i,j,-tp))
    # ---------- basis for one spin species ----------
    def configs(self, n):
        cs = [sum(1<<b for b in comb) for comb in itertools.combinations(range(self.Nc), n)]
        cs = np.array(sorted(cs), dtype=np.int64)
        idx = {c:i for i,c in enumerate(cs)}
        return cs, idx
    def hop_matrix(self, cs, idx):
        """single-species hopping matrix in the basis cs (fermionic signs included)."""
        rows, cols, vals = [], [], []
        for i, j, amp in self.hops:
            bi, bj = 1<<i, 1<<j
            # c+_i c_j : occupied j, empty i
            m = ((cs & bj) != 0) & ((cs & bi) == 0)
            src = cs[m]; dst = (src ^ bj) | bi
            # sign: remove j: (-1)^{# occupied below j}; then add i: (-1)^{# occupied below i in (src^bj)}
            s1 = popcount(src & (bj-1)); s2 = popcount((src ^ bj) & (bi-1))
            sign = 1 - 2*((s1+s2) % 2)
            rows += [idx[d] for d in dst]; cols += [idx[s_] for s_ in src]; vals += list(amp*sign)
            # hermitian conjugate c+_j c_i
            m = ((cs & bi) != 0) & ((cs & bj) == 0)
            src = cs[m]; dst = (src ^ bi) | bj
            s1 = popcount(src & (bi-1)); s2 = popcount((src ^ bi) & (bj-1))
            sign = 1 - 2*((s1+s2) % 2)
            rows += [idx[d] for d in dst]; cols += [idx[s_] for s_ in src]; vals += list(amp*sign)
        n = len(cs)
        return sp.csr_matrix((vals, (rows, cols)), shape=(n, n))
    def hamiltonian(self, nup, ndn):
        cu, iu = self.configs(nup); cd, idn = self.configs(ndn)
        Hu = self.hop_matrix(cu, iu); Hd = self.hop_matrix(cd, idn)
        # double occupancy count: for state (u, d): popcount(u & d)
        D = popcount(cu[:,None] & cd[None,:]).ravel().astype(float)
        H = sp.kron(Hu, sp.identity(len(cd), format='csr'), format='csr') + sp.kron(sp.identity(len(cu), format='csr'), Hd, format='csr') + sp.diags(self.U*D)
        return H.tocsr(), (cu, iu, cd, idn)
    def ground_state(self, nup, ndn, k=1):
        H, basis = self.hamiltonian(nup, ndn)
        if H.shape[0] <= 400:
            w, v = np.linalg.eigh(H.toarray()); return w[0], v[:,0], basis, H
        w, v = spla.eigsh(H, k=k, which='SA', tol=1e-10, maxiter=5000)
        i = np.argmin(w); return w[i], v[:,i], basis, H
    # ---------- creation/annihilation (spin up) between sectors ----------
    def cdag_up(self, a, basis_from, basis_to):
        """matrix of c+_{a,up} from (nup, ndn) basis to (nup+1, ndn) basis."""
        cu, iu, cd, idn = basis_from; cu2, iu2, cd2, idn2 = basis_to
        ba = 1<<a
        m = (cu & ba) == 0
        src = cu[m]; dst = src | ba
        sign = 1 - 2*(popcount(src & (ba-1)) % 2)
        rows_u = np.array([iu2[d] for d in dst]); cols_u = np.array([iu[s_] for s_ in src])
        Cu = sp.csr_matrix((sign.astype(float), (rows_u, cols_u)), shape=(len(cu2), len(cu)))
        return sp.kron(Cu, sp.identity(len(cd), format='csr'), format='csr')
    def c_up(self, a, basis_from, basis_to):
        """matrix of c_{a,up} from (nup, ndn) to (nup-1, ndn)."""
        cu, iu, cd, idn = basis_from; cu2, iu2, cd2, idn2 = basis_to
        ba = 1<<a
        m = (cu & ba) != 0
        src = cu[m]; dst = src ^ ba
        sign = 1 - 2*(popcount(src & (ba-1)) % 2)
        rows_u = np.array([iu2[d] for d in dst]); cols_u = np.array([iu[s_] for s_ in src])
        Cu = sp.csr_matrix((sign.astype(float), (rows_u, cols_u)), shape=(len(cu2), len(cu)))
        return sp.kron(Cu, sp.identity(len(cd), format='csr'), format='csr')

def lanczos_spectral(H, phi, nmax=200, tol=1e-12):
    """Return (poles, weights) such that <phi|(z-H)^-1|phi> = sum_n weights_n/(z - poles_n)."""
    norm2 = np.vdot(phi, phi).real
    if norm2 < 1e-14: return np.array([]), np.array([])
    v = (phi/np.sqrt(norm2)).astype(float)
    alphas, betas = [], []
    reorth = (len(v) <= 60000)
    V = [v] if reorth else None
    w = H @ v
    a = float(v @ w); alphas.append(a)
    w = w - a*v
    for n in range(1, nmax):
        b = np.linalg.norm(w)
        if b < tol: break
        betas.append(b)
        v_new = w/b
        if reorth:
            for u in V: v_new -= (u @ v_new)*u
            v_new /= np.linalg.norm(v_new)
            V.append(v_new)
        w = H @ v_new - b*v
        a = float(v_new @ w); alphas.append(a)
        w = w - a*v_new
        v = v_new
    T = np.diag(alphas) + np.diag(betas, 1) + np.diag(betas, -1)
    ev, evec = np.linalg.eigh(T)
    weights = norm2*np.abs(evec[0,:])**2
    return ev, weights

def lehmann_matrix(H, Phis, nblocks=60, exact_dim=9000, verbose=False):
    """Matrix spectral representation of <phi_a|(z-H)^-1|phi_b>: returns (poles eps_n, Q[a,n]) with
    G_ab(z) = sum_n Q[a,n] Q[b,n] / (z - eps_n)   (real symmetric case).
    Exact diagonalisation if dim <= exact_dim, otherwise block Lanczos with full orthogonalisation."""
    Phis = np.array([np.asarray(p, dtype=float) for p in Phis])           # (Nc, dim)
    dim = H.shape[0]
    if dim <= exact_dim:
        ev, U = np.linalg.eigh(H.toarray())
        Q = Phis @ U                                                        # <phi_a|n>
        return ev, Q
    # block Lanczos
    Nc = Phis.shape[0]
    Vs = []                                                                 # orthonormal Krylov basis vectors
    # orthonormalise the starting block
    B, _ = np.linalg.qr(Phis.T)                                             # (dim, Nc)
    for j in range(B.shape[1]): Vs.append(B[:, j].copy())
    W = H @ B
    for blk in range(1, nblocks):
        # project out all previous vectors (full orthogonalisation, twice for stability)
        Vmat = np.array(Vs).T
        for _ in range(2):
            W = W - Vmat @ (Vmat.T @ W)
        Bn, R = np.linalg.qr(W)
        # drop (near-)dependent directions
        keep = np.abs(np.diag(R)) > 1e-8
        if not keep.any(): break
        Bn = Bn[:, keep]
        for j in range(Bn.shape[1]): Vs.append(Bn[:, j].copy())
        W = H @ Bn
        if verbose and blk % 10 == 0: print(f"      block {blk}, Krylov dim {len(Vs)}", flush=True)
    Vmat = np.array(Vs).T                                                   # (dim, K)
    T = Vmat.T @ (H @ Vmat); T = 0.5*(T + T.T)
    ev, S = np.linalg.eigh(T)
    Q = (Phis @ Vmat) @ S                                                   # <phi_a|n> in the Krylov space
    return ev, Q

class CPT:
    def __init__(self, cl, nup, ndn, nlanczos=150, nblocks=60, verbose=True):
        self.cl = cl; t0 = time.time()
        E0, psi0, basis0, H0 = cl.ground_state(nup, ndn)
        self.E0 = E0; self.basis0 = basis0
        if verbose: print(f"  GS energy (N={nup+ndn}, Sz={(nup-ndn)/2}): {E0:.6f}   dim={H0.shape[0]}   [{time.time()-t0:.1f}s]", flush=True)
        Hp, basisp = cl.hamiltonian(nup+1, ndn); Hm, basism = cl.hamiltonian(nup-1, ndn)
        Nc = cl.Nc
        phis_e = [cl.cdag_up(a, basis0, basisp) @ psi0 for a in range(Nc)]
        phis_h = [cl.c_up(a, basis0, basism) @ psi0 for a in range(Nc)]
        Hp_s = Hp - E0*sp.identity(Hp.shape[0]); Hm_s = Hm - E0*sp.identity(Hm.shape[0])
        # electron part: G^e_ab(z) = <0|c_a (z-(H-E0))^-1 c+_b|0> ; hole part: G^h_ab(z) = <0|c+_b (z+(H-E0))^-1 c_a|0>
        self.eps_e, self.Q_e = lehmann_matrix(Hp_s, phis_e, nblocks, verbose=verbose)
        self.eps_h, self.Q_h = lehmann_matrix(Hm_s, phis_h, nblocks, verbose=verbose)
        if verbose: print(f"  Green's function (exact Lehmann / block Lanczos) computed: {len(self.eps_e)}+{len(self.eps_h)} poles [{time.time()-t0:.1f}s]", flush=True)
        self.Nc = Nc
    def Gc(self, z):
        """cluster Green's function matrix (Nc x Nc) at complex z (frequencies measured from the cluster E0)."""
        Ge = (self.Q_e/(z - self.eps_e)[None,:]) @ self.Q_e.T
        Gh = (self.Q_h/(z + self.eps_h)[None,:]) @ self.Q_h.T
        return Ge + Gh.T
    def V(self, kx, ky):
        """inter-cluster hopping matrix V(k)_{ab} = sum_{R != 0} t(r_a, r_b + R) exp(i k.R)."""
        cl = self.cl; Nc = cl.Nc; V = np.zeros((Nc, Nc), dtype=complex)
        Lx, Ly = cl.Lx, cl.Ly
        for a in range(Nc):
            for b in range(Nc):
                for Rx in (-1,0,1):
                    for Ry in (-1,0,1):
                        if Rx == 0 and Ry == 0: continue
                        R = np.array([Rx*Lx, Ry*Ly]); d = cl.pos[b] + R - cl.pos[a]
                        if np.allclose(np.abs(d),[1,0]) or np.allclose(np.abs(d),[0,1]): amp = -cl.t
                        elif np.allclose(np.abs(d),[1,1]): amp = -cl.tp
                        else: continue
                        V[a,b] += amp*np.exp(1j*(kx*R[0] + ky*R[1]))
        return V
    def G_cpt(self, kx, ky, z):
        """periodized CPT Green's function at lattice momentum (kx,ky) and complex frequency z."""
        Gc = self.Gc(z); Ginv = np.linalg.inv(Gc)
        Gk = np.linalg.inv(Ginv - self.V(kx, ky))
        ph = np.exp(-1j*(kx*self.cl.pos[:,0] + ky*self.cl.pos[:,1]))
        return (ph.conj()[:,None]*ph[None,:]*Gk).sum()/self.cl.Nc   # (1/Nc) sum_ab e^{-ik(ra-rb)} G_ab
    def V_many(self, kxs, kys):
        """stacked inter-cluster hopping matrices (Nk, Nc, Nc) and periodisation phases (Nk, Nc)."""
        cl = self.cl; Nc = cl.Nc; Lx, Ly = cl.Lx, cl.Ly
        kxs = np.asarray(kxs); kys = np.asarray(kys)
        V = np.zeros((len(kxs), Nc, Nc), dtype=complex)
        for a in range(Nc):
            for b in range(Nc):
                for Rx in (-1,0,1):
                    for Ry in (-1,0,1):
                        if Rx == 0 and Ry == 0: continue
                        R = np.array([Rx*Lx, Ry*Ly]); d = cl.pos[b] + R - cl.pos[a]
                        if np.allclose(np.abs(d),[1,0]) or np.allclose(np.abs(d),[0,1]): amp = -cl.t
                        elif np.allclose(np.abs(d),[1,1]): amp = -cl.tp
                        else: continue
                        V[:,a,b] += amp*np.exp(1j*(kxs*R[0] + kys*R[1]))
        ph = np.exp(-1j*(kxs[:,None]*cl.pos[None,:,0] + kys[:,None]*cl.pos[None,:,1]))
        return V, ph
    def G_cpt_many(self, kxs, kys, z, VP=None):
        Gc = self.Gc(z); Ginv = np.linalg.inv(Gc)
        if VP is None: VP = self.V_many(kxs, kys)
        V, ph = VP
        Gk = np.linalg.inv(Ginv[None,:,:] - V)                      # (Nk, Nc, Nc)
        return np.einsum('ka,kab,kb->k', ph.conj(), Gk, ph)/self.cl.Nc

if __name__ == '__main__':
    Lx, Ly = int(sys.argv[1]), int(sys.argv[2]); U = float(sys.argv[3])
    cl = Cluster(Lx, Ly, U=U)
    Nc = cl.Nc; n = Nc//2
    t0 = time.time()
    print(f"=== cluster {Lx}x{Ly}, U={U}, t'={cl.tp}")
    E0, psi0, b0, H0 = cl.ground_state(n, n)
    Ep1 = cl.ground_state(n+1, n)[0]; Em1 = cl.ground_state(n-1, n)[0]
    Es1 = cl.ground_state(n+1, n-1)[0]
    print(f"  E0(N)={E0:.5f}  E0(N+1)={Ep1:.5f}  E0(N-1)={Em1:.5f}  E0(N,Sz=1)={Es1:.5f}")
    print(f"  charge gap = {Ep1+Em1-2*E0:.4f}    spin gap (Sz=1 - Sz=0) = {Es1-E0:.4f}   [{time.time()-t0:.1f}s]")
