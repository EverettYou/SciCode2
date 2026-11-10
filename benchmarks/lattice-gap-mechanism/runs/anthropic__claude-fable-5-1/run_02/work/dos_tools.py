import numpy as np
def band(t=1.0, tp=-0.2, nk=1200):
    k = (np.arange(nk)+0.5)*2*np.pi/nk - np.pi
    kx, ky = np.meshgrid(k, k, indexing='ij')
    eps = -2*t*(np.cos(kx)+np.cos(ky)) + 4*tp*np.cos(kx)*np.cos(ky)
    return kx, ky, eps
def dos_from_E(E, W, grid, sigma):
    """DOS on energy grid from energies E (flattened) with weights W, Gaussian broadening sigma"""
    dE = grid[1]-grid[0]
    edges = np.concatenate([grid-dE/2, [grid[-1]+dE/2]])
    h,_ = np.histogram(E.ravel(), bins=edges, weights=np.broadcast_to(W, E.shape).ravel())
    h = h/E.size/dE
    if sigma>0:
        n = int(5*sigma/dE)
        x = np.arange(-n, n+1)*dE
        g = np.exp(-x**2/(2*sigma**2)); g/=g.sum()
        h = np.convolve(h, g, mode='same')
    return h
