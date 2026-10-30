"""3x3 bilayer torus (18 sites, up to 2.4e9 states) with lean matvec: charge gap, spin gap and the
single-particle poles at k=(0,0) [PBC] and (pi,pi) [APBC], all without double-counted bonds."""
import torch, sys, json, time, numpy as np
sys.path.insert(0, '.'); import ed_gpu as ed
torch.cuda.set_device(1)
Lx, Ly, t1, t2, J = 3, 3, 1.0, 0.2, 8.0
NIT = 90
out = {'params': dict(Lx=Lx, Ly=Ly, t1=t1, t2=t2, J=J)}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def save(): json.dump(out, open('../data/ed_3x3.json', 'w'), indent=1)
def sector(nup, ndn, bc): return ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, bc, lean=True, chunk=4096)
def energy(nup, ndn, bc, want_vec=False, niter=NIT):
    sec = sector(nup, ndn, bc)
    E, psi, al, be = ed.lanczos(sec, sec.random_vec(1), niter=niter, tol=1e-9, want_vec=want_vec, verbose=True)
    return sec, E, psi
for name, bc in {'pp': (1, 1), 'aa': (-1, -1)}.items():
    log('3x3 N=18 bc', name)
    sec0, E0, psi = energy(9, 9, bc, want_vec=True); out[f'E18_{name}'] = E0; log(f'E18({name})={E0:.8f}'); save()
    k = (0.0, 0.0) if name == 'pp' else (np.pi, np.pi)
    for sign, dn in ((+1, (10, 9)), (-1, (8, 9))):
        sect = sector(*dn, bc)
        re, im = ed.c_k_vector(sec0, sect, psi, k[0], k[1], 0, sign > 0)
        parts = ed.spectrum_for_vector(sect, re, im, NIT)
        p = ed.poles(parts, E0, sign)
        key = 'add' if sign > 0 else 'rem'
        out[f'A_{name}_{key}'] = {'k': list(k), 'poles': p}
        Emin = min(np.min(al_e) for al_e in [ed.poles_from_lanczos(a, b, n)[0] for a, b, n in parts])
        out[f'E{18+sign}_{name}_ksector'] = float(Emin)
        log(f'  {key} at k=({k[0]/np.pi:.0f},{k[1]/np.pi:.0f})pi: extreme pole {min(p[0]) if sign>0 else max(p[0]):.5f} weight {p[1][int(np.argmin(p[0])) if sign>0 else int(np.argmax(p[0]))]:.4f}  sum {sum(p[1]):.4f}  E_sector_min {Emin:.6f}')
        del sect, re, im; torch.cuda.empty_cache(); save()
    # triplon at this k (rung-odd S+)
    re, im, bT = ed.splus_k_vector(sec0, psi, k[0], k[1], 'odd'); secT = sector(bT.nup, bT.ndn, bc)
    parts = ed.spectrum_for_vector(secT, re, im, NIT); p = ed.poles(parts, E0, +1)
    out[f'S_{name}'] = {'k': list(k), 'poles': p}; log(f'  triplon at k=({k[0]/np.pi:.0f},{k[1]/np.pi:.0f})pi: lowest pole {min(p[0]):.5f} weight {p[1][int(np.argmin(p[0]))]:.4f}')
    del secT, re, im, sec0, psi; torch.cuda.empty_cache(); save()
    # N+-1 ground energies (full sector, not k-resolved) and Sz=1
    for lab, (nu, nd) in {'E19': (10, 9), 'E17': (8, 9), 'E18_Sz1': (10, 8)}.items():
        sec, E, _ = energy(nu, nd, bc); out[f'{lab}_{name}'] = E; log(f'{lab}({name})={E:.8f}'); del sec; torch.cuda.empty_cache(); save()
log('done')
