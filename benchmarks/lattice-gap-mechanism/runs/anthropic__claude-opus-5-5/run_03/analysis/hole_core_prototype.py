import sys; sys.path.insert(0,'/app/code')
import numpy as np
from ed_core import Cluster, singlet_product_state
def hole_heff(R, rbonds, J, U=0.0):
    cl = Cluster(R, rbonds, J, U); L = cl.L
    # N=2R ground state (Sz=0)
    stN = cl.basis(R, R); HN = cl.H(stN); wN, vN = np.linalg.eigh(HN); E0 = wN[0]
    # hole sector: remove an up electron from layer 0 -> nup=R-1, ndn=R, layer-0 count R-1
    stH = cl.basis(R-1, R, layer_counts=(R-1, R)); HH = cl.H(stH); wH, vH = np.linalg.eigh(HH)
    S = singlet_product_state(cl, stN)
    refs = []
    for r in range(R):
        C = cl.op_c(2*r, stN, stH)     # c_{r, layer0, up}
        v = C @ S; refs.append(v/np.linalg.norm(v))
    Bref = np.array(refs).T            # reference hole states
    low = vH[:, :R]                    # R lowest hole states
    P = Bref.T @ low                   # projections <h_r|psi_n>
    # Loewdin-orthonormalized effective Hamiltonian (CORE): Heff = A diag(E) A^T with A = P (P^T P)^-1/2
    U_, s_, Vt = np.linalg.svd(P); A = U_ @ Vt
    Heff = A @ np.diag(wH[:R]) @ A.T
    nxt = wH[R]-E0 if len(wH) > R else np.nan
    return Heff - E0*np.eye(R), wH[:R]-E0, nxt, np.abs(P).min()
if __name__ == '__main__':
    t, tp, J = 1.0, 0.1945, 8.0
    for (R, rb, lab) in [(1, [], 'single rung'), (2, [(0,1,t)], 'NN pair'), (2, [(0,1,tp)], 'NNN pair'),
                          (3, [(0,1,t),(1,2,t)], 'straight 3'), (3, [(0,1,t),(1,2,t),(0,2,tp)], 'L-shape 3')]:
        Heff, ws, gapnext, ov = hole_heff(R, rb, J)
        print('%-12s hole levels %s  next=%.3f  min overlap %.3f\n   Heff=\n%s' % (lab, np.round(ws,4), gapnext, ov, np.round(Heff,4)))
