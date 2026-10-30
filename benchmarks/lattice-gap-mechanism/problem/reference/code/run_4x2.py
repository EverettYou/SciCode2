"""Production ED on the 4x2 bilayer torus (16 sites): J=8, t1=1, t2=0.2.
Half filling: ground states under 4 boundary conditions, single-particle spectral poles at
all allowed k, triplon (rung-odd S+) spectra, gaps.  Doped sectors N=10 (nu=5/16) and N=6 (nu=3/16)."""
import torch, sys, json, time, numpy as np
sys.path.insert(0, '.'); import ed_gpu as ed
torch.cuda.set_device(0)
Lx, Ly, t1, t2, J = 4, 2, 1.0, 0.2, 8.0
NIT = 160
out = {'params': dict(Lx=Lx, Ly=Ly, t1=t1, t2=t2, J=J), 'half': {}, 'doped': {}, 'energies': {}}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def save(): json.dump(out, open('../data/ed_4x2.json', 'w'), indent=1)
BCS = {'pp': (1, 1), 'ap': (-1, 1), 'pa': (1, -1), 'aa': (-1, -1)}

def ground(nup, ndn, bc, want_vec=True, niter=NIT):
    sec = ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, bc)
    E0, psi, al, be = ed.lanczos(sec, sec.random_vec(1), niter=niter, tol=1e-11, want_vec=want_vec)
    return sec, E0, psi

def single_particle(sec0, E0, psi, bc, rec):
    secp = ed.Sector(Lx, Ly, sec0.nup+1, sec0.ndn, t1, t2, J, bc); secm = ed.Sector(Lx, Ly, sec0.nup-1, sec0.ndn, t1, t2, J, bc)
    kxs, kys = ed.allowed_k(Lx, Ly, bc)
    rec['A'] = {}
    for kx in kxs:
        for ky in kys:
            re, im = ed.c_k_vector(sec0, secp, psi, kx, ky, 0, True)
            pp = ed.poles(ed.spectrum_for_vector(secp, re, im, NIT), E0, +1)
            re, im = ed.c_k_vector(sec0, secm, psi, kx, ky, 0, False)
            ph = ed.poles(ed.spectrum_for_vector(secm, re, im, NIT), E0, -1)
            rec['A'][f'{kx:.6f},{ky:.6f}'] = {'add': pp, 'rem': ph, 'n_k': float(sum(ph[1])), 'one_minus_n_k': float(sum(pp[1]))}
            log(f'  k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi  n(k)={sum(ph[1]):.4f}  lowest add {min(pp[0]) if pp[0] else None:.4f}  highest rem {max(ph[0]) if ph[0] else None:.4f}')
    del secp, secm; torch.cuda.empty_cache()

def triplon(sec0, E0, psi, bc, rec):
    kxs, kys = ed.allowed_k(Lx, Ly, bc)
    rec['S'] = {}
    secT = None
    for kx in kxs:
        for ky in kys:
            re, im, bT = ed.splus_k_vector(sec0, psi, kx, ky, 'odd')
            if secT is None: secT = ed.Sector(Lx, Ly, bT.nup, bT.ndn, t1, t2, J, bc)
            p = ed.poles(ed.spectrum_for_vector(secT, re, im, NIT), E0, +1)
            rec['S'][f'{kx:.6f},{ky:.6f}'] = {'odd': p}
            log(f'  triplon k=({kx/np.pi:.2f},{ky/np.pi:.2f})pi lowest pole {min(p[0]):.4f} weight {p[1][int(np.argmin(p[0]))]:.4f} total {sum(p[1]):.4f}')
    del secT; torch.cuda.empty_cache()

# ---------------- half filling ----------------
for name, bc in BCS.items():
    log('half filling bc', name)
    sec0, E0, psi = ground(8, 8, bc)
    rec = {'E0': E0}; out['half'][name] = rec; log(f'  E0={E0:.8f}')
    single_particle(sec0, E0, psi, bc, rec); save()
    triplon(sec0, E0, psi, bc, rec); save()
    del sec0, psi; torch.cuda.empty_cache()

# ---------------- doped sectors ----------------
for N, (nup, ndn) in {10: (5, 5), 6: (3, 3)}.items():
    for name, bc in BCS.items():
        log(f'doped N={N} bc {name}')
        sec0, E0, psi = ground(nup, ndn, bc)
        rec = {'E0': E0, 'nu': N/32}; out['doped'][f'N{N}_{name}'] = rec
        single_particle(sec0, E0, psi, bc, rec); save()
        # spin gap (Sz=1 lowest)
        secS = ed.Sector(Lx, Ly, nup+1, ndn-1, t1, t2, J, bc); ES, _, _, _ = ed.lanczos(secS, secS.random_vec(1), niter=NIT, tol=1e-11)
        rec['E_Sz1'] = ES; rec['spin_gap'] = ES-E0; log(f'  spin gap {ES-E0:.4f}'); del secS
        if name == 'pp':
            triplon(sec0, E0, psi, bc, rec); save()
        del sec0, psi; torch.cuda.empty_cache()

# ---------------- ground energies vs N (PBC and APBC-APBC) for pair binding ----------------
for name in ('pp', 'aa'):
    bc = BCS[name]
    for N in range(4, 21):
        nup = (N+1)//2; ndn = N//2
        sec = ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, bc)
        E, _, _, _ = ed.lanczos(sec, sec.random_vec(1), niter=NIT, tol=1e-11)
        out['energies'][f'N{N}_{name}'] = E; log(f'  E(N={N},{name}) = {E:.6f}'); del sec; torch.cuda.empty_cache(); save()
log('done')
