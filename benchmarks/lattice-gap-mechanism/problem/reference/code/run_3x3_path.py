"""3x3 bilayer torus: single-particle poles on a 6x6 k grid (3 boundary conditions), triplon poles,
doped sectors N=12 (nu=1/3) and N=8 (nu=2/9), gaps.  Lean GPU matvec.  Writes data/ed_3x3_path.json"""
import torch, sys, json, time, os, numpy as np
sys.path.insert(0, '.'); import ed_gpu as ed
torch.cuda.set_device(int(os.environ.get('GPU', '1')))
Lx, Ly, t1, t2, J = 3, 3, 1.0, 0.2, 8.0
NIT_GS, NIT_SP = 60, 70
P3 = np.pi/3
KPTS = {'pp': [(0, 0), (2*P3, 0), (2*P3, 2*P3)],
        'ap': [(P3, 0), (np.pi, 0), (P3, 2*P3), (np.pi, 2*P3)],
        'aa': [(P3, P3), (np.pi, P3), (np.pi, np.pi)]}
BCS = {'pp': (1, 1), 'ap': (-1, 1), 'aa': (-1, -1)}
fn = '../data/ed_3x3_path.json'
out = json.load(open(fn)) if os.path.exists(fn) else {'params': dict(Lx=Lx, Ly=Ly, t1=t1, t2=t2, J=J)}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def save(): json.dump(out, open(fn, 'w'), indent=1)
def sector(nup, ndn, bc): return ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, bc, lean=True, chunk=4096)
def ground(nup, ndn, bc, want_vec=True):
    sec = sector(nup, ndn, bc); E, psi, _, _ = ed.lanczos(sec, sec.random_vec(1), niter=NIT_GS, tol=1e-9, want_vec=want_vec)
    return sec, E, psi
def spectra(sec0, E0, psi, bc, kpts, rec, triplon=False):
    secp = sector(sec0.nup+1, sec0.ndn, bc)
    for (kx, ky) in kpts:
        re, im = ed.c_k_vector(sec0, secp, psi, kx, ky, 0, True); p = ed.poles(ed.spectrum_for_vector(secp, re, im, NIT_SP), E0, +1); del re, im
        rec.setdefault('A', {}).setdefault(f'{kx:.6f},{ky:.6f}', {})['add'] = p; save()
        log(f'   add k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi: lowest {min(p[0]):.4f} (w {p[1][int(np.argmin(p[0]))]:.3f}) total {sum(p[1]):.4f}')
    del secp; torch.cuda.empty_cache()
    secm = sector(sec0.nup-1, sec0.ndn, bc)
    for (kx, ky) in kpts:
        re, im = ed.c_k_vector(sec0, secm, psi, kx, ky, 0, False); p = ed.poles(ed.spectrum_for_vector(secm, re, im, NIT_SP), E0, -1); del re, im
        rec['A'][f'{kx:.6f},{ky:.6f}']['rem'] = p; rec['A'][f'{kx:.6f},{ky:.6f}']['n_k'] = float(sum(p[1])); save()
        log(f'   rem k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi: highest {max(p[0]):.4f} (w {p[1][int(np.argmax(p[0]))]:.3f}) n(k) {sum(p[1]):.4f}')
    del secm; torch.cuda.empty_cache()
    if triplon:
        secT = None
        for (kx, ky) in kpts:
            re, im, bT = ed.splus_k_vector(sec0, psi, kx, ky, 'odd')
            if secT is None: secT = sector(bT.nup, bT.ndn, bc)
            p = ed.poles(ed.spectrum_for_vector(secT, re, im, NIT_SP), E0, +1); del re, im
            rec.setdefault('S', {})[f'{kx:.6f},{ky:.6f}'] = p; save()
            log(f'   triplon k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi: lowest {min(p[0]):.4f} (w {p[1][int(np.argmin(p[0]))]:.3f})')
        del secT; torch.cuda.empty_cache()

for N, (nup, ndn) in {18: (9, 9), 12: (6, 6), 8: (4, 4)}.items():
    for name, bc in BCS.items():
        key = f'N{N}_{name}'
        if key in out and 'S' in out[key] if N == 18 else (key in out and len(out[key].get('A', {})) == len(KPTS[name]) and 'rem' in list(out[key]['A'].values())[-1]):
            log('skip', key); continue
        log(f'=== N={N} bc={name}')
        sec0, E0, psi = ground(nup, ndn, bc); rec = out.setdefault(key, {}); rec['E0'] = E0; rec['nu'] = N/36; save(); log(f'   E0={E0:.8f}')
        spectra(sec0, E0, psi, bc, KPTS[name], rec, triplon=(N == 18))
        del sec0, psi; torch.cuda.empty_cache()
# gaps in the doped sectors (PBC): spin gap, E(N+-1), E(N+-2)
for N in (12, 8):
    nup = ndn = N//2; bc = (1, 1)
    for lab, (nu_, nd_) in {'Sz1': (nup+1, ndn-1), 'Np1': (nup+1, ndn), 'Nm1': (nup-1, ndn), 'Np2': (nup+1, ndn+1), 'Nm2': (nup-1, ndn-1)}.items():
        key = f'N{N}_pp_{lab}'
        if key in out: continue
        sec = sector(nu_, nd_, bc); E, _, _, _ = ed.lanczos(sec, sec.random_vec(1), niter=NIT_GS, tol=1e-9); out[key] = E; save(); log(f'   {key} = {E:.6f}'); del sec; torch.cuda.empty_cache()
log('done')
