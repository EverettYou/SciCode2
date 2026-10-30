import sys, numpy as np
sys.path.insert(0, "code")
from model import Lattice, hamiltonian_terms, spin_corr_terms, interlayer_pair_terms, hop_terms, density_corr_terms
from ed import Sector, build_operator, ground_state, expect
lat = Lattice(2, 2, "oo"); nc = lat.n_cell
for J in [2.0, 8.0]:
    terms = hamiltonian_terms(lat, J)
    res = {}
    for name,(N1,N2,Nu,Nd) in {"N8_Sz0":(4,4,4,4), "N8_Sz1":(4,4,5,3), "N10_Sz0":(5,5,5,5), "N6_Sz0":(3,3,3,3), "N9":(5,4,5,4), "N7":(4,3,4,3)}.items():
        sec = Sector(lat, N1, N2, Nu, Nd)
        H = build_operator(sec, sec, terms)
        w, v = ground_state(H, k=1)
        res[name] = w[0]
        if name == "N8_Sz0":
            psi = v[:,0]
            print(f"J={J} N8_Sz0: rung S1.S2={expect(sec,psi,spin_corr_terms(lat,0,0,1,0)):.4f} S11(0,1)={expect(sec,psi,spin_corr_terms(lat,0,0,0,1)):.4f} pair(0,3)={expect(sec,psi,interlayer_pair_terms(lat,0,3)):.4f} pair(0,0)={expect(sec,psi,interlayer_pair_terms(lat,0,0)):.4f} g(0,1)={expect(sec,psi,hop_terms(lat,0,1,0,1)):.4f} docc={expect(sec,psi,[(1.0,((lat.mode(0,0,1),1),(lat.mode(0,0,1),0),(lat.mode(0,0,0),1),(lat.mode(0,0,0),0)))]):.4f} n1n2={expect(sec,psi,density_corr_terms(lat,0,0,1,0)):.4f}")
    print(f"J={J}: " + "  ".join(f"{k}={v:.5f}" for k,v in res.items()))
    print(f"   spin gap = {res['N8_Sz1']-res['N8_Sz0']:.4f}   charge gap(2) = {(res['N10_Sz0']+res['N6_Sz0']-2*res['N8_Sz0'])/2:.4f}   gap(1) = {res['N9']+res['N7']-2*res['N8_Sz0']:.4f}")
