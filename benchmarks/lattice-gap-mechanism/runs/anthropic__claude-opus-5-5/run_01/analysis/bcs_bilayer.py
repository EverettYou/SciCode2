"""BCS mean-field for interlayer singlet pairing driven by J_perp (gap eq. identical to attractive-U with |U_eff|=J_perp),
including the intralayer Hartree shift (absorbed in mu). Returns Delta(nu,T), mu, T_MF."""
import numpy as np
from scipy.optimize import brentq
N = 256
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k, k, indexing='ij')
def eps(t=1.0, tp=0.2):
    return (-2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)).ravel()
E_K = eps()
def solve(J, nu, T=1e-4, e=E_K, D0=1.0):
    D = D0
    for it in range(2000):
        def nfun(mu):
            xi = e - mu; Ek = np.sqrt(xi**2 + D**2)
            return np.mean(1 - xi/Ek*np.tanh(Ek/(2*T))) - 2*nu
        mu = brentq(nfun, -400, 400)
        xi = e - mu; Ek = np.sqrt(xi**2 + D**2)
        Dn = J*np.mean(D/(2*Ek)*np.tanh(Ek/(2*T)))
        if abs(Dn - D) < 1e-8: break
        D = 0.3*D + 0.7*Dn
        if D < 1e-7: return 0.0, mu
    return D, mu
def Tmf(J, nu, e=E_K):
    # linearized gap eq at fixed density
    def f(T):
        def nfun(mu): return np.mean(1 - np.tanh((e-mu)/(2*T))) - 2*nu
        mu = brentq(nfun, -400, 400)
        xi = e - mu
        chi = np.mean(np.where(np.abs(xi) > 1e-9, np.tanh(xi/(2*T))/(2*xi), 1/(4*T)))
        return J*chi - 1
    return brentq(f, 1e-3, 20)
if __name__ == '__main__':
    for J in [5.0, 5.5, 6.0, 6.5, 7.0]:
        line = []
        for nu in [0.1, 0.2, 0.3, 0.4, 0.5]:
            D, mu = solve(J, nu)
            line.append(f'{nu}:D={D:.2f},Tmf={Tmf(J,nu):.2f}')
        print(f'J={J}: ' + ' | '.join(line))
