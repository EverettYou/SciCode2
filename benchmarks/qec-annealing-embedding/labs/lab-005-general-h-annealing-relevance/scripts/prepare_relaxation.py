from pathlib import Path
import json,time,statistics
from models import compile_model
from evaluator import get_groups
from embedding import graph_from_witness
from numeric_certificate import rational_audit
from relax_chains import relax
from dynamics import certificate
OUT=Path(__file__).resolve().parents[1]/'results'


def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']]
    folder=OUT/'relaxation';folder.mkdir(exist_ok=True);rows=[];start=time.perf_counter()
    for path in sorted(OUT.glob('*_balanced.json')):
        r=json.loads(path.read_text())
        if r['status']!='ok':continue
        emb={int(i):ch for i,ch in r['selected']['embedding'].items()};p=r['selected']['program'];new,stats=relax(p,emb,groups)
        row={'name':r['name'],'statistics':stats}
        if new:
            audit=rational_audit(r['model'],new,emb,target,groups)
            if not audit['float_projected_ground_states_certified']:raise AssertionError(('relax numeric',r['name'],audit))
            if new['classical_break_bound']>p['epsilon_requested']:raise AssertionError('requested chain budget lost')
            before=certificate(r['input'],r['repair_witness'],emb,p);after=certificate(r['input'],r['repair_witness'],emb,new)
            row.update({'before_dynamics':before['strongest'],'after_dynamics':after['strongest'],'numeric_certificate':audit})
            obj={'name':r['name'],'input':r['input'],'model':r['model'],'repair_witness':r['repair_witness'],
                 'embedding':emb,'before_program':p,'after_program':new,'statistics':stats,'numeric_certificate':audit,
                 'before_dynamics':before,'after_dynamics':after}
            (folder/(r['name']+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
        rows.append(row)
    (OUT/'relaxation_summary.json').write_text(json.dumps({'records':rows,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('programs',len(rows))
if __name__=='__main__':main()
