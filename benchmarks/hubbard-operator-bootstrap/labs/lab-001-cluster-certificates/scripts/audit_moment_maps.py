#!/usr/bin/env python3
"""Independent exact physical-map audit of exported Hubbard PQG/T1/T2 data.

Does not import the optimization builder or any of its CAR routines. Normal
ordering multiplies canonical exterior monomials from left to right, rather
than the builder's recursive adjacent transpositions. Every stored affine
coefficient, equality, constant and Hamiltonian coefficient is compared.
"""
from __future__ import annotations
import argparse,ast,collections,functools,hashlib,itertools,json,math,os,re,resource,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp

L=4;V=16;NMODE=32

def momadd(a,b):return (a%4+b%4)%4+4*((a//4+b//4)%4)
def momsub(a,b):return (a%4-b%4)%4+4*((a//4-b//4)%4)
def dagger(w):return tuple((1-c,p) for c,p in reversed(w))

def add_scaled(out,p,scale=1):
    for key,val in p.items():out[key]+=scale*val

@functools.lru_cache(maxsize=40000)
def exterior_normal(word):
    """Canonical keys=(creators ascending, annihilators descending)."""
    poly={((),()):1}
    for create,p in word:
        new=collections.defaultdict(int)
        for (cs,ans),v in poly.items():
            if create:
                # Contract c_p^dagger with each matching annihilator as it
                # commutes from the right, before joining the creator wedge.
                if p in ans:
                    j=ans.index(p);new[cs,ans[:j]+ans[j+1:]]+=v*(-1)**(len(ans)-j-1)
                if p not in cs:
                    sign=(-1)**(len(ans)+sum(c>p for c in cs))
                    new[tuple(sorted(cs+(p,))),ans]+=v*sign
            elif p not in ans:
                sign=(-1)**sum(a<p for a in ans)
                new[cs,tuple(sorted(ans+(p,),reverse=True))]+=v*sign
        poly={k:v for k,v in new.items() if v}
    return tuple(sorted(poly.items()))


def sum_word_polys(words):
    poly=collections.defaultdict(int)
    for scale,word in words:
        for key,val in exterior_normal(tuple(word)):poly[key]+=scale*val
    return {k:v for k,v in poly.items() if v}


def contracted_t2_words(t,u):
    """CAR contraction table derived by commuting two annihilators past
    two creators in A_t^dagger A_u. Sextic products cancel against A_u A_t^dag.
    Exhaustive relative-order/equality patterns are checked below.
    """
    a,b,c=t;d,e,f=u;words=[]
    coef=int(a==d)*int(b==e)-int(a==e)*int(b==d)
    if coef:words.append((coef,((1,c),(0,f))))
    if a==d:words.append((-1,((1,c),(1,e),(0,b),(0,f))))
    if b==d:words.append((1,((1,c),(1,e),(0,a),(0,f))))
    if a==e:words.append((1,((1,c),(1,d),(0,b),(0,f))))
    if b==e:words.append((-1,((1,c),(1,d),(0,a),(0,f))))
    if f==c:words.append((1,((1,d),(1,e),(0,b),(0,a))))
    return words

def exhaustive_t2_contraction_test():
    # All six indices can be replaced by their relative-order ranks 0..5.
    # Thus 6^6 cases cover every equality and ordering pattern for 32 modes.
    count=0
    for vals in itertools.product(range(6),repeat=6):
        t,u=vals[:3],vals[3:];a,b,c=t;d,e,f=u
        wi=((1,a),(1,b),(0,c));wj=((1,d),(1,e),(0,f))
        full=sum_word_polys([(1,dagger(wi)+wj),(1,wj+dagger(wi))])
        contracted=sum_word_polys(contracted_t2_words(t,u))
        assert full==contracted,(t,u,full,contracted)
        count+=1
    exterior_normal.cache_clear()
    return count

class Audit:
    def __init__(self,names):
        self.names=names;self.index={n:i for i,n in enumerate(names)}
        if len(self.index)!=len(names):raise AssertionError('Repeated variable names')
        for a in range(32):assert f'n_{a}' in self.index
        self.pairs=list(itertools.combinations(range(32),2));self.pgroups=collections.defaultdict(list);self.ggroups=collections.defaultdict(list)
        for a,b in self.pairs:self.pgroups[momadd(a%16,b%16),a//16+b//16].append((a,b))
        for a,b in itertools.product(range(32),repeat=2):self.ggroups[momsub(a%16,b%16),a//16-b//16].append((a,b))
        self.tgroups=collections.defaultdict(list)
        for t in itertools.combinations(range(32),3):
            k=0
            for a in t:k=momadd(k,a%16)
            self.tgroups[sum(a<16 for a in t),k%4,k//4].append(t)
        # Validate that exactly the translation/spin-allowed pair coordinates
        # are represented, with one variable per real Hermitian entry.
        expected={f'n_{a}' for a in range(32)}
        for pairs in self.pgroups.values():
            for i,(a,b) in enumerate(pairs):
                for c,d in pairs[i:]:expected.add(f'Gamma_{a}_{b}_{c}_{d}')
        assert expected==set(names),('variable-name mismatch',len(expected),len(names))

    def gamma(self,a,b,c,d):
        if a==b or c==d:return {}
        sign=1
        if a>b:a,b=b,a;sign=-sign
        if c>d:c,d=d,c;sign=-sign
        key=f'Gamma_{a}_{b}_{c}_{d}'
        alt=f'Gamma_{c}_{d}_{a}_{b}'
        if key in self.index:return {self.index[key]:sign}
        if alt in self.index:return {self.index[alt]:sign}
        return {}

    def affine(self,poly):
        out=collections.defaultdict(int)
        for (cs,ans),v in poly.items():
            if not cs and not ans:out[-1]+=v
            elif len(cs)==len(ans)==1:
                if cs[0]==ans[0]:out[self.index[f'n_{cs[0]}']]+=v
            elif len(cs)==len(ans)==2:
                for z,c in self.gamma(cs[0],cs[1],ans[1],ans[0]).items():out[z]+=v*c
            else:raise AssertionError(('Uncancelled degree above four',cs,ans,v))
        return {k:v for k,v in out.items() if v}

    def words_affine(self,words):return self.affine(sum_word_polys(words))

    def objective(self):
        c=np.zeros(len(self.names),dtype=np.int64);cos=(1,0,-1,0)
        for a in range(32):c[self.index[f'n_{a}']]=-4*(cos[a%4]+cos[(a%16)//4])
        # Return 2H, so every coefficient is an exact integer.
        for k,p,q in itertools.product(range(16),repeat=3):
            for z,v in self.gamma(momadd(k,q),16+momsub(p,q),k,16+p).items():c[z]+=v
        return c

    def equalities(self):
        rows=[];rhs=[8,8]
        for spin in range(2):rows.append({self.index[f'n_{a}']:1 for a in range(16*spin,16*(spin+1))})
        for a in range(32):
            for spin in range(2):
                row=collections.defaultdict(int);row[self.index[f'n_{a}']]-=8-int(a//16==spin)
                for b in range(16*spin,16*(spin+1)):add_scaled(row,self.gamma(a,b,a,b))
                rows.append(dict(row));rhs.append(0)
        return sparse_rows(rows,len(self.names)),np.array(rhs,dtype=np.int64)

    def block_entries(self,name,descriptors):
        if name.startswith(('P_','Q_')):
            key=ast.literal_eval(name[2:]);pairs=self.pgroups[key]
            ops=[tuple((0,p) for p in reversed(pair)) if name[0]=='P' else tuple((1,p) for p in pair) for pair in pairs]
            for i,oi in enumerate(ops):
                for j,oj in enumerate(ops):yield i,j,self.words_affine([(1,dagger(oi)+oj)])
        elif name.startswith('G_'):
            key=ast.literal_eval(name[2:]);ops=[((1,a),(0,b)) for a,b in self.ggroups[key]]
            for i,oi in enumerate(ops):
                for j,oj in enumerate(ops):yield i,j,self.words_affine([(1,dagger(oi)+oj)])
        elif name.startswith('n_'):
            a=int(name[2:]);yield 0,0,{self.index[f'n_{a}']:1}
        elif name.startswith('hole_'):
            a=int(name[5:]);yield 0,0,{-1:1,self.index[f'n_{a}']:-1}
        elif name.startswith('T1_'):
            key=ast.literal_eval(name[3:]);ts=self.tgroups[key]
            for i,t in enumerate(ts):
                ct=tuple((1,p) for p in t)
                for j in range(i,len(ts)):
                    au=tuple((0,p) for p in reversed(ts[j]))
                    p=self.words_affine([(1,ct+au),(1,au+ct)])
                    yield i,j,p
                    if i!=j:yield j,i,p
        elif name.startswith('T2pure_extreme_spin'):
            m=re.fullmatch(r'T2pure_extreme_spin([01])_k(\d+)',name);assert m
            spin,k=map(int,m.groups());source=descriptors[name];ops=source['operators'];assert len(ops)==15 and source['form']=='T2pure'
            for q,op in enumerate(ops,1):
                expected=[{'coefficient':1,'word':[[1,16*spin+momadd(k,q)],[1,16*spin+momsub(p,q)],[0,16*(1-spin)+p]]} for p in range(16)]
                assert op['terms']==expected,(name,q,'operator descriptor mismatch')
            for i,oi in enumerate(ops):
                for j in range(i,len(ops)):
                    pol=collections.defaultdict(int)
                    for ti,tj in itertools.product(oi['terms'],ops[j]['terms']):
                        t=tuple(z[1] for z in ti['word']);u=tuple(z[1] for z in tj['word']);scale=ti['coefficient']*tj['coefficient']
                        add_scaled(pol,self.words_affine(contracted_t2_words(t,u)),scale)
                    p={z:v for z,v in pol.items() if v};yield i,j,p
                    if i!=j:yield j,i,p
        elif name.startswith(('T2primefull_','T2primemixed_')):
            source=descriptors.get(name);mixed=name.startswith('T2primemixed_');key=ast.literal_eval(name[name.index('_')+1:])
            if source is not None:assert bool(source.get('mixed_only',False))==mixed
            expected=[]
            for a,b in self.pairs:
                if mixed and a//16==b//16:continue
                for c in range(32):
                    if (a//16+b//16-c//16,momsub(momadd(a%16,b%16),c%16))==key:expected.append(((1,a),(1,b),(0,c)))
            if key[0] in [0,1]:expected.append(((1,16*key[0]+key[1]),))
            ops=expected
            if source is not None:assert [tuple(map(tuple,op)) for op in source['ops']]==expected and source['kind']=='T2prime'
            for i,oi in enumerate(ops):
                for j in range(i,len(ops)):
                    oj=ops[j]
                    if len(oi)==len(oj)==3:p=self.words_affine(contracted_t2_words(tuple(v[1] for v in oi),tuple(v[1] for v in oj)))
                    else:p=self.words_affine([(1,dagger(oi)+oj)])
                    yield i,j,p
                    if i!=j:yield j,i,p
        elif name.startswith('T2prime_'):
            d=descriptors[name];ops=d['operators'];aug=d['augmented_operator'];bw=tuple(map(tuple,aug['word']));bc=aug['coefficient'];last=len(ops)
            # Independently reconstruct every advertised descriptor from the
            # physically selected spin/k density Fourier operators.
            m=re.fullmatch(r'T2prime_(density|two_site)_spin([01])_k(\d+)',name);assert m
            choice=m.group(1);spin,k=map(int,m.groups()[1:]);assert last==(15 if choice=='density' else 60) and bw==((1,16*spin+k),) and bc==4
            for oi,op in enumerate(ops):
                q=oi%15+1;family=('opposite_density','same_density','doublon_pair','spin_exchange')[oi//15]
                if choice=='density':assert op['q']==q
                else:assert op['family']==family and op['relative_momentum']==q
                triples=[]
                for p in range(16):
                    if family=='opposite_density':t=(16*spin+momadd(k,q),16*(1-spin)+momsub(p,q),16*(1-spin)+p)
                    elif family=='same_density':t=(16*spin+momadd(k,q),16*spin+momsub(p,q),16*spin+p)
                    elif family=='doublon_pair':t=(16*spin+p,16*(1-spin)+momsub(momadd(k,q),p),16*(1-spin)+q)
                    else:t=(16*spin+p,16*(1-spin)+q,16*(1-spin)+momsub(momadd(p,q),k))
                    triples.append(t)
                expected=[{'coefficient':1,'word':[[1,a],[1,b],[0,c]]} for a,b,c in triples]
                assert op['terms']==expected,(name,oi,'operator descriptor mismatch')
            for i,oi in enumerate(ops):
                for j in range(i,last):
                    pol=collections.defaultdict(int)
                    for ti,tj in itertools.product(oi['terms'],ops[j]['terms']):
                        t=tuple(z[1] for z in ti['word']);u=tuple(z[1] for z in tj['word']);s=ti['coefficient']*tj['coefficient']
                        add_scaled(pol,self.words_affine(contracted_t2_words(t,u)),s)
                    p={z:v for z,v in pol.items() if v};yield i,j,p
                    if i!=j:yield j,i,p
                words=[(bc*ti['coefficient'],dagger(tuple(map(tuple,ti['word'])))+bw) for ti in oi['terms']]
                p=self.words_affine(words);yield i,last,p;yield last,i,p
            yield last,last,self.words_affine([(bc*bc,dagger(bw)+bw)])
        else:raise ValueError('Unknown operator block '+name)


def sparse_rows(rows,nvar):
    rr=[];cc=[];dd=[]
    for r,p in enumerate(rows):
        for z,v in p.items():
            if v:rr.append(r);cc.append(z);dd.append(v)
    return sp.csr_matrix((dd,(rr,cc)),shape=(len(rows),nvar),dtype=np.int64)

def exact_sparse_equal(A,B,label):
    A=A.tocsr();B=B.tocsr();D=A-B;D.eliminate_zeros()
    assert A.shape==B.shape and D.nnz==0,(label,'sparse mismatch',D.nnz)

def car_self_test():
    rng=np.random.default_rng(38819)
    def apply(word,mask):
        sign=1
        for create,p in reversed(word):
            occ=(mask>>p)&1
            if occ==create:return None,0
            sign*=(-1)**((mask&((1<<p)-1)).bit_count());mask^=1<<p
        return mask,sign
    for t in range(2000):
        word=tuple((int(rng.integers(2)),int(rng.integers(6))) for _ in range(int(rng.integers(7))))
        p=exterior_normal(word)
        for mask in (int(rng.integers(64)),int(rng.integers(64))):
            direct=collections.defaultdict(int);out,s=apply(word,mask)
            if s:direct[out]+=s
            derived=collections.defaultdict(int)
            for (cs,ans),v in p:
                out,s=apply(tuple((1,z) for z in cs)+tuple((0,z) for z in ans),mask)
                if s:derived[out]+=s*v
            assert {k:v for k,v in direct.items() if v}=={k:v for k,v in derived.items() if v}
    return 4000

def geometry_test():
    sites=list(itertools.product(range(4),repeat=2));edges=set()
    for x,y in sites:
        for q in [((x+1)%4,y),(x,(y+1)%4)]:edges.add(tuple(sorted(((x,y),q))))
    assert len(edges)==32
    # Integer Gaussian roots prove the hopping Fourier transform exactly.
    roots=(1,1j,-1,-1j);cos=(1,0,-1,0)
    for kx,ky in sites:
        for px,py in sites:
            val=0j
            for a,b in edges:
                for r,s in [(a,b),(b,a)]:val-=roots[(-kx*r[0]-ky*r[1]+px*s[0]+py*s[1])%4]
            expected=-32*(cos[kx]+cos[ky]) if (kx,ky)==(px,py) else 0
            assert val==expected
    return len(edges)


def mode_transform(mode,kind):
    spin,k=divmod(mode,16);x,y=k%4,k//4
    if kind=='rot':x,y=(-y)%4,x
    elif kind=='rx':x=(-x)%4
    elif kind=='ry':y=(-y)%4
    elif kind=='swap':x,y=y,x
    elif kind=='antiswap':x,y=(-y)%4,(-x)%4
    elif kind=='spin':spin=1-spin
    else:raise ValueError(kind)
    return 16*spin+x+4*y

def audit_symmetry_expansion(a,T):
    T=T.tocsr();assert T.shape[0]==len(a.names)
    assert set(T.data).issubset({-1,1}) and np.max(np.diff(T.indptr),initial=0)<=1
    adjacency=[[] for _ in a.names]
    for i,name in enumerate(a.names):
        nums=tuple(map(int,name.split('_')[1:]))
        for kind in ('rot','rx','spin'):
            mapped=tuple(mode_transform(p,kind) for p in nums)
            if len(nums)==1:j=a.index[f'n_{mapped[0]}'];sign=1
            else:
                g=a.gamma(*mapped);assert len(g)==1;j,sign=next(iter(g.items()))
            adjacency[i].append((j,sign));adjacency[j].append((i,sign))
    seen=set();columns=set();zero_orbits=0;nonzero=0
    for seed in range(len(a.names)):
        if seed in seen:continue
        phase={seed:1};queue=[seed];conflict=False
        for i in queue:
            for j,sign in adjacency[i]:
                desired=phase[i]*sign
                if j not in phase:phase[j]=desired;queue.append(j)
                elif phase[j]!=desired:conflict=True
        seen.update(queue)
        if conflict:
            zero_orbits+=1
            assert all(T.indptr[i]==T.indptr[i+1] for i in queue)
        else:
            nonzero+=1;col=None;scale=None
            for i in queue:
                assert T.indptr[i+1]-T.indptr[i]==1
                ptr=T.indptr[i];ci=int(T.indices[ptr]);si=int(T.data[ptr])*phase[i]
                if col is None:col,scale=ci,si
                assert ci==col and si==scale
            assert col not in columns;columns.add(col)
    assert nonzero==T.shape[1] and columns==set(range(T.shape[1]))
    return {'group':'D4 spatial rotations/reflections and spin interchange','signed_nonzero_variable_orbits':nonzero,'signed_zero_variable_orbits':zero_orbits}

def physical_block(a,name,dim,descriptors):
    rows=[{} for _ in range(dim*dim)];b=np.zeros(dim*dim,dtype=np.int64)
    for i,j,p in a.block_entries(name,descriptors):
        assert i<dim and j<dim
        rows[i*dim+j]={z:v for z,v in p.items() if z>=0};b[i*dim+j]=p.get(-1,0)
    return sparse_rows(rows,len(a.names)),b

def character_permutation(a,name,dim,kind):
    if name.startswith('T1_'):
        triples=a.tgroups[ast.literal_eval(name[3:])];assert len(triples)==dim;index={t:i for i,t in enumerate(triples)}
        pairs=[]
        for i,t in enumerate(triples):
            mapped=tuple(mode_transform(p,kind) for p in t)
            sign=(-1)**sum(mapped[j]>mapped[k] for j in range(3) for k in range(j+1,3))
            pairs.append((index[tuple(sorted(mapped))],i,sign))
    elif name.startswith('T2pure_extreme_spin'):
        assert dim==15;pairs=[]
        for i in range(dim):
            mapped=mode_transform(i+1,kind);assert 1<=mapped<16
            pairs.append((mapped-1,i,1))
    elif name.startswith(('T2primefull_','T2primemixed_')):
        mixed=name.startswith('T2primemixed_');key=ast.literal_eval(name[name.index('_')+1:]);ops=[]
        for c1,c2 in a.pairs:
            if mixed and c1//16==c2//16:continue
            for an in range(32):
                if (c1//16+c2//16-an//16,momsub(momadd(c1%16,c2%16),an%16))==key:ops.append(((1,c1),(1,c2),(0,an)))
        if key[0] in [0,1]:ops.append(((1,16*key[0]+key[1]),))
        assert len(ops)==dim;index={op:i for i,op in enumerate(ops)};pairs=[]
        for i,op in enumerate(ops):
            mapped=[(create,mode_transform(p,kind)) for create,p in op];cs=[p for create,p in mapped if create];ans=[p for create,p in mapped if not create]
            sign=(-1)**sum(cs[j]>cs[k] for j in range(len(cs)) for k in range(j+1,len(cs)))
            word=tuple((1,p) for p in sorted(cs))+tuple((0,p) for p in ans)
            pairs.append((index[word],i,sign))
    elif name.startswith('T2prime_'):
        assert (dim-1)%15==0;pairs=[]
        for i in range(dim-1):
            family,q=divmod(i,15);q+=1;mapped=mode_transform(q,kind);assert 1<=mapped<16
            pairs.append((family*15+mapped-1,i,1))
        pairs.append((dim-1,dim-1,1))
    else:raise ValueError(name)
    R=sp.csr_matrix(([p[2] for p in pairs],([p[0] for p in pairs],[p[1] for p in pairs])),shape=(dim,dim),dtype=np.int64)
    exact_sparse_equal(R@R,sp.eye(dim,dtype=np.int64,format='csr'),'reflection involution')
    return R


def modular_rank(A,prime=1000003):
    assert all(prime%d for d in range(2,math.isqrt(prime)+1))
    A=np.asarray(A,dtype=np.int64).copy()%prime;r=0
    for j in range(A.shape[1]):
        candidates=np.flatnonzero(A[r:,j])
        if not len(candidates):continue
        pivot=r+int(candidates[0]);A[[r,pivot]]=A[[pivot,r]]
        A[r]=A[r]*pow(int(A[r,j]),-1,prime)%prime
        for i in range(r+1,A.shape[0]):
            if A[i,j]:A[i]=(A[i]-A[i,j]*A[r])%prime
        r+=1
        if r==A.shape[0]:break
    return r

def star_selection(a,name,labels):
    down,k=ast.literal_eval(name[len('T2primefull_'):]);assert down==0
    ops=[]
    for ca,cb in a.pairs:
        for an in range(32):
            if (ca//16+cb//16-an//16,momsub(momadd(ca%16,cb%16),an%16))==(0,k):ops.append((ca,cb,an))
    index={t:i for i,t in enumerate(ops)};columns=[]
    nn=(1,3,4,12);reps=[(r,s) for r in nn for s in nn if r!=s and (r,s)<(momsub(0,r),momsub(0,s))]
    expected={(family,q) for family in ('opposite_density','same_density','doublon_pair','spin_exchange') for q in range(1,16)}
    expected|={('star',tau,r,s,part) for tau in range(2) for r,s in reps for part in ('cos','sin')};expected.add(('linear',k))
    labels=list(map(tuple,labels));assert set(labels)==expected and len(labels)==len(expected)==85
    roots=(1,1j,-1,-1j)
    for label in labels:
        terms=[]
        if label[0]=='linear':columns.append({len(ops):4});continue
        if label[0]=='star':
            _,tau,r,ss,part=label
            for b,c in itertools.product(range(16),repeat=2):
                phase=(-(b%4)*(r%4)-(b//4)*(r//4)+(c%4)*(ss%4)+(c//4)*(ss//4))%4
                z=roots[phase];coef=int(z.real if part=='cos' else z.imag)
                if coef:terms.append((momadd(k,momsub(c,b)),16*tau+b,16*tau+c,coef))
        else:
            family,q=label
            for p in range(16):
                if family=='opposite_density':t=(momadd(k,q),16+momsub(p,q),16+p)
                elif family=='same_density':t=(momadd(k,q),momsub(p,q),p)
                elif family=='doublon_pair':t=(p,16+momsub(momadd(k,q),p),16+q)
                else:t=(p,16+q,16+momsub(momadd(p,q),k))
                terms.append((*t,1))
        col=collections.defaultdict(int)
        for ca,cb,an,v in terms:
            if ca==cb:continue
            if ca>cb:ca,cb,v=cb,ca,-v
            col[index[ca,cb,an]]+=v
        columns.append({i:v for i,v in col.items() if v})
    rr=[];cc=[];dd=[]
    for j,col in enumerate(columns):
        for i,v in col.items():rr.append(i);cc.append(j);dd.append(v)
    return sp.csr_matrix((dd,(rr,cc)),shape=(len(ops)+1,len(columns)),dtype=np.int64)

def audit_character_source(a,name,A,b,metas,inp):
    dim=metas[0]['source_dim'];ws=[]
    for m in metas:
        W=sp.load_npz(inp/m['projection']).tocsr()
        assert W.shape==(dim,m['dim']) and np.all(W.data==np.rint(W.data))
        for chi,kind in zip(m['characters'],m['reflections']):
            assert chi in [-1,1];R=character_permutation(a,name,dim,kind)
            exact_sparse_equal(R@W,chi*W,'character eigenplane')
        ws.append(W)
    joined=sp.hstack(ws,format='csr')
    if (inp/'star_construction.json').exists() and name.startswith('T2primefull_'):
        k=ast.literal_eval(name[len('T2primefull_'):])[1];meta=next(d for d in json.loads((inp/'star_construction.json').read_text()) if d['k']==k)
        P=star_selection(a,name,meta['labels']);assert P.shape==joined.shape==(dim,85)
        # A floating solve only proposes an integer change of basis. Exact
        # residual zero and nonzero modular determinants validate it fully.
        C=np.rint(np.linalg.lstsq(P.toarray(),joined.toarray(),rcond=None)[0]).astype(np.int64)
        exact_sparse_equal(P@sp.csr_matrix(C),joined,'selected-star column span')
        assert modular_rank(P.toarray())==modular_rank(C)==85
    else:
        assert joined.shape==(dim,dim)
        gram=(joined.T@joined).tocsr();diagonal=gram.diagonal();assert np.all(diagonal>0)
        off=gram-sp.diags(diagonal,format='csr',dtype=diagonal.dtype);off.eliminate_zeros();assert off.nnz==0,'Character planes do not span orthogonally'
    for i,Wi in enumerate(ws):
        for Wj in ws[i+1:]:
            cross=sp.kron(Wi.T,Wj.T,format='csr')
            z=(cross@A).tocsr();z.eliminate_zeros();assert z.nnz==0,'Nonzero off-character affine block'
            assert np.all(cross@b==0),'Nonzero off-character constant'
    return ws


def load_descriptors(inp):
    result={}
    if (inp/'operator_descriptors.json').exists():result.update({d['name']:d for d in json.loads((inp/'operator_descriptors.json').read_text())})
    if (inp/'source_operator_blocks.json').exists():result.update({d['source_name']:d for d in json.loads((inp/'source_operator_blocks.json').read_text())})
    return result

def load_projections(inp):
    result=[]
    if (inp/'cone_projections.json').exists():result.extend(json.loads((inp/'cone_projections.json').read_text()))
    if (inp/'projection_descriptors.json').exists():
        for d in json.loads((inp/'projection_descriptors.json').read_text()):result.append({'name':d['block_name'],'source_name':d['source_name'],'source_dim':d['source_dim'],'dim':d['projected_dim'],'characters':d['characters'],'reflections':d['reflection_generators'],'projection':d['W_file']})
    return result

def singlet_row(a):
    row=collections.defaultdict(int)
    for k,p in itertools.product(range(16),repeat=2):add_scaled(row,a.words_affine([(1,((1,16+k),(0,k),(1,p),(0,16+p)))]))
    return sparse_rows([{z:v for z,v in row.items() if v}],len(a.names))


def adaptive_map(a,T,inp,name,cache):
    if name.startswith('ADAPTIVE_UNUSED_'):return sp.csr_matrix((1,T.shape[1])),np.ones(1)
    metadata=json.loads((inp/'adaptive_cuts.json').read_text());index=int(name.rsplit('_',1)[1]);cut=next(d for d in metadata['cuts'] if d['index']==index)
    oracle=Path(metadata['oracle_directory']);prefix=cut['source_prefix'];key=(str(oracle),prefix)
    if key not in cache:
        exact_sparse_equal(T,sp.load_npz(oracle/'symmetry_expansion.npz'),'adaptive oracle variable expansion')
        block=next(b for b in json.loads((oracle/'blocks.json').read_text()) if b['prefix']==prefix);assert block['name']==cut['source_name']
        projection=next(m for m in load_projections(oracle) if m['name']==block['name']);source=projection['source_name']
        fullA,fullb=physical_block(a,source,projection['source_dim'],load_descriptors(oracle));W=sp.load_npz(oracle/projection['projection']).tocsr();assert np.all(W.data==np.rint(W.data))
        for chi,kind in zip(projection['characters'],projection['reflections']):exact_sparse_equal(character_permutation(a,source,projection['source_dim'],kind)@W,chi*W,'adaptive oracle reflection')
        C=sp.kron(W.T,W.T,format='csr');A=(C@fullA@T).tocsr();b=np.asarray(C@fullb).ravel()
        exact_sparse_equal(A,sp.load_npz(oracle/(prefix+'_A.npz')),'adaptive physical oracle map');assert np.array_equal(b,np.load(oracle/(prefix+'.npz'))['b'])
        assert np.all(A.data==np.rint(A.data)) and np.all(b==np.rint(b));cache[key]=(A.astype(np.int64),b.astype(np.int64))
    A,b=cache[key];cp=inp/cut['file']
    if not cp.exists():cp=Path(metadata['cut_directory'])/cut['file']
    data=np.load(cp);K=data['K'];assert np.issubdtype(K.dtype,np.integer) and K.shape[0]**2==A.shape[0]
    maxk=max(abs(int(z)) for z in K);assert maxk*maxk<2**63
    outer=np.outer(K,K).ravel();maxo=max(abs(int(z)) for z in outer)
    maxcol=int(np.max(np.asarray(abs(A).sum(axis=0)).ravel(),initial=0));assert maxo*maxcol<2**63 and maxo*sum(abs(int(z)) for z in b)<2**63
    an=np.asarray(A.T@outer).ravel();bn=int(b@outer);bits=2*cut['bits'];assert bits==int(data['denominator_bits'])
    assert np.array_equal(an,data['a_numerator']) and bn==int(data['b_numerator'][0])
    assert max((abs(int(z)) for z in an),default=0)<=2**53 and abs(bn)<=2**53
    den=1<<bits
    return sp.csr_matrix((an.astype(float)/den)[None,:]),np.array([bn/den])

def dual_block_map(a,T,inp,name,cache):
    """Audit a matrix cone assembled from already audited dyadic directions.

    The final augmentation is an existing one-body operator, so it adds no
    cubic direction to the declared group-closed operator space.
    """
    metadata=json.loads((inp/'dual_blocks.json').read_text());entry=next(d for d in metadata['blocks'] if d['name']==name)
    oracle=Path(metadata['oracle_directory']);cuts=json.loads((inp/'adaptive_cuts.json').read_text())
    data=np.load(inp/entry['file']);P=data['P_integer'];assert np.issubdtype(P.dtype,np.integer)
    assert P.shape[1]==len(entry['cut_indices'])+1
    for j,index in enumerate(entry['cut_indices']):
        cut=next(d for d in cuts['cuts'] if d['index']==index)
        assert cut['source_prefix']==entry['source_prefix'] and cut['source_name']==entry['source_name'] and cut['bits']==entry['bits']
        adaptive_map(a,T,inp,f'DUAL_CUT_{index:03d}',cache)
        cp=inp/cut['file']
        if not cp.exists():cp=Path(cuts['cut_directory'])/cut['file']
        assert np.array_equal(P[:,j],np.load(cp)['K']),(name,j,'changed selected direction')
    linear=np.zeros(P.shape[0],dtype=np.int64);linear[entry['linear_index']]=1<<entry['bits']
    assert np.array_equal(P[:,-1],linear),(name,'augmentation is not pure one-body')
    projection=next(m for m in load_projections(oracle) if m['name']==entry['source_name'])
    W=sp.load_npz(oracle/projection['projection']).tocsr();column=W[:,entry['linear_index']].toarray().ravel()
    assert np.count_nonzero(column)==1 and column[-1]==1,(name,'raw augmentation not c-dagger')
    A,b=cache[(str(oracle),entry['source_prefix'])]
    maxp=max(abs(int(z)) for z in P.ravel());maxcol=int(np.max(np.asarray(abs(A).sum(axis=0)).ravel(),initial=0))
    assert maxp*maxp<2**63 and maxp*maxp*maxcol<2**63 and maxp*maxp*sum(abs(int(z)) for z in b)<2**63
    C=sp.kron(sp.csr_matrix(P.T),sp.csr_matrix(P.T),format='csr');An=(C@A).tocsr();An.eliminate_zeros();bn=np.asarray(C@b).ravel()
    bits=2*entry['bits'];assert int(data['denominator_bits'])==bits
    exact_sparse_equal(An,sp.load_npz(inp/(Path(entry['file']).stem+'_A_integer.npz')),'dyadic matrix numerator')
    assert np.array_equal(bn,data['b_numerator'])
    assert max((abs(int(z)) for z in An.data),default=0)<=2**53 and max((abs(int(z)) for z in bn),default=0)<=2**53
    return An.astype(float)/(1<<bits),bn.astype(float)/(1<<bits)

def portable_dual_block_map(a,T,operator_input,name,cache):
    """Rebuild a portable selected cone directly from canonical CAR words.

    No discovery/oracle map, solver module or external projection is read.
    """
    entries=json.loads((operator_input/'source_blocks.json').read_text());entry=next(d for d in entries if d['name']==name)
    source=entry['raw_source_name'];ops=entry['ops'];data=np.load(operator_input/entry['projection']);R=data['R_integer']
    assert R.shape[0]==len(ops) and np.issubdtype(R.dtype,np.integer)
    nc=entry['n_cubic_directions'];assert R.shape[1]==nc+1 and entry['augmentation_last_column']
    linear=np.zeros(R.shape[0],dtype=np.int64);linear[-1]=1<<entry['bits'];assert np.array_equal(R[:,-1],linear)
    if source not in cache:
        A,b=physical_block(a,source,len(ops),{source:{'kind':'T2prime','ops':ops}})
        cache[source]=((A@T).tocsr(),b)
    A,b=cache[source]
    maxr=max(abs(int(z)) for z in R.ravel());maxcol=int(np.max(np.asarray(abs(A).sum(axis=0)).ravel(),initial=0))
    assert maxr*maxr<2**63 and maxr*maxr*maxcol<2**63 and maxr*maxr*sum(abs(int(z)) for z in b)<2**63
    C=sp.kron(sp.csr_matrix(R.T),sp.csr_matrix(R.T),format='csr');An=(C@A).tocsr();An.eliminate_zeros();bn=np.asarray(C@b).ravel()
    bits=2*entry['bits'];assert int(np.asarray(data['denominator_bits']).item())==bits
    assert max((abs(int(z)) for z in An.data),default=0)<=2**53 and max((abs(int(z)) for z in bn),default=0)<=2**53
    return An.astype(float)/(1<<bits),bn.astype(float)/(1<<bits)

def run(inp,out,allow_singlet=False,operator_input=None):
    inp=Path(inp);out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);tick=time.perf_counter()
    tests=car_self_test();bonds=geometry_test();contraction_cases=exhaustive_t2_contraction_test()
    reduced=(inp/'symmetry_expansion.npz').exists()
    names=json.loads((inp/('full_variable_names.json' if reduced else 'variable_names.json')).read_text());a=Audit(names)
    T=sp.load_npz(inp/'symmetry_expansion.npz').tocsr() if reduced else sp.eye(len(names),dtype=np.int64,format='csr')
    symstats=audit_symmetry_expansion(a,T) if reduced else None
    T=T.astype(np.int64)
    c=np.load(inp/'objective.npy');expected_c=np.asarray(T.T@(a.objective()/2)).ravel();objective_delta=float(np.max(np.abs(expected_c-c)));assert objective_delta<1e-12,'Hamiltonian coefficients mismatch'
    E,e=a.equalities();E=(E@T).tocsr();storedE=sp.load_npz(inp/'equalities.npz');singlet=False
    if storedE.shape[0]==E.shape[0]+1:
        assert allow_singlet,'Additional singlet equality requires explicit --allow-singlet audit scope'
        E=sp.vstack([E,singlet_row(a)@T],format='csr');e=np.r_[e,0];singlet=True
    exact_sparse_equal(E,storedE,'equalities');assert np.array_equal(e,np.load(inp/'rhs.npy'))
    descriptors=load_descriptors(inp)
    projections={};source_projections=collections.defaultdict(list)
    for m in load_projections(inp):projections[m['name']]=m;source_projections[m['source_name']].append(m)
    cache={};blocks=json.loads((inp/'blocks.json').read_text());logs=[];nnz=0
    for block in blocks:
        bt=time.perf_counter();dim=block['dim'];meta=projections.get(block['name']);source=meta['source_name'] if meta else block['name'];sdim=meta['source_dim'] if meta else dim
        if block['name'].startswith(('ADAPTIVE_','DUAL_CUT_')):
            assert dim==1;A,b=adaptive_map(a,T,inp,block['name'],cache)
        elif block['name'].startswith('DUAL_BLOCK_'):
            A,b=portable_dual_block_map(a,T,operator_input,block['name'],cache) if operator_input else dual_block_map(a,T,inp,block['name'],cache)
            assert A.shape[0]==dim**2
        else:
            if source not in cache:
                fullA,b=physical_block(a,source,sdim,descriptors);A=(fullA@T).tocsr();A.eliminate_zeros()
                if source in source_projections:audit_character_source(a,source,A,b,source_projections[source],inp)
                cache[source]=(A,b)
            A,b=cache[source]
        if meta:
            W=sp.load_npz(inp/meta['projection']).tocsr();K=sp.kron(W.T,W.T,format='csr');A=(K@A).tocsr();A.eliminate_zeros();b=np.asarray(K@b).ravel()
        prefix=block['prefix'];storedA=sp.load_npz(inp/(prefix+'_A.npz'));storedb=np.load(inp/(prefix+'.npz'))['b']
        exact_sparse_equal(A,storedA,block['name']);assert np.array_equal(b,storedb),(block['name'],'constant mismatch')
        nnz+=A.nnz;logs.append({'name':block['name'],'dim':dim,'nnz':A.nnz,'seconds':time.perf_counter()-bt})
        print(json.dumps(logs[-1]),flush=True);exterior_normal.cache_clear()
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result={'passed':True,'input_directory':str(inp.resolve()),'portable_operator_input_directory':str(operator_input.resolve()) if operator_input else None,'portable_selected_maps_checked':sum(b['name'].startswith('DUAL_BLOCK_') for b in blocks) if operator_input else 0,'independent_CAR_Fock_action_tests':tests,'exhaustive_T2_CAR_order_equality_patterns':contraction_cases,'distinct_lattice_bonds':bonds,'full_variables':len(names),'variables':T.shape[1],'symmetry_expansion_audit':symstats,'singlet_ground_sector_restriction':singlet,'character_projection_sources_audited':len(source_projections),'star_selected_subspace_rank_per_source':85 if (inp/'star_construction.json').exists() else None,'adaptive_cut_maps_checked':len(json.loads((inp/'adaptive_cuts.json').read_text())['cuts']) if (inp/'adaptive_cuts.json').exists() and not operator_input else 0,'equalities':len(e),'blocks':len(blocks),'affine_nonzero_coefficients_checked':nnz,'all_affine_coefficient_differences':0,'objective_float_max_difference':objective_delta,'objective_handling':'Use independently reconstructed exact half-integer coefficients in final certificate.','elapsed_seconds':time.perf_counter()-tick,'peak_rss_bytes':rss,'block_details':logs,'physical_sector':{'L':4,'t':1,'U':8,'Nup':8,'Ndown':8},'notes':['All sparse coefficients and constants compared exactly.','Real Hermitian moments and momentum/spin block selection are rebuilt from variable names.','T1 degree-six cancellation uses independent exterior multiplication; the T2 contraction table is exhaustively verified against it for all 46,656 relative-order/equality patterns.','Symmetry expansion is independently checked by signed orbit traversal; character projections are checked for the declared reflection action, complete source span or explicitly selected85-dimensional star span, and exact vanishing cross-character maps.','Fermionic real moment symmetrization is valid because the Fourier Hamiltonian and operator spaces are closed under complex conjugation.']}
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='block_details'},indent=2))


def audit_construction(inp,out):
    inp=Path(inp);out=Path(out);tick=time.perf_counter()
    tests=car_self_test();bonds=geometry_test();cases=exhaustive_t2_contraction_test()
    a=Audit(json.loads((inp/'full_variable_names.json').read_text()));T=sp.load_npz(inp/'symmetry_expansion.npz').tocsr();symstats=audit_symmetry_expansion(a,T)
    if (inp/'full_objective.npy').exists():assert np.array_equal(a.objective(),2*np.load(inp/'full_objective.npy'))
    desc=load_descriptors(inp);sources=collections.defaultdict(list)
    for m in load_projections(inp):sources[m['source_name']].append(m)
    logs=[]
    for name,metas in sources.items():
        bt=time.perf_counter();fullA,b=physical_block(a,name,metas[0]['source_dim'],desc);A=(fullA@T).tocsr();A.eliminate_zeros();ws=audit_character_source(a,name,A,b,metas,inp)
        logs.append({'source':name,'source_dim':metas[0]['source_dim'],'character_dims':[W.shape[1] for W in ws],'seconds':time.perf_counter()-bt})
        print(json.dumps(logs[-1]),flush=True);exterior_normal.cache_clear()
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result={'passed_construction_checks':True,'full_export_audit_complete':False,'input_directory':str(inp.resolve()),'independent_CAR_Fock_action_tests':tests,'exhaustive_T2_CAR_order_equality_patterns':cases,'distinct_lattice_bonds':bonds,'symmetry_expansion_audit':symstats,'character_projection_sources':len(sources),'elapsed_seconds':time.perf_counter()-tick,'peak_rss_bytes':rss,'source_details':logs,'remaining_check':'Compare every exported A,b,E,rhs,c coefficient after solver export completes.'}
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_details'},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--construction-only',action='store_true');p.add_argument('--allow-singlet',action='store_true');p.add_argument('--operator-input',type=Path);args=p.parse_args();audit_construction(args.input,args.output) if args.construction_only else run(args.input,args.output,args.allow_singlet,args.operator_input)
