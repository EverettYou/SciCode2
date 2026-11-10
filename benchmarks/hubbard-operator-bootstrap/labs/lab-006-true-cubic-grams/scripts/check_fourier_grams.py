#!/usr/bin/env python3
"""Independent direct-Fock test of separate cubic Fourier Gram formulas."""
import json,itertools
import numpy as np

def action(word,psi):
    out=np.zeros_like(psi,dtype=complex)
    for mask,amp in enumerate(psi):
        if not amp:continue
        target=mask;sgn=1
        for create,p in reversed(word):
            occupied=(target>>p)&1
            if occupied==create:break
            sgn*=(-1)**((target&((1<<p)-1)).bit_count());target^=1<<p
        else:out[target]+=sgn*amp
    return out

def test():
    L=4;dim=1<<(2*L);roots=np.array([1,1j,-1,-1j])
    def ph(k,r):return roots[(k*r)%L]
    psi=np.zeros(dim,dtype=complex)
    for up in itertools.combinations(range(L),2):
        u=np.array([[ph(k,i)/2 for k in (0,1)] for i in up]);au=np.linalg.det(u)
        for down in itertools.combinations(range(L),2):
            d=np.array([[ph(k,i)/2 for k in (0,1)] for i in down]);ad=np.linalg.det(d)
            mask=sum(1<<i for i in up)+sum(1<<(L+i) for i in down)
            psi[mask]=au*ad
    assert abs(np.linalg.norm(psi)-1)<1e-14
    states=[psi,psi.conj()]
    def expectation(word):return sum(np.vdot(p,action(word,p)) for p in states)/2
    def densityword(a):return ((True,L+a),(False,L+a))
    def Y(d,a):return expectation(((True,d),(False,0))+densityword(a))
    def X(d,a,b):return expectation(((True,d),(False,0))+densityword(a)+densityword(b))
    def D(a,b):return expectation(densityword(a)+densityword(b))
    maxerr=0;mineig=1
    for k in range(L):
        for create in (True,False):
            vectors=[]
            for p in states:
                images=[]
                for r in (1,2,3,None):
                    v=np.zeros(dim,dtype=complex)
                    for i in range(L):
                        word=((create,i),)+(densityword((i+r)%L) if r is not None else ())
                        coeff=ph(k,i) if create else np.conj(ph(k,i))
                        v+=coeff/2*action(word,p)
                    images.append(v)
                vectors.append(images)
            direct=sum(np.array([[np.vdot(u,v) for v in im] for u in im]) for im in vectors)/2
            M=np.zeros((L,L),dtype=complex)
            for ii,r in enumerate((1,2,3)):
                for jj,s in enumerate((1,2,3)):
                    M[ii,jj]=D(r,s) if create else 0
                    for d in range(L):
                        coeff=ph(k,d) if create else np.conj(ph(k,d))
                        M[ii,jj]+=(-coeff if create else coeff)*X(d,r,(d+s)%L)
                M[ii,3]=expectation(densityword(r)) if create else 0
                for d in range(L):
                    coeff=ph(k,d) if create else np.conj(ph(k,d))
                    M[ii,3]+=(-coeff if create else coeff)*Y(d,r)
                M[3,ii]=M[ii,3].conjugate()
            nk=sum(ph(k,d)*expectation(((True,d),(False,0))) for d in range(L))
            M[3,3]=1-nk if create else nk
            maxerr=max(maxerr,float(np.max(np.abs(M-direct))))
            mineig=min(mineig,float(np.linalg.eigvalsh(M)[0]))
    assert maxerr<1e-13,(maxerr,mineig)
    assert mineig>-1e-13,(maxerr,mineig)
    result=dict(max_direct_fock_fourier_gram_error=maxerr,min_gram_eigenvalue=mineig,one_dimensional_sites=L,modes=2*L,fixed_up_particles=2,fixed_down_particles=2,states='Slater momenta {0,1} and its conjugate, equal mixture')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':test()
