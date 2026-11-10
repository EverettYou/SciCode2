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


def signed_op_permutation(model,ops,kind):
    index={op:i for i,op in enumerate(ops)}
    permutation=[];signs=[]
    for op in ops:
        from t1_extension import normal_order
        mapped=tuple((dagger,mode_transform(model,kind,p)) for dagger,p in op)
        ordered=normal_order(mapped)
        assert len(ordered)==1
        (creators,annihilators),sgn=ordered[0]
        canon=tuple((True,p) for p in creators)+tuple((False,p) for p in reversed(annihilators))
        permutation.append(index[canon]);signs.append(sgn)
    assert all(permutation[permutation[j]]==j and signs[j]*signs[permutation[j]]==1 for j in range(len(ops)))
    return permutation,signs


def character_bases(permutations):
    """Integer ±1 orthogonal character spaces for one/two commuting reflections."""
    n=len(permutations[0][0]);ng=len(permutations)
    assert ng in (1,2)
    bases={chars:[] for chars in __import__('itertools').product((1,-1),repeat=ng)}
    visited=set()
    for seed in range(n):
        if seed in visited:continue
        orbit={seed}
        for p,s in permutations:
            orbit|={p[j] for j in tuple(orbit)}
        visited|=orbit
        for chars in bases:
            col={seed:1}
            for chi,(p,s) in zip(chars,permutations):
                new=defaultdict(int,col)
                for j,v in col.items():new[p[j]]+=chi*s[j]*v
                col={j:v for j,v in new.items() if v}
            if col:
                factor=reduce(gcd,map(abs,col.values()))
                bases[chars].append({j:v//factor for j,v in col.items()})
    out=[]
    for chars,cols in bases.items():
        if not cols:continue
        rr=[];cc=[];dd=[]
        for k,col in enumerate(cols):
            for j,v in col.items():rr.append(j);cc.append(k);dd.append(v)
        W=sp.csr_matrix((dd,(rr,cc)),shape=(n,len(cols)))
        out.append((chars,W))
    assert sum(W.shape[1] for _,W in out)==n
    return out


def project_t2_little_groups(model):
    """Split T2 PSD matrices using integer signed reflection characters."""
    newblocks=[];stats=[]
    for block in model.blocks:
        if 'ops' not in block:
            newblocks.append(block);continue
        down,q=block['key'];x,y=model.xy[q];L=model.L
        special=lambda z:z==0 or (L%2==0 and z==L//2)
        if special(x) and special(y):kinds=['rx','ry']
        elif special(x):kinds=['rx']
        elif special(y):kinds=['ry']
        elif x==y:kinds=['swap']
        elif (x+y)%L==0:kinds=['antiswap']
        else:
            newblocks.append(block);continue
        perms=[signed_op_permutation(model,block['ops'],kind) for kind in kinds]
        bases=character_bases(perms)
        # Symmetry-restricted affine matrices must have exactly zero cross blocks.
        for ii,(_,Wi) in enumerate(bases):
            for _,Wj in bases[ii+1:]:
                cross=sp.kron(Wi.T,Wj.T,format='csr')
                cross_A=(cross@block['A']).tocsr();cross_A.eliminate_zeros()
                assert cross_A.nnz==0,(block['name'],'nonzero cross affine map',cross_A.nnz)
                assert np.max(np.abs(cross@block['b']),initial=0)==0,(block['name'],'nonzero cross constant')
        for chars,W in bases:
            K=sp.kron(W.T,W.T,format='csr')
            A=(K@block['A']).tocsr();A.eliminate_zeros()
            b=np.asarray(K@block['b']).ravel()
            newblocks.append(dict(name=f'{block["name"]}_char{chars}',dim=W.shape[1],A=A,b=b))
        stats.append(dict(name=block['name'],original_dim=block['dim'],
                          new_dims=[W.shape[1] for _,W in bases],exact_cross_block_zero=True))
    model.blocks=newblocks
    return stats
