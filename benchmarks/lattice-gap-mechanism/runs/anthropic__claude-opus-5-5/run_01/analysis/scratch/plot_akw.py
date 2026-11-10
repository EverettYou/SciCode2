import numpy as np, sys
from cpt_bilayer import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fn = sys.argv[1]; Lx = int(sys.argv[2]); Ly = int(sys.argv[3]); out = sys.argv[4]
tp = float(sys.argv[5]) if len(sys.argv) > 5 else 0.2
wmin, wmax = (float(sys.argv[6]), float(sys.argv[7])) if len(sys.argv) > 7 else (-10, 10)
cpt = CPT(fn=fn, Lx=Lx, Ly=Ly, t=1.0, tp=tp)
# path G-X-M-G
npts = 60
G = np.array([0,0.]); X = np.array([np.pi,0.]); Mp = np.array([np.pi,np.pi])
path = [G + (X-G)*s for s in np.linspace(0,1,npts,endpoint=False)] + \
       [X + (Mp-X)*s for s in np.linspace(0,1,npts,endpoint=False)] + \
       [Mp + (G-Mp)*s for s in np.linspace(0,1,int(npts*1.414)+1)]
eta = 0.06
w = np.linspace(wmin, wmax, 801)
Gci = [np.linalg.inv(cpt.Gc(x+1j*eta)) for x in w]
A = np.array([[-cpt.Gk(k, x+1j*eta, Gci[i]).imag/np.pi for i, x in enumerate(w)] for k in path])
np.save(out.replace('.png','.npy'), A)
fig, ax = plt.subplots(figsize=(8,6))
ax.imshow(A.T, origin='lower', aspect='auto', extent=[0, len(path), w[0], w[-1]], cmap='magma', vmax=np.percentile(A, 99.5))
ax.set_xticks([0, npts, 2*npts, len(path)-1]); ax.set_xticklabels(['G','X','M','G'])
eps = np.array([-2*(np.cos(k[0])+np.cos(k[1])) - 4*tp*np.cos(k[0])*np.cos(k[1]) for k in path])
ax.plot(np.arange(len(path)), eps, 'c--', lw=0.8, alpha=0.6)
plt.savefig(out, dpi=80)
