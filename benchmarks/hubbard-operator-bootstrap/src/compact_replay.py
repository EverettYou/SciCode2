#!/usr/bin/env python3
"""Portable construction/replay of the 2257-dimensional Hubbard test space.

Only this directory, NumPy, SciPy, CVXPY and Clarabel are required. No lab
module, full-T2 oracle, or two-site model is imported or loaded.
"""
import argparse,ast,json,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from momentum_pqg import Model,solve
from symmetry_reduce import reduce_variables,q_orbit_representatives

def addto(out,p,scale=1):
    for z,v in p.items():out[z]=out.get(z,0)+scale*v

def cubic_anticommutator(m,t,u):
    a,b,c=t;d,e,f=u;out={}
    val=int(a==d)*int(b==e)-int(a==e)*int(b==d)
    if c==f and val:out[c]=val
    if a==d:addto(out,m.gamma(c,e,f,b),-1)
    if b==d:addto(out,m.gamma(c,e,f,a),1)
    if a==e:addto(out,m.gamma(c,d,f,b),1)
    if b==e:addto(out,m.gamma(c,d,f,a),-1)
    if f==c:addto(out,m.gamma(d,e,a,b),1)
    return {z:v for z,v in out.items() if v}

def raw_prime_block(algebra,ops):
    """Exact integer affine T2' map, cubic anticommutators/linear Gram."""
    n=len(ops);entries=[]
    for i,t in enumerate(ops):
        for j in range(i,n):
            u=ops[j]
            if len(t)==len(u)==3:
                p=cubic_anticommutator(algebra,tuple(a for _,a in t),tuple(a for _,a in u))
            else:
                dt=tuple((1-int(d),a) for d,a in reversed(t))
                p=algebra.poly(dt+tuple((int(d),a) for d,a in u))
            if p:
                entries.append((i,j,p))
                if i!=j:entries.append((j,i,p))
    algebra.block('raw',entries,n);return algebra.blocks.pop()

def build_problem(input_dir):
    start=time.perf_counter();input_dir=Path(input_dir)
    model=Model().build_pqg();full_names=model.names.copy();full_c=model.c.copy()
    stats,T=reduce_variables(model);T=T.astype(np.int64);reps=q_orbit_representatives(model)
    core=[]
    for block in model.blocks:
        name=block['name']
        if name.startswith(('P_','Q_','G_')):
            q,spin=ast.literal_eval(name[2:]);keep=reps[q]==q and spin in(0,1)
        else:
            a=int(name.split('_')[-1]);keep=a<model.V and reps[a]==a
        if keep:core.append(block)
    model.blocks=core;algebra=Model();sources=json.loads((input_dir/'source_blocks.json').read_text())
    for source in sources:
        raw=raw_prime_block(algebra,source['ops']);data=np.load(input_dir/source['projection']);R=data['R_integer'];bits=int(data['denominator_bits'][0]);assert bits==2*source['bits']
        # All products/sums are integer, before exact dyadic scaling.
        assert np.issubdtype(R.dtype,np.integer)
        maxr=max(abs(int(v)) for v in R.ravel())
        assert maxr*maxr<2**63
        assert np.all(raw['A'].data==np.rint(raw['A'].data))
        assert np.all(raw['b']==np.rint(raw['b']))
        K=sp.kron(sp.csr_matrix(R.T),sp.csr_matrix(R.T),format='csr')
        bound=int(np.max(np.abs(K.data)))*float(np.max(np.asarray(abs(raw['A']).sum(axis=0))))
        assert bound<2**62
        intermediate=(K@raw['A'].astype(np.int64)).tocsr()
        expansion_bound=max(abs(int(v)) for v in intermediate.data)*int(np.max(np.asarray(abs(T).sum(axis=0))))
        constant_bound=int(np.max(np.asarray(abs(K).sum(axis=1))))*int(np.max(np.abs(raw['b'])))
        assert expansion_bound<2**63 and constant_bound<2**63
        An=(intermediate@T).tocsr();bn=np.asarray(K@raw['b'].astype(np.int64)).ravel()
        assert np.max(np.abs(An.data))<2**53 and np.max(np.abs(bn))<2**53
        den=2**bits
        model.blocks.append({'name':source['name'],'dim':R.shape[1],'A':An.astype(float)/den,'b':bn/den})
    expected=json.loads((input_dir/'reference_variable_names.json').read_text());assert model.names==expected
    model.construction_sec=time.perf_counter()-start
    return model,{'construction_sec':model.construction_sec,'reduction':stats,'full_names':full_names,'full_objective':full_c,'expansion':T}

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',default=str(Path(__file__).resolve().parent/'input'));p.add_argument('--out',required=True);p.add_argument('--solver',default='CLARABEL');p.add_argument('--eps',type=float,default=1e-9);p.add_argument('--max-iters',type=int,default=100);p.add_argument('--verbose',action='store_true');a=p.parse_args()
    model,stats=build_problem(a.input);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/'full_variable_names.json').write_text(json.dumps(stats.pop('full_names')));np.save(out/'full_objective.npy',stats.pop('full_objective'));sp.save_npz(out/'symmetry_expansion.npz',stats.pop('expansion'))
    (out/'construction.json').write_text(json.dumps(stats,indent=2));print(json.dumps({'phase':'portable_constructed',**stats,'nvar':model.nvar,'ncones':len(model.blocks),'max_dim':max(b['dim'] for b in model.blocks),'entries':sum(b['dim']**2 for b in model.blocks)}),flush=True)
    solve(model,out,a.solver,a.eps,a.max_iters,a.verbose)
if __name__=='__main__':main()
