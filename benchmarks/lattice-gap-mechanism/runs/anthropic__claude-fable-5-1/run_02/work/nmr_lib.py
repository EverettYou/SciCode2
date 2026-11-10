import numpy as np
from fitlib import kgrid, ebar

def hyperfine_terms(kx, ky, AoverB):
    """return list of (a_j*a_l, H_jl(k)) for F(q)=(A+2B(cos qx+cos qy))^2 with B=1"""
    A = AoverB; B = 1.0
    h = [np.ones_like(kx), np.cos(kx), np.sin(kx), np.cos(ky), np.sin(ky)]
    a = [A, 2*B, 2*B, 2*B, 2*B]
    terms = []
    for j in range(5):
        for l in range(5):
            terms.append((a[j]*a[l], h[j]*h[l]))
    return terms

def phi_E(E_list, w_list, terms, grid, sigma):
    """Phi(E) = sum_jl a_j a_l sum_m c_m [sum_bands sum_k w_m(k) H_jl(k) delta(E-E_b(k))]^2
       E_list: list of band energy arrays; w_list: list of (c_m, [w_m for each band])"""
    dE = grid[1]-grid[0]
    edges = np.concatenate([grid-dE/2,[grid[-1]+dE/2]])
    n = int(5*sigma/dE)+1; x = np.arange(-n,n+1)*dE
    gk = np.exp(-x**2/(2*sigma**2)); gk/=gk.sum()
    Phi = np.zeros(len(grid))
    N = E_list[0].size
    for (ajl, H) in terms:
        for (cm, wb) in w_list:
            dens = np.zeros(len(grid))
            for Eb, w in zip(E_list, wb):
                hh,_ = np.histogram(Eb.ravel(), bins=edges, weights=(w*H).ravel())
                dens += hh
            dens = np.convolve(dens/N/dE, gk, mode='same')
            Phi += ajl*cm*dens**2
    return Phi

def dfdw(w, T):
    x = np.clip(w/(2*T), -300, 300); return 1/(4*T*np.cosh(x)**2)

def T1T_from_phi(Phi, grid, T):
    return np.trapezoid(dfdw(grid, T)*Phi, grid)
