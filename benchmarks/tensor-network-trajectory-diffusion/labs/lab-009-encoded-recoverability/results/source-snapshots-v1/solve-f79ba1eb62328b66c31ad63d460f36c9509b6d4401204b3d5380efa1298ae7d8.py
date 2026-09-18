"""All-record exact dense recovery SDP with saved independently checkable certificates."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import time

import cvxpy as cp
import numpy as np

from physical import objectives, full_record_formula
from certificates import repair, verify


def run(n,g,eta,output,solver='SCS',eps=1e-10):
    start=time.perf_counter()
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    cs=objectives(n,g,eta)
    d=2**n
    cpar=cp.Parameter((2*d,2*d),hermitian=True)
    j=cp.Variable((2*d,2*d),hermitian=True)
    trace_constraint=j[:d,:d]+j[d:,d:]==np.eye(d)
    prob=cp.Problem(cp.Maximize(cp.real(cp.trace(cpar@j))),[j >> 0,trace_constraint])
    rows=[]
    for i,(record,c) in enumerate(cs.items()):
        weight=float(np.trace(c).real)
        cn=c/weight
        cpar.value=cn
        t=time.perf_counter()
        if solver=='SCS':
            prob.solve(solver=solver,eps=eps,max_iters=100000,warm_start=False)
        else:
            prob.solve(solver=solver,tol_gap_abs=eps,tol_gap_rel=eps,tol_feas=eps,max_iter=200)
        if j.value is None or trace_constraint.dual_value is None:
            raise RuntimeError(f'{record}: {prob.status}')
        cert=repair(cn,j.value,trace_constraint.dual_value)
        result=verify(cn,cert)
        name=f'branch-{i:04d}.npz'
        np.savez_compressed(output/name,**cert,raw_j=j.value,raw_y=trace_constraint.dual_value,
                            record=record)
        rows.append(dict(record=list(record),weight=weight,certificate=name,status=prob.status,
                         solver_value=float(prob.value),seconds=time.perf_counter()-t,
                         iterations=prob.solver_stats.num_iters,**result))
        (output/'progress.json').write_text(json.dumps(dict(n=n,g=g,eta=eta,completed=len(rows),
                           total=len(cs),elapsed_seconds=time.perf_counter()-start),indent=2)+'\n')
        if i==0 or (i+1)%10==0:
            print(json.dumps(dict(n=n,g=g,eta=eta,completed=i+1,total=len(cs),
                       seconds=time.perf_counter()-start,max_gap=max(r['gap'] for r in rows))),flush=True)
    lower=sum(r['weight']*r['lower'] for r in rows)
    upper=sum(r['weight']*r['upper'] for r in rows)
    summary=dict(n=n,g=g,eta=eta,solver=solver,eps=eps,lower=lower,upper=upper,gap=upper-lower,
                 seconds=time.perf_counter()-start,peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                 full_record_formula=full_record_formula(n,g),rows=rows,
                 numerical_scope='Explicit residual-repaired double-precision bounds; not interval-arithmetic proof',
                 versions=dict(python=platform.python_version(),numpy=np.__version__,cvxpy=cp.__version__),
                 threads={k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},
                 source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
                 lock_sha256=hashlib.sha256((Path(__file__).parent.parent/'uv.lock').read_bytes()).hexdigest())
    (output/'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k in ['n','g','eta','solver','lower','upper','gap','seconds']}),flush=True)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--n',type=int,required=True);p.add_argument('--g',type=float,required=True)
    p.add_argument('--eta',type=float,required=True);p.add_argument('--output',required=True)
    p.add_argument('--solver',choices=['SCS','CLARABEL'],default='SCS')
    p.add_argument('--eps',type=float,default=1e-10)
    a=p.parse_args();run(a.n,a.g,a.eta,a.output,a.solver,a.eps)
