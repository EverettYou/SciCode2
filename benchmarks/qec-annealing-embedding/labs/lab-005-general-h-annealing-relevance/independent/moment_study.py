from pathlib import Path
from fractions import Fraction as F
import json,time,statistics,sys
sys.dont_write_bytecode=True
from forward_certificate import cost_moments
from forward_moments import evaluate_moments
LAB=Path(__file__).resolve().parents[1]
def main():
 records=[];start=time.perf_counter()
 for path in sorted((LAB/'results').glob('*_n*_s*_standard.json'))+sorted((LAB/'results').glob('*_n*_s*_balanced.json')):
  d=json.loads(path.read_text())
  if 'selected' not in d:continue
  p=d['selected']['program'];st=time.perf_counter();m=cost_moments(d['input']['rows'],d['input']['n'],d['input']['syndrome'],d['input']['weights']);a=evaluate_moments(d['input'],p,m);a['seconds']=time.perf_counter()-st
  variance=float(F(*m['variance_exact']));a['objective_only_cost_T2']=-p['scale']*variance/6;a['cost_T2_deviation']=a['conditional_cost_T2']-a['objective_only_cost_T2'];a.update(name=d['name'],scheme=d['scheme'],cohort='compiler_comparison');records.append(a)
 for path in sorted((LAB/'results/penalty').glob('*.json')):
  d=json.loads(path.read_text());old=d['selected']['global_first']['program'];m=cost_moments(d['input']['rows'],d['input']['n'],d['input']['syndrome'],d['input']['weights']);v=float(F(*m['variance_exact']));pair=[]
  # The finite-forward matched comparison fixes roots; use the stored forward programs.
  f=json.loads((LAB/'results/forward_ordinary'/path.name).read_text())
  for label,p in [('baseline',f['baseline_program']),('amplified',f['amplified_program'])]:
   st=time.perf_counter();a=evaluate_moments(d['input'],p,m);a['seconds']=time.perf_counter()-st;a.update(name=d['name'],scheme='standard',cohort='fixed_coupler_'+label);records.append(a);pair.append(a)
  predicted=-(f['amplified_program']['scale']-f['baseline_program']['scale'])*v/6
  for a in pair:a['matched_cost_T2_change']=pair[1]['conditional_cost_T2']-pair[0]['conditional_cost_T2'];a['matched_cost_T2_prediction']=predicted
 out={'status':'pass','records':records,'seconds':time.perf_counter()-start,'summary':{}}
 for cohort in sorted({r['cohort'] for r in records}):
  a=[r for r in records if r['cohort']==cohort];out['summary'][cohort]={'programs':len(a),'median_seconds':statistics.median(r['seconds'] for r in a),'max_seconds':max(r['seconds'] for r in a),'median_q4_terms':statistics.median(r['q4_terms'] for r in a),'max_q4_terms':max(r['q4_terms'] for r in a)}
 out['matched_identity_max_abs_error']=max(abs(r['matched_cost_T2_change']-r['matched_cost_T2_prediction']) for r in records if 'matched_cost_T2_change' in r)
 out['balanced_cost_T2_identity_max_abs_error']=max(abs(r['cost_T2_deviation']) for r in records if r['scheme']=='balanced')
 (LAB/'results/quantum_moment_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
