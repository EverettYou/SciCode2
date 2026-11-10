from pathlib import Path
import json,time,subprocess
LAB=Path(__file__).resolve().parents[1];OUT=LAB/'results/long_forward';OUT.mkdir(exist_ok=True)
def main():
 start=time.perf_counter();records=[]
 for path in sorted((LAB/'results/forward_anchors').glob('*_n6_*.json')):
  d=json.loads(path.read_text());result={'name':d['name'],'dynamics':{}}
  for T in [32.,64.,128.]:
   result['dynamics'][str(T)]={}
   for label in ['baseline','amplified']:
    steps=128
    while steps<64*T:steps*=2
    levels=[];status='step_cap_unresolved'
    while steps<=32768:
     if time.perf_counter()-start>1200:status='total_budget_exhausted';break
     try:r=subprocess.run([str(LAB/'independent/quantum_forward_backend'),str(path.with_name(d['name']+'_'+label+'.dat')),str(T),str(steps)],capture_output=True,text=True,timeout=180)
     except subprocess.TimeoutExpired:status='call_timeout';break
     if r.returncode:status='backend_error';break
     row=json.loads(r.stdout);levels.append(row)
     if len(levels)>1 and max(abs(levels[-1][k]-levels[-2][k]) for k in ['original_optimal','chain_broken','full_ground'])<=2e-5 and abs(row['norm']-1)<1e-8:status='converged';break
     steps*=2
    result['dynamics'][str(T)][label]={'status':status,'levels':levels,'final':levels[-1] if levels else None};(OUT/path.name).write_text(json.dumps(result,indent=2)+'\n')
   records.append({'name':d['name'],'T':T,**{label:result['dynamics'][str(T)][label] for label in ['baseline','amplified']}});print(json.dumps({'name':d['name'],'T':T,'status':{k:result['dynamics'][str(T)][k]['status'] for k in ['baseline','amplified']}}),flush=True)
 out={'records':records,'seconds':time.perf_counter()-start,'converged_pairs':sum(all(r[k]['status']=='converged' for k in ['baseline','amplified']) for r in records)}
 both=[r for r in records if all(r[k]['status']=='converged' for k in ['baseline','amplified'])];out['positive_orders']=sum(r['amplified']['final']['original_optimal']>r['baseline']['final']['original_optimal'] for r in both);out['negative_orders']=sum(r['amplified']['final']['original_optimal']<r['baseline']['final']['original_optimal'] for r in both)
 (LAB/'results/long_forward_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
