"""Exact cluster Green's function G_11(K, w) (layer 1, spin up) of the periodic 16-site bilayer at its
allowed momenta, via Lanczos continued fractions. Used as a CPT-independent check of the sign
structure of G(K, midgap) at half filling."""
import numpy as np, sys, time, json
from ed_hubbard import make_cluster, lanczos, _apply_c_up, _apply_cdag_up_safe
from ed_bilayer import BSector, bilayer_hopping


def run(U, J, a1=(2, 2), a2=(-2, 2), N=16, tp=0.2, maxit=250, Klist=None, tag='x'):
    sites, red, Ks = make_cluster(a1, a2)
    M = len(sites)
    T = bilayer_hopping(sites, red, 1.0, tp, 0.0)
    n2 = N // 2
    sec0 = BSector(M, n2, n2, T, U, J)
    rng = np.random.default_rng(3)
    t0 = time.time()
    ev, a, b, gs = lanczos(sec0, rng.standard_normal(sec0.shape), maxit=500, want_vec=True)
    E0 = ev[0]
    print(f'GS E0={E0:.8f} ({time.time()-t0:.0f}s)', flush=True)
    secp = BSector(M, n2 + 1, n2, T, U, J)
    secm = BSector(M, n2 - 1, n2, T, U, J)
    allsites = np.vstack([sites, sites])  # 2M site positions (layer 1 then layer 2)
    out = {'E0': E0, 'K': [], 'p': [], 'h': []}
    if Klist is None:
        Klist = Ks
    for K in Klist:
        K = np.asarray(K, float)
        phase_p = np.zeros(2 * M, complex); phase_p[:M] = np.exp(1j * (sites @ K)) / np.sqrt(M)
        phase_h = np.zeros(2 * M, complex); phase_h[:M] = np.exp(-1j * (sites @ K)) / np.sqrt(M)
        vp = np.zeros(secp.shape, complex)
        _apply_cdag_up_safe(gs.astype(complex), secp.mu, sec0.lu, sec0.shape[1], phase_p, 2 * M, vp)
        vh = np.zeros(secm.shape, complex)
        _apply_c_up(gs.astype(complex), secm.mu, sec0.md, sec0.lu, sec0.shape[1], phase_h, 2 * M, vh)
        res = {}
        for lab, sec, v in [('p', secp, vp), ('h', secm, vh)]:
            n2v = np.vdot(v, v).real
            evv, aa, bb = lanczos(sec, v, maxit=maxit, tol=1e-12)
            res[lab] = (n2v, aa.tolist(), bb.tolist())
        out['K'].append(K.tolist()); out['p'].append(res['p']); out['h'].append(res['h'])
        print(f'K={np.round(K/np.pi,3)} pi: particle weight {res["p"][0]:.4f}, hole weight {res["h"][0]:.4f} ({time.time()-t0:.0f}s)', flush=True)
    json.dump(out, open(f'edgk_{tag}.json', 'w'))
    return out


if __name__ == '__main__':
    U = float(sys.argv[1]); J = float(sys.argv[2]); tag = sys.argv[3]
    Kl = [(0, 0), (np.pi, 0), (np.pi, np.pi), (np.pi / 2, np.pi / 2)]
    run(U, J, Klist=Kl, tag=tag)
