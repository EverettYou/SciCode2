"""Exact reference Gibbs mass: enumerate original errors, sum row auxiliaries."""
import json,math,time
from pathlib import Path
import numpy as np
from run_suite import OUT,save


def logical_gibbs(data,penalty,t):
    n=data['n'];states=((np.arange(2**n,dtype=np.uint64)[:,None]>>np.arange(n,dtype=np.uint64))&1).astype(np.int8)
    cost=states@np.array(data['weights']);feasible=np.ones(len(states),dtype=bool)
    factors=np.ones(len(states))
    for support,s in zip(data['rows'],data['syndrome']):
        d=len(support);feasible&=(states[:,support].sum(axis=1)%2==s)
        if d==0:
            if s:factors*=math.exp(-t*penalty)
        elif d==1:factors*=np.exp(-t*penalty*(states[:,support[0]]-s)**2)
        elif d==2:factors*=np.exp(-t*penalty*((states[:,support[0]]^states[:,support[1]])!=s))
        else:
            prev=states[:,support[0]];f0=(prev==0).astype(float);f1=(prev==1).astype(float)
            for col in support[1:-1]:
                x=states[:,col];new=[]
                for p in [0,1]:
                    a0=sum(np.exp(-t*penalty*(x-p-2*a)**2) for a in [0,1])
                    a1=sum(np.exp(-t*penalty*(1+x-p-2*a)**2) for a in [0,1])
                    new.append(f0*a0+f1*a1)
                f0,f1=new
            x=states[:,support[-1]]
            factors*=f0*np.exp(-t*penalty*(x!=s))+f1*np.exp(-t*penalty*((1^x)!=s))
    optimum=float(cost[feasible].min());optimal=feasible&(cost==optimum)
    weights=np.exp(-t*(cost-cost.min()))*factors
    partition=float(weights.sum());groundmass=int(optimal.sum())*math.exp(-t*(optimum-cost.min()))/partition
    distribution=weights/partition
    return {'ground_probability':groundmass,'projected_optimum_probability':float(distribution[optimal].sum()),'ground_degeneracy':int(optimal.sum()),'optimum':optimum,
            'feasible_errors':int(feasible.sum()),'ground_mask':optimal,'distribution':distribution,
            'log_partition':math.log(partition)-t*float(cost.min())}


def main():
    start=time.perf_counter();records=[]
    for path in sorted(OUT.glob('*_n16_s*.json')):
        r=json.loads(path.read_text());data=r['input'];row={'name':r['name'],'split':data['split'],'scores':{}}
        for label in ['first','guided_pool','guided_pruned','size_only_pool']:
            p=r['selected'][label]['program'];g=logical_gibbs(data,r['model']['penalty'],20*p['scale'])
            row['scores'][label]={k:v for k,v in g.items() if k not in ('ground_mask','distribution')}
            row['scores'][label]['scale']=p['scale'];row['scores'][label]['qubits']=p['physical_qubits']
        if row['scores']['guided_pruned']['ground_probability']+1e-12<row['scores']['first']['ground_probability']:
            raise AssertionError('conditional Gibbs monotonicity violation')
        records.append(row)
    result={'records':records,'elapsed_seconds':time.perf_counter()-start,
            'reference_only':True,'construction_used_reference_solution':False}
    save(OUT/'logical_gibbs_validation.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
