"""dDelta/dJ on the 4x2 bilayer torus (pp): ground-state energies of the N=16 Sz=0, N=16 Sz=1, N=15 and N=17
sectors at J=7, 8, 9 (t1=1, t2=0.2).  Charge gap E(17)+E(15)-2E(16); spin gap E(16,Sz=1)-E(16,Sz=0).
Writes data/dgap_dJ.json"""
import torch, sys, json, time
sys.path.insert(0, '.'); import ed_gpu as ed
torch.cuda.set_device(0)
Lx, Ly, t1, t2 = 4, 2, 1.0, 0.2
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
out = {}
for J in (7.0, 8.0, 9.0):
    E = {}
    for name, (nup, ndn) in {'N16_S0': (8, 8), 'N16_S1': (9, 7), 'N15': (8, 7), 'N17': (9, 8)}.items():
        sec = ed.Sector(Lx, Ly, nup, ndn, t1, t2, J, (1, 1))
        E0, *_ = ed.lanczos(sec, sec.random_vec(1), niter=200, tol=1e-11, want_vec=False)
        E[name] = float(E0); log(f'J={J} {name} E0={E0:.8f}')
        del sec; torch.cuda.empty_cache()
    out[str(J)] = dict(E=E, charge_gap=E['N17']+E['N15']-2*E['N16_S0'], spin_gap=E['N16_S1']-E['N16_S0'])
    log(f'J={J}: charge gap {out[str(J)]["charge_gap"]:.4f}  spin gap {out[str(J)]["spin_gap"]:.4f}')
    json.dump(out, open('../data/dgap_dJ.json', 'w'), indent=1)
out['dDc_dJ'] = (out['9.0']['charge_gap']-out['7.0']['charge_gap'])/2; out['dDs_dJ'] = (out['9.0']['spin_gap']-out['7.0']['spin_gap'])/2
log(f"dDelta_c/dJ = {out['dDc_dJ']:.3f}   dDelta_s/dJ = {out['dDs_dJ']:.3f}")
json.dump(out, open('../data/dgap_dJ.json', 'w'), indent=1); log('done')
