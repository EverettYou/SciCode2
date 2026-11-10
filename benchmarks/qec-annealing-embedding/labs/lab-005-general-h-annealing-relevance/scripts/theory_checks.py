import json,time,itertools,math
from pathlib import Path
import numpy as np
from models import compile_model,complete,EVEN_FLIPS
from thermal import row_log_factor,balanced_row_logs,exact_original_gibbs,row_envelopes
OUT=Path(__file__).resolve().parents[1]/'results'


def energies(model,bits):
    E=np.full(len(bits),model['offset'])
    for i,a in enumerate(model['linear']):E+=a*bits[:,i]
    for i,j,a in model['quadratic']:E+=a*bits[:,i]*bits[:,j]
    return E


def main():
    start=time.perf_counter();records=[]
    # Full row spectra and partition sums, including all hidden/prefix states.
    for d in [1,2,3,4]:
        for s in [0,1]:
            for scheme in ['standard','balanced']:
                model=compile_model([list(range(d))],d,[s],[0.]*d,scheme,penalty=1.)
                N=len(model['linear']);bits=((np.arange(2**N,dtype=np.uint64)[:,None]>>np.arange(N,dtype=np.uint64))&1).astype(np.int16);E=energies(model,bits)
                codes=sum(bits[:,i]*(2**i) for i in range(d));errors=((np.arange(2**d,dtype=np.uint64)[:,None]>>np.arange(d,dtype=np.uint64))&1).astype(np.int16)
                ground=E==0;valid=errors.sum(axis=1)%2==s
                if len(E[ground])!=int(valid.sum()):raise AssertionError('zero-extension multiplicity incorrect')
                if np.any(E[~ground]<1-1e-12):raise AssertionError('minimum nonzero penalty below M')
                for u in [.1,1.,5.,20.]:
                    partition=np.bincount(codes,weights=np.exp(-u*E),minlength=2**d);pred=np.exp(row_log_factor(errors,s,u,scheme))
                    err=float(np.max(abs(partition-pred)))
                    if err>1e-9:raise AssertionError(('row partition mismatch',scheme,d,u,err))
                    if scheme=='balanced' and np.ptp(partition[valid])>1e-10:raise AssertionError('valid-sector entropy not balanced')
                    if scheme=='balanced' and np.ptp(partition[~valid])>1e-10:raise AssertionError('invalid-sector entropy not balanced')
                    records.append({'degree':d,'syndrome':s,'scheme':scheme,'tM':u,'max_partition_error':err,'variables':N})
    # Diverse matrices with dependent rows, negative/zero weights and isolates.
    data={'n':4,'rows':[[0,1,2],[0,1,2],[1,3],[]],'syndrome':[1,1,0,0],'weights':[0.,-.5,.25,.5]}
    for scheme in ['standard','balanced']:
        model=compile_model(data['rows'],4,data['syndrome'],data['weights'],scheme)
        N=len(model['linear']);bits=((np.arange(2**N,dtype=np.uint64)[:,None]>>np.arange(N,dtype=np.uint64))&1).astype(np.int16);E=energies(model,bits)
        orig=bits[:,:4];feas=np.array([all(sum(e[i] for i in row)%2==s for row,s in zip(data['rows'],data['syndrome'])) for e in orig]);cost=orig@np.array(data['weights']);opt=cost[feas].min();gs=(E==E.min())
        if np.any(~feas[gs]) or np.any(cost[gs]!=opt):raise AssertionError('ground-state decoder failure')
        for t in [.5,2.,10.]:
            mass=np.exp(-t*(E-E.min()));mass/=mass.sum();actual=float(mass[feas&(cost==opt)].sum());g=exact_original_gibbs(data,model['penalty'],t,scheme)
            if abs(actual-g['original_optimum_probability'])>1e-11:raise AssertionError('original optimum event mismatch')
    OUT.mkdir(exist_ok=True);result={'status':'pass','row_partition_cases':len(records),'records':records,'elapsed_seconds':time.perf_counter()-start}
    (OUT/'theory_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
