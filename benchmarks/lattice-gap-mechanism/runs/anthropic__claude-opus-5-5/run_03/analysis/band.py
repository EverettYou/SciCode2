import numpy as np
def eps(kx, ky, t=1.0, tp=0.2, tpp=0.0):
    # momenta in units of 2pi/a -> phases 2pi k
    cx, cy = np.cos(2*np.pi*kx), np.cos(2*np.pi*ky)
    return -2*t*(cx+cy) - 4*tp*cx*cy - 2*tpp*(np.cos(4*np.pi*kx)+np.cos(4*np.pi*ky))
def grid(N):
    k = (np.arange(N)+0.5)/N - 0.5
    KX, KY = np.meshgrid(k, k, indexing='ij')
    return KX, KY
def dos(t=1.0, tp=0.2, tpp=0.0, N=1024, bins=None, eta=0.0):
    KX, KY = grid(N)
    e = eps(KX, KY, t, tp, tpp).ravel()
    return e
