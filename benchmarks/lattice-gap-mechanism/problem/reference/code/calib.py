"""Harmonic fits on the square lattice used to interpolate ED pole data to arbitrary k."""
import numpy as np
def basis(kx, ky, n=4):
    kx = np.asarray(kx, float); ky = np.asarray(ky, float)
    cols = [np.ones_like(kx), np.cos(kx)+np.cos(ky), np.cos(kx)*np.cos(ky), np.cos(2*kx)+np.cos(2*ky),
            np.cos(2*kx)*np.cos(ky)+np.cos(kx)*np.cos(2*ky)]
    return np.stack(cols[:n], -1)
def fit(kx, ky, y, n=4):
    X = basis(kx, ky, n); coef, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    rms = float(np.sqrt(np.mean((X@coef-y)**2))); return coef.tolist(), rms
def ev(coef, kx, ky):
    coef = np.asarray(coef, float); return basis(kx, ky, len(coef)) @ coef
