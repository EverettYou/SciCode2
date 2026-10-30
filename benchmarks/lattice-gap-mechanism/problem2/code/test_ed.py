import sys, time
import numpy as np
sys.path.insert(0, "code")
from model import Lattice, hamiltonian_terms, free_energy_sector, spin_corr_terms, interlayer_pair_terms
from ed import Sector, build_operator, ground_state, expect

lat = Lattice(2, 2, "oo")
print("nn bonds", lat.nn_bonds)
print("nnn bonds", lat.nnn_bonds)
nc = lat.n_cell
# half filling: N1=N2=nc, Nup=Ndn=nc
sec = Sector(lat, nc, nc, nc, nc)
print("dim half filling sector:", sec.dim)
for J in [0.0, 0.5, 2.0, 8.0, 40.0]:
    t0 = time.time()
    H = build_operator(sec, sec, hamiltonian_terms(lat, J))
    w, v = ground_state(H, k=1)
    psi = v[:, 0]
    rung = expect(sec, psi, spin_corr_terms(lat, 0, 0, 1, 0))
    pair = expect(sec, psi, interlayer_pair_terms(lat, 0, 3))
    print(f"J={J:5.1f} E0={w[0]:.6f} E/site={w[0]/nc:.6f}  <S1.S2>rung={rung:.4f}  P(0,3)={pair:.4f}  ({time.time()-t0:.1f}s)")
e_free, info = free_energy_sector(lat, {(0,1):nc//2,(0,0):nc//2,(1,1):nc//2,(1,0):nc//2})
print("free J=0 energy (closed shell check):", e_free, info)
print("strong-coupling leading: -3J/4 per rung -> E = ", -0.75*40*nc)
