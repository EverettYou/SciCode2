import numpy as np, json
from scipy.ndimage import gaussian_filter1d
N=600
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k,k,indexing='ij')
def eps(t,tp): return (-2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)).ravel()
e = eps(1.0,0.2); es = np.sort(e)
mu0 = {nu: es[int(nu*len(es))] for nu in [0.2,0.3,0.5]}
print('normal-state mu0', mu0)
for nu, D in [(0.2,2.0),(0.2,1.9),(0.3,2.6),(0.3,5.0),(0.5,4.0)]:
    xi = e - mu0[nu]; E = np.sqrt(xi**2+D**2)
    v2 = 0.5*(1-xi/E)
    print(f"nu={nu} Delta={D}: fixed-mu sum v^2 (occupied weight per spin) = {v2.mean():.3f}")
