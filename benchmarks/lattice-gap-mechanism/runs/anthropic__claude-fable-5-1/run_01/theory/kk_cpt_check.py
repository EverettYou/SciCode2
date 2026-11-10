"""Literal Kramers-Kronig check on the CPT spectrum (2x4, U=-12): Re G(k,0) = P∫ A(k,w)/(0-w) dw vs direct Re G."""
import numpy as np, sys, time
sys.path.insert(0,'/app/theory')
from ed_cpt import Cluster, CPT
from scipy import ndimage
t0 = time.time()
cl = Cluster(2, 4, U=-12.0); cpt = CPT(cl, 4, 4, nlanczos=160, verbose=False)
z = np.load('/app/theory/cpt_2x4_U-12.npz'); mu_mid = float(z['mu_mid'])
Ng = 48; kg = (np.arange(Ng)+0.5)/Ng*2*np.pi - np.pi
GX, GY = np.meshgrid(kg, kg, indexing='ij'); kxs, kys = GX.ravel(), GY.ravel()
VP = cpt.V_many(kxs, kys)
w = np.arange(-20, 20, 0.02) + 0.01 + mu_mid       # symmetric about mu_mid -> principal value
eta = 0.05
A = np.zeros((len(kxs), len(w)))
for i, wi in enumerate(w):
    A[:, i] = -cpt.G_cpt_many(kxs, kys, wi + 1j*eta, VP).imag/np.pi
print("spectra done", time.time()-t0)
ReG_KK = np.trapz(A/(mu_mid - w)[None,:], w, axis=1).reshape(Ng, Ng)
ReG_dir = cpt.G_cpt_many(kxs, kys, mu_mid + 1j*eta, VP).real.reshape(Ng, Ng)
sym = lambda M: 0.5*(M + M.T)
ReG_KK, ReG_dir = sym(ReG_KK), sym(ReG_dir)
print("max |KK - direct| =", np.max(np.abs(ReG_KK-ReG_dir)), " max|ReG| =", np.max(np.abs(ReG_dir)))
for name, M in [('KK', ReG_KK), ('direct', ReG_dir)]:
    lab, nl = ndimage.label(np.sign(M) == np.sign(M[Ng//2, Ng//2]))
    print(f"{name}: Re G(Gamma)={M[Ng//2,Ng//2]:.4f}, Re G(M)={M[0,0]:.4f}, fraction containing (0,0) = {np.mean(lab==lab[Ng//2,Ng//2]):.4f}, regions={nl}, sum rule ∫A = {np.trapz(A, w, axis=1).mean():.4f}")
np.savez('/app/theory/kk_cpt_check.npz', ReG_KK=ReG_KK, ReG_dir=ReG_dir, kg=kg)
