import numpy as np, sys
from cpt_bilayer import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fn = sys.argv[1]; Lx = int(sys.argv[2]); Ly = int(sys.argv[3]); tp = float(sys.argv[4]) if len(sys.argv) > 4 else 0.2
cpt = CPT(fn=fn, Lx=Lx, Ly=Ly, t=1.0, tp=tp)
# 1) band edges from poles: scan omega with tiny eta on a k grid, find max of lower band and min of upper band
def spectrum_edges(nk=48, eta=0.02):
    w = np.linspace(-9, 9, 3601)
    Gci = [np.linalg.inv(cpt.Gc(x + 1j*eta)) for x in w]
    lo_top, up_bot = -np.inf, np.inf
    # rough midgap from cluster poles
    mid0 = 0.5*(cpt.ep.min() + cpt.em.max())
    kk = np.linspace(-np.pi, np.pi, nk, endpoint=False) + np.pi/nk
    for kx in kk[:nk//2+1]:
        for ky in kk[:nk//2+1]:
            A = np.array([-cpt.Gk((kx,ky), x+1j*eta, Gci[i]).imag for i, x in enumerate(w)])
            peaks = w[1:-1][(A[1:-1] > A[:-2]) & (A[1:-1] > A[2:]) & (A[1:-1] > 0.02*A.max())]
            lo = peaks[peaks < mid0]; up = peaks[peaks > mid0]
            if len(lo): lo_top = max(lo_top, lo.max())
            if len(up): up_bot = min(up_bot, up.min())
    return lo_top, up_bot
lo_top, up_bot = spectrum_edges()
mid = 0.5*(lo_top + up_bot)
print(f'band edges: lower top {lo_top:.3f}, upper bottom {up_bot:.3f}, gap {up_bot-lo_top:.3f}, midgap {mid:.3f}')
# 2) Re G(k, mid) on a fine grid (G real in the gap)
nk = 121
kk = np.linspace(-np.pi, np.pi, nk)
Gci = np.linalg.inv(cpt.Gc(mid + 1e-9j))
Gmap = np.zeros((nk, nk))
for i, kx in enumerate(kk):
    for j, ky in enumerate(kk):
        Gmap[i, j] = cpt.Gk((kx, ky), mid + 1e-9j, Gci).real
print('Re G range:', Gmap.min(), Gmap.max(), ' sign at Gamma:', np.sign(Gmap[nk//2, nk//2]), ' at M:', np.sign(Gmap[0,0]))
# area fraction on the side containing Gamma: same sign as Gamma, connected region
sg = np.sign(Gmap[nk//2, nk//2])
frac = np.mean(np.sign(Gmap[:-1,:-1]) == sg)
print(f'fraction of BZ with sign(ReG)=sign at Gamma: {frac:.4f}')
np.save(fn.replace('.npz','_zeromap.npy'), np.array([mid, lo_top, up_bot]))
np.save(fn.replace('.npz','_Gmap.npy'), Gmap)
fig, ax = plt.subplots(figsize=(5,5))
ax.contourf(kk/(2*np.pi), kk/(2*np.pi), Gmap.T, levels=40, cmap='RdBu_r')
ax.contour(kk/(2*np.pi), kk/(2*np.pi), Gmap.T, levels=[0], colors='k')
ax.set_aspect('equal'); ax.set_title(f'Re G(k, midgap); frac={frac:.3f}')
plt.savefig(fn.replace('.npz','_zeros.png'), dpi=80)
