import numpy as np, time, sys
from ed_hubbard import make_cluster
from ed_bilayer import *
U = float(sys.argv[1]); J = float(sys.argv[2]); a1 = eval(sys.argv[3]); a2 = eval(sys.argv[4]); Nlist = eval(sys.argv[5])
tperp = float(sys.argv[6]) if len(sys.argv)>6 else 0.0
sites, red, Ks = make_cluster(a1, a2)
M = len(sites); Ns = 2*M
T = bilayer_hopping(sites, red, 1.0, 0.2, tperp)
res = {}
def E(nup, ndn):
    if (nup, ndn) in res: return res[(nup, ndn)]
    if nup < 0 or ndn < 0: return np.nan
    t0 = time.time(); sec = BSector(M, nup, ndn, T, U, J)
    ev, *_ = ground_state(sec, want_vec=False, maxit=400)
    res[(nup, ndn)] = ev[0]
    print(f'  E({nup},{ndn}) = {ev[0]:.6f} dim={sec.dim} ({time.time()-t0:.1f}s)', flush=True)
    return ev[0]
for N in Nlist:
    n2 = N//2
    E0 = E(n2, n2); Ep = E(n2+1, n2); Em = E(n2, n2-1); Es = E(n2+1, n2-1)
    print(f'RESULT U={U} J={J} tperp={tperp} M={M} N={N} nu={N/(2*Ns):.4f}: gap_sp={(Ep+Em-2*E0)/2:.4f} spin_gap={Es-E0:.4f} '
          f'mu+={Ep-E0:.4f} mu-={E0-Em:.4f}', flush=True)
