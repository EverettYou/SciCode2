from pathlib import Path
from fractions import Fraction as F
import json,sys,time,statistics
from optimality_lp import root_second,subtract,evaluate
from run import HERE,LAB,read,pair
sys.path.insert(0,str(LAB/'theory_extensions/scripts'))
from word_majorant import schedule_coefficients,remainder

def strength(p):
 load={q:abs(F(v)) for q,v in p['h']}
 for q,r,v in p['J']:load[q]+=abs(F(v));load[r]+=abs(F(v))
 return max(load.values(),default=F(0))

def main():
 start=time.perf_counter();out=HERE/'results/upper';out.mkdir(exist_ok=True);records=[];cache={}
 for path in sorted((LAB/'results/certified_mapping').glob('*_standard.json')):
  d=json.loads(path.read_text());inp=d['input'];m=d['moments'];n=inp['n'];base=d['comparisons'][0];bp=root_second(inp,base['program'],m);g0=strength(base['program']);allrows=[]
  if n not in cache:cache[n]=schedule_coefficients(n)
  for a in d['comparisons']:
   delta=subtract(bp,root_second(inp,a['program'],m));r=evaluate(inp,m,{k:-v for k,v in delta.items()},'triangles');upper=None if 'bound' not in r else -r['bound'];curves=[];g1=strength(a['program'])
   for k in range(6,13):
    T=F(1,2**k);r0=remainder(n,g0,T,cache[n]);r1=remainder(n,g1,T,cache[n]);gap=None if upper is None or r0 is None or r1 is None else -upper*T*T-r0-r1
    curves.append({'T':float(T),'baseline_strictly_better':gap is not None and gap>0,'relative_baseline_advantage_lower_exact':None if gap is None else pair(gap)})
   row={'seed':a['seed'],'N':a['physical_qubits'],'no_larger_than_first':a['physical_qubits']<=base['physical_qubits'],'curvature_upper_exact':None if upper is None else pair(upper),'curvature_upper':None if upper is None else float(upper),'status':r['status'],'seconds':r['seconds'],'dual_nonzero':[[row['id'],pair(nu)] for row,nu in zip(r['rows'],r.get('multipliers',[])) if nu],'curves':curves};allrows.append(row)
  result={'name':d['name'],'input':inp,'moments':m,'baseline_seed':base['seed'],'baseline_N':base['physical_qubits'],'candidates':allrows};(out/path.name).write_text(json.dumps(result,indent=2)+'\n');records.extend([{'name':d['name'],**row} for row in allrows])
 compact=[r for r in records if r['no_larger_than_first'] and r['seed']!=11];negative=[r for r in compact if r['curvature_upper'] is not None and r['curvature_upper']<0]
 summary={'status':'complete','candidates':len(records),'nonbaseline_no_larger_candidates':len(compact),'negative_upper_curvature_all':sum(r['curvature_upper'] is not None and r['curvature_upper']<0 for r in records),'negative_upper_curvature_no_larger':len(negative),'negative_pools_no_larger':len(set(r['name'] for r in negative)),'finite_negative_counts':{str(1/2**k):sum(next(c for c in r['curves'] if c['T']==1/2**k)['baseline_strictly_better'] for r in compact) for k in range(6,13)},'seconds':time.perf_counter()-start,'records':records};(HERE/'results/upper_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='records'}))
if __name__=='__main__':main()
