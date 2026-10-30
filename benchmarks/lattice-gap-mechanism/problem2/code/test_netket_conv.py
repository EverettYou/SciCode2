import sys, time
import numpy as np
sys.path.insert(0, "code")
import netket as nk
from model import Lattice, hamiltonian_terms
from ed import Sector, build_operator, ground_state

lat = Lattice(2, 2, "oo")
nc = lat.n_cell
hi = nk.hilbert.SpinOrbitalFermions(lat.n_orb, s=1/2, n_fermions_per_spin=(nc, nc))
print("hilbert size", hi.size, "n_states", hi.n_states)
# check index layout
try:
    print("index(orbital=0, spin=-1):", hi._get_index(0, -1), " index(orbital=0, spin=+1):", hi._get_index(0, +1))
    print("index(orbital=3, spin=-1):", hi._get_index(3, -1), " index(orbital=3, spin=+1):", hi._get_index(3, +1))
except Exception as e:
    print("no _get_index:", e)
J = 2.0
terms = hamiltonian_terms(lat, J)
ops = [list(t[1]) for t in terms]
ws = [t[0] for t in terms]
H_nk = nk.operator.FermionOperator2nd(hi, ops, ws)
t0 = time.time()
Hs = H_nk.to_sparse()
w_nk = np.linalg.eigvalsh(Hs.toarray())
print("netket spectrum (lowest 5):", w_nk[:5], f"({time.time()-t0:.1f}s)")
# my ED over all (N1,N2) sectors with Nup=Ndn=nc
allw = []
for N1 in range(0, 2*nc+1):
    N2 = 2*nc - N1
    sec = Sector(lat, N1, N2, nc, nc)
    if sec.dim == 0: continue
    H = build_operator(sec, sec, terms)
    allw.append(np.linalg.eigvalsh(H.toarray()))
allw = np.sort(np.concatenate(allw))
print("my ED spectrum (lowest 5):   ", allw[:5], "total dim", len(allw))
print("max |diff| over full spectrum:", np.max(np.abs(allw - w_nk)))
# Also check the jax-compatible conserving operator
try:
    Hc = nk.experimental.operator.ParticleNumberAndSpinConservingFermioperator2nd.from_fermionoperator2nd(H_nk)
    print("conserving op ok; n_conn max:", Hc.max_conn_size)
except Exception as e:
    print("conserving op error:", repr(e)[:300])
