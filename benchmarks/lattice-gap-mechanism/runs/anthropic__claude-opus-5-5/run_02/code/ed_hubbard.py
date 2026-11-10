"""Exact diagonalization of the single-band t-t'-U Hubbard model on small periodic clusters.
States: bit strings for up and down spins (site i <-> bit i). Fermion sign convention:
operators ordered all-up then all-down; within a spin species by site index."""
import numpy as np, itertools
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.linalg import eigsh

def tilted_cluster(a1,a2):
    """sites of the square-lattice cluster spanned by a1,a2 (integer vectors), with PBC."""
    N=abs(a1[0]*a2[1]-a1[1]*a2[0])
    # find N inequivalent sites by reduction
    A=np.array([a1,a2]).T.astype(float); Ainv=np.linalg.inv(A)
    def reduce(r):
        f=Ainv@np.array(r,float); f=f-np.floor(f+1e-9)
        v=A@f; return (int(round(v[0])),int(round(v[1])))
    sites=[];idx={}
    for x in range(-N,N+1):
        for y in range(-N,N+1):
            r=reduce((x,y))
            if r not in idx:
                idx[r]=len(sites); sites.append(r)
    assert len(sites)==N
    return sites,idx,reduce

def bonds(sites,idx,reduce,vecs):
    B=set()
    for i,(x,y) in enumerate(sites):
        for d in vecs:
            j=idx[reduce((x+d[0],y+d[1]))]
            if i!=j: B.add((min(i,j),max(i,j),d))
    # keep unique pairs with multiplicity (for tiny clusters a pair can be connected twice)
    return B

def hopping_matrix(Ns,sites,idx,reduce,t,tp):
    T=np.zeros((Ns,Ns))
    for i,(x,y) in enumerate(sites):
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            j=idx[reduce((x+d[0],y+d[1]))]; T[i,j]+=-t
        for d in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            j=idx[reduce((x+d[0],y+d[1]))]; T[i,j]+=-tp
    return T

def basis(Ns,n):
    return [sum(1<<i for i in c) for c in itertools.combinations(range(Ns),n)]

def popcount(x): return bin(x).count('1')

def build_H(Ns,T,U,nup,ndn,mu=0.0):
    bu=basis(Ns,nup); bd=basis(Ns,ndn)
    iu={s:k for k,s in enumerate(bu)}; idd={s:k for k,s in enumerate(bd)}
    Du,Dd=len(bu),len(bd); dim=Du*Dd
    rows=[];cols=[];vals=[]
    # hopping within one species: list of (i,j,amp) with i!=j
    hops=[(i,j,T[i,j]) for i in range(Ns) for j in range(Ns) if i!=j and T[i,j]!=0]
    def hop_list(b,ind):
        out=[]
        for k,s in enumerate(b):
            for (i,j,a) in hops:   # c_i^dag c_j
                if (s>>j)&1 and not (s>>i)&1:
                    s2=s^(1<<j)^(1<<i)
                    lo,hi=min(i,j),max(i,j)
                    nb=popcount(s & (((1<<hi)-1) ^ ((1<<(lo+1))-1)))
                    sign=-1 if nb%2 else 1
                    out.append((k,ind[s2],a*sign))
        return out
    Hu=hop_list(bu,iu); Hd=hop_list(bd,idd)
    # sign for down hops: up operators all to the left -> crossing nup up fermions (even/odd) cancels in pairs (c^dag c), so no extra sign
    diag=np.zeros(dim)
    for ku,su in enumerate(bu):
        for kd,sd in enumerate(bd):
            diag[ku*Dd+kd]=U*popcount(su&sd)-mu*(nup+ndn)
    I=np.arange(dim)
    rows.append(I);cols.append(I);vals.append(diag)
    if Hu:
        a=np.array(Hu)
        ku,ku2,amp=a[:,0].astype(int),a[:,1].astype(int),a[:,2]
        kd=np.arange(Dd)
        rows.append((ku2[:,None]*Dd+kd[None,:]).ravel()); cols.append((ku[:,None]*Dd+kd[None,:]).ravel()); vals.append(np.repeat(amp,Dd))
    if Hd:
        a=np.array(Hd)
        kd,kd2,amp=a[:,0].astype(int),a[:,1].astype(int),a[:,2]
        kuu=np.arange(Du)
        rows.append((kuu[:,None]*Dd+kd2[None,:]).ravel()); cols.append((kuu[:,None]*Dd+kd[None,:]).ravel()); vals.append(np.tile(amp,Du))
    H=coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(dim,dim)).tocsr()
    return H,bu,bd

def ground(Ns,T,U,nup,ndn,k=1):
    H,bu,bd=build_H(Ns,T,U,nup,ndn)
    dim=H.shape[0]
    if dim<=400:
        w,v=np.linalg.eigh(H.toarray()); return w[:k],v[:,:k]
    w,v=eigsh(H,k=k,which='SA',tol=1e-10)
    o=np.argsort(w); return w[o],v[:,o]
