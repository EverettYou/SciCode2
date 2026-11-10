from pathlib import Path
from fractions import Fraction as F
import sys,json,time,statistics
sys.dont_write_bytecode=True
from forward_certificate import cost_moments,amplify,certificate
from penalty_bound import load_module
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'))
from numeric_certificate import rational_audit
from embedding import graph_from_witness
OUT=LAB/'results/forward_ordinary';OUT.mkdir(exist_ok=True)
def main():
    start=time.perf_counter();td=json.loads((OLD/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];rows=[]
    for path in sorted((LAB/'results/penalty').glob('*.json')):
        data=json.loads(path.read_text())
        if data['status']!='ok':continue
        inp=data['input'];st=time.perf_counter();moments=cost_moments(inp['rows'],inp['n'],inp['syndrome'],inp['weights'],data['repair_witness']);moments_seconds=time.perf_counter()-st
        base=data['selected']['global_first'];eta=F(base['program']['scale'])*F(data['models']['global']['penalty'])/F(data['models']['repair']['penalty'])
        p,parameters=amplify(base['program'],inp['weights'],eta);st=time.perf_counter();bound=certificate(moments,parameters);bound_seconds=time.perf_counter()-st
        emb={int(i):v for i,v in base['embedding'].items()};audit=rational_audit(data['models']['repair'],p,emb,target,groups);assert audit['float_projected_ground_states_certified'],data['name']
        record={'name':data['name'],'input':inp,'embedding':emb,'baseline_program':base['program'],'amplified_program':p,'moments':moments,
         'parameters':{k:[v.numerator,v.denominator] for k,v in parameters.items()},'certificate':bound,'static_audit':audit,'moments_seconds':moments_seconds,'bound_seconds':bound_seconds}
        (OUT/path.name).write_text(json.dumps(record,indent=2)+'\n')
        rows.append({'name':data['name'],'n':inp['n'],'physical_spins':len(p['h']),'split':inp['split'],'status':bound['status'],'duration':bound.get('duration'),
          'relative_advantage_lower':bound.get('relative_probability_advantage_lower'),'moment_seconds':moments_seconds,'certificate_seconds':bound_seconds})
    good=[r for r in rows if r['status']=='strict_finite_forward_order'];out={'status':'pass','instances':len(rows),'strict_finite_orders':len(good),
      'certified_duration_min':min(r['duration'] for r in good),'certified_duration_max':max(r['duration'] for r in good),'certified_duration_median':statistics.median(r['duration'] for r in good),
      'median_moments_seconds':statistics.median(r['moment_seconds'] for r in rows),'median_bound_seconds':statistics.median(r['certificate_seconds'] for r in rows),
      'seconds':time.perf_counter()-start,'records':rows,'interpretation':'Rigorous standard-initial-state finite-forward orders on ordinary H at very conservative short durations. No useful moderate-time or large-time order inferred.'}
    (LAB/'results/forward_ordinary_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
