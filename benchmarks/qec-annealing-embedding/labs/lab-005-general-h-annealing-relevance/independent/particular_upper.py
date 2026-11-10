from pathlib import Path
from fractions import Fraction as F
import json,time,statistics,sys
sys.dont_write_bytecode=True
from event_fourth import tail_after_fourth,schedule_coefficients,parameters
from exact_json import encode,decode
LAB=Path(__file__).resolve().parents[1]
def main():
 start=time.perf_counter();out=LAB/'results/particular_upper_bound';out.mkdir(exist_ok=True);cache={};records=[]
 for path in sorted((LAB/'results/forward_ordinary').glob('*.json')):
  d=json.loads(path.read_text());ts=time.perf_counter();m=d['moments'];e=m['particular_solution'];inp=d['input'];assert all(sum(e[i] for i in row)%2==s for row,s in zip(inp['rows'],inp['syndrome']));cost=sum((F(w)*v for w,v in zip(inp['weights'],e)),F(0));old=F(*m['minimum_cost_upper_exact']);upper=min(old,cost);D=sum(map(F,inp['weights']),F(0))-2*upper;bound_seconds=time.perf_counter()-ts;p=parameters(d);p['curvature']=p['eta']*D/12-p['rho']/6;coefficient=json.loads((LAB/'results/event_fourth'/path.name).read_text());L4=decode(coefficient['fourth_lower_exact']);n=inp['n']
  if n not in cache:cache[n]=schedule_coefficients(n)
  certificate=None
  for k in range(81):
   T=F(1,2**k);a=tail_after_fourth(n,p['g0'],T,cache[n]);b=tail_after_fourth(n,p['g1'],T,cache[n])
   if a is None or b is None:continue
   gap=p['curvature']*T*T+L4*T**4-a-b
   if gap>0:certificate={'duration':float(T),'duration_exact':encode(T),'relative_advantage_lower':float(gap),'relative_advantage_lower_exact':encode(gap)};break
  result={'name':d['name'],'particular_error':e,'particular_cost_exact':encode(cost),'prior_upper_exact':encode(old),'new_upper_exact':encode(upper),'curvature_lower_exact':encode(p['curvature']),'fourth_lower_exact':encode(L4),'certificate':certificate,'additional_upper_bound_seconds':bound_seconds,'seconds':time.perf_counter()-ts};(out/path.name).write_text(json.dumps(result,indent=2)+'\n');previous=coefficient['certificate'];records.append({'name':d['name'],'n':n,'upper_improved':upper<old,'previous_duration':previous['duration'] if previous else None,'duration':certificate['duration'] if certificate else None,'bound_seconds':bound_seconds,'seconds':result['seconds']})
 good=[r for r in records if r['duration']];out={'status':'completed','instances':len(records),'certified':len(good),'upper_improved':sum(r['upper_improved'] for r in records),'newly_certified':sum(r['duration'] is not None and r['previous_duration'] is None for r in records),'median_duration':statistics.median(r['duration'] for r in good),'min_duration':min(r['duration'] for r in good),'max_duration':max(r['duration'] for r in good),'median_additional_upper_seconds':statistics.median(r['bound_seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records,'cost_scope':'Incremental upper-bound/certificate control reuses previously charged exact q4 polynomials and physical programs.'};(LAB/'results/particular_upper_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
