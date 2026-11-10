"""Small-cluster exact diagonalization for the bilayer t-t'-J_perp(-U) model.
Sites are (rung r, layer l) -> index 2r+l.  Fermion ordering: spin-up modes 0..L-1, spin-down L..2L-1.
Used for (i) triplon and pair parameters, (ii) CORE/cluster-expansion effective hole Hamiltonian."""
import numpy as np, itertools
def popcount(x): return bin(x).count('1')
class Cluster:
    def __init__(self, R, rbonds, J, U=0.0):
        """R rungs; rbonds = list of (r, s, t_rs) in-plane bonds (same layer hopping on both layers)."""
        self.R, self.L, self.J, self.U = R, 2*R, J, U
        self.bonds = []
        for (r, s, t) in rbonds:
            for l in (0, 1): self.bonds.append((2*r+l, 2*s+l, t))
        self.rungs = [(2*r, 2*r+1) for r in range(R)]
    def basis(self, nup, ndn, layer_counts=None):
        L = self.L; st = []
        for up in itertools.combinations(range(L), nup):
            for dn in itertools.combinations(range(L), ndn):
                s = sum(1 << i for i in up) | sum(1 << (i+L) for i in dn)
                if layer_counts is not None:
                    n0 = sum(((s >> i) & 1) + ((s >> (i+L)) & 1) for i in range(0, L, 2))
                    if n0 != layer_counts[0]: continue
                st.append(s)
        return st
    def hop(self, s, a, b):
        if not (s >> b) & 1: return None
        if a != b and (s >> a) & 1: return None
        sign = (-1) ** popcount(s & ((1 << b) - 1)); s2 = s ^ (1 << b)
        sign *= (-1) ** popcount(s2 & ((1 << a) - 1))
        return sign, s2 | (1 << a)
    def H(self, states):
        L = self.L; idx = {s: i for i, s in enumerate(states)}; D = len(states)
        Hm = np.zeros((D, D))
        n = lambda s, i: (s >> i) & 1
        for k, s in enumerate(states):
            for (a, b, t) in self.bonds:
                for off in (0, L):
                    for (x, y) in ((a, b), (b, a)):
                        r = self.hop(s, x+off, y+off)
                        if r and r[1] in idx: Hm[idx[r[1]], k] += -t * r[0]
            for i in range(L): Hm[k, k] += self.U * n(s, i) * n(s, i+L)
            for (i, j) in self.rungs:
                szi = 0.5*(n(s, i)-n(s, i+L)); szj = 0.5*(n(s, j)-n(s, j+L))
                Hm[k, k] += self.J * szi * szj
                for (p, q) in ((i, j), (j, i)):
                    r1 = self.hop(s, q+L, q)
                    if r1:
                        r2 = self.hop(r1[1], p, p+L)
                        if r2 and r2[1] in idx: Hm[idx[r2[1]], k] += 0.5*self.J*r1[0]*r2[0]
        return Hm
    def op_c(self, mode, states_in, states_out):
        """matrix of annihilation operator c_mode from states_in to states_out"""
        idx = {s: i for i, s in enumerate(states_out)}
        M = np.zeros((len(states_out), len(states_in)))
        for k, s in enumerate(states_in):
            if (s >> mode) & 1:
                sign = (-1) ** popcount(s & ((1 << mode) - 1)); s2 = s ^ (1 << mode)
                if s2 in idx: M[idx[s2], k] = sign
        return M
def singlet_product_state(cl, states):
    """|S...S> with rung singlets (c+_{1u}c+_{2d} - c+_{1d}c+_{2u})/sqrt2 on every rung"""
    L = cl.L; vec = np.zeros(len(states)); idx = {s: i for i, s in enumerate(states)}
    for choice in itertools.product((0, 1), repeat=cl.R):
        ops = []; amp = 1.0
        for r, c in enumerate(choice):
            i, j = cl.rungs[r]
            if c == 0: ops += [i, j+L]            # c+_{i,up} c+_{j,dn}
            else: ops += [i+L, j]; amp *= -1      # -c+_{i,dn} c+_{j,up}
        # apply creation operators in order (rightmost first)
        s = 0; sign = 1
        for m in reversed(ops):
            if (s >> m) & 1: sign = 0; break
            sign *= (-1) ** popcount(s & ((1 << m) - 1)); s |= (1 << m)
        if sign != 0 and s in idx: vec[idx[s]] += amp * sign * (1/np.sqrt(2))**cl.R
    return vec
