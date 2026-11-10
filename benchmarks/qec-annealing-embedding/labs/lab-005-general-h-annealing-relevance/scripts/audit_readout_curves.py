from pathlib import Path
import json,time
from models import compile_model
from evaluator import evaluate,json_program
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit
from embedding import graph_from_witness,qubo_to_ising
OUT=Path(__file__).resolve().parents[1]/'results'

def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];folder=OUT/'readout_audits';folder.mkdir(exist_ok=True);records=[];start=time.perf_counter()
    for path in sorted(OUT.glob('*_s*_*.json')):
        if not(path.stem.endswith('_balanced') or path.stem.endswith('_standard')):continue
        r=json.loads(path.read_text())
        if r['status']!='ok':continue
        m=r['model'];h,J,c=qubo_to_ising(m['linear'],m['quadratic'],m['offset']);emb={int(i):ch for i,ch in r['selected']['embedding'].items()};curves=[]
        for original in r['thermal_curves']:
            beta=original['beta'];u=evaluate(h,J,c,target,emb,groups=groups,beta=beta);p=allocate_lp(h,J,c,target,emb,u,groups)
            if not p['feasible'] or p['scale']<u['scale']:p=u
            if abs(p['scale']-original['scale'])>1e-12:raise AssertionError('reprogramming not reproducible')
            pw=json_program(p);audit=rational_audit(m,pw,emb,target,groups)
            if not audit['float_projected_ground_states_certified']:raise AssertionError('curve numeric fidelity')
            correction=audit['logical_gibbs_tv_rounding_correction'];bound=min(1.,original['root_readout_tv_bound']+correction)
            curves.append({'beta':beta,'program':pw,'numeric_certificate':audit,'corrected_root_readout_tv_bound':bound})
            records.append({'name':r['name'],'beta':beta,'rounding_tv_correction':correction,'corrected_root_readout_tv_bound':bound})
        (folder/(r['name']+'.json')).write_text(json.dumps({'source_file':path.name,'curves':curves},indent=2)+'\n')
    (OUT/'readout_curve_audit.json').write_text(json.dumps({'status':'pass','records':records,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('audited',len(records))
if __name__=='__main__':main()
