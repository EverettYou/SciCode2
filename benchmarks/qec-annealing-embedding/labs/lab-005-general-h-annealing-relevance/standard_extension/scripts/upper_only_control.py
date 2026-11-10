from pathlib import Path
from fractions import Fraction as F
import json,time,statistics
from optimality_lp import root_second,subtract
from run import HERE,LAB,read,pair

def bound(delta,inp,m):
 chars=[int(v,16) for v in m['kernel_character_hex']];ref=m['particular_solution'];cost={}
 for i,c in enumerate(chars):
  if c:cost[c]=cost.get(c,F(0))+F(inp['weights'][i])*(2*ref[i]-1)/2
 cost={k:v for k,v in cost.items() if v};mean=F(*m['mean_exact']);U=F(*m['minimum_cost_upper_exact']);points={F(0)}
 for k,c in cost.items():
  lam=-delta.get(k,F(0))/c
  if lam>=0:points.add(lam)
 def value(lam):return delta.get(0,F(0))+lam*(mean-U)-sum((abs(delta.get(k,F(0))+lam*cost.get(k,F(0))) for k in delta.keys()|cost.keys() if k),F(0))
 lam=max(points,key=lambda t:(value(t),-t));return value(lam),lam

def main():
 start=time.perf_counter();out=HERE/'results/upper_only';out.mkdir(exist_ok=True);records=[]
 for variant in ['particular','witness']:
  rows=[]
  for path in sorted((LAB/'results/certified_mapping').glob('*_standard.json')):
   st=time.perf_counter();d=json.loads(path.read_text());tight=json.loads((HERE/'results'/variant/path.name).read_text());inp=d['input'];m=tight['moments_with_witness_upper'];base=d['comparisons'][0];bp=root_second(inp,base['program'],m);comparisons=[]
   for a in d['comparisons']:
    delta=subtract(bp,root_second(inp,a['program'],m));L2,lam=bound(delta,inp,m);old=read(a['L2_exact']);L2=max(old,L2);curves=[]
    for c in a['curves']:
     T=F(c['T']);gap=None if c['relative_advantage_lower_exact'] is None else read(c['relative_advantage_lower_exact'])+(L2-old)*T*T;curves.append({'T':float(T),'strict':gap is not None and gap>0,'gap_exact':None if gap is None else pair(gap),'gap':None if gap is None else float(gap)})
    comparisons.append({'seed':a['seed'],'N':a['physical_qubits'],'L2_exact':pair(L2),'lambda_exact':pair(lam),'curves':curves})
   selections=[]
   for j,s in enumerate(d['selections']):
    eligible=[a for a in comparisons if a['N']<=base['physical_qubits'] and a['curves'][j]['strict']];sel=min(eligible,key=lambda a:(a['N'],-read(a['curves'][j]['gap_exact']),a['seed'])) if eligible else comparisons[0];selections.append({'T':s['T'],'selected_seed':sel['seed'],'certified_change':bool(eligible),'baseline_N':base['physical_qubits'],'selected_N':sel['N'],'saved_qubits':base['physical_qubits']-sel['N']})
   r={'name':d['name'],'variant':variant,'comparisons':comparisons,'selections':selections,'seconds':time.perf_counter()-st};(out/(variant+'_'+path.name)).write_text(json.dumps(r,indent=2)+'\n');rows.append({'name':d['name'],'seconds':r['seconds'],'selections':selections})
  summary={}
  for k in range(6,13):
   T=1/2**k;ss=[next(s for s in r['selections'] if s['T']==T) for r in rows];summary[str(T)]={'certified_changes':sum(s['certified_change'] for s in ss),'strict_qubit_reductions':sum(s['saved_qubits']>0 for s in ss),'mean_qubit_reduction_fraction':statistics.mean(s['saved_qubits']/s['baseline_N'] for s in ss)}
  records.append({'variant':variant,'summary':summary,'seconds':sum(r['seconds'] for r in rows),'records':rows})
 result={'status':'complete','seconds':time.perf_counter()-start,'variants':records};(HERE/'results/upper_only_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'complete','seconds':result['seconds'],'variants':[{k:v for k,v in r.items() if k!='records'} for r in records]}))
if __name__=='__main__':main()
