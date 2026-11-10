import numpy as np
from scipy.optimize import brentq
N=1024
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k,k,indexing='ij')
t, tp = 1.0, 0.2
eps = (-2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)).ravel()
emin = eps.min()
for U in [4,6,8,10,11,12,13]:
    f = lambda E: U*np.mean(1.0/(2*eps - E)) - 1.0
    E = brentq(f, -100, 2*emin-1e-9)
    Eb = 2*emin - E
    print(f"|U|={U}: pair energy E={E:.4f}, binding E_b={Eb:.4f}, E_b/2={Eb/2:.4f}")
