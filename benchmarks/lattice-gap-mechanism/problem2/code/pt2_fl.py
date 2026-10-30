"""Exact second-order perturbation theory in J for the closed-shell Fermi liquid on the finite
lattice: E2 = - sum_n |<n|V|FL>|^2 / (E_n - E_FL),  V = J sum_i S_i1 . S_i2.
V acting on the filled-band determinant creates one particle-hole pair in each layer
(with total momentum zero).  Computed in the momentum basis of the actual L x L cluster."""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from model import Lattice, dispersion

def pt2(L=4, bc="pa", nu=0.5, J=1.0):
    lat = Lattice(L, L, bc)
    ks = lat.kpoints(); nc = lat.n_cell
    eps = dispersion(ks[:, 0], ks[:, 1])
    n = int(round(nu * nc))  # per layer per spin
    order = np.argsort(eps); occ = np.zeros(nc, bool); occ[order[:n]] = True
    # momentum index arithmetic: k = 2pi n/L + shift; differences live on the unshifted grid
    nx = np.round((ks[:, 0] - ks[0, 0]) * L / (2 * np.pi)).astype(int) % L
    ny = np.round((ks[:, 1] - ks[0, 1]) * L / (2 * np.pi)).astype(int) % L
    idx = {(a, b): i for i, (a, b) in enumerate(zip(nx, ny))}
    # S_i1.S_i2 = Sz Sz + (S+S- + S-S+)/2 ; in k space: (1/Nc) sum_q [ Sz(q)_1 Sz(-q)_2 + (S+(q)_1 S-(-q)_2 + h.c.)/2 ]
    # S^a(q) = sum_k c+_{k+q} (sigma^a/2) c_k ; acting on the FL: k occupied, k+q empty (q != 0 for nonzero)
    # Intermediate states: |k1 -> k1+q, s1 s1'> in layer 1 and |k2 -> k2-q, s2 s2'> in layer 2.
    # Matrix elements: Sz channel: (1/2)(s)(1/2)(s') for same-spin p-h ; S+S- channel: 1/2 * 1 * 1 for spin-flip p-h.
    E2 = 0.0
    for q in range(nc):
        if nx[q] == 0 and ny[q] == 0:
            continue
        # p-h pairs in layer 1 with momentum transfer +q, in layer 2 with -q
        def ph(sign):
            out = []
            for k in range(nc):
                if not occ[k]:
                    continue
                kp = idx[((nx[k] + sign * nx[q]) % L, (ny[k] + sign * ny[q]) % L)]
                if occ[kp]:
                    continue
                out.append((k, kp, eps[kp] - eps[k]))
            return out
        ph1, ph2 = ph(+1), ph(-1)
        for (k1, k1p, d1) in ph1:
            for (k2, k2p, d2) in ph2:
                dE = d1 + d2
                # Sz Sz : four spin combinations (s1, s2) with amplitude (s1 s2)/4 -> |M|^2 summed = 4*(1/16) = 1/4
                # S+S- + S-S+ : two spin-flip combinations, amplitude 1/2 each -> |M|^2 summed = 2*(1/4) = 1/2
                M2 = (0.25 + 0.5) / nc ** 2
                E2 -= J ** 2 * M2 / dE
    return E2 / nc  # per site

if __name__ == "__main__":
    for J in (0.5, 1.0, 2.0):
        print(f"L=4 pa nu=1/2 J={J}: E2/site = {pt2(4,'pa',0.5,J):.5f}")
    for J in (0.5, 1.0, 2.0):
        print(f"L=4 aa nu=1/4 J={J}: E2/site = {pt2(4,'aa',0.25,J):.5f}")
    print(f"L=6 pa nu=1/2 J=1: E2/site = {pt2(6,'pa',0.5,1.0):.5f};  L=16 pa: {pt2(16,'pa',0.5,1.0):.5f}; L=32 pa: {pt2(32,'pa',0.5,1.0):.5f}")
