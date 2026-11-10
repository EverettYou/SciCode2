#!/usr/bin/env python3
"""Test if a fixed global two-RDM point admits the shared cubic Gram extension."""
import argparse,json,pickle,sys,time,resource,os
from pathlib import Path
import numpy as np
import cvxpy as cp
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lab-002-moment-sdp'/'scripts'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('model');ap.add_argument('global_primal');ap.add_argument('out');args=ap.parse_args()
    start=time.perf_counter();inp=Path(args.model);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    with (inp/'model_cache.pkl').open('rb') as f:m=pickle.load(f)
    g=np.load(args.global_primal);ng=len(g);x=cp.Variable(m.nvar-ng);slack=cp.Variable(nonneg=True);cons=[x<=1,x>=-1]
    E=m.eqmatrix();e=np.array(m.rhs);rows=np.array([name.startswith('X_') for name in m.eqnames])
    er=(E[rows,ng:]@x+E[rows,:ng]@g-e[rows])/256
    cons.extend([er<=slack,er>=-slack])
    selected=[b for b in m.blocks if b['name'].startswith('true_density_')]
    for b in selected:
        M=cp.reshape((b['A'][:,ng:]@x+b['A'][:,:ng]@g+b['b'])/256,(b['dim'],b['dim']),order='C')
        cons.append(M+slack*np.eye(b['dim'])>>0)
    prob=cp.Problem(cp.Minimize(slack),cons)
    prob.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=100,max_threads=1)
    result=dict(status=prob.status,seconds=time.perf_counter()-start,nextra=m.nvar-ng,number_of_gram_cones=len(selected),max_gram_dimension=max(b['dim'] for b in selected))
    if x.value is not None:
        result['optimal_uniform_cone_and_equality_slack']=float(slack.value)
        y=np.r_[g,x.value];np.save(out/'extended_primal.npy',y)
        result['unscaled_contraction_error']=float(np.max(np.abs((E[rows]@y-e[rows])/256)))
        result['unscaled_min_gram_eigenvalue']=min(float(np.linalg.eigvalsh((b['A']@y+b['b']).reshape(b['dim'],b['dim'])/256)[0]) for b in selected)
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result['peak_rss_bytes']=rss
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
