import numpy as np, sys
sys.path.insert(0,'/app/code')
from ed_hubbard import *
sites,idx,red=tilted_cluster((3,1),(-1,3)); Ns=len(sites)
t,tp=1.0,0.195
for U in [-12.0,-6.0,0.0]:
    T=hopping_matrix(Ns,sites,idx,red,t,tp)
    E={}
    for N in range(0,Ns+2):
        nup=(N+1)//2; ndn=N-nup
        if N==0: E[0]=0.0; continue
        w,_=ground(Ns,T,U,nup,ndn); E[N]=w[0]
    print('U=',U,' band bottom',-4*t-4*tp)
    for N in [2,4,6,8,10]:
        mu=(E[N+1]-E[N-1])/2; gap=(E[N+1]+E[N-1]-2*E[N])/2
        print(f'   N={N} n={N/Ns:.1f}: mu={mu:7.3f}  mu-mid relative to band bottom={mu+4*t+4*tp:6.3f}  E(N+1)-E(N)={E[N+1]-E[N]:7.3f}  E(N)-E(N-1)={E[N]-E[N-1]:7.3f} gap={gap:6.3f}')
