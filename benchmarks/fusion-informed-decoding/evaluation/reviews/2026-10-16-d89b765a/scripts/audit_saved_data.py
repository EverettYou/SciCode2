"""Reaggregate existing artifacts only; no new physical sampling or phase campaign."""
from pathlib import Path
import json,csv,hashlib
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/home/Downloads/20261014-102308_d89b765a')
out={}

# Every saved GPT1 main study file: means, counts, hard losses and finite range.
d=SOURCE/'openai__gpt-6-astra/run_01';total=0;bad=[];files=0
for p in sorted((d/'data/trials').glob('*.npz')):
    a=np.load(p)['trials'];m=json.loads(p.with_suffix('.json').read_text())
    total+=len(a);files+=1
    ok=(len(a)==m['trials'] and abs(a[:,3].mean()-m['risk'])<1e-12 and
        int(a[:,2].sum())==m['failures'] and int(a[:,4].sum())==m['invalid'])
    valid=a[:,4]==0;q=a[valid,0]
    ok=ok and np.all(np.isfinite(q)) and np.all((q>=0)&(q<=1))
    ok=ok and np.allclose(a[valid,3],np.minimum(q,1-q),atol=1e-12)
    if not ok:bad.append(str(p.relative_to(d)))
out['GPT1']={'files':files,'trials':total,'inconsistencies':bad}

# Every GPT2 planned scientific CSV: audit archived hash and each risk field.
d=SOURCE/'openai__gpt-6-astra/run_02';audit=json.loads((d/'data/run_audit.json').read_text());rows=0;bad=[]
for item in audit['runs']:
    p=d/item['data'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
    with p.open() as f:
        for x in csv.DictReader(f):
            rows+=1
            q=float(x['posterior_zero']);risk=float(x['conditional_risk'])
            if not x['exception'] and (not np.isfinite(q) or not 0<=q<=1 or abs(risk-min(q,1-q))>1e-12):bad.append(rows)
out['GPT2']={'decoder_evaluation_rows':rows,'matching_archived_data_hashes':len(audit['runs']),'inconsistencies':bad}

# Every saved GPT3 main job: direct raw array to sidecar comparison.
d=SOURCE/'openai__gpt-6-astra/run_03';total=0;bad=[];files=0
for p in sorted((d/'data/study').glob('*.npz')):
    a=np.load(p);m=json.loads(p.with_suffix('.json').read_text());files+=1;total+=len(a['posterior'])
    for j,kind in enumerate(m['kinds']):
        z=m['summaries'][kind]
        if abs(a['risk'][:,j].mean()-z['risk'])>1e-12:bad.append(str(p.name)+':risk')
        if abs(a['failure'][:,j].mean()-z['hard_failure_rate'])>1e-12:bad.append(str(p.name)+':failure')
        valid=a['invalid'][:,j]==0;q=a['posterior'][valid,j]
        if not np.allclose(a['risk'][valid,j],np.minimum(q,1-q),atol=1e-12):bad.append(str(p.name)+':posterior')
out['GPT3']={'files':files,'archived_trial_slots':total,'inconsistencies':bad,
             'note':'Includes the 200 conservatively failed reserved slots in the externally terminated batch; these are not evidence that 200 physical trials actually ran.'}
(ROOT/'results/saved-data-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
