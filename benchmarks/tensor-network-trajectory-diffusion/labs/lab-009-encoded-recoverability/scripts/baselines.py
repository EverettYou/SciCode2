"""No-training/no-SDP transpose-recovery baseline and full-record upper bound."""
import argparse
import itertools
import json
import time
from pathlib import Path
import numpy as np
from physical import effective_kraus


def evaluate(n,g,eta=.75):
    start=time.perf_counter();maps=effective_kraus(n,g);d=2**n
    lower=upper=0.;max_residual=0.;rows=[]
    for c in itertools.product((-1,0,1),repeat=n):
        missing=c.count(0);weight=eta**(n-missing)*(1-eta)**missing
        if weight==0:continue
        ops=[a for s,a in maps.items() if all(x==0 or x==y for x,y in zip(c,s))]
        t=sum(a@a.conj().T for a in ops)
        w,u=np.linalg.eigh(t);cut=1e-12*max(w.max(),1e-30)
        factors=np.zeros_like(w);keep=w>cut;factors[keep]=1/np.sqrt(w[keep])
        inverse=(u*factors)@u.conj().T
        recoveries=[a.conj().T@inverse for a in ops]
        # Normalize CP map to trace-nonincreasing with an explicit upper bound,
        # then complete by reset. This remains valid even after rank cutoff.
        tp=sum(r.conj().T@r for r in recoveries)
        tw,tq=np.linalg.eigh((tp+tp.conj().T)/2)
        reconstruction=(tq*tw)@tq.conj().T
        residual_bound=float(np.linalg.norm(tp-reconstruction,'fro'))
        orth=float(np.linalg.norm(tq.conj().T@tq-np.eye(d),'fro'))
        scale=max(1.,float(tw.max())*(1+orth)+residual_bound)+1e-12
        residual=np.eye(d)-tp/scale
        contribution=sum(abs(np.trace(r@a))**2 for r in recoveries for a in ops)/(4*scale)
        # Completion resets to logical |0>; its fidelity contribution is
        # sum_h <0| A_h^dagger residual A_h |0>/4.
        contribution+=sum(np.vdot(a[:,0],residual@a[:,0]).real for a in ops)/4
        informed=sum(np.linalg.svd(a,compute_uv=False).sum()**2/4 for a in ops)
        lower+=weight*contribution;upper+=weight*informed
        minres=float(np.linalg.eigvalsh(residual).min());max_residual=max(max_residual,-minres)
        rows.append(dict(record=list(c),weight=weight,lower=float(contribution),
                         upper=float(informed),scale=scale,rank=int(keep.sum())))
    return dict(n=n,g=g,eta=eta,lower=lower,upper=upper,gap=upper-lower,
                seconds=time.perf_counter()-start,max_negative_completion_eigenvalue=max_residual,
                method='transpose recovery with explicit TP completion; full-record analytic upper',rows=rows)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--sizes',type=int,nargs='+',default=[2,4,6]);a=p.parse_args()
    rows=[]
    for n in a.sizes:
        for g in [.2,.5,.8]:
            r=evaluate(n,g);rows.append(r)
            print(json.dumps({k:v for k,v in r.items() if k!='rows'}),flush=True)
    with a.output.open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
