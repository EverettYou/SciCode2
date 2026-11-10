import numpy as np, time, sys, json
from ed_hubbard import *
sites, red, Ks = make_cluster((4,0),(0,4))
T = hopping_matrix(sites, red, 1.0, 0.2)
U = float(sys.argv[1])
Ns = 16
res = {}
def E(nup, ndn):
    key = (nup, ndn)
    if key in res: return res[key]
    t0=time.time()
    sec = Sector(Ns, nup, ndn, T, U)
    ev, *_ = ground_state(sec, want_vec=False, maxit=500)
    res[key] = ev[0]
    print(f'  E({nup},{ndn}) = {ev[0]:.8f}   dim={sec.dim}  ({time.time()-t0:.1f}s)', flush=True)
    return ev[0]
for N in [6, 10]:
    n2 = N//2
    E0 = E(n2, n2); Ep = E(n2+1, n2); Em = E(n2, n2-1)
    Ep2 = E(n2+1, n2+1); Em2 = E(n2-1, n2-1)
    Es1 = E(n2+1, n2-1)
    dsp = 0.5*(Ep + Em - 2*E0)
    print(f"U={U} N={N} (nu={N/32:.4f}): single-particle gap (E(N+1)+E(N-1)-2E(N))/2 = {dsp:.4f}; "
          f"spin gap E(Sz=1)-E(Sz=0) = {Es1-E0:.4f}; pair binding 2E(N+1)-E(N)-E(N+2) = {2*Ep-E0-Ep2:.4f}; "
          f"mu+ = {Ep-E0:.4f}, mu- = {E0-Em:.4f}", flush=True)
