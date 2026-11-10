from pathlib import Path
import json,hashlib
import numpy as np
from independent_oracle import reference,brute,sample_record,force_active_record

ROOT=Path(__file__).resolve().parents[1]
rng=np.random.default_rng(202610160314)
cases=[];brute_errors=[]
for L,ps in [(2,[.03,.25,.5,.79,.97]),(3,[.11,.43,.88]),(4,[.23,.67])]:
    for N in range(2,9):
        for p in ps:
            records=sample_record(L,p,N,rng)
            for r,rec in records.items():
                q=reference(L,p,N,r,rec)
                if L==2 and p==.43:raise AssertionError
                if L==2 and p==.25:
                    qb=brute(L,p,N,r,rec);brute_errors.append(abs(q-qb));assert abs(q-qb)<1e-12
                cases.append(dict(id=len(cases),L=L,p=p,N=N,record_type=r,record=[[list(v),z] for v,z in rec.items()],reference=q,kind='ordinary'))
for L in [2,3,4]:
    for p in [1e-180,1e-310,float.fromhex('0x0.0000000000001p-1022')]:
        for r in ['O1','O2']:
            rec=force_active_record(L,8,r)
            cases.append(dict(id=len(cases),L=L,p=p,N=8,record_type=r,record=[[list(v),z] for v,z in rec.items()],reference=float(L%2==0),kind='endpoint_stress'))
(ROOT/'results').mkdir(parents=True,exist_ok=True)
(ROOT/'results/heldout-cases.json').write_text(json.dumps(cases,indent=2)+'\n')
summary=dict(seed=202610160314,cases=len(cases),ordinary=sum(c['kind']=='ordinary' for c in cases),endpoint_stress=18,independent_L2_brute_comparisons=len(brute_errors),max_reference_brute_difference=max(brute_errors))
(ROOT/'results/oracle-check.json').write_text(json.dumps(summary,indent=2)+'\n')
print(summary)
