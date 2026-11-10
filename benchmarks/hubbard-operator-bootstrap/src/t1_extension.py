"""Momentum/spin-blocked three-particle T1 constraints in degree-four moments.

For T=(p<q<r), A_T = a_r a_q a_p.  The Hermitian matrix
  T1[T,U] = < A_T^dagger A_U + A_U A_T^dagger >
is PSD for any physical state.  CAR cancels its degree-six terms exactly.

`normal_order` returns keys (creators, annihilators), each in ascending order,
with actual monomial a†_c0 ... a†_cn a_an ... a_a0.  `build_t1_maps`
accepts a callback sending each such key to a sparse real affine variable map,
using index -1 for the constant.  It returns sparse maps for column-major vec.
No assumptions about a particular SDP package are made.
"""
from functools import lru_cache
from itertools import combinations
from collections import defaultdict
import time
import numpy as np
import scipy.sparse as sp

@lru_cache(maxsize=300000)
def normal_order(word):
    """Exact fermion normal ordering; word tuples are (dagger_bool, mode)."""
    word = tuple(word)
    # Canonical creation order ascending; annihilation order descending.
    def sortkey(op):
        dagger, mode = op
        return (0, mode) if dagger else (1, -mode)
    for j in range(len(word)-1):
        left, right = word[j], word[j+1]
        if left == right:
            return ()
        if sortkey(left) > sortkey(right):
            swapped = word[:j]+(right,left)+word[j+2:]
            result = defaultdict(int)
            for key, coeff in normal_order(swapped):
                result[key] -= coeff
            if not left[0] and right[0] and left[1]==right[1]:
                contracted = word[:j]+word[j+2:]
                for key, coeff in normal_order(contracted):
                    result[key] += coeff
            return tuple(sorted((k,v) for k,v in result.items() if v))
    creators = tuple(op[1] for op in word if op[0])
    annihilators = tuple(reversed([op[1] for op in word if not op[0]]))
    return (((creators,annihilators),1),)


def t1_polynomial(triple_t,triple_u):
    """Sparse exact polynomial for the T1 matrix element indexed by T,U."""
    create_t = tuple((True,p) for p in triple_t)
    annih_u = tuple((False,p) for p in reversed(triple_u))
    result = defaultdict(int)
    for word in (create_t+annih_u, annih_u+create_t):
        for key,coeff in normal_order(word):
            result[key] += coeff
    result = {key:coeff for key,coeff in result.items() if coeff}
    assert all(len(key[0])<=2 for key in result), (triple_t,triple_u,result)
    return result


def momentum_add(momenta, lattice_length=4):
    L=lattice_length
    return (sum(p%L for p in momenta)%L,
            sum(p//L for p in momenta)%L)


def triple_blocks(lattice_length=4):
    L=lattice_length
    V=L*L
    blocks=defaultdict(list)
    for triple in combinations(range(2*V),3):
        n_up=sum(p<V for p in triple)
        qx,qy=momentum_add([p%V for p in triple],L)
        blocks[(n_up,qx,qy)].append(triple)
    return dict(sorted(blocks.items()))


def build_t1_maps(moment_map,nvar,lattice_length=4,spin_counts=None,progress=None,key_filter=None):
    """Return list of {key, triples, A, b} for T1 = reshape(A@x+b).

    `moment_map(creators, annihilators)` must return {index: coefficient},
    with -1 as constant. Omit identities that vanish (return {}).  Variables
    and maps must be real; inversion plus time reversal validates this for
    the Hubbard instance when built in a symmetry-closed operator space.
    `spin_counts` optionally selects block spin counts, e.g. (1,2).
    """
    result=[]
    start=time.perf_counter()
    for key,triples in triple_blocks(lattice_length).items():
        if spin_counts is not None and key[0] not in spin_counts:
            continue
        if key_filter is not None and not key_filter(key):continue
        n=len(triples)
        rows=[];cols=[];data=[];b=np.zeros(n*n)
        for j,u in enumerate(triples):
            for i in range(j+1):
                t=triples[i]
                coeff=defaultdict(float)
                for (creators,annihilators),mult in t1_polynomial(t,u).items():
                    for var,value in moment_map(creators,annihilators).items():
                        coeff[var] += mult*value
                for row in ([i+n*j] if i==j else [i+n*j,j+n*i]):
                    for var,value in coeff.items():
                        if not value: continue
                        if var==-1: b[row]+=value
                        else:
                            rows.append(row);cols.append(var);data.append(value)
        A=sp.coo_matrix((data,(rows,cols)),shape=(n*n,nvar)).tocsr()
        result.append(dict(key=key,triples=triples,A=A,b=b))
        if progress: progress(key,n,A.nnz,time.perf_counter()-start)
        # Normal ordering caches are useful within blocks but not globally.
        normal_order.cache_clear()
    return result


def self_test():
    """Independent dense Fock-space CAR and anticommutator validation."""
    nmode=6; dim=1<<nmode
    annih=[]
    for p in range(nmode):
        a=np.zeros((dim,dim))
        for mask in range(dim):
            if (mask>>p)&1:
                a[mask^(1<<p),mask]=(-1)**((mask&((1<<p)-1)).bit_count())
        annih.append(a)
    def mat(creators,annihilators):
        m=np.eye(dim)
        for p in creators: m=m@annih[p].T
        for p in reversed(annihilators): m=m@annih[p]
        return m
    triples=list(combinations(range(nmode),3))
    rng=np.random.default_rng(271828)
    psi=rng.normal(size=dim); psi/=np.linalg.norm(psi)
    M=np.empty((len(triples),len(triples)))
    maxerr=0
    for i,t in enumerate(triples):
        At=mat((),t)
        for j,u in enumerate(triples):
            Au=mat((),u)
            direct=At.T@Au+Au@At.T
            derived=sum((coeff*mat(*key) for key,coeff in t1_polynomial(t,u).items()),np.zeros((dim,dim)))
            maxerr=max(maxerr,float(np.max(np.abs(derived-direct))))
            M[i,j]=psi@derived@psi
    vals=np.linalg.eigvalsh(M)
    assert maxerr==0 and vals[0]>-1e-12
    print(dict(max_car_matrix_error=maxerr,min_t1_eig=float(vals[0]),
               block_sizes=sorted(set(map(len,triple_blocks().values()))),
               sum_block_dims=sum(map(len,triple_blocks().values())),
               sum_squared_dims=sum(len(v)**2 for v in triple_blocks().values())))

if __name__=='__main__': self_test()


def add_t1_constraints(model,spin_counts=None,progress=None,key_filter=None):
    """Integrate with lab002's momentum_pqg.Model, retaining sparse maps."""
    def moment_map(creators,annihilators):
        if not creators:
            return {-1:1} if not annihilators else {}
        if len(creators)==1:
            return {creators[0]:1} if creators==annihilators else {}
        if len(creators)==2:
            return model.gamma(*creators,*annihilators)
        raise ValueError((creators,annihilators))
    maps=build_t1_maps(moment_map,model.nvar,model.L,spin_counts,progress,key_filter)
    for block in maps:
        model.blocks.append(dict(name=f'T1_{block["key"]}',dim=len(block['triples']),
                                 A=block['A'],b=block['b'],
                                 ops=[tuple((False,p) for p in reversed(t)) for t in block['triples']],
                                 key=(block['key'][0],block['key'][1]+model.L*block['key'][2])))
    return model
