import json,time
from pathlib import Path
import numpy as np
from models import compile_model
from repair_api import REPAIR
from repair_followup import rescale_balanced
OUT=Path(__file__).resolve().parents[1]/'results'

def main():
    start=time.perf_counter();records=[]
    for seed in range(12):
        rng=np.random.default_rng(seed);n=4;rows=[[0,1,2],[1,2,3]];truth=rng.integers(0,2,n);s=[int(sum(truth[i] for i in row)%2) for row in rows];w=[0.,float(rng.integers(-2,6))/4,1.25,-.5]
        wit=REPAIR.witness(rows,n,w)
        for scheme in ['standard','balanced']:
            if scheme=='standard':m=REPAIR.compile_with_bound(rows,n,s,w,wit)
            else:m=rescale_balanced(compile_model(rows,n,s,w,'balanced'),wit)
            N=len(m['linear']);bits=((np.arange(2**N,dtype=np.uint64)[:,None]>>np.arange(N,dtype=np.uint64))&1).astype(np.int16);E=np.full(len(bits),m['offset'])
            for i,a in enumerate(m['linear']):E+=a*bits[:,i]
            for i,j,a in m['quadratic']:E+=a*bits[:,i]*bits[:,j]
            valid=np.ones(len(bits),dtype=bool)
            for row,ss in zip(rows,s):valid&=(bits[:,row].sum(axis=1)%2==ss)
            cost=bits[:,:n]@np.array(w);optimum=cost[valid].min();ground=np.isclose(E,E.min(),atol=1e-12,rtol=0)
            if np.any(~valid[ground]) or np.any(cost[ground]!=optimum):raise AssertionError('repair compiler ground-state failure')
            gap=float((E[~ground]-E.min()).min());claimed=m['numeric_certificate']['nonoptimal_gap_lower_bound_exact'];claimed=claimed[0]/claimed[1]
            if gap+1e-12<claimed:raise AssertionError('repair compiler gap failure')
            records.append({'seed':seed,'scheme':scheme,'penalty':m['penalty'],'global_weight_L1':sum(map(abs,w)),
                            'actual_gap':gap,'claimed_gap':claimed,'variables':N})
    (OUT/'repair_compiler_checks.json').write_text(json.dumps({'status':'pass','records':records,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('checked',len(records))
if __name__=='__main__':main()
