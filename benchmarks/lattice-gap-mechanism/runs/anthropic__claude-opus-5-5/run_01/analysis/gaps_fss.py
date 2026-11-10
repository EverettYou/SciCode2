import numpy as np, time, sys
from ed_hubbard import *
U = float(sys.argv[1]); a1 = eval(sys.argv[2]); a2 = eval(sys.argv[3]); Nlist = eval(sys.argv[4])
sites, red, Ks = make_cluster(a1, a2)
Ns = len(sites)
T = hopping_matrix(sites, red, 1.0, 0.2)
print(f'cluster {a1},{a2} Ns={Ns}; single-particle levels:', np.round(np.linalg.eigvalsh(T),3))
res = {}
def E(nup, ndn):
    if (nup, ndn) in res: return res[(nup, ndn)]
    if nup < 0 or ndn < 0: return np.nan
    if nup == 0 and ndn == 0: return 0.0
    t0=time.time(); sec = Sector(Ns, nup, ndn, T, U)
    ev, *_ = ground_state(sec, want_vec=False, maxit=500)
    res[(nup, ndn)] = ev[0]
    print(f'  E({nup},{ndn}) = {ev[0]:.8f} dim={sec.dim} ({time.time()-t0:.1f}s)', flush=True)
    return ev[0]
for N in Nlist:
    n2 = N//2
    E0 = E(n2,n2); Ep = E(n2+1,n2); Em = E(n2,n2-1) if n2>0 else np.nan
    Es = E(n2+1,n2-1)
    print(f'RESULT U={U} Ns={Ns} N={N} nu={N/(2*Ns):.4f}: gap_sp={(Ep+Em-2*E0)/2:.4f} spin_gap={Es-E0:.4f} mu+={Ep-E0:.4f} mu-={E0-Em:.4f}', flush=True)
