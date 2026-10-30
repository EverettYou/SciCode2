"""GPU exact diagonalization of the bilayer t1-t2-J model on an Lx x Ly torus.

H = -t1 sum_<ij>,l,s c+ c - t2 sum_<<ij>>,l,s c+ c + J sum_r S_{r,1}.S_{r,2}

The many-body state is stored as a dense matrix Psi[u, d] over up-spin and down-spin
configurations (each a bit mask over the Ns = 2 Lx Ly sites).  Hopping acts as
H_up Psi + Psi H_down^T, the Ising part of J is an element-wise mask, and the spin-flip
part is sum_r A_r Psi B_r^T with sparse single-hop matrices.  Everything runs in torch on
the GPU.  Boundary conditions are periodic or antiperiodic in each direction (real
arithmetic), which gives k grids shifted by half a reciprocal-lattice step.
"""
import numpy as np, scipy.sparse as sp, torch, time, itertools, json, sys, os
from math import comb

def site_index(x, y, l, Lx, Ly):
    return l*Lx*Ly + (y % Ly)*Lx + (x % Lx)

def bonds(Lx, Ly, t1, t2, bc=(1, 1)):
    """Directed bond list (a, b, amp, phase) for ONE layer offset 0; torus convention:
    every (site, displacement) pair is a bond, so for Ly=2 the +y and -y bonds coincide
    (amplitude doubles), which reproduces eps(k) on the allowed k points exactly.
    phase = product of boundary signs crossed."""
    out = []
    disp = [((1, 0), t1), ((-1, 0), t1), ((0, 1), t1), ((0, -1), t1),
            ((1, 1), t2), ((1, -1), t2), ((-1, 1), t2), ((-1, -1), t2)]
    for y in range(Ly):
        for x in range(Lx):
            for (dx, dy), t in disp:
                if t == 0: continue
                ph = 1.0
                if (x+dx) // Lx != 0: ph *= bc[0]
                if (y+dy) // Ly != 0: ph *= bc[1]
                out.append((site_index(x, y, 0, Lx, Ly), site_index(x+dx, y+dy, 0, Lx, Ly), t, ph))
    return out

def all_bonds(Lx, Ly, t1, t2, bc):
    """bonds in both layers: list of (a, b, amp) meaning -amp c+_a c_b (directed; the
    reverse direction appears as its own entry)."""
    b0 = bonds(Lx, Ly, t1, t2, bc)
    out = []
    for l in (0, 1):
        off = l*Lx*Ly
        for a, b, t, ph in b0:
            out.append((a+off, b+off, t*ph))
    return out

def configs(Ns, n):
    """all bit masks with n bits set among Ns, sorted; plus lookup table mask->index"""
    masks = np.array([sum(1 << i for i in c) for c in itertools.combinations(range(Ns), n)], dtype=np.int64)
    masks.sort()
    lut = -np.ones(1 << Ns, dtype=np.int64); lut[masks] = np.arange(len(masks))
    return masks, lut

def popcount_between(masks, a, b):
    lo, hi = (a, b) if a < b else (b, a)
    m = ((1 << hi) - 1) ^ ((1 << (lo+1)) - 1)   # bits strictly between lo and hi
    x = masks & m
    # popcount via bit tricks on int64
    x = x - ((x >> 1) & 0x5555555555555555)
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f
    return (x * 0x0101010101010101 >> 56) & 0x7f

def hop_matrix(masks, lut, a, b, amp):
    """sparse matrix of amp * c+_a c_b in the basis `masks` (same particle number)"""
    occ_b = (masks >> b) & 1; emp_a = 1 - ((masks >> a) & 1)
    sel = np.where((occ_b == 1) & (emp_a == 1))[0]
    if a == b:
        sel = np.where(occ_b == 1)[0]
        return sp.csr_matrix((amp*np.ones(len(sel)), (sel, sel)), shape=(len(masks), len(masks)))
    src = masks[sel]; dst = src ^ (1 << b) ^ (1 << a)
    sign = 1 - 2*(popcount_between(src, a, b) & 1)
    return sp.csr_matrix((amp*sign.astype(float), (lut[dst], sel)), shape=(len(masks), len(masks)))

def create_matrix(masks_from, lut_to, a):
    """sparse matrix of c+_a : basis(n) -> basis(n+1)"""
    emp = ((masks_from >> a) & 1) == 0
    sel = np.where(emp)[0]; src = masks_from[sel]; dst = src | (1 << a)
    sign = 1 - 2*(popcount_between(src, -1, a) & 1)   # bits below a
    nto = int((lut_to >= 0).sum())
    return sp.csr_matrix((sign.astype(float), (lut_to[dst], sel)), shape=(nto, len(masks_from)))

def annihilate_matrix(masks_from, lut_to, a):
    occ = ((masks_from >> a) & 1) == 1
    sel = np.where(occ)[0]; src = masks_from[sel]; dst = src ^ (1 << a)
    sign = 1 - 2*(popcount_between(src, -1, a) & 1)
    nto = int((lut_to >= 0).sum())
    return sp.csr_matrix((sign.astype(float), (lut_to[dst], sel)), shape=(nto, len(masks_from)))

def to_torch(M, device, dtype=torch.float64):
    M = M.tocsr(); M.sum_duplicates()
    return torch.sparse_csr_tensor(torch.from_numpy(M.indptr.astype(np.int64)), torch.from_numpy(M.indices.astype(np.int64)),
                                   torch.from_numpy(M.data.astype(np.float64)).to(dtype), size=M.shape).to(device)

class Sector:
    """Hamiltonian in the (N_up, N_down) sector on the GPU."""
    def __init__(self, Lx, Ly, nup, ndn, t1=1.0, t2=0.2, J=8.0, bc=(1, 1), device='cuda', dtype=torch.float64, lean=False, chunk=4096):
        self.Lx, self.Ly, self.nup, self.ndn, self.t1, self.t2, self.J, self.bc = Lx, Ly, nup, ndn, t1, t2, J, bc
        self.Ns = 2*Lx*Ly; self.Nr = Lx*Ly; self.device = device; self.dtype = dtype
        self.mu, self.lu = configs(self.Ns, nup); self.md, self.ld = configs(self.Ns, ndn)
        self.dim = len(self.mu)*len(self.md)
        bl = all_bonds(Lx, Ly, t1, t2, bc)
        def hopping(masks, lut):
            H = sp.csr_matrix((len(masks), len(masks)))
            for a, b, amp in bl:
                H = H + hop_matrix(masks, lut, a, b, -amp)
            return H
        self._Hu_scipy = hopping(self.mu, self.lu).tocsr(); self._Hd_scipy = hopping(self.md, self.ld).tocsr()
        self.lean = False
        if not lean:
            self.Hu = to_torch(self._Hu_scipy, device, dtype)
        self.Hd = to_torch(self._Hd_scipy, device, dtype)
        # Ising part
        def occ(masks, s): return ((masks >> s) & 1).astype(np.float64)
        nu1 = np.stack([occ(self.mu, r) for r in range(self.Nr)], 1); nu2 = np.stack([occ(self.mu, r+self.Nr) for r in range(self.Nr)], 1)
        nd1 = np.stack([occ(self.md, r) for r in range(self.Nr)], 1); nd2 = np.stack([occ(self.md, r+self.Nr) for r in range(self.Nr)], 1)
        tu = torch.from_numpy; dev = device
        D = (tu((nu1*nu2).sum(1))[:, None] + tu((nd1*nd2).sum(1))[None, :]
             - tu(nu1) @ tu(nd2).T - tu(nu2) @ tu(nd1).T)
        if lean:
            self.D8 = D.round().to(torch.int8)      # exact: D is an integer in [-Nr, Nr]
        else:
            self.D = (0.25*J*D).to(dtype).to(dev)
        # spin flips: -(J/2) [A_r Psi B_r^T + A_r^T Psi B_r], A_r = c+_{r1,up} c_{r2,up}, B_r = c+_{r2,dn} c_{r1,dn}
        self.A, self.B, self._A_scipy = [], [], []
        for r in range(self.Nr):
            A = hop_matrix(self.mu, self.lu, r, r+self.Nr, 1.0); B = hop_matrix(self.md, self.ld, r+self.Nr, r, 1.0)
            self._A_scipy.append(A.tocsr())
            if not lean: self.A.append((to_torch(A, dev, dtype), to_torch(A.T, dev, dtype)))
            self.B.append((to_torch(B, dev, dtype), to_torch(B.T, dev, dtype)))
        if lean: self.build_chunks(chunk)
    def build_chunks(self, chunk=4096):
        """row-chunked copies of the left-acting sparse matrices for the lean matvec"""
        self.chunk = chunk; nu = len(self.mu)
        self.blocks = [(i, min(i+chunk, nu)) for i in range(0, nu, chunk)]
        Hu = self._Hu_scipy
        self.Hu_blocks = [to_torch(Hu[a:b, :], self.device, self.dtype) for a, b in self.blocks]
        self.A_blocks = []
        for A in self._A_scipy:
            self.A_blocks.append(([to_torch(A[a:b, :], self.device, self.dtype) for a, b in self.blocks],
                                  [to_torch(A.T.tocsr()[a:b, :], self.device, self.dtype) for a, b in self.blocks]))
        self.Dint = self.D8.to(self.device)
        self.lean = True
    def matvec_lean(self, P, out=None):
        if out is None: out = torch.empty_like(P)
        J = self.J
        for ib, ((a, b), Hu_b) in enumerate(zip(self.blocks, self.Hu_blocks)):
            ob = torch.sparse.mm(Hu_b, P)                      # (chunk, n_down)
            Pb = P[a:b]
            ob += torch.sparse.mm(self.Hd, Pb.T.contiguous()).T
            ob.addcmul_(self.Dint[a:b].to(self.dtype), Pb, value=0.25*J)
            for (Ablocks, Atblocks), (B, Bt) in zip(self.A_blocks, self.B):
                T = torch.sparse.mm(Ablocks[ib], P)
                ob -= 0.5*J*torch.sparse.mm(B, T.T.contiguous()).T
                T = torch.sparse.mm(Atblocks[ib], P)
                ob -= 0.5*J*torch.sparse.mm(Bt, T.T.contiguous()).T
            out[a:b] = ob
        return out
    def matvec(self, P):
        if getattr(self, 'lean', False): return self.matvec_lean(P)
        out = torch.sparse.mm(self.Hu, P)
        out += torch.sparse.mm(self.Hd, P.T.contiguous()).T
        out += self.D*P
        for (A, At), (B, Bt) in zip(self.A, self.B):
            T = torch.sparse.mm(A, P)
            out -= 0.5*self.J*torch.sparse.mm(B, T.T.contiguous()).T
            T = torch.sparse.mm(At, P)
            out -= 0.5*self.J*torch.sparse.mm(Bt, T.T.contiguous()).T
        return out
    def random_vec(self, seed=0):
        g = torch.Generator(device='cpu').manual_seed(seed)
        v = torch.randn(len(self.mu), len(self.md), generator=g, dtype=self.dtype).to(self.device)
        return v/bnorm(v)

def bdot(v, w, chunk=2048):
    """<v|w> for real tensors of any size (row-chunked to stay below the BLAS 2^31 limit)"""
    s = 0.0
    for a in range(0, v.shape[0], chunk):
        s += float(torch.vdot(v[a:a+chunk].ravel(), w[a:a+chunk].ravel()).real)
    return s
def bnorm(v): return np.sqrt(bdot(v, v))

def lanczos(sec, v0, niter=120, tol=1e-10, want_vec=False, verbose=False):
    """Lanczos ground state; returns (E0, vec or None, alphas, betas).  Two-pass for the vector."""
    def run(v0, store_coef=None):
        v = v0.clone(); vprev = torch.zeros_like(v); beta = 0.0
        al, be = [], []
        E_old = None
        for it in range(niter):
            w = sec.matvec(v)
            alpha = bdot(v, w)
            w.add_(v, alpha=-alpha)
            if beta != 0.0: w.add_(vprev, alpha=-beta)
            beta_new = bnorm(w)
            al.append(alpha); be.append(beta_new)
            if store_coef is not None:
                store_coef['acc'].add_(v, alpha=float(store_coef['y'][it]))
            if beta_new < 1e-12 or it == niter-1:
                break
            T = np.diag(al) + np.diag(be[:-1], 1) + np.diag(be[:-1], -1)
            ev = np.linalg.eigvalsh(T)
            if verbose and it % 10 == 0: print(f'  it {it} E0={ev[0]:.10f}', flush=True)
            if E_old is not None and abs(ev[0]-E_old) < tol and it > 10 and store_coef is None:
                break
            E_old = ev[0]
            w.div_(beta_new); vprev, v = v, w; beta = beta_new
            if store_coef is not None and it+1 >= len(store_coef['y']): break
        return al, be
    al, be = run(v0)
    T = np.diag(al) + np.diag(be[:-1], 1) + np.diag(be[:-1], -1)
    ev, U = np.linalg.eigh(T)
    E0 = ev[0]
    vec = None
    if want_vec:
        y = U[:, 0]
        store = {'y': y, 'acc': torch.zeros_like(v0)}
        run(v0, store_coef=store)
        vec = store['acc']; vec /= bnorm(vec)
    return E0, vec, al, be

def continued_fraction(al, be, norm2, omega, eta):
    """-1/pi Im <phi|(omega - H + i eta)^-1|phi> for the tridiagonal Lanczos matrix (H measured
    however the caller shifts omega); norm2 = <phi|phi>."""
    z = omega + 1j*eta
    n = len(al)
    f = np.zeros_like(z)
    for i in range(n-1, -1, -1):
        b2 = be[i]**2 if i < n-1 else 0.0
        f = 1.0/(z - al[i] - b2*f)
    return -norm2*f.imag/np.pi

def spectral_lanczos(sec_target, phi, niter=150):
    """Lanczos coefficients for the vector phi in the target sector (for continued fraction)."""
    norm2 = bdot(phi, phi)
    if norm2 < 1e-14: return [], [], 0.0
    v = phi/np.sqrt(norm2); vprev = torch.zeros_like(v); beta = 0.0; al, be = [], []
    for it in range(niter):
        w = sec_target.matvec(v)
        alpha = bdot(v, w)
        w.add_(v, alpha=-alpha)
        if beta != 0.0: w.add_(vprev, alpha=-beta)
        bn = bnorm(w); al.append(alpha); be.append(bn)
        if bn < 1e-10: break
        w.div_(bn); vprev, v = v, w; beta = bn
    return al, be, norm2

def poles_from_lanczos(al, be, norm2):
    """eigen-decomposition of the tridiagonal matrix -> (positions, weights)"""
    n = len(al)
    T = np.diag(al) + np.diag(be[:n-1], 1) + np.diag(be[:n-1], -1)
    ev, U = np.linalg.eigh(T)
    return ev, norm2*U[0, :]**2

# ---------- operators that change sector ----------
def apply_cdag(sec_from, sec_to, P, site, spin):
    """c+_{site,spin} Psi : (nup,ndn) -> (nup+1,ndn) or (nup,ndn+1)"""
    if spin == 0:
        C = to_torch(create_matrix(sec_from.mu, sec_to.lu, site), P.device, P.dtype)
        return torch.sparse.mm(C, P)
    else:
        C = to_torch(create_matrix(sec_from.md, sec_to.ld, site), P.device, P.dtype)
        # down operators act after passing the up string: sign (-1)^{N_up}
        sgn = (-1)**sec_from.nup
        return sgn*torch.sparse.mm(C, P.T.contiguous()).T

def apply_c(sec_from, sec_to, P, site, spin):
    if spin == 0:
        C = to_torch(annihilate_matrix(sec_from.mu, sec_to.lu, site), P.device, P.dtype)
        return torch.sparse.mm(C, P)
    else:
        C = to_torch(annihilate_matrix(sec_from.md, sec_to.ld, site), P.device, P.dtype)
        sgn = (-1)**sec_from.nup
        return sgn*torch.sparse.mm(C, P.T.contiguous()).T

def kphase(sec, kx, ky, layer=0):
    """e^{i k.r} for every site of a layer, with r = (x, y); returns arrays (sites, phases)"""
    sites, ph = [], []
    for y in range(sec.Ly):
        for x in range(sec.Lx):
            sites.append(site_index(x, y, layer, sec.Lx, sec.Ly)); ph.append(np.exp(1j*(kx*x+ky*y)))
    return sites, np.array(ph)

def allowed_k(Lx, Ly, bc):
    kx = [2*np.pi*n/Lx + (np.pi/Lx if bc[0] == -1 else 0) for n in range(Lx)]
    ky = [2*np.pi*n/Ly + (np.pi/Ly if bc[1] == -1 else 0) for n in range(Ly)]
    return kx, ky

def c_k_vector(sec_from, sec_to, P, kx, ky, spin, dagger, layer=0):
    """(real part, imag part) of  (1/sqrt(Nr)) sum_r e^{+-ik r} c(+)_{r,layer,spin} Psi"""
    sites, ph = kphase(sec_from, kx, ky, layer)
    if dagger: ph = ph  # c+_k = 1/sqrt(N) sum_r e^{ikr} c+_r
    else: ph = np.conj(ph)
    re = None; im = None; need_im = bool(np.any(np.abs(ph.imag) > 1e-12))
    for s, p in zip(sites, ph):
        v = apply_cdag(sec_from, sec_to, P, s, spin) if dagger else apply_c(sec_from, sec_to, P, s, spin)
        if re is None:
            re = v*(p.real/np.sqrt(sec_from.Nr))
            im = v*(p.imag/np.sqrt(sec_from.Nr)) if need_im else None
        else:
            re.add_(v, alpha=float(p.real/np.sqrt(sec_from.Nr)))
            if need_im: im.add_(v, alpha=float(p.imag/np.sqrt(sec_from.Nr)))
        del v
    return re, im

class Basis:
    """light-weight configuration tables for a sector (no Hamiltonian), usable by apply_c/apply_cdag"""
    def __init__(self, Lx, Ly, nup, ndn):
        self.Lx, self.Ly, self.nup, self.ndn = Lx, Ly, nup, ndn; self.Ns = 2*Lx*Ly; self.Nr = Lx*Ly
        self.mu, self.lu = configs(self.Ns, nup); self.md, self.ld = configs(self.Ns, ndn)

def splus_k_vector(sec_from, P, kx, ky, channel='odd'):
    """(re, im) of (1/sqrt(Nr)) sum_r e^{ikr} (S+_{r,1} -/+ S+_{r,2}) Psi,  S+ = c+_up c_dn ; lands in (nup+1, ndn-1)"""
    Lx, Ly = sec_from.Lx, sec_from.Ly
    mid = Basis(Lx, Ly, sec_from.nup, sec_from.ndn-1); out = Basis(Lx, Ly, sec_from.nup+1, sec_from.ndn-1)
    re = im = None
    need_im = any(abs(np.exp(1j*(kx*x+ky*y)).imag) > 1e-12 for x in range(Lx) for y in range(Ly))
    for y in range(Ly):
        for x in range(Lx):
            ph = np.exp(1j*(kx*x+ky*y))/np.sqrt(sec_from.Nr)
            for l, sgn in ((0, 1.0), (1, -1.0 if channel == 'odd' else 1.0)):
                s = site_index(x, y, l, Lx, Ly)
                tmp = apply_c(sec_from, mid, P, s, 1)
                v = apply_cdag(mid, out, tmp, s, 0); del tmp
                if re is None:
                    re = v*(sgn*ph.real); im = v*(sgn*ph.imag) if need_im else None
                else:
                    re.add_(v, alpha=float(sgn*ph.real))
                    if need_im: im.add_(v, alpha=float(sgn*ph.imag))
                del v
    return re, im, out

def spectrum_for_vector(sec_target, re, im, niter=150):
    """Lanczos continued-fraction data for a complex vector re + i im: list of (al, be, norm2)."""
    parts = []
    for v in (re, im):
        if v is None: continue
        n2 = bdot(v, v)
        if n2 > 1e-12:
            al, be, n2 = spectral_lanczos(sec_target, v, niter); parts.append((al, be, n2))
    return parts

def poles(parts, E0, sign=+1, wmin=1e-8):
    """pole positions omega = sign*(E_n - E0) and weights, merged over the real/imag parts"""
    pos, wts = [], []
    for al, be, n2 in parts:
        e, w = poles_from_lanczos(al, be, n2)
        pos.extend((sign*(e-E0)).tolist()); wts.extend(w.tolist())
    pos = np.array(pos); wts = np.array(wts); m = wts > wmin
    o = np.argsort(pos[m])
    return pos[m][o].tolist(), wts[m][o].tolist()
