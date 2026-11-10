import numpy as np, sys
sys.path.insert(0,'/app/code')
from ed_hubbard import *
a1,a2=(3,1),(-1,3)          # 10-site tilted cluster
sites,idx,red=tilted_cluster(a1,a2); Ns=len(sites)
t,tp=1.0,0.195
for U in [-12.0,-10.0,-8.0,-6.0]:
    T=hopping_matrix(Ns,sites,idx,red,t,tp)
    E={}
    for N in range(1,Ns+2):
        for Sz2 in ([0] if N%2==0 else [1]):
            nup=(N+Sz2)//2; ndn=N-nup
            if nup>Ns or ndn>Ns: continue
            w,_=ground(Ns,T,U,nup,ndn); E[N]=w[0]
    # spin gap: lowest S_z=1 state for even N
    out=[]
    for N in [2,4,6,8,10]:
        dpb=(E[N+1]+E[N-1]-2*E[N])/2
        w1,_=ground(Ns,T,U,N//2+1,N//2-1)
        sg=w1[0]-E[N]
        out.append(f'n={N/Ns:.1f}(nu={N/Ns/2:.2f}): pair-breaking gap={dpb:6.3f} spin gap={sg:6.3f}')
    print('U=',U); print('   '+'\n   '.join(out))
