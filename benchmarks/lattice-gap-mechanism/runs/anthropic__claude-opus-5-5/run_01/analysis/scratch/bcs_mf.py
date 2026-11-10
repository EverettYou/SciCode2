import numpy as np
from scipy.optimize import brentq
N=200
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k,k,indexing='ij')
t, tp = 1.0, 0.2
eps = (-2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)).ravel()
def solve(U, nu, T=1e-3):
    # attractive U>0 magnitude; n per spin = nu; Hartree shift -U*nu absorbed in mu
    n_target = 2*nu
    D = 1.0
    for it in range(500):
        def nfun(mu):
            xi = eps - mu; E = np.sqrt(xi**2 + D**2)
            return np.mean(1 - xi/E*np.tanh(E/(2*T))) - n_target
        mu = brentq(nfun, -30, 30)
        xi = eps-mu; E = np.sqrt(xi**2 + D**2)
        Dn = U*np.mean(D/(2*E)*np.tanh(E/(2*T)))
        if abs(Dn-D)<1e-7: break
        D = 0.5*D+0.5*Dn
    return D, mu
for U in [3,4,5,6,8,12]:
    out=[]
    for nu in [0.2,0.3,0.5]:
        D, mu = solve(U, nu)
        xi = eps-mu
        gapedge = np.sqrt(xi**2+D**2).min()
        out.append(f"nu={nu}: Delta={D:.2f} mu-bottom={mu-eps.min():.2f} gap_edge={gapedge:.2f}")
    print(f"|U|={U}: "+' | '.join(out))
