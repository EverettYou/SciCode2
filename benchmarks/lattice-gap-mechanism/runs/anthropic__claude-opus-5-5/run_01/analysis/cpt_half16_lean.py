"""Memory-lean cluster Green's function for the 4x2 (x2 layers) open bilayer cluster at half filling.
Uses the mirror y -> 1-y: mirror-even/odd combinations c+_{x,+/-} = (c+_{x,0} +/- c+_{x,1})/sqrt2 decouple, so the
8x8 layer-1 Green's function is assembled from two 4x4 blocks, each from a block Lanczos with p=4 and a plain
three-block recursion (Q_prev, Q, W only).  Peak memory ~ 15 GB for dim 1.5e8 (container cap 32 GiB)."""
import numpy as np, time, sys, gc
from cpt_bilayer import cluster_geometry, intra_hopping, _cdag_site, _c_site, poles_from_band
from ed_bilayer import BSector
from ed_hubbard import lanczos

U, J, tp, nsteps = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
tag = sys.argv[5]
Lx = int(sys.argv[6]) if len(sys.argv) > 6 else 4
Ly = 2
pos = cluster_geometry(Lx, Ly); M = len(pos)
T = intra_hopping(pos, 1.0, tp, 0.0)
NH = M  # half filling: M electrons per spin on 2M sites
sec0 = BSector(M, NH, NH, T, U, J)
t0 = time.time()
rng = np.random.default_rng(7)
ev, a_, b_, gs = lanczos(sec0, rng.standard_normal(sec0.shape), maxit=400, want_vec=True, nev=1)
E0 = ev[0]
print(f'GS E0={E0:.8f} dim={sec0.dim} ({time.time()-t0:.0f}s)', flush=True)
# check mirror parity of GS: apply site permutation implicitly via <c+ ...> later; assume non-degenerate GS


def lean_block_lanczos(sec, make_vec, p, nsteps):
    """make_vec(c) returns starting vector c (array sec.shape). Returns R0 (p x p), Tm."""
    dim = sec.dim
    Phi = np.empty((p, dim))
    for c in range(p):
        Phi[c] = make_vec(c).ravel()
    G = Phi @ Phi.T
    L = np.linalg.cholesky(G)
    Q = np.linalg.inv(L) @ Phi          # rows orthonormal
    del Phi; gc.collect()
    R0 = L.T                             # Phi = L Q  -> Phi^T = Q^T L^T
    Qprev = None; Bprev = None
    As, Bs = [], []
    out = np.empty(sec.shape)
    tt = time.time()
    for j in range(nsteps):
        W = np.empty((p, dim))
        for c in range(p):
            sec.hv(Q[c].reshape(sec.shape), out)
            W[c] = out.ravel()
        if Qprev is not None:
            W -= Bprev @ Qprev
        A = Q @ W.T; A = 0.5 * (A + A.T)
        W -= A @ Q
        # local re-orthogonalization against Q and Qprev (cheap, no extra storage)
        W -= (W @ Q.T) @ Q
        if Qprev is not None:
            W -= (W @ Qprev.T) @ Qprev
        G = W @ W.T
        try:
            Lw = np.linalg.cholesky(G)
        except np.linalg.LinAlgError:
            As.append(A); break
        Qn = np.linalg.inv(Lw) @ W
        del W; gc.collect()
        As.append(A); Bs.append(Lw.T)      # W = Lw Qn = B^T Qn with B = Lw^T
        Qprev, Q, Bprev = Q, Qn, Lw.T        # column-convention block B_j = Lw^T; next step: W -= B_j @ Qprev
        if j % 5 == 0:
            print(f'      step {j}/{nsteps} t={time.time()-tt:.0f}s', flush=True)
    n = len(As)
    Tm = np.zeros((n * p, n * p))
    for j in range(n):
        Tm[j*p:(j+1)*p, j*p:(j+1)*p] = As[j]
        if j + 1 < n:
            Tm[(j+1)*p:(j+2)*p, j*p:(j+1)*p] = Bs[j]
            Tm[j*p:(j+1)*p, (j+1)*p:(j+2)*p] = Bs[j].T
    del Q, Qprev; gc.collect()
    return R0, Tm


res = {}
for kind in ['p', 'h']:
    if kind == 'p':
        sec = BSector(M, NH + 1, NH, T, U, J)
    else:
        sec = BSector(M, NH - 1, NH, T, U, J)
    for parity, sgn in [('even', +1.0), ('odd', -1.0)]:
        def make_vec(c, sec=sec, sgn=sgn, kind=kind):
            s0 = c + Lx * 0; s1 = c + Lx * 1
            v0 = np.empty(sec.shape); v1 = np.empty(sec.shape)
            if kind == 'p':
                _cdag_site(gs, sec.mu, sec0.lu, sec0.shape[1], s0, v0)
                _cdag_site(gs, sec.mu, sec0.lu, sec0.shape[1], s1, v1)
            else:
                _c_site(gs, sec.mu, sec0.lu, sec0.shape[1], s0, v0)
                _c_site(gs, sec.mu, sec0.lu, sec0.shape[1], s1, v1)
            v0 += sgn * v1
            v0 *= 1 / np.sqrt(2)
            return v0
        t1 = time.time()
        R0, Tm = lean_block_lanczos(sec, make_vec, Lx, nsteps)
        e, Res = poles_from_band(R0, Tm, Lx)
        res[(kind, parity)] = (e, Res)
        print(f'  {kind} {parity}: done ({time.time()-t1:.0f}s), weights {np.round(np.einsum("maa->a", Res), 4)}', flush=True)
    del sec; gc.collect()
# assemble 8x8 layer-1 Green's function poles: G_{(x,y),(x',y')} = 1/2[G^{ee}_{xx'} + (-1)^{y+y'} G^{oo}_{xx'}]
def embed(Res4, sgn):
    m = Res4.shape[0]
    R8 = np.zeros((m, 2 * Lx, 2 * Lx))
    for y in range(2):
        for yp in range(2):
            fac = 0.5 * (sgn ** (y + yp))
            R8[:, Lx*y:Lx*(y+1), Lx*yp:Lx*(yp+1)] = fac * Res4
    return R8
ep = np.concatenate([res[('p', 'even')][0], res[('p', 'odd')][0]]) - E0
Rp = np.concatenate([embed(res[('p', 'even')][1], 1.0), embed(res[('p', 'odd')][1], -1.0)])
em = E0 - np.concatenate([res[('h', 'even')][0], res[('h', 'odd')][0]])
Rm = np.concatenate([embed(res[('h', 'even')][1], 1.0), embed(res[('h', 'odd')][1], -1.0)])
np.savez(f'cgf_{tag}.npz', ep=ep, Rp=Rp, em=em, Rm=Rm, E0=E0, E1=np.nan, pos=pos, sites=np.arange(2 * Lx))
print('saved; total weights per site:', np.round(np.einsum('maa->a', Rp) + np.einsum('maa->a', Rm), 4), flush=True)
