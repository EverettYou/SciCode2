"""Reviewer-owned local likelihoods and generic tensor contraction, not solver code."""
from functools import lru_cache
from fractions import Fraction
from itertools import product
import numpy as np


def geometry(L):
    edges=[]
    for j in range(1,L):
        edges += [((i,j),(i+1,j)) for i in range(2*L-1)]
    for j in range(L):
        edges += [((i,j),(i,j+1)) for i in range(2*L) if (i+j)%2==0]
    edges=sorted(edges)
    detectors=[(i,j) for i in range(2*L) for j in range(1,L)]
    assert len(edges)==3*L*L-3*L+1
    return edges,detectors


@lru_cache(None)
def fundamental(w):
    N=len(w)+1
    rows=[sum(w[i:]) for i in range(N-1)]+[0]
    out=[]
    for i in range(N):
        if i and rows[i]>=rows[i-1]:continue
        r=rows.copy();r[i]+=1
        out.append(tuple(r[j]-r[j+1] for j in range(N-1)))
    return out


def dimension(w):
    N=len(w)+1;r=[sum(w[i:]) for i in range(N-1)]+[0]
    v=Fraction(1)
    for i in range(N):
        for j in range(i+1,N):v*=Fraction(r[i]-r[j]+j-i,j-i)
    assert v.denominator==1
    return int(v)


@lru_cache(None)
def irrep_law(N,a,b):
    counts={(0,)*(N-1):1}
    for conjugate in [False]*a+[True]*b:
        nxt={}
        for w,m in counts.items():
            for t in fundamental(w[::-1] if conjugate else w):
                t=t[::-1] if conjugate else t
                nxt[t]=nxt.get(t,0)+m
        counts=nxt
    law={w:Fraction(m*dimension(w),N**(a+b)) for w,m in counts.items()}
    assert sum(law.values())==1
    assert all(sum((i+1)*c for i,c in enumerate(w))%N==(a-b)%N for w in law)
    return law


def counts_at(edges,v,states):
    a=b=0
    for e,t in zip(edges,states):
        if not t or v not in e:continue
        if (t==1)==(v==e[0]):a+=1
        else:b+=1
    return a,b


def likelihood(N,r,obs,a,b):
    if r=='O0':return float((a+b)%2==obs)
    s,z=obs
    if (a+b)%2!=s:return 0.
    if r=='O1':return float((a-b)%N==z)
    return float(irrep_law(N,a,b).get(tuple(z),0))


def reference(L,p,N,r,record):
    """Generic numpy-einsum optimizer; no row/column transfer implementation."""
    E,V=geometry(L);n=len(E);weights=np.array([1-p,p/2,p/2])
    owners={k:min(v for v in e if v in V) for k,e in enumerate(E)}
    args=[]
    for v in V:
        ix=[k for k,e in enumerate(E) if v in e]
        f=np.zeros((3,)*len(ix))
        for ts in product(range(3),repeat=len(ix)):
            a=b=0;w=1.
            for k,t in zip(ix,ts):
                if owners[k]==v:w*=weights[t]
                if t:
                    if (t==1)==(E[k][0]==v):a+=1
                    else:b+=1
            f[ts]=w*likelihood(N,r,record[v],a,b)
        args += [f,ix]
    top=[k for k,e in enumerate(E) if e[1][1]==L]
    f=np.zeros((3,)*len(top)+(2,))
    for ts in product(range(3),repeat=len(top)):
        f[ts+(sum(t!=0 for t in ts)%2,)]=1.
    args += [f,top+[n],[n]]
    z=np.einsum(*args,optimize='greedy')
    assert z.sum()>0 and np.isfinite(z).all()
    return float(z[0]/z.sum())


def brute(L,p,N,r,record):
    E,V=geometry(L);w=[1-p,p/2,p/2];z=np.zeros(2)
    for ts in product(range(3),repeat=len(E)):
        v=1.
        for t in ts:v*=w[t]
        for d in V:
            a,b=counts_at(E,d,ts);v*=likelihood(N,r,record[d],a,b)
            if not v:break
        q=sum(t!=0 for e,t in zip(E,ts) if e[1][1]==L)%2
        z[q]+=v
    return float(z[0]/z.sum())


def sample_record(L,p,N,rng):
    E,V=geometry(L)
    ts=[int(rng.integers(1,3)) if rng.random()<p else 0 for _ in E]
    records={r:{} for r in ['O0','O1','O2']}
    for v in V:
        a,b=counts_at(E,v,ts);s=(a+b)%2
        law=irrep_law(N,a,b);labs=list(law)
        w=labs[rng.choice(len(labs),p=[float(law[t]) for t in labs])]
        records['O0'][v]=s;records['O1'][v]=(s,(a-b)%N);records['O2'][v]=(s,w)
    return records


def force_active_record(L,N,r):
    """Supported record uniquely fixing all activity bits, at every p>0."""
    E,V=geometry(L);out={}
    for v in V:
        d=sum(v in e for e in E);black=sum(v)%2==0
        if r=='O1':out[v]=(d%2,(d if black else -d)%N)
        else:
            w=[0]*(N-1);w[0 if black else -1]=d
            out[v]=(d%2,tuple(w))
    return out
