import numpy as np
from ed_hubbard import make_cluster
from ed_stiffness import bilayer_hopping_twist
sites, red, Ks = make_cluster((2,2),(-2,2)); M = len(sites)
h = 0.15
for N in [6, 10, 16]:
    E = []
    for a in (0.0, h):
        T = bilayer_hopping_twist(sites, red, 1.0, 0.2, a)
        ev = np.linalg.eigvalsh(T)
        n = N//2
        E.append(2*ev[:n].sum())   # spin up + down
    print(f'N={N} nu={N/(4*M):.4f} Dfree={2*(E[1]-E[0])/h**2/M:.4f}')
