import numpy as np
from scipy.optimize import brentq
N=400
k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
t,tp=1.008,0.192
e=(-2*t*(cx+cy)-4*tp*cx*cy).ravel()
def mu_free(nu): return np.quantile(e,nu)
def gap_fixed_mu(U,mu):
    f=lambda D: U*np.mean(1/(2*np.sqrt((e-mu)**2+D**2)))-1
    if f(1e-4)<0: return 0.0
    return brentq(f,1e-4,50)
def gap_selfcons(U,nu):
    # solve gap and mu simultaneously (BCS-Leggett, T=0, no Hartree)
    def eqs(mu):
        D=gap_fixed_mu(U,mu)
        xi=e-mu; E=np.sqrt(xi**2+D**2)
        return np.mean(0.5*(1-xi/E))-nu, D
    mu=brentq(lambda m: eqs(m)[0],-20,20)
    return eqs(mu)[1],mu
for U in [6,7,8,8.5,9,10]:
    row=[]
    for nu in [0.2,0.3,0.5]:
        D1=gap_fixed_mu(U,mu_free(nu))
        D2,mu2=gap_selfcons(U,nu)
        row.append(f'nu={nu}: D(fixed mu)={D1:.2f} D(selfc)={D2:.2f}')
    print('U=',U,' | '.join(row))
