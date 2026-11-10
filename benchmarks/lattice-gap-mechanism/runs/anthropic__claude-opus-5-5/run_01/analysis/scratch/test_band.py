import numpy as np, time
from cpt_bilayer import *
from band_lanczos_fast import band_lanczos_fast
import cpt_bilayer as cb
pos = cluster_geometry(2, 2)
cg1 = ClusterGF(pos, 1.0, 0.2, 1.8, 6.5, 4, 4, sites_list=list(range(4)), nsteps=40, verbose=False)
cb.band_lanczos = band_lanczos_fast
cg2 = ClusterGF(pos, 1.0, 0.2, 1.8, 6.5, 4, 4, sites_list=list(range(4)), nsteps=40, verbose=False)
for z in [0.3+0.05j, -6+0.1j, 6.5+0.1j]:
    print(z, np.abs(cg1.G(z) - cg2.G(z)).max(), np.abs(cg1.G(z)).max())
