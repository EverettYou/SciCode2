import numpy as np, itertools
from fitlib import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# modes: 0:k up, 1:k dn, 2:-k up, 3:-k dn
def ops():
    dim=16
    def c_op(m):
        M=np.zeros((dim,dim))
        for s in range(dim):
            if (s>>m)&1:
                sign=(-1)**bin(s&((1<<m)-1)).count('1')
                M[s^(1<<m),s]=sign
        return M
    return [c_op(m) for m in range(4)]
C=ops(); Cd=[c.T for c in C]; N=[Cd[m]@C[m] for m in range(4)]
def spectral_pair(xi,U,Delta,T,grid,eta):
    H=xi*(N[0]+N[1]+N[2]+N[3])+U*(N[0]@N[1]+N[2]@N[3])
    pair=Cd[0]@Cd[3]+Cd[2]@Cd[1]   # c†_{k up} c†_{-k dn} + c†_{-k up} c†_{k dn}
    H=H-Delta*(pair+pair.T)
    E,W=np.linalg.eigh(H)
    w=np.exp(-(E-E.min())/T); Z=w.sum(); w/=Z
    A=np.zeros_like(grid); nk=0.0
    Cd0=W.T@Cd[0]@W
    for m in range(16):
        for n in range(16):
            amp=Cd0[n,m]**2
            if amp<1e-12: continue
            A+=(w[m]+w[n])*amp*eta/np.pi/((grid-(E[n]-E[m]))**2+eta**2)
    nk=sum(w[m]*(W.T@(N[0]+N[1])@W)[m,m] for m in range(16))
    return A,nk
if __name__=="__main__":
    grid=np.linspace(-14,14,1401)

    t,tp=0.99,0.195
    eps=band(t,tp)
    # coarse k grid for speed
    sub=eps[::14,::14].ravel()
    for (U,Delta,mu,T,label) in [(12,2.4,-0.93,0.05,'HK U=12 D=2.4 mu free-band'),(12,2.4,2.0,0.05,'HK U=12 D=2.4 mu=2'),(6,2.4,-0.93,0.05,'HK U=6')]:
        rho=np.zeros_like(grid); ntot=0
        for e in sub:
            A,nk=spectral_pair(e-mu,U,Delta,T,grid,0.12); rho+=A; ntot+=nk
        rho/=len(sub); ntot/=len(sub)
        print(label," n=",ntot)
        plt.plot(grid,rho/rho.max(),label=f"{label} n={ntot:.2f}")
    s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
    plt.plot(V,g,'k',lw=0.6,label='panel b')
    plt.xlim(-14,14); plt.legend(); plt.savefig('hk_bcs.png',dpi=80)
