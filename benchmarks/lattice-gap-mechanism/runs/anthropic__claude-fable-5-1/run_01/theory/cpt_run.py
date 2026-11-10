"""CPT at half filling: A(k,w) along the path, total DOS, midgap, Luttinger surface (zeros of Re G(k, mu_mid))."""
import numpy as np, sys, time, json
sys.path.insert(0, '/app/theory')
from ed_cpt import Cluster, CPT
from common import kpath
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm

Lx, Ly, U = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
tag = f"{Lx}x{Ly}_U{int(U)}"
cl = Cluster(Lx, Ly, U=U); n = cl.Nc//2
t0 = time.time()
cpt = CPT(cl, n, n, nlanczos=160, nblocks=int(sys.argv[4]) if len(sys.argv)>4 else 60)
print(f"[{tag}] CPT ready {time.time()-t0:.1f}s")
# ---- total DOS on a coarse k grid, to locate the gap ----
eta = 0.05
w = np.arange(-16, 16, 0.02)
Nk = 32
ks = (np.arange(Nk)+0.5)/Nk*2*np.pi - np.pi
KX, KY = np.meshgrid(ks, ks, indexing='ij'); kxs, kys = KX.ravel(), KY.ravel()
dos = np.zeros(len(w)); VPd = cpt.V_many(kxs, kys)
for i, wi in enumerate(w):
    dos[i] = -np.mean(cpt.G_cpt_many(kxs, kys, wi + 1j*eta, VPd).imag)/np.pi
print(f"[{tag}] DOS done {time.time()-t0:.1f}s ; integral = {np.trapz(dos, w):.4f}")
# gap edges: largest interval around the DOS minimum region near the center of the spectrum where dos < thr
thr = 0.004
# find the centre of mass of the spectrum, then search outward from the point of minimal dos between the two main bands
# locate the two main band maxima
from scipy.signal import find_peaks
ipk, _ = find_peaks(dos, prominence=0.02)
# choose the gap as the region between the highest-energy peak below the spectral centre and lowest above
wc = np.sum(w*dos)/np.sum(dos)
below = [i for i in ipk if w[i] < wc]; above = [i for i in ipk if w[i] > wc]
i1 = max(below); i2 = min(above)
seg = np.arange(i1, i2)
inside = seg[dos[seg] < thr]
if len(inside) == 0:
    imin = seg[np.argmin(dos[seg])]; lo = hi = w[imin]
else:
    lo, hi = w[inside[0]], w[inside[-1]]
mu_mid = 0.5*(lo+hi)
print(f"[{tag}] gap region (dos<{thr}): [{lo:.3f}, {hi:.3f}] width {hi-lo:.3f}; midgap mu = {mu_mid:.3f}; spectral centre {wc:.3f}")
# ---- A(k,w) along the path ----
kx, ky, dist, ticks, labels = kpath(240)
wpath = np.arange(-10, 10, 0.04) + mu_mid
Ak = np.zeros((len(dist), len(wpath))); VPp = cpt.V_many(kx, ky)
for i, wi in enumerate(wpath):
    Ak[:, i] = -cpt.G_cpt_many(kx, ky, wi + 1j*0.15, VPp).imag/np.pi
print(f"[{tag}] A(k,w) path done {time.time()-t0:.1f}s")
# ---- Re G(k, mu_mid) on a grid: Luttinger surface ----
Ng = 64
kg = (np.arange(Ng)+0.5)/Ng*2*np.pi - np.pi
GX, GY = np.meshgrid(kg, kg, indexing='ij')
ReG = cpt.G_cpt_many(GX.ravel(), GY.ravel(), mu_mid + 1j*0.01).real.reshape(Ng, Ng)
sgn0 = np.sign(ReG[Ng//2, Ng//2])  # (0,0) is at the centre of the grid (k in [-pi,pi))
frac_same_sign = np.mean(np.sign(ReG) == sgn0)
# connected region containing (0,0)
from scipy import ndimage
lab, nlab = ndimage.label(np.sign(ReG) == sgn0)
lab0 = lab[Ng//2, Ng//2]
frac_connected = np.mean(lab == lab0)
print(f"[{tag}] Re G at (0,0) = {ReG[Ng//2,Ng//2]:.4f}; at (pi,pi) = {ReG[0,0]:.4f}; at (pi,0) = {ReG[0,Ng//2]:.4f}")
print(f"[{tag}] fraction of BZ with same sign of Re G as (0,0): {frac_same_sign:.4f}; connected region containing (0,0): {frac_connected:.4f}; number of regions {nlab}")
np.savez(f'/app/theory/cpt_{tag}.npz', w=w, dos=dos, wpath=wpath, Ak=Ak, dist=dist, ticks=ticks, ReG=ReG, kg=kg, mu_mid=mu_mid, lo=lo, hi=hi, frac=frac_connected, frac_same=frac_same_sign)
# figure
fig, axs = plt.subplots(1, 3, figsize=(17, 5.2), constrained_layout=True)
axs[0].plot(w - mu_mid, dos); axs[0].set_xlabel(r'$\omega-\mu$ (D)'); axs[0].set_ylabel('DOS per spin (1/D)'); axs[0].set_title(f'CPT {Lx}x{Ly}, U={U:+.0f}D: total DOS')
axs[0].axvline(lo-mu_mid, color='r', ls=':'); axs[0].axvline(hi-mu_mid, color='r', ls=':'); axs[0].set_xlim(-10,10)
im = axs[1].pcolormesh(dist, wpath - mu_mid, Ak.T, shading='auto', cmap='magma', norm=PowerNorm(0.5, vmin=0, vmax=np.percentile(Ak, 99.5)))
axs[1].set_xticks(ticks); axs[1].set_xticklabels(labels); axs[1].set_title(r'CPT $A(k,\omega)$, $\nu=1/2$'); axs[1].set_ylabel(r'$\omega-\mu$ (D)')
for t_ in ticks[1:-1]: axs[1].axvline(t_, color='w', lw=0.5)
plt.colorbar(im, ax=axs[1], shrink=0.8)
ext = [-0.5, 0.5, -0.5, 0.5]
vm = np.max(np.abs(ReG))
im2 = axs[2].imshow(ReG.T, origin='lower', extent=ext, cmap='RdBu_r', vmin=-vm, vmax=vm)
axs[2].contour(kg/(2*np.pi), kg/(2*np.pi), ReG.T, levels=[0], colors='k')
axs[2].set_xlabel(r'$k_x$ ($2\pi/a$)'); axs[2].set_ylabel(r'$k_y$ ($2\pi/a$)'); axs[2].set_title(r'Re $G(k,\omega=0)$ at mid-gap; zeros = black curve' + f'\nfraction containing (0,0): {frac_connected:.3f}')
plt.colorbar(im2, ax=axs[2], shrink=0.8)
plt.savefig(f'/app/figures/fig_cpt_{tag}.png', dpi=130)
print(f"[{tag}] done {time.time()-t0:.1f}s")
