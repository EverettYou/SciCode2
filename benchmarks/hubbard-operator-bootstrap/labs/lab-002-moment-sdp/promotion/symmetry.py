"""Exact signed D4 and spin-swap variable/cone reductions for Hubbard SDP."""
from collections import defaultdict
from functools import reduce
from math import gcd
import numpy as np
import scipy.sparse as sp

class SignedDSU:
    def __init__(self,n):self.parent=list(range(n));self.sign=[1]*n;self.zero=set()
    def find(self,i):
        if self.parent[i]!=i:
            p,s=self.find(self.parent[i]);self.sign[i]*=s;self.parent[i]=p
        return self.parent[i],self.sign[i]
    def union(self,i,j,s):
        a,si=self.find(i);b,sj=self.find(j);rel=s*si*sj
        if a==b:
            if rel==-1:self.zero.add(a)
            return
        if a>b:a,b=b,a
        self.parent[b]=a;self.sign[b]=rel
        if b in self.zero or a in self.zero:self.zero.add(a)
        self.zero.discard(b)


def mode_transform(model,kind,mode):
    V=model.V;L=model.L;s,k=divmod(mode,V);x,y=model.xy[k]
    if kind=='rot':x,y=(-y)%L,x
    elif kind=='rx':x=(-x)%L
    elif kind=='ry':y=(-y)%L
    elif kind=='swap':x,y=y,x
    elif kind=='antiswap':x,y=(-y)%L,(-x)%L
    elif kind=='spin':s=1-s
    else:raise ValueError(kind)
    return s*V+x+L*y


def reduce_variables(model):
    """Set x_i=±y_orbit, preserving all PSD constraints and Eq(2) symmetries."""
    original_nvar=model.nvar
    dsu=SignedDSU(original_nvar)
    for kind in ('rot','rx','spin'):
        for i,name in enumerate(model.names):
            nums=list(map(int,name.split('_')[1:]))
            if len(nums)==1:
                j=mode_transform(model,kind,nums[0]);sgn=1
            else:
                a,b,c,d=(mode_transform(model,kind,p) for p in nums)
                affine=model.gamma(a,b,c,d)
                assert len(affine)==1
                j,sgn=next(iter(affine.items()))
            dsu.union(i,j,sgn)
    roots={}
    for i in range(original_nvar):
        root,sgn=dsu.find(i)
        if root not in dsu.zero:roots.setdefault(root,len(roots))
    rows=[];cols=[];values=[]
    for i in range(original_nvar):
        root,sgn=dsu.find(i)
        if root not in dsu.zero:rows.append(i);cols.append(roots[root]);values.append(sgn)
    T=sp.csr_matrix((values,(rows,cols)),shape=(original_nvar,len(roots)))
    E=model.eqmatrix()@T
    model.erows=[]
    for i in range(E.shape[0]):
        row=E.getrow(i);model.erows.append(dict(zip(row.indices,row.data)))
    for b in model.blocks:
        b['A']=(b['A']@T).tocsr();b['A'].eliminate_zeros()
    model.c=np.asarray(T.T@model.c).ravel()
    model.names=[model.names[root] for root in roots]
    model.nvar=len(roots)
    return dict(original_nvar=original_nvar,reduced_nvar=model.nvar,
                zero_variables=original_nvar-len(rows)),T


def q_orbit_representatives(model):
    V=model.V
    reps={}
    for q in range(V):
        orbit=set()
        a=q
        for _ in range(4):
            orbit.add(a);orbit.add(mode_transform(model,'rx',a))
            a=mode_transform(model,'rot',a)
        reps[q]=min(orbit)
    return reps

