#!/usr/bin/env python3
"""Refine an exported SDP with primal, dual, and slack SCS warm starts."""
import argparse,json,pickle,sys,shutil,time
from pathlib import Path
import numpy as np
import cvxpy as cp
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import solve

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('out');ap.add_argument('--eps',type=float,default=1e-7);ap.add_argument('--max-iters',type=int,default=5000);args=ap.parse_args()
    inp=Path(args.input);out=Path(args.out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    with (inp/'model_cache.pkl').open('rb') as f:m=pickle.load(f)
    x=cp.Variable(m.nvar);cons=[]
    for b in m.blocks:
        M=cp.reshape(b['A']@x+b['b'],(b['dim'],b['dim']),order='C');cons.append(M>>0)
    E=m.eqmatrix();e=np.array(m.rhs);eq=E@x==e;cons.append(eq)
    prob=cp.Problem(cp.Minimize(m.c@x),cons)
    data,chain,inverse=prob.get_problem_data(cp.SCS)
    yparts=[np.load(inp/'lambda.npy')];expected=m.c+E.T@yparts[0]
    for b,meta in zip(m.blocks,json.loads((inp/'blocks.json').read_text())):
        Y=np.load(inp/(meta['prefix']+'.npz'))['dual'];idx=np.triu_indices(b['dim'])
        packed=Y[idx].copy();packed[idx[0]!=idx[1]]*=np.sqrt(2);yparts.append(packed)
        expected-=b['A'].T@Y.ravel()
    warmx=np.load(inp/'primal.npy');warmy=np.concatenate(yparts);warms=data['b']-data['A']@warmx
    error=float(np.max(np.abs(data['c']+data['A'].T@warmy-expected)))
    assert error<1e-9,error
    assert data['A'].shape==(len(warmy),len(warmx))
    prob._solver_cache['SCS']={'x':warmx,'y':warmy,'s':warms}
    for name in ['symmetry_expansion.npz','full_variable_names.json','full_objective.npy','source_operator_blocks.json','projection_descriptors.json','construction.json']:
        if (inp/name).exists():shutil.copyfile(inp/name,out/name)
    for path in inp.glob('projection_*.npz'):shutil.copyfile(path,out/path.name)
    print(json.dumps(dict(warm_start_dual_mapping_max_error=error,preparation_seconds=time.perf_counter()-start)),flush=True)
    result=solve(m,out,'SCS',args.eps,args.max_iters,True,prebuilt=(prob,x,cons,eq),warm_start=True)
    result['warm_start_source']=str(inp.resolve());result['warm_start_dual_mapping_max_error']=error
    (out/'result.json').write_text(json.dumps(result,indent=2))
    with (out/'model_cache.pkl').open('wb') as f:pickle.dump(m,f)
if __name__=='__main__':main()
