import numpy as np, sys, json, time
from cpt_bilayer import *
U = float(sys.argv[1]); J = float(sys.argv[2]); Lx = int(sys.argv[3]); Ly = int(sys.argv[4]); tag = sys.argv[5]
tp = float(sys.argv[6]) if len(sys.argv) > 6 else 0.2
nsteps = int(sys.argv[7]) if len(sys.argv) > 7 else 60
pos = cluster_geometry(Lx, Ly); M = len(pos)
t0 = time.time()
cg = ClusterGF(pos, 1.0, tp, U, J, M, M, sites_list=list(range(M)), nsteps=nsteps)
cg.save(f'cgf_{tag}.npz')
print('cluster GF done', time.time()-t0, 's; cluster gap (min ep, max em):', cg.ep.min(), cg.em.max())
cpt = CPT(fn=f'cgf_{tag}.npz', Lx=Lx, Ly=Ly, t=1.0, tp=tp)
# DOS on a k grid
eta = 0.08
w = np.linspace(-14, 14, 1401)
nk = 24
ks = [(2*np.pi*(i+0.5)/nk - np.pi, 2*np.pi*(j+0.5)/nk - np.pi) for i in range(nk) for j in range(nk)]
dos = np.zeros_like(w)
Gcinv = [np.linalg.inv(cpt.Gc(ww + 1j*eta)) for ww in w]
for k in ks:
    for iw, ww in enumerate(w):
        dos[iw] += -cpt.Gk(k, ww+1j*eta, Gcinv[iw]).imag/np.pi
dos /= len(ks)
np.save(f'dos_{tag}.npy', np.vstack([w, dos]))
# find gap edges (where dos > 1% of max)
thr = 0.01*dos.max()
neg = w[(w < 0.5*(cg.ep.min()+cg.em.max())) & (dos > thr)]
pos_ = w[(w > 0.5*(cg.ep.min()+cg.em.max())) & (dos > thr)]
print('approx band edges: lower band top', neg.max(), ' upper band bottom', pos_.min(), ' midgap', 0.5*(neg.max()+pos_.min()))
