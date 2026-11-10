import numpy as np, itertools
# 2 sites x 2 spins = 4 modes: (1u,1d,2u,2d) -> indices 0..3 ; full Fock space 16
M=4; D=2**M
def cop(i):
    C=np.zeros((D,D))
    for s in range(D):
        if (s>>i)&1:
            sign=(-1)**bin(s&((1<<i)-1)).count('1')
            C[s^(1<<i), s]=sign
    return C
c=[cop(i) for i in range(M)]; cd=[x.T for x in c]
n=[cd[i]@c[i] for i in range(M)]
u1,d1,u2,d2=0,1,2,3
def S(a,b):  # spin ops on site with up a, down b
    Sp=cd[a]@c[b]; Sm=Sp.T; Sz=0.5*(n[a]-n[b])
    return Sp,Sm,Sz
Sp1,Sm1,Sz1=S(u1,d1); Sp2,Sm2,Sz2=S(u2,d2)
SS=Sz1@Sz2+0.5*(Sp1@Sm2+Sm1@Sp2)
K=sum(cd[a]@c[b]+cd[b]@c[a] for (a,b) in [(u1,u2),(d1,d2)])
Kc=sum(1j*(cd[a]@c[b]-cd[b]@c[a]) for (a,b) in [(u1,u2),(d1,d2)])
N1=n[u1]+n[d1]; N2=n[u2]+n[d2]; D1=n[u1]@n[d1]; D2=n[u2]@n[d2]; I=np.eye(D)
basis={'K2':K@K,'Kc2':(Kc@Kc).real,'N1+N2':N1+N2,'N1N2':N1@N2,'D1+D2':D1+D2,'I':I}
names=list(basis); A=np.array([basis[k].ravel() for k in names]).T
for target,lab in [(SS,'S1.S2')]:
    for subset in [['K2','N1+N2','N1N2','D1+D2','I'],['Kc2','N1+N2','N1N2','D1+D2','I'],['K2','Kc2','N1+N2','N1N2','D1+D2','I']]:
        As=np.array([basis[k].ravel() for k in subset]).T
        x,res,rk,sv=np.linalg.lstsq(As,target.ravel(),rcond=None)
        err=np.abs(As@x-target.ravel()).max()
        print(lab,'=',' + '.join('%.4f*%s'%(v,k) for v,k in zip(x,subset)),'   max err %.1e'%err)
