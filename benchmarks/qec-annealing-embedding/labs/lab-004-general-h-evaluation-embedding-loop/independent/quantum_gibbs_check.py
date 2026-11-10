"""Independent small-system check of a local Gibbs chain-defect bound.

Dense diagonalization is for validation only. No experimental embedding code is
imported. This is not a model of finite-time D-Wave output.
"""
from pathlib import Path
import json,time,itertools,platform
import numpy as np
from scipy.special import logsumexp

LAB=Path(__file__).resolve().parents[1]

def matrix(n, fields, couplings, gamma):
    dim=1<<n; ids=np.arange(dim);z=2*((ids[:,None]>>np.arange(n))&1)-1
    diag=z@fields
    for (i,j),c in couplings.items():diag+=c*z[:,i]*z[:,j]
    a=np.diag(diag)
    for i,g in enumerate(gamma):a[ids,ids^(1<<i)]-=g
    return a,z

def thermal(a,beta,mask):
    vals,vec=np.linalg.eigh(a)
    logs=-beta*vals; lz=logsumexp(logs)
    p=float((np.abs(vec[mask,:])**2).sum(axis=0)@np.exp(logs-lz))
    return p,float(lz)

def loads_for_root(r,tree,loads,root):
    adj=[[] for _ in range(r)]
    for a,b in tree:adj[a].append(b);adj[b].append(a)
    parent={root:-1};order=[root]
    for q in order:
        for u in adj[q]:
            if u not in parent:parent[u]=q;order.append(u)
    subtotal=loads.copy();f={}
    for q in reversed(order[1:]):
        f[tuple(sorted((q,parent[q])))]=float(subtotal[q]);subtotal[parent[q]]+=subtotal[q]
    return f

def main():
    rng=np.random.default_rng(6161604);out=[];start=time.perf_counter()
    for idx in range(30):
        r=2+idx%3;n=r+2+idx%2
        tree=[(i,i+1) for i in range(r-1)] if idx%2 else [(0,i) for i in range(1,r)]
        fields=rng.uniform(-.3,.3,n);couplings={}
        for i in range(n):
            for j in range(i+1,n):
                if i<r and j<r:continue
                if rng.random()<.65:couplings[i,j]=float(rng.uniform(-.4,.4))
        loads=np.abs(fields[:r]).copy()
        for (i,j),v in couplings.items():
            if i<r:loads[i]+=abs(v)
        root=min(range(r),key=lambda q:max(loads_for_root(r,tree,loads,q).values(),default=0))
        f=loads_for_root(r,tree,loads,root)
        delta={edge:float(rng.uniform(.15,.8)) for edge in f}
        for edge,v in f.items():couplings[edge]=-v-delta[edge]
        gamma=rng.uniform(.05,.6,n);basegamma=gamma.copy();basegamma[:r]=0
        h0,z=matrix(n,fields,couplings,basegamma)
        mask=np.any(z[:,:r]!=z[:,[0]],axis=1)
        for beta in [.5,2.,5.]:
            p0,lz0=thermal(h0,beta,mask)
            classical=1-np.exp(-sum(np.log1p(np.exp(-2*beta*d)) for d in delta.values()))
            assert p0<=classical+2e-12,(idx,beta,p0,classical)
            for scale in [.01,.05,.2]:
                driver=basegamma.copy();driver[:r]=scale
                h,_=matrix(n,fields,couplings,driver)
                p,lz=thermal(h,beta,mask);v=float(driver[:r].sum())
                corr=min(beta*v,float(np.cosh(beta*v)-1))
                upper=min(1.,classical+corr)
                stronger=min(1.,p0+float(np.cosh(beta*v)-1))
                assert lz>=lz0-2e-12,(idx,'partition decrease',lz,lz0)
                assert p<=upper+3e-12 and p<=stronger+3e-12,(idx,beta,scale,p,upper,stronger)
                out.append({'model':idx,'physical_qubits':n,'branch_qubits':r,'beta':beta,'gamma_branch':scale,'p_without_local_driver':p0,'classical_bound':float(classical),'p_quantum':p,'quantum_bound':upper,'local_quantum_correction':corr,'partition_log_ratio':lz-lz0})
    result={'status':'pass','random_models':30,'quantum_parameter_cases':len(out),'maximum_qubits':max(x['physical_qubits'] for x in out),'nonvacuous_cases':int(sum(x['quantum_bound']<1 for x in out)),'maximum_observed_minus_bound':max(x['p_quantum']-x['quantum_bound'] for x in out),'seconds':time.perf_counter()-start,'numpy':np.__version__,'python':platform.python_version(),'records':out,'interpretation':'Exact dense quantum Gibbs validation of the derived local-bound inequalities; no annealing dynamics or hardware output inferred.'}
    p=LAB/'results/independent_quantum_gibbs_check.json';p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
