"""Square-lattice band with nearest (t1) and next-nearest (t2) hopping, and
helpers used throughout the solution.  Energies in units of D (= t1 as fitted)."""
import numpy as np

def eps(kx, ky, t1=1.0, t2=0.2):
    """Bare dispersion. (pi,0) van Hove sits at +4 t2; band edges -4t1-4t2 and 4t1-4t2."""
    return -2*t1*(np.cos(kx)+np.cos(ky)) - 4*t2*np.cos(kx)*np.cos(ky)

def kgrid(n=1200):
    k = (np.arange(n)+0.5)*2*np.pi/n - np.pi
    return np.meshgrid(k, k, indexing='ij')

def dos(E, t1=1.0, t2=0.2, n=2400, sigma=0.02):
    """DOS per site per spin of eps(k) on the energy grid E (Gaussian broadening sigma)."""
    kx, ky = kgrid(n)
    e = eps(kx, ky, t1, t2).ravel()
    dE = E[1]-E[0]
    h, edges = np.histogram(e, bins=np.concatenate([E-dE/2, [E[-1]+dE/2]]))
    rho = h/(len(e)*dE)
    if sigma > 0:
        from scipy.ndimage import gaussian_filter1d
        rho = gaussian_filter1d(rho, sigma/dE)
    return rho

def filling(mu, t1=1.0, t2=0.2, n=2000):
    """Fraction of the Brillouin zone with eps(k) < mu  (= nu, the filling fraction)."""
    kx, ky = kgrid(n)
    return np.mean(eps(kx, ky, t1, t2) < mu)

def mu_of_filling(nu, t1=1.0, t2=0.2, n=2000):
    kx, ky = kgrid(n)
    e = np.sort(eps(kx, ky, t1, t2).ravel())
    return e[int(round(nu*len(e)))-1] if nu > 0 else e[0]

def path_kpoints(npts=200):
    """(0,0)->(1/2,0)->(1/2,1/2)->(0,0) in units of 2pi/a; returns kx,ky arrays and the
    cumulative path coordinate plus tick positions."""
    G = np.array([0.0, 0.0]); X = np.array([np.pi, 0.0]); M = np.array([np.pi, np.pi])
    segs = [(G, X), (X, M), (M, G)]
    ks, s, ticks = [], [], [0.0]
    s0 = 0.0
    for a, b in segs:
        L = np.linalg.norm(b-a)
        for i in range(npts):
            f = i/npts
            ks.append(a + f*(b-a)); s.append(s0 + f*L)
        s0 += L; ticks.append(s0)
    ks.append(G); s.append(s0)
    ks = np.array(ks)
    return ks[:, 0], ks[:, 1], np.array(s), ticks
