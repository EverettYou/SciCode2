"""Support-reduced SDP, lifted and repaired in full physical space for verification."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import resource
import time
import cvxpy as cp
import numpy as np
from physical import objectives, full_record_formula
from certificates import repair, verify


def run(n,g,eta,output,eps=1e-9):
    start=time.perf_counter();output=Path(output);output.mkdir(parents=True,exist_ok=False)
    cs=objectives(n,g,eta);d=2**n;problems={};rows=[]
    for i,(record,c) in enumerate(cs.items()):
        weight=float(np.trace(c).real);cn=c/weight
        r=min(d,2**(record.count(0)+1))
        marginal=cn[:d,:d]+cn[d:,d:]
        eig,basis=np.linalg.eigh(marginal);q=basis[:,-r:]
        w=np.kron(np.eye(2),q)
        cr=w.conj().T@cn@w
        trunc=float(np.linalg.norm(cn-w@cr@w.conj().T,'fro'))
        if r not in problems:
            par=cp.Parameter((2*r,2*r),hermitian=True)
            j=cp.Variable((2*r,2*r),hermitian=True)
            con=j[:r,:r]+j[r:,r:]==np.eye(r)
            prob=cp.Problem(cp.Maximize(cp.real(cp.trace(par@j))),[j>>0,con])
            problems[r]=(par,j,con,prob)
        par,j,con,prob=problems[r];par.value=(cr+cr.conj().T)/2
        t=time.perf_counter()
        prob.solve(solver='SCS',eps=eps,max_iters=100000,warm_start=False)
        if j.value is None:raise RuntimeError(prob.status)
        raw_j=w@j.value@w.conj().T
        raw_j[:d,:d]+=np.eye(d)-q@q.conj().T
        raw_y=q@con.dual_value@q.conj().T
        # Full-space repair counts all projection/roundoff residuals. No
        # support-truncation assumption is required by the saved verifier.
        cert=repair(cn,raw_j,raw_y);result=verify(cn,cert)
        name=f'branch-{i:04d}.npz'
        np.savez_compressed(output/name,**cert,raw_j=raw_j,raw_y=raw_y,record=record)
        rows.append(dict(record=list(record),weight=weight,certificate=name,status=prob.status,
                         support=r,projection_residual=trunc,solver_value=float(prob.value),
                         seconds=time.perf_counter()-t,iterations=prob.solver_stats.num_iters,**result))
        (output/'progress.json').write_text(json.dumps(dict(n=n,g=g,eta=eta,completed=len(rows),
                 total=len(cs),elapsed_seconds=time.perf_counter()-start),indent=2)+'\n')
        if i==0 or (i+1)%50==0:
            print(json.dumps(dict(n=n,completed=i+1,total=len(cs),seconds=time.perf_counter()-start,
                       max_gap=max(x['gap'] for x in rows))),flush=True)
    lo=sum(x['weight']*x['lower'] for x in rows);hi=sum(x['weight']*x['upper'] for x in rows)
    result=dict(n=n,g=g,eta=eta,solver='SCS-support-reduced',eps=eps,lower=lo,upper=hi,gap=hi-lo,
                seconds=time.perf_counter()-start,rows=rows,full_record_formula=full_record_formula(n,g),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                versions=dict(python=platform.python_version(),numpy=np.__version__,cvxpy=cp.__version__),
                source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
                lock_sha256=hashlib.sha256((Path(__file__).parent.parent/'uv.lock').read_bytes()).hexdigest(),
                numerical_scope='Full-space residual-repaired numerical bounds; no interval arithmetic')
    (output/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['n','g','eta','lower','upper','gap','seconds']}),flush=True)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--n',type=int,required=True)
    p.add_argument('--g',type=float,required=True);p.add_argument('--eta',type=float,default=.75)
    p.add_argument('--eps',type=float,default=1e-9);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.n,a.g,a.eta,a.output,a.eps)
