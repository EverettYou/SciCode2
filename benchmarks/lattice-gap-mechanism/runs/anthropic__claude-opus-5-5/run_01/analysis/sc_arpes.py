"""Spectral functions of the superconducting crystals (top layer = any layer for t_perp=0), Bogoliubov form
with mu fixed at the normal-state value mu0(nu) (underlying FS encloses nu, as found from STS (c)):
  nu~0.2 : constant gap Delta = 2.03 (J_perp = 6.6 mean field; STS gives 1.96)
  nu~0.3 : two-scale gap Delta(xi) = Dinf - (Dinf - D0) exp(-|xi|/w), D0=2.85 (coherent, at k_F), Dinf=5.23 (local
           rung-pair scale ~ half-filled spin gap), w=1.08  (parameters fixed by the STS fit, scales tied to the model)"""
import numpy as np, json
from cpt_analyze import kpath
def eps(k, t=1.0, tp=0.2):
    return -2*t*(np.cos(k[:,0])+np.cos(k[:,1])) - 4*tp*np.cos(k[:,0])*np.cos(k[:,1])
N = 1000; kk = 2*np.pi*(np.arange(N)+0.5)/N; KX, KY = np.meshgrid(kk, kk, indexing='ij')
EALL = np.sort((-2*(np.cos(KX)+np.cos(KY)) - 0.8*np.cos(KX)*np.cos(KY)).ravel())
def mu0(nu): return EALL[int(nu*len(EALL))]
def sc_akw(nu, D0, Dinf=None, wid=1.0, w=np.linspace(-12,12,961), eta=0.06, npath=50):
    kp, dist, ticks = kpath(npath)
    m = mu0(nu); xi = eps(kp) - m
    D = D0 if Dinf is None else Dinf - (Dinf - D0)*np.exp(-np.abs(xi)/wid)
    E = np.sqrt(xi**2 + D**2); u2 = 0.5*(1+xi/E); v2 = 0.5*(1-xi/E)
    L = lambda x: eta/np.pi/(x**2+eta**2)
    A = u2[:,None]*L(w[None,:]-E[:,None]) + v2[:,None]*L(w[None,:]+E[:,None])
    return dict(w=w, A=A, dist=dist, ticks=np.array(ticks), kpath=kp, midgap=0.0, mu0=m, Delta=np.atleast_1d(D), E=E)
r2 = sc_akw(0.2, 2.03); np.savez('sc_akw_nu0.2.npz', **r2)
r3 = sc_akw(0.3, 2.85, 5.23, 1.08); np.savez('sc_akw_nu0.3.npz', **r3)
print('mu0(0.2)=%.3f mu0(0.3)=%.3f mu0(0.5)=%.3f' % (mu0(0.2), mu0(0.3), mu0(0.5)))
