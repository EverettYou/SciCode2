"""Task 5: recover G(k, w) from the predicted spectral function by Kramers-Kronig and locate the zeros at
w = 0 (chemical potential at midgap).  Re G(k,0) = P int dw' A(k,w') / (0 - w').
Also cross-checks against the directly evaluated CPT Green's function."""
import numpy as np, sys, json
from cpt_analyze import vk_batch, G_batch, band_edges_from_path
from cpt_bilayer import CPT


def area_fraction_gamma_side(G):
    """G on an (nk x nk) grid covering [-pi,pi)^2 (endpoint excluded); fraction with the sign found at Gamma."""
    nk = G.shape[0]
    # Gamma is not on the offset grid: use the sign at the grid point nearest to Gamma
    s0 = np.sign(G[nk // 2, nk // 2])
    return float(np.mean(np.sign(G) == s0)), s0


def run(cgf, Lx, Ly, nk=64, eta=0.02, wmax=16.0, dw=0.005, tp=0.2, mid=None):
    cpt = CPT(fn=cgf, Lx=Lx, Ly=Ly, t=1.0, tp=tp)
    if mid is None:
        w0 = 0.5 * (cpt.ep.min() + cpt.em.max())
        lo, up = band_edges_from_path(cpt, Lx, Ly, w0, tp=tp)
        mid = 0.5 * (lo + up)
    else:
        lo = up = np.nan
    kg = -np.pi + 2 * np.pi * (np.arange(nk) + 0.5) / nk   # offset grid (avoids sampling exactly on symmetry lines)
    KX, KY = np.meshgrid(kg, kg, indexing='ij')
    ks = np.stack([KX.ravel(), KY.ravel()], axis=1)
    V = vk_batch(cpt, ks)
    rot = Lx != Ly
    Vr = vk_batch(cpt, ks[:, ::-1]) if rot else None
    # spectral function on a fine grid (w measured from midgap)
    w = np.arange(-wmax, wmax + dw / 2, dw)
    A = np.zeros((len(ks), len(w)))
    for i, x in enumerate(w):
        g = G_batch(cpt, ks, mid + x + 1j * eta, V)
        if rot:
            g = 0.5 * (g + G_batch(cpt, ks[:, ::-1], mid + x + 1j * eta, Vr))
        A[:, i] = -g.imag / np.pi
    # Kramers-Kronig at w=0: Re G = -P int A(w')/w' dw'  (principal value by symmetric exclusion of |w'|<dw/2)
    kernel = np.where(np.abs(w) > dw / 2, -1.0 / np.where(w == 0, 1, w), 0.0)
    ReG_kk = (A * kernel[None, :]).sum(axis=1) * dw
    # direct evaluation (eta -> 0+ in the gap)
    g = G_batch(cpt, ks, mid + 1e-9j, V)
    if rot:
        g = 0.5 * (g + G_batch(cpt, ks[:, ::-1], mid + 1e-9j, Vr))
    ReG_dir = g.real
    wsum = A.sum(axis=1) * dw
    Gk = ReG_kk.reshape(nk, nk); Gd = ReG_dir.reshape(nk, nk)
    f_kk, s_kk = area_fraction_gamma_side(Gk)
    f_d, s_d = area_fraction_gamma_side(Gd)
    nf = 241
    kf = -np.pi + 2 * np.pi * (np.arange(nf) + 0.5) / nf
    KXf, KYf = np.meshgrid(kf, kf, indexing='ij'); ksf = np.stack([KXf.ravel(), KYf.ravel()], axis=1)
    gf = G_batch(cpt, ksf, mid + 1e-9j)
    if rot:
        gf = 0.5 * (gf + G_batch(cpt, ksf[:, ::-1], mid + 1e-9j))
    Gf = gf.real.reshape(nf, nf)
    f_fine, _ = area_fraction_gamma_side(Gf)
    np.save(cgf.replace('.npz', '_Gfine.npy'), Gf)
    res = dict(cgf=cgf, frac_gamma_side_fine241=f_fine, midgap=float(mid), lower_top=float(lo), upper_bottom=float(up),
               frac_gamma_side_KK=f_kk, frac_gamma_side_direct=f_d, sign_at_gamma=float(s_kk),
               sum_rule_min=float(wsum.min()), sum_rule_max=float(wsum.max()))
    np.savez(cgf.replace('.npz', '_kk.npz'), kg=kg, ReG_kk=Gk, ReG_dir=Gd, mid=mid)
    return res


if __name__ == '__main__':
    cgf = sys.argv[1]; Lx = int(sys.argv[2]); Ly = int(sys.argv[3])
    nk = int(sys.argv[4]) if len(sys.argv) > 4 else 64
    print(json.dumps(run(cgf, Lx, Ly, nk=nk), indent=1))
