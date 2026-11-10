"""Outward actual-program readout comparisons; auxiliary excitations count."""
from pathlib import Path
from fractions import Fraction as F
import json,math,time,sys
sys.dont_write_bytecode=True
from balanced_intervals import interval_mass as balanced_mass,self_check
from penalty_bound import load_module
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'));sys.path.insert(0,str(LAB.parent/'lab-002-agent-test-general-h/scripts'))
from embedding import graph_from_witness
from numeric_certificate import rational_audit
standard=load_module('prior_standard_positive_intervals',OLD/'independent/logical_gibbs_intervals.py')
ia=load_module('prior_actual_readout_audit',OLD/'independent/audit_programs.py')
def main():
 start=time.perf_counter();check=self_check();td=json.loads((LAB/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];records=[]
 for path in sorted((LAB/'results/readout_audits').glob('*_n16_*.json')):
  curves=json.loads(path.read_text());d=json.loads((LAB/'results'/path.name).read_text());emb={int(i):v for i,v in d['selected']['embedding'].items()}
  for row in curves['curves']:
   p=row['program'];entry={'embedding':emb,'program':p};datum={**d,'selected':{'first':entry}};audit=ia.audit(datum,'outward_readout',entry,target,groups);exact=rational_audit(d['model'],p,emb,target,groups);assert exact['float_projected_ground_states_certified']
   inp=d['input'];mass=(balanced_mass if d['scheme']=='balanced' else standard.interval_mass)(inp['rows'],inp['n'],inp['syndrome'],inp['weights'],F(d['model']['penalty']),F(p['beta'])*F(p['scale']))
   tv=audit['thermal_rounding_tv_upper'];defect=audit['classical_defect_upper'];lower=max(0.,math.nextafter((1-defect)*max(0.,mass['decoded_error_lower']-tv),-math.inf));upper=min(1.,math.nextafter(mass['decoded_error_upper']+tv+defect,math.inf))
   ref=next(c for c in d['thermal_curves'] if c['beta']==row['beta'])['exact_reference']['original_optimum_probability'];assert mass['decoded_error_lower']<=ref+1e-12 and mass['decoded_error_upper']>=ref-1e-12
   records.append({'name':d['name'],'scheme':d['scheme'],'beta':row['beta'],'mass':mass,'chain_defect_upper':defect,'rounding_tv_upper':tv,'actual_root_error_lower':lower,'actual_root_error_upper':upper,'independent_actual_audit':audit,'exact_static_audit':exact})
  print(json.dumps({'name':d['name'],'finished':len(records)}),flush=True)
 pairs=[]
 for row in records:
  if row['scheme']!='balanced':continue
  base=next(r for r in records if r['name']==row['name'].replace('_balanced','_standard') and r['beta']==row['beta'])
  pairs.append({'name':row['name'].replace('_balanced',''),'beta':row['beta'],'strict_balanced_actual_error_order':row['actual_root_error_lower']>base['actual_root_error_upper'],'strict_standard_actual_error_order':base['actual_root_error_lower']>row['actual_root_error_upper']})
 summary={str(b):{'comparisons':len([r for r in pairs if r['beta']==b]),'balanced_strict_orders':sum(r['strict_balanced_actual_error_order'] for r in pairs if r['beta']==b),'standard_strict_orders':sum(r['strict_standard_actual_error_order'] for r in pairs if r['beta']==b)} for b in sorted({r['beta'] for r in pairs})}
 out={'status':'pass','self_check':check,'summary':summary,'records':records,'comparisons':pairs,'seconds':time.perf_counter()-start,'interpretation':'Outward interval terminal Gibbs original-error comparisons for actual binary64 programs; all auxiliary and chain excitations allowed in the event. No finite-time equilibration or quantum dynamical claim.'}
 (LAB/'results/independent_readout_intervals.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['records','comparisons','self_check']}))
if __name__=='__main__':main()
