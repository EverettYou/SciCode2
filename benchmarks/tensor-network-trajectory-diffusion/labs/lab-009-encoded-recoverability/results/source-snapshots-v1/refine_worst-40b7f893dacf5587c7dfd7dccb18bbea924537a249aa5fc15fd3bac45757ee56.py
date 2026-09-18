"""Refine the largest weighted certificate gap; preserve the original run."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import cvxpy as cp
import numpy as np
from physical import objectives
from certificates import repair, verify


def run(source,output):
    start=time.perf_counter();source=Path(source);output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    s=json.loads((source/'summary.json').read_text())
    row=max(s['rows'],key=lambda r:r['weight']*r['gap'])
    n=s['n'];d=2**n;key=tuple(row['record']);c=objectives(n,s['g'],s['eta'])[key]
    weight=float(np.trace(c).real);cn=c/weight;r=min(d,2**(key.count(0)+1))
    _,q=np.linalg.eigh(cn[:d,:d]+cn[d:,d:]);q=q[:,-r:];w=np.kron(np.eye(2),q)
    cr=w.conj().T@cn@w
    j=cp.Variable((2*r,2*r),hermitian=True);con=j[:r,:r]+j[r:,r:]==np.eye(r)
    problem=cp.Problem(cp.Maximize(cp.real(cp.trace(cr@j))),[j>>0,con])
    problem.solve(solver='SCS',eps=1e-8,max_iters=20000)
    if j.value is None:raise RuntimeError(problem.status)
    raw_j=w@j.value@w.conj().T;raw_j[:d,:d]+=np.eye(d)-q@q.conj().T
    raw_y=q@con.dual_value@q.conj().T
    cert=repair(cn,raw_j,raw_y);result=verify(cn,cert)
    if result['gap']>=row['gap']:raise RuntimeError('refinement did not improve gap')
    for old in source.glob('branch-*.npz'):
        if old.name!=row['certificate']:os.link(old,output/old.name)
    np.savez_compressed(output/row['certificate'],**cert,raw_j=raw_j,raw_y=raw_y,record=key)
    previous=dict(row)
    row.update(result,status=problem.status,iterations=problem.solver_stats.num_iters,
               local_eps=1e-8,max_iters=20000,seconds=time.perf_counter()-start)
    s.update(lower=sum(x['weight']*x['lower'] for x in s['rows']),
             upper=sum(x['weight']*x['upper'] for x in s['rows']))
    s['gap']=s['upper']-s['lower'];s['solver']='SCS-adaptive-plus-targeted-refinement'
    s['refinement']=dict(previous_run=str(source),record=key,previous_branch=previous,
                         seconds=time.perf_counter()-start)
    s['seconds']+=s['refinement']['seconds']
    s['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
    (output/'summary.json').write_text(json.dumps(s,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:s[k] for k in ['n','lower','upper','gap','seconds','refinement']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('output')
    a=p.parse_args();run(a.source,a.output)
