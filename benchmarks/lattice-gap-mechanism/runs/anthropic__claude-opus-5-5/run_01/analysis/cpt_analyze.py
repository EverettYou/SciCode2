"""Vectorized CPT analysis: DOS, A(k,w) on Gamma-X-M-Gamma, band edges, Re G(k, w0) map."""
import numpy as np
from cpt_bilayer import CPT


def vk_batch(cpt, ks):
    """inter-cluster hopping V(k) for an array of k (nk,2) -> (nk, M, M)"""
    pos = cpt.pos; M = len(pos); Lx, Ly, t, tp = cpt.Lx, cpt.Ly, cpt.t, cpt.tp
    ks = np.asarray(ks, float)
    V = np.zeros((len(ks), M, M), complex)
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            if (a, b) == (0, 0):
                continue
            R = np.array([Lx * a, Ly * b])
            T = np.zeros((M, M))
            for i in range(M):
                for j in range(M):
                    d = pos[j] + R - pos[i]
                    if abs(d[0]) + abs(d[1]) == 1:
                        T[i, j] += -t
                    elif abs(d[0]) == 1 and abs(d[1]) == 1:
                        T[i, j] += -tp
            if np.any(T):
                ph = np.exp(1j * (ks @ R))
                V += ph[:, None, None] * T[None, :, :]
    return V


def G_batch(cpt, ks, z, V=None):
    if V is None:
        V = vk_batch(cpt, ks)
    Gci = np.linalg.inv(cpt.Gc(z))
    Gcpt = np.linalg.inv(Gci[None, :, :] - V)
    ph = np.exp(1j * (np.asarray(ks, float) @ cpt.pos.T))  # (nk, M)
    return np.einsum('ka,kab,kb->k', ph.conj(), Gcpt, ph) / len(cpt.pos)


def kpath(npts=60):
    G = np.array([0, 0.]); X = np.array([np.pi, 0.]); Mp = np.array([np.pi, np.pi])
    seg1 = [G + (X - G) * s for s in np.linspace(0, 1, npts, endpoint=False)]
    seg2 = [X + (Mp - X) * s for s in np.linspace(0, 1, npts, endpoint=False)]
    n3 = int(round(npts * np.sqrt(2)))
    seg3 = [Mp + (G - Mp) * s for s in np.linspace(0, 1, n3 + 1)]
    ks = np.array(seg1 + seg2 + seg3)
    # cumulative distance (in units of 2pi/a) for the x axis
    dist = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(ks, axis=0), axis=1))]) / (2 * np.pi)
    ticks = [0, dist[npts], dist[2 * npts], dist[-1]]
    return ks, dist, ticks


def analyze(cgf_file, Lx, Ly, tp=0.2, eta=0.06, w=None, nk_dos=32, npath=60, nk_map=101, mid=None,
            orient_avg=True):
    cpt = CPT(fn=cgf_file, Lx=Lx, Ly=Ly, t=1.0, tp=tp)
    if w is None:
        w = np.linspace(-12, 12, 1201)
    # orientation average (for Lx != Ly clusters): average over k and its 90-degree rotation
    rot = (lambda ks: ks[:, ::-1]) if (orient_avg and Lx != Ly) else None
    # DOS
    kg = (np.arange(nk_dos) + 0.5) / nk_dos * 2 * np.pi - np.pi
    KX, KY = np.meshgrid(kg, kg, indexing='ij')
    ks = np.stack([KX.ravel(), KY.ravel()], axis=1)
    Vg = vk_batch(cpt, ks)
    Vg_r = vk_batch(cpt, ks[:, ::-1]) if rot else None
    dos = np.zeros(len(w))
    for i, x in enumerate(w):
        g = G_batch(cpt, ks, x + 1j * eta, Vg)
        if rot:
            g = 0.5 * (g + G_batch(cpt, ks[:, ::-1], x + 1j * eta, Vg_r))
        dos[i] = -g.imag.mean() / np.pi
    # path spectral function
    kp, dist, ticks = kpath(npath)
    Vp = vk_batch(cpt, kp)
    Vp_r = vk_batch(cpt, kp[:, ::-1]) if rot else None
    A = np.zeros((len(kp), len(w)))
    for i, x in enumerate(w):
        g = G_batch(cpt, kp, x + 1j * eta, Vp)
        if rot:
            g = 0.5 * (g + G_batch(cpt, kp[:, ::-1], x + 1j * eta, Vp_r))
        A[:, i] = -g.imag / np.pi
    out = dict(w=w, dos=dos, A=A, dist=dist, ticks=np.array(ticks), kpath=kp)
    return cpt, out


def band_edges_from_path(cpt, Lx, Ly, w0, tp=0.2, eta=0.01, wr=(-12, 12), nw=6001, nk=40, rel=0.02):
    """Find max of spectral peaks below w0 and min above w0 on a k grid (with small eta)."""
    w = np.linspace(wr[0], wr[1], nw)
    kg = np.linspace(0, np.pi, nk)
    KX, KY = np.meshgrid(kg, kg, indexing='ij')
    ks = np.stack([KX.ravel(), KY.ravel()], axis=1)
    V = vk_batch(cpt, ks)
    rot = Lx != Ly
    Vr = vk_batch(cpt, ks[:, ::-1]) if rot else None
    A = np.zeros((len(ks), len(w)))
    for i, x in enumerate(w):
        g = G_batch(cpt, ks, x + 1j * eta, V)
        if rot:
            g = 0.5 * (g + G_batch(cpt, ks[:, ::-1], x + 1j * eta, Vr))
        A[:, i] = -g.imag
    lo, up = -np.inf, np.inf
    for a in A:
        pk = (a[1:-1] > a[:-2]) & (a[1:-1] > a[2:]) & (a[1:-1] > rel * a.max())
        wp = w[1:-1][pk]
        if np.any(wp < w0): lo = max(lo, wp[wp < w0].max())
        if np.any(wp > w0): up = min(up, wp[wp > w0].min())
    return lo, up


def zero_map(cpt, Lx, Ly, w0, nk=121):
    kg = np.linspace(-np.pi, np.pi, nk)
    KX, KY = np.meshgrid(kg, kg, indexing='ij')
    ks = np.stack([KX.ravel(), KY.ravel()], axis=1)
    g = G_batch(cpt, ks, w0 + 1e-9j)
    if Lx != Ly:
        g = 0.5 * (g + G_batch(cpt, ks[:, ::-1], w0 + 1e-9j))
    return kg, g.real.reshape(nk, nk)
