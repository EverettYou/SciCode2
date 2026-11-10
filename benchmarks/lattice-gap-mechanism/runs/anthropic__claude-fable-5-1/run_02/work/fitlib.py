import numpy as np
from scipy.optimize import minimize

def kgrid(nk):
    k = (np.arange(nk)+0.5)*2*np.pi/nk - np.pi
    kx, ky = np.meshgrid(k, k, indexing='ij')
    return kx, ky

def ebar(kx, ky, t=1.0, tp=-0.2):
    eps = -2*t*(np.cos(kx)+np.cos(ky)) + 4*tp*np.cos(kx)*np.cos(ky)
    mid = (-4*t+4*tp + 4*t+4*tp)/2  # (eps(0,0)+eps(pi,pi))/2 = 4tp
    return eps - mid

def dos(Es, Ws, grid, sigma):
    dE = grid[1]-grid[0]
    edges = np.concatenate([grid-dE/2, [grid[-1]+dE/2]])
    h = np.zeros(len(grid))
    for E, W in zip(Es, Ws):
        hh,_ = np.histogram(E.ravel(), bins=edges, weights=np.broadcast_to(W, E.shape).ravel())
        h += hh
    h = h/Es[0].size/dE
    if sigma > 0:
        n = int(5*sigma/dE)+1
        x = np.arange(-n, n+1)*dE
        g = np.exp(-x**2/(2*sigma**2)); g /= g.sum()
        h = np.convolve(h, g, mode='same')
    return h

def chi2(model, data, mask, bg=None):
    """normalize model to max 1 (within mask) and compare; data noise ~0.012"""
    m = model/model[mask].max()
    if bg is not None: m = m + bg
    r = (m - data)[mask]
    return np.sum(r**2)/0.012**2/mask.sum()
