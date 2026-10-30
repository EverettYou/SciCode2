"""Closed-shell table: for each L, filling and boundary condition, the single-particle
gap at the Fermi level of the free band (t1=1, t2=0.2)."""
import sys; sys.path.insert(0, "code")
import numpy as np
from model import Lattice, dispersion
for L in (4, 6, 8):
    nc = L*L
    print(f"--- L={L} ---")
    for nu in (1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8):
        n = nu*nc
        if abs(n-round(n))>1e-9: continue
        n = int(round(n))
        row = []
        for bc in ("pp","pa","ap","aa"):
            lat = Lattice(L, L, bc); ks = lat.kpoints()
            eps = np.sort(dispersion(ks[:,0], ks[:,1]))
            gap = eps[n]-eps[n-1] if n < nc else np.nan
            deg_below = np.sum(np.abs(eps-eps[n-1])<1e-9); deg_above = np.sum(np.abs(eps-eps[n])<1e-9) if n<nc else 0
            row.append(f"{bc}: gap={gap:6.3f} (deg {deg_below}/{deg_above}) E0/site={2*eps[:n].sum()/nc:8.4f}")
        print(f"nu={nu:5.3f} N/flavor={n:3d} | " + " | ".join(row))
