"""Common band-structure utilities for the effective theory.
Units: energies in D (= nearest-neighbour hopping t), momenta in 2*pi/a.
Bare band fitted to STS panel (d):  t = 1.00 D, t' = 0.196 D, t'' = 0.
"""
import numpy as np
T, TP = 1.0, 0.196

def eps_k(kx, ky, t=T, tp=TP):
    """kx, ky in radians (k * a)."""
    return -2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)

def kgrid(N):
    k = (np.arange(N)+0.5)/N*2*np.pi - np.pi
    KX, KY = np.meshgrid(k, k, indexing='ij')
    return KX, KY

def band_constants(N=1200):
    KX, KY = kgrid(N); E = eps_k(KX, KY)
    return dict(emin=E.min(), emax=E.max(), ebar=0.5*(E.min()+E.max()), emean=E.mean(), W=E.max()-E.min())

def mu_bare(nu, N=1200):
    """bare chemical potential giving filling nu (fraction of band filled, nu = n/2)."""
    from scipy.optimize import brentq
    KX, KY = kgrid(N); E = eps_k(KX, KY)
    return brentq(lambda m: (E < m).mean() - nu, E.min(), E.max())

def kpath(npts=400):
    """(0,0)->(1/2,0)->(1/2,1/2)->(0,0) in units of 2pi/a ; returns kx,ky (radians), distance, ticks"""
    G = np.array([0,0]); X = np.array([0.5,0]); M = np.array([0.5,0.5])
    segs = [(G,X),(X,M),(M,G)]
    kx, ky, dist = [], [], []
    d0 = 0.0; ticks=[0.0]
    for a,b in segs:
        L = np.linalg.norm(b-a)
        n = int(npts*L/ (0.5+0.5+np.sqrt(0.5)))
        for s in np.linspace(0,1,n,endpoint=False):
            p = a + s*(b-a); kx.append(2*np.pi*p[0]); ky.append(2*np.pi*p[1]); dist.append(d0 + s*L)
        d0 += L; ticks.append(d0)
    kx.append(0.0); ky.append(0.0); dist.append(d0)
    return np.array(kx), np.array(ky), np.array(dist), ticks, ['(0,0)','(1/2,0)','(1/2,1/2)','(0,0)']

def lorentz(w, w0, eta):
    return (eta/np.pi)/((w-w0)**2 + eta**2)

# ---------- spectral functions of the effective theory ----------
def A_halffilling(kx, ky, w, U=12.0, eta=0.084, Dc=None, tilt_center=None):
    """nu=1/2 local-pair/Mott insulator, first order in t/|U| (two-pole):
       E±(k) = ±U/2 + (eps_k - ebar)/2  (chemical potential at mid-gap),
       w±(k) = 1/2 (1 ± (eps_k - c)/Dc).  Canonical strong-coupling weights: Dc = U, c = <eps>=0.
    """
    bc = band_constants()
    e = eps_k(kx, ky)
    if Dc is None: Dc = U
    if tilt_center is None: tilt_center = bc['emean']
    Ep = U/2 + (e - bc['ebar'])/2; Em = -U/2 + (e - bc['ebar'])/2
    wm = np.clip(0.5*(1 - (e - tilt_center)/Dc), 0, 1); wp = 1 - wm
    return wm[...,None]*lorentz(w[None,:], Em[...,None], eta) + wp[...,None]*lorentz(w[None,:], Ep[...,None], eta), (Em, Ep, wm, wp)

def A_localpair(kx, ky, w, mu=-0.75, Dpg=4.3, Dc=2.0, eta=0.1):
    """nu~0.3 preformed-local-pair superconductor: Sigma = Dpg^2/omega (dispersionless pair partner)
       E±(k) = xi/2 ± sqrt(xi^2/4 + Dpg^2); weights = coherence factors with the spectral gap scale Dc."""
    xi = eps_k(kx, ky) - mu
    root = np.sqrt(xi**2/4 + Dpg**2)
    Ep = xi/2 + root; Em = xi/2 - root
    wp = 0.5*(1 + xi/np.sqrt(xi**2 + Dc**2)); wm = 1 - wp
    return wm[...,None]*lorentz(w[None,:], Em[...,None], eta) + wp[...,None]*lorentz(w[None,:], Ep[...,None], eta), (Em, Ep, wm, wp)

def A_bcs(kx, ky, w, mu=-1.92, Delta=1.965, eta=0.083):
    xi = eps_k(kx, ky) - mu
    E = np.sqrt(xi**2 + Delta**2)
    u2 = 0.5*(1 + xi/E); v2 = 1 - u2
    return v2[...,None]*lorentz(w[None,:], -E[...,None], eta) + u2[...,None]*lorentz(w[None,:], E[...,None], eta), (-E, E, v2, u2)
