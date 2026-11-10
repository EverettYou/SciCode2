"""Run reviewer-owned records through the submitted public API; no production run."""
from pathlib import Path
import sys,json,time,importlib,traceback
import numpy as np
from independent_oracle import geometry

ROOT=Path(__file__).resolve().parents[1]
run=Path(sys.argv[1]).resolve();sys.path.insert(0,str(run))
module=importlib.import_module('api' if (run/'api.py').exists() else 'solution')
cases=json.loads((ROOT/'results/heldout-cases.json').read_text());out=[]
for case in cases:
    L,p,N,r=[case[k] for k in ['L','p','N','record_type']]
    rec={tuple(v):z for v,z in case['record']}
    if r=='O2':rec={v:(z[0],tuple(z[1])) for v,z in rec.items()}
    row={k:case[k] for k in ['id','L','p','N','record_type','reference','kind']};t=time.monotonic()
    try:
        q=float(module.posterior(L,p,N,r,rec));row['observed']=q if np.isfinite(q) else str(q)
        row['error']=float(abs(q-case['reference'])) if np.isfinite(q) else None
        row['posterior_pass']=bool(np.isfinite(q) and abs(q-case['reference'])<=1e-9)
        if case['kind']=='ordinary':
            correction=module.decode(L,p,N,r,rec,rng=np.random.default_rng(case['id']+120))
            correction={tuple(sorted((tuple(e[0]),tuple(e[1])))) for e in correction}
            E,V=geometry(L);valid=correction.issubset(set(E))
            syn=all(sum(v in e for e in correction)%2==(rec[v] if r=='O0' else rec[v][0]) for v in V)
            label=sum(e[1][1]==L for e in correction)%2
            right=abs(case['reference']-.5)<1e-9 or label==int(case['reference']<.5)
            row['correction_pass']=bool(valid and syn and right)
        else:row['correction_pass']=None
    except Exception as e:
        row.update(posterior_pass=False,exception=repr(e),traceback=traceback.format_exc(limit=3),correction_pass=None)
    row['seconds']=time.monotonic()-t;out.append(row)
    # Preserve incremental results if a verification case stalls.
    (ROOT/'results'/f'{run.parent.name}-{run.name}-checks.json').write_text(json.dumps(out,indent=2)+'\n')
for kind in ['ordinary','endpoint_stress']:
    rr=[x for x in out if x['kind']==kind]
    ee=[x['error'] for x in rr if x.get('error') is not None]
    print(run.parent.name,run.name,kind,len(rr),'posterior passed',sum(x['posterior_pass'] for x in rr),'correction failed',sum(x.get('correction_pass') is False for x in rr),'max error',max(ee,default=None),flush=True)
