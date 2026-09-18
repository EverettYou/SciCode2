"""Apply saved recovery Kraus operators to joint reference/physical states.

This check uses neither C objectives nor the SDP trace formula.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from physical import effective_kraus


def check(directory):
    directory=Path(directory);s=json.loads((directory/'summary.json').read_text())
    n,g,eta=s['n'],s['g'],s['eta'];maps=effective_kraus(n,g,dense=True)
    phi=np.array([1,0,0,1],complex)/np.sqrt(2);rho=np.zeros((4,4),complex)
    clipped_negative_mass=0.
    for row in s['rows']:
        c=row['record'];m=c.count(0);weight=eta**(n-m)*(1-eta)**m
        with np.load(directory/row['certificate'],allow_pickle=False) as data:j=data['j']
        vals,vecs=np.linalg.eigh((j+j.conj().T)/2)
        clipped_negative_mass+=float(np.abs(vals[vals<0]).sum())*weight
        for k,val in enumerate(vals):
            if val<=0:continue
            r=(vecs[:,k]*np.sqrt(val)).reshape(2,2**n)
            recovery=np.kron(np.eye(2),r)
            for outcome,a in maps.items():
                if not all(x==0 or x==y for x,y in zip(c,outcome)):continue
                bell=a.T.reshape(-1)/np.sqrt(2)
                restored=recovery@bell
                rho+=weight*np.outer(restored,restored.conj())
    fidelity=float(np.vdot(phi,rho@phi).real)
    residual=float(abs(np.trace(rho)-1))
    difference=abs(fidelity-s['lower'])
    if residual>1e-10 or difference>1e-10:raise ValueError('explicit recovery action disagrees')
    return dict(n=n,g=g,eta=eta,fidelity=fidelity,reported_lower=s['lower'],
                difference=difference,trace_residual=residual,
                clipped_negative_choi_mass=clipped_negative_mass,
                status='explicit-Bell-recovery-action-passed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directories',nargs='+');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();rows=[check(d) for d in a.directories]
    with a.output.open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
    print(json.dumps(rows,indent=2))
