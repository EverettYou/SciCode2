#!/usr/bin/env python3
"""Translation-averaged Hubbard cluster lower bounds with full-basis certificates.

All numerical certification is explicit (no reliance on eigensolver success status).
The certificate assumes IEEE binary64 round-to-nearest and gamma_k BLAS error
bounds. Exact cluster coefficients are chosen dyadic.
"""
from __future__ import annotations
import argparse,itertools,json,math,os,resource,time
from pathlib import Path
import numpy as np
import scipy.linalg as la
import scipy.sparse as sp
import scipy.sparse.linalg as sla

EPS=np.finfo(float).eps/2

def gamma(k):
    z=k*EPS
    return float(np.nextafter(z/(1-z),math.inf))

def upper_sum(x,axis=None):
    x=np.asarray(x)
    n=x.size if axis is None else x.shape[axis]
    return np.nextafter(np.sum(x,axis=axis)/(1-gamma(max(n,1))),math.inf)

def norm_inf(a): return float(np.max(upper_sum(np.abs(a),axis=1)))
def norm_one(a): return float(np.max(upper_sum(np.abs(a),axis=0)))

def geometry(w,h,periodic_x=False,periodic_y=False):
    sites=[(x,y) for y in range(h) for x in range(w)]
    index={s:i for i,s in enumerate(sites)}
    edges=[]
    for i,(x,y) in enumerate(sites):
        for axis,(dx,dy) in enumerate([(1,0),(0,1)]):
            q=(x+dx,y+dy)
            if axis==0 and periodic_x: q=(q[0]%w,q[1])
            if axis==1 and periodic_y: q=(q[0],q[1]%h)
            if q in index:
                j=index[q]
                if i!=j and not any({i,j}=={a,b} for a,b,c in edges):edges.append((i,j,axis))
    return sites,edges

def spin_hamiltonian(n,k,edges,weights):
    basis=[sum(1<<i for i in c) for c in itertools.combinations(range(n),k)]
    inv={b:i for i,b in enumerate(basis)}
    rows=[];cols=[];vals=[]
    for col,b in enumerate(basis):
        for e,(i,j,axis) in enumerate(edges):
            if bool(b&(1<<i)) != bool(b&(1<<j)):
                sign=(-1)**((b&(((1<<max(i,j))-1)^((1<<(min(i,j)+1))-1))).bit_count())
                target=b^(1<<i)^(1<<j)
                rows.append(inv[target]);cols.append(col);vals.append(-weights[e]*sign)
    return np.array(basis,dtype=np.int64),sp.csr_matrix((vals,(rows,cols)),shape=(len(basis),len(basis)))

def build_block(n,a,b,edges,weights,us):
    ba,ta=spin_hamiltonian(n,a,edges,weights)
    bb,tb=spin_hamiltonian(n,b,edges,weights)
    # Fermion order is all spin-up modes then all spin-down modes.
    kinetic=sp.kron(ta,sp.eye(len(bb)),format='csr')+sp.kron(sp.eye(len(ba)),tb,format='csr')
    diag=np.zeros((len(ba),len(bb)))
    for i,u in enumerate(us):diag+=u*((((ba>>i)&1)-.5)[:,None])*((((bb>>i)&1)-.5)[None,:])
    return kinetic+sp.diags(diag.ravel(),format='csr')

def certify_basis(A,evals,Q):
    """Bound lambda_min(A) from complete approximate eigenbasis Q.

    Let R=AQ-QD and eta>=||Q.T Q-I||_2. For a lowest left eigenvector
    x of A, z=Q.T x has norm >=sqrt(1-eta)||x||; if lambda<min D,
    (min D-lambda)||z|| <=||R||_2||x||. Hence the reported bound.
    Every norm gets a nonnegative-summation and dot-product roundoff allowance.
    """
    d=A.shape[0]
    qi,q1=norm_inf(Q),norm_one(Q)
    G=Q.T@Q
    G.flat[::d+1]-=1
    eta=float(np.nextafter((norm_inf(G)+gamma(d)*q1*qi+EPS)*(1+1e-12),math.inf))
    if eta>=1:raise RuntimeError('Basis not verified invertible')
    AQ=A@Q
    R=AQ-Q*evals[None,:]
    # Each sparse row multiplication has <=s entries; the subtraction and
    # multiplication by D add two operations. Bound errors entrywise by one
    # uniform bound, then propagate to 1/infinity norms.
    s=int(np.max(np.diff(A.indptr)))
    an=float(np.max(upper_sum(np.abs(A.toarray()),axis=1))) if d<16 else float(np.max(np.asarray(abs(A).sum(axis=1)).ravel()))/(1-gamma(s))
    maxq=float(np.max(np.abs(Q)))
    delta=float(np.nextafter(gamma(s+2)*maxq*(an+float(np.max(np.abs(evals))))*(1+1e-12),math.inf))
    rinf=float(np.nextafter((norm_inf(R)+d*delta)*(1+1e-12),math.inf))
    rone=float(np.nextafter((norm_one(R)+d*delta)*(1+1e-12),math.inf))
    rnorm=float(np.nextafter(math.sqrt(float(np.nextafter(rinf*rone,math.inf))),math.inf))
    sigma=float(np.nextafter(math.sqrt(float(np.nextafter(1-eta,-math.inf))),-math.inf))
    lower=float(np.nextafter(float(evals[0])-float(np.nextafter(rnorm/sigma,math.inf))-1e-12,-math.inf))
    return {'lower':lower,'ritz':float(evals[0]),'dimension':d,'eta':eta,'residual_norm_bound':rnorm,'sparse_row_nnz':s,'entry_roundoff_bound':delta}

def independent_sector_lower(n,a,b,onebody):
    # Kinetic minimum plus min possible interaction at fixed numbers.
    return float(sum(onebody[:a])+sum(onebody[:b])+8*(max(a+b-n,0)-(a+b)/2+n/4))

def run(args):
    start=time.perf_counter()
    sites,edges=geometry(args.w,args.h,args.periodic_x,args.periodic_y)
    n=len(sites)
    assert 1<=args.w<=4 and 1<=args.h<=4
    # Every local edge must be a physical4x4 torus edge and flip its
    # bipartite sign; this also validates particle-hole sector reduction.
    for i,j,axis in edges:
        dx=(sites[j][0]-sites[i][0])%4;dy=(sites[j][1]-sites[i][1])%4
        assert (dx,dy) in [(1,0),(3,0),(0,1),(0,3)]
        assert (sum(sites[i])-sum(sites[j]))%2==1
    counts=[sum(z==a for i,j,z in edges) for a in range(2)]
    weights=np.array([n/counts[z] for i,j,z in edges])
    us=np.full(n,8.)
    if args.weights:
        z=json.loads(Path(args.weights).read_text());weights=np.array(z['weights']);us=np.array(z['us'])
    # Require exact dyadic representation and exact cover constraints.
    from fractions import Fraction
    for axis in range(2):assert sum(Fraction(float(weights[e])) for e,(_,_,z) in enumerate(edges) if z==axis)==n
    assert sum(Fraction(float(u)) for u in us)==8*n
    one=np.zeros((n,n))
    for z,(i,j,a) in enumerate(edges):one[i,j]=one[j,i]=-weights[z]
    onebody=la.eigvalsh(one)
    spin_lowers=[]
    for k in range(n+1):
        _,T=spin_hamiltonian(n,k,edges,weights)
        dv,qv=la.eigh(T.toarray(),check_finite=False,driver='evd')
        spin_lowers.append(certify_basis(T,dv,qv)['lower'])
    sectors=[]
    for a in range(n+1):
        for b in range(n+1):
            orbit={(a,b),(b,a),(n-a,n-b),(n-b,n-a)}
            if (a,b)==min(orbit):sectors.append((a,b))
    # Half-filled balanced block first, then descending size.
    sectors.sort(key=lambda ab:(abs(sum(ab)-n),abs(ab[0]-ab[1]),-math.comb(n,ab[0])*math.comb(n,ab[1])))
    results=[];best_ritz=math.inf;global_low=math.inf
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    for a,b in sectors:
        tick=time.perf_counter()
        # Use independently verified kinetic-sector minima; uniform onsite
        # interaction minimum at fixed spin numbers is exact.
        if np.all(us==8):
            interaction_min=8*(max(a+b-n,0)-(a+b)/2+n/4)
        else:
            ba,_=spin_hamiltonian(n,a,[],[]);bb,_=spin_hamiltonian(n,b,[],[])
            ddiag=np.zeros((len(ba),len(bb)))
            for i,u in enumerate(us):ddiag+=u*((((ba>>i)&1)-.5)[:,None])*((((bb>>i)&1)-.5)[None,:])
            interaction_min=float(ddiag.min())
        elementary=float(np.nextafter(spin_lowers[a]+spin_lowers[b]+interaction_min-1e-12,-math.inf))
        if elementary>best_ritz:
            r={'a':a,'b':b,'lower':elementary,'dimension':math.comb(n,a)*math.comb(n,b),'method':'kinetic-plus-min-interaction'}
        else:
            A=build_block(n,a,b,edges,weights,us)
            if args.certify:
                vals,Q=la.eigh(A.toarray(),overwrite_a=True,check_finite=False,driver='evd')
                r=certify_basis(A,vals,Q);r['method']='full-eigenbasis-residual'
                best_ritz=min(best_ritz,r['ritz'])
                if args.save_basis:
                    np.savez_compressed(out.with_name(out.stem+f'-basis-{a}-{b}.npz'),evals=vals,Q=Q)
            else:
                val=float(sla.eigsh(A,k=1,which='SA',return_eigenvectors=False,tol=1e-10)[0]) if A.shape[0]>2 else float(la.eigvalsh(A.toarray())[0])
                r={'ritz':val,'lower':None,'dimension':A.shape[0],'method':'discovery-eigsh'};best_ritz=min(best_ritz,val)
            r.update(a=a,b=b)
        r['seconds']=time.perf_counter()-tick
        results.append(r)
        print(json.dumps(r),flush=True)
        if r['lower'] is not None:global_low=min(global_low,r['lower'])
        report={'geometry':{'w':args.w,'h':args.h,'periodic_x':args.periodic_x,'periodic_y':args.periodic_y,'sites':sites,'edges':edges},'n':n,'weights':weights.tolist(),'us':us.tolist(),'spin_lower_bounds':spin_lowers,'results':results,'cluster_ritz':best_ritz,'cluster_lower':global_low if args.certify else None,'target_lower':16/n*global_low+32 if args.certify else None,'target_ritz_suggested':16/n*best_ritz+32,'elapsed_seconds':time.perf_counter()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if os.uname().sysname=='Darwin' else 1024),'numerical_model':'IEEE754 binary64 round-to-nearest; standard gamma_k dot-product bounds'}
        out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--w',type=int,default=2);p.add_argument('--h',type=int,default=2);p.add_argument('--periodic-x',action='store_true');p.add_argument('--periodic-y',action='store_true');p.add_argument('--certify',action='store_true');p.add_argument('--save-basis',action='store_true');p.add_argument('--weights');p.add_argument('--output',default='results.json');run(p.parse_args())
