import numpy as np, time, sys, resource
def band_lanczos_fast(sec, block, nsteps=60):
    """Block Lanczos with contiguous (p, dim) storage and CholQR (+ one re-orthogonalization pass).
    Returns (R0, Tm) such that <phi_a|(z-H)^-1|phi_b> = [R0^T ((z-T)^-1)_{00} R0]_ab."""
    p = len(block)
    W = np.array([b.ravel() for b in block])          # p x dim (contiguous rows)
    def cholqr(X):
        G = X @ X.T
        L = np.linalg.cholesky(G)
        Q = np.linalg.solve(L, X)                      # rows orthonormal
        # second pass for stability
        G2 = Q @ Q.T; L2 = np.linalg.cholesky(G2); Q = np.linalg.solve(L2, Q)
        R = (L @ L2).T                                 # X = R^T Q  => X^T = Q^T R
        return Q, R
    Q, R0 = cholqr(W)
    Qprev = np.zeros_like(Q); Bprev = np.zeros((p, p))
    hist = [Q]
    As, Bs = [], []
    out = np.empty(sec.shape)
    t0 = time.time()
    for j in range(nsteps):
        if j % 5 == 0:
            print(f'      band-Lanczos step {j}/{nsteps}, dim={Q.shape[1]}, t={time.time()-t0:.0f}s, maxrss={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6:.1f}GB', flush=True)
        W = np.empty_like(Q)
        for c in range(p):
            sec.hv(Q[c].reshape(sec.shape), out)
            W[c] = out.ravel()
        W -= Bprev @ Qprev
        A = Q @ W.T; A = 0.5 * (A + A.T)
        W -= A @ Q
        for Qo in hist[-3:]:
            W -= (W @ Qo.T) @ Qo
        try:
            Qn, B = cholqr(W)
        except np.linalg.LinAlgError:
            As.append(A); break
        As.append(A); Bs.append(B)
        Qprev, Q, Bprev = Q, Qn, B
        hist.append(Q)
        if len(hist) > 4: hist.pop(0)
    n = len(As)
    Tm = np.zeros((n * p, n * p))
    for j in range(n):
        Tm[j*p:(j+1)*p, j*p:(j+1)*p] = As[j]
        if j + 1 < n:
            # W_j = B_j^T Q_{j+1} (rows)  =>  <Q_{j+1}|H|Q_j> = B_j^T ... in column convention: T_{j+1,j} = B_j^T
            Tm[(j+1)*p:(j+2)*p, j*p:(j+1)*p] = Bs[j]
            Tm[j*p:(j+1)*p, (j+1)*p:(j+2)*p] = Bs[j].T
    return R0, Tm
