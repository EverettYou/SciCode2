import torch, sys, numpy as np
sys.path.insert(0, '.'); import ed_gpu as ed
torch.cuda.set_device(0)
Lx, Ly = 4, 2
for J in (0.0, 100.0):
    sec0 = ed.Sector(Lx, Ly, 8, 8, 1.0, 0.2, J, (1, 1))
    E0, psi, _, _ = ed.lanczos(sec0, sec0.random_vec(1), niter=150, tol=1e-11, want_vec=True)
    secp = ed.Sector(Lx, Ly, 9, 8, 1.0, 0.2, J, (1, 1)); secm = ed.Sector(Lx, Ly, 7, 8, 1.0, 0.2, J, (1, 1))
    print(f'J={J}: E0={E0:.6f}')
    for (kx, ky) in [(0, 0), (0, np.pi), (np.pi, 0), (np.pi/2, 0), (np.pi, np.pi)]:
        eps = -2*(np.cos(kx)+np.cos(ky)) - 0.8*np.cos(kx)*np.cos(ky)
        re, im = ed.c_k_vector(sec0, secp, psi, kx, ky, 0, True); pa = ed.poles(ed.spectrum_for_vector(secp, re, im, 120), E0, +1)
        re, im = ed.c_k_vector(sec0, secm, psi, kx, ky, 0, False); pr = ed.poles(ed.spectrum_for_vector(secm, re, im, 120), E0, -1)
        wa = np.array(pa[1]); pa0 = np.array(pa[0]); wr = np.array(pr[1]); pr0 = np.array(pr[0])
        ia = np.argmax(wa) if len(wa) else None; ir = np.argmax(wr) if len(wr) else None
        print(f'  k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi eps={eps:+.2f}: main add {pa0[ia] if ia is not None else None} w={wa[ia] if ia is not None else 0:.3f} | main rem {pr0[ir] if ir is not None else None} w={wr[ir] if ir is not None else 0:.3f}; first-order add {0.75*J+eps/2:.3f} rem {-0.75*J+eps/2:.3f}')
    del sec0, secp, secm, psi; torch.cuda.empty_cache()
