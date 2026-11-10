"""Coherent superconducting spectral function of the bilayer model in J_perp mean field (t_perp=0):
A_11(k,w) = u^2 L(w-E) + v^2 L(w+E),  E=sqrt(xi^2+Delta^2), xi = eps_k - mu  (mu, Delta self-consistent at nu)."""
import numpy as np, sys
from bcs_bilayer import solve
from cpt_analyze import kpath
def eps(k, t=1.0, tp=0.2):
    return -2*t*(np.cos(k[:,0])+np.cos(k[:,1])) - 4*tp*np.cos(k[:,0])*np.cos(k[:,1])
def bcs_akw(J, nu, w, eta=0.06, npath=50):
    D, mu = solve(J, nu)
    kp, dist, ticks = kpath(npath)
    xi = eps(kp) - mu; E = np.sqrt(xi**2 + D**2)
    u2 = 0.5*(1 + xi/E); v2 = 0.5*(1 - xi/E)
    L = lambda x: eta/np.pi/(x**2 + eta**2)
    A = u2[:,None]*L(w[None,:] - E[:,None]) + v2[:,None]*L(w[None,:] + E[:,None])
    return dict(w=w, A=A, dist=dist, ticks=np.array(ticks), kpath=kp, midgap=0.0, Delta=D, mu=mu)
if __name__ == '__main__':
    J = float(sys.argv[1])
    w = np.linspace(-12, 12, 961)
    for nu, tag in [(0.3, 'N10'), (0.2, 'N6')]:
        r = bcs_akw(J, nu, w)
        np.savez(f'bcs_akw_nu{nu}.npz', **r)
        print(nu, 'Delta=%.3f mu=%.3f' % (r['Delta'], r['mu']))
