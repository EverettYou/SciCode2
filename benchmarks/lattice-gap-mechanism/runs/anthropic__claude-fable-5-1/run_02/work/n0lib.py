import numpy as np
from fitlib import kgrid, ebar
def N0_grid(t=1.0, tp=-0.2, nk=2000, ne=4001):
    kx, ky = kgrid(nk)
    eb = ebar(kx, ky, t, tp)
    egrid = np.linspace(-4.2*t, 4.2*t, ne)
    de = egrid[1]-egrid[0]
    edges = np.concatenate([egrid-de/2,[egrid[-1]+de/2]])
    h,_ = np.histogram(eb.ravel(), bins=edges)
    return egrid, h/eb.size/de
def broaden(h, grid, sigma):
    dE = grid[1]-grid[0]
    if sigma<=0: return h
    n = int(5*sigma/dE)+1
    x = np.arange(-n,n+1)*dE
    g = np.exp(-x**2/(2*sigma**2)); g/=g.sum()
    return np.convolve(h, g, mode='same')
def hist_poles(Es, Ws, N0, de, grid, sigma):
    """Es, Ws: lists of arrays over ebar grid (pole energies and weights); N0 bare dos on ebar grid"""
    dE = grid[1]-grid[0]
    edges = np.concatenate([grid-dE/2,[grid[-1]+dE/2]])
    h = np.zeros(len(grid))
    for E,W in zip(Es,Ws):
        hh,_ = np.histogram(E, bins=edges, weights=W*N0*de)
        h += hh
    return broaden(h/dE, grid, sigma)
def bgfun(V, b0, p, Vin, w=0.1):
    s = 0.5*(1+np.tanh((np.abs(V)-Vin)/w))
    return b0*(np.abs(V)/5.0)**p * s
