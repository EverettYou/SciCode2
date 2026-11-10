"""Generic CPT driver: cluster GF at (nup,ndn) for an Lx x Ly bilayer cluster; saves npz; prints gap info and DOS."""
import numpy as np, sys, time
from cpt_bilayer import *
import cpt_bilayer as _cb
from band_lanczos_fast import band_lanczos_fast
_cb.band_lanczos = band_lanczos_fast
U = float(sys.argv[1]); J = float(sys.argv[2]); Lx = int(sys.argv[3]); Ly = int(sys.argv[4])
nup = int(sys.argv[5]); ndn = int(sys.argv[6]); tag = sys.argv[7]
tp = float(sys.argv[8]) if len(sys.argv) > 8 else 0.2
nsteps = int(sys.argv[9]) if len(sys.argv) > 9 else 60
pos = cluster_geometry(Lx, Ly); M = len(pos)
t0 = time.time()
cg = ClusterGF(pos, 1.0, tp, U, J, nup, ndn, sites_list=list(range(M)), nsteps=nsteps)
cg.save(f'cgf_{tag}.npz')
print(f'done in {time.time()-t0:.1f}s; nu_cluster={(nup+ndn)/(4*M):.4f}; cluster mu+={cg.ep.min():.4f} mu-={cg.em.max():.4f}', flush=True)
