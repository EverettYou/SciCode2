"""Minimal Fock-space tools for small bilayer clusters (dense or sparse), used for
two-rung perturbation theory and for validating the GPU code."""
import numpy as np, scipy.sparse as sp

class Fock:
    """Spin-orbitals indexed o = 2*site + spin (spin 0=up,1=down). States are bit masks."""
    def __init__(self, nsites, nelec=None):
        self.nsites = nsites; self.norb = 2*nsites
        allst = np.arange(1 << self.norb, dtype=np.int64)
        if nelec is None:
            self.states = allst
        else:
            pc = np.array([bin(s).count('1') for s in allst])
            self.states = allst[pc == nelec]
        self.index = {int(s): i for i, s in enumerate(self.states)}
        self.dim = len(self.states)
    def _sign(self, s, o):
        return (-1)**bin(s & ((1 << o)-1)).count('1')
    def hop(self, o_to, o_from, amp):
        """amp * c^dag_{o_to} c_{o_from}"""
        rows, cols, vals = [], [], []
        for i, s in enumerate(self.states):
            s = int(s)
            if not (s >> o_from) & 1: continue
            sg = self._sign(s, o_from); s1 = s ^ (1 << o_from)
            if (s1 >> o_to) & 1: continue
            sg *= self._sign(s1, o_to); s2 = s1 | (1 << o_to)
            j = self.index.get(s2)
            if j is None: continue
            rows.append(j); cols.append(i); vals.append(amp*sg)
        return sp.csr_matrix((vals, (rows, cols)), shape=(self.dim, self.dim))
    def n(self, o):
        return sp.diags([float((int(s) >> o) & 1) for s in self.states])
    def cdag(self, o):
        return self.hop(o, o, 0)  # placeholder (not used)
    def spin_ops(self, site):
        up, dn = 2*site, 2*site+1
        Sp = self.hop(up, dn, 1.0); Sm = Sp.T.tocsr()
        Sz = 0.5*(self.n(up)-self.n(dn))
        return Sp, Sm, Sz
    def SdotS(self, i, j):
        Spi, Smi, Szi = self.spin_ops(i); Spj, Smj, Szj = self.spin_ops(j)
        return 0.5*(Spi@Smj + Smi@Spj) + Szi@Szj
    def hopping(self, bonds):
        """bonds: list of (site_a, site_b, t) -> -t sum_sigma (c^dag_a c_b + h.c.)"""
        H = sp.csr_matrix((self.dim, self.dim))
        for a, b, t in bonds:
            for s in (0, 1):
                H = H + self.hop(2*a+s, 2*b+s, -t) + self.hop(2*b+s, 2*a+s, -t)
        return H
