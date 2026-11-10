from pathlib import Path
import json,time
from models import compile_model
from embedding import graph_from_witness
from numeric_certificate import rational_audit
from relax_chains import relax
OUT=Path(__file__).resolve().parents[1]/'results'

def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];folder=OUT/'relaxation_standard';folder.mkdir(exist_ok=True);rows=[]
    for path in sorted(OUT.glob('*_standard.json')):
        r=json.loads(path.read_text())
        if r['status']!='ok':continue
        emb={int(i):ch for i,ch in r['selected']['embedding'].items()};p=r['selected']['program'];new,stats=relax(p,emb,groups)
        if not new:raise AssertionError(('standard relaxation',r['name'],stats))
        audit=rational_audit(r['model'],new,emb,target,groups)
        if not audit['float_projected_ground_states_certified'] or new['classical_break_bound']>p['epsilon_requested']:raise AssertionError('standard relaxation fidelity')
        obj={'name':r['name'],'input':r['input'],'model':r['model'],'repair_witness':r['repair_witness'],'embedding':emb,
             'before_program':p,'after_program':new,'statistics':stats,'numeric_certificate':audit}
        (folder/(r['name']+'.json')).write_text(json.dumps(obj,indent=2)+'\n');rows.append({'name':r['name'],'statistics':stats})
    (OUT/'standard_relaxation_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
