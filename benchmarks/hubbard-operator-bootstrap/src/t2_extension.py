"""Momentum-blocked full or mixed-spin T2 anticommutator constraints.

A_(a,b;c)=a†_a a†_b a_c, a<b.  For odd A, the matrix
T2_ij=<A_i† A_j+A_j A_i†> is PSD, with degree-six CAR cancellation.
Optional one-body augmentation uses A=a†_k (anticommutator formulation).
This is an SOS-valid relaxation of cubic moment positivity, not a claim of
exact equality to the original full cubic moment minimization.
"""
from collections import defaultdict
from itertools import combinations
import time
import numpy as np
import scipy.sparse as sp
from t1_extension import normal_order


def adjoint(word):
    return tuple((not dagger,p) for dagger,p in reversed(word))


def anticommutator_polynomial(word_t,word_u):
    result=defaultdict(int)
    dt=adjoint(word_t)
    for word in (dt+word_u,word_u+dt):
        for key,coeff in normal_order(word):result[key]+=coeff
    result={k:v for k,v in result.items() if v}
    assert all(len(k[0])<=2 for k in result), (word_t,word_u,result)
    return result


def t2_blocks(model,mixed_only=False,augment=True):
    groups=defaultdict(list)
    V=model.V
    for a,b in combinations(range(2*V),2):
        if mixed_only and (a//V)==(b//V):continue
        for c in range(2*V):
            q=model.sub(model.add(a%V,b%V),c%V)
            down=a//V+b//V-c//V
            groups[(down,q)].append(((True,a),(True,b),(False,c)))
    if augment:
        for down in (0,1):
            for q in range(V):groups[(down,q)].append(((True,q+down*V),))
    return dict(sorted(groups.items()))


def add_t2_constraints(model,mixed_only=False,augment=True,prime=True,progress=None,key_filter=None):
    def moment_map(creators,annihilators):
        if not creators:return {-1:1} if not annihilators else {}
        if len(creators)==1:return {creators[0]:1} if creators==annihilators else {}
        if len(creators)==2:return model.gamma(*creators,*annihilators)
        raise ValueError((creators,annihilators))
    start=time.perf_counter()
    for key,ops in t2_blocks(model,mixed_only,augment).items():
        if key_filter is not None and not key_filter(key):continue
        n=len(ops)
        rows=[];cols=[];data=[];b=np.zeros(n*n)
        supports=[set(mode for _,mode in op) for op in ops]
        for j,u in enumerate(ops):
            for i in range(j+1):
                if len(ops[i])==3 and len(u)==3:
                    if not supports[i].intersection(supports[j]):continue
                    poly=anticommutator_polynomial(ops[i],u)
                elif prime:
                    poly=dict(normal_order(adjoint(ops[i])+u))
                else:
                    poly=anticommutator_polynomial(ops[i],u)
                coeff=defaultdict(float)
                for (creators,annihilators),mult in poly.items():
                    for var,value in moment_map(creators,annihilators).items():coeff[var]+=mult*value
                for row in ([i*n+j] if i==j else [i*n+j,j*n+i]):
                    for var,value in coeff.items():
                        if not value:continue
                        if var==-1:b[row]+=value
                        else:rows.append(row);cols.append(var);data.append(value)
        A=sp.coo_matrix((data,(rows,cols)),shape=(n*n,model.nvar)).tocsr()
        model.blocks.append(dict(name=f'T2{"prime" if prime and augment else ""}{"mixed" if mixed_only else "full"}_{key}',dim=n,A=A,b=b,ops=ops,key=key))
        if progress:progress(key,n,A.nnz,time.perf_counter()-start)
        normal_order.cache_clear()
    return model


def self_test():
    nmode=5;dim=1<<nmode
    annih=[]
    for p in range(nmode):
        a=np.zeros((dim,dim))
        for mask in range(dim):
            if (mask>>p)&1:a[mask^(1<<p),mask]=(-1)**((mask&((1<<p)-1)).bit_count())
        annih.append(a)
    def wordmat(word):
        result=np.eye(dim)
        for dagger,p in word:result=result@(annih[p].T if dagger else annih[p])
        return result
    def normmat(creators,annihilators):
        return wordmat(tuple((True,p) for p in creators)+tuple((False,p) for p in reversed(annihilators)))
    ops=[((True,a),(True,b),(False,c)) for a,b in combinations(range(nmode),2) for c in range(nmode)]
    ops += [((True,a),) for a in range(nmode)]
    rng=np.random.default_rng(314159)
    psi=rng.normal(size=dim);psi/=np.linalg.norm(psi)
    M=np.empty((len(ops),len(ops)));maxerr=0
    for i,t in enumerate(ops):
        At=wordmat(t)
        for j,u in enumerate(ops):
            Au=wordmat(u)
            direct=At.T@Au+Au@At.T
            derived=sum((coeff*normmat(*key) for key,coeff in anticommutator_polynomial(t,u).items()),np.zeros((dim,dim)))
            maxerr=max(maxerr,float(np.max(np.abs(derived-direct))))
            M[i,j]=psi@derived@psi
    vals=np.linalg.eigvalsh(M)
    assert maxerr==0 and vals[0]>-1e-12
    print(dict(max_car_matrix_error=maxerr,min_t2_eig=float(vals[0]),nops=len(ops)))
if __name__=='__main__':self_test()


def self_test_prime():
    """Check standard one-sided linear augmentation in a direct Fock model."""
    nmode=4;dim=1<<nmode
    annih=[]
    for p in range(nmode):
        a=np.zeros((dim,dim))
        for mask in range(dim):
            if (mask>>p)&1:a[mask^(1<<p),mask]=(-1)**((mask&((1<<p)-1)).bit_count())
        annih.append(a)
    def wordmat(word):
        m=np.eye(dim)
        for dagger,p in word:m=m@(annih[p].T if dagger else annih[p])
        return m
    ops=[((True,a),(True,b),(False,c)) for a,b in combinations(range(nmode),2) for c in range(nmode)]
    ncubic=len(ops);ops.extend(((True,a),) for a in range(nmode))
    rng=np.random.default_rng(161803)
    psi=rng.normal(size=dim);psi/=np.linalg.norm(psi)
    M=np.empty((len(ops),len(ops)));maxerr=0
    for i,t in enumerate(ops):
        At=wordmat(t)
        for j,u in enumerate(ops):
            Au=wordmat(u)
            direct=At.T@Au
            if i<ncubic and j<ncubic:
                direct+=Au@At.T
                poly=anticommutator_polynomial(t,u)
            else:poly=dict(normal_order(adjoint(t)+u))
            derived=sum((coeff*wordmat(tuple((True,p) for p in cs)+tuple((False,p) for p in reversed(ans))) for (cs,ans),coeff in poly.items()),np.zeros((dim,dim)))
            maxerr=max(maxerr,float(np.max(np.abs(derived-direct))))
            M[i,j]=psi@derived@psi
    mineig=float(np.linalg.eigvalsh(M)[0])
    assert maxerr==0 and mineig>-1e-12
    print(dict(max_prime_matrix_error=maxerr,min_t2prime_eig=mineig,nops=len(ops)))
