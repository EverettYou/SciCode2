"""Exact-rational local-observable quantum-forward certificates."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import json,time,statistics,sys
sys.dont_write_bytecode=True
from forward_moments import expansion
LAB=Path(__file__).resolve().parents[1]
def local_data(program,weights):
 nodes=sorted(q for q,v in program['h']);idx={q:i for i,q in enumerate(nodes)};h={idx[q]:F(v) for q,v in program['h']};J={(idx[q],idx[r]):F(v) for q,r,v in program['J'] if v};q2,q4=expansion(h,J,exact=True);roots={int(i):idx[q] for i,q in program['roots'].items()};c2=F(0);c4=F(0)
 for i,w in enumerate(weights):
  bit=1<<roots[i];a4=q4.get(bit,F(0))+sum((v*q2.get(mask^bit,F(0)) for mask,v in q2.items()),F(0))/2
  c2+=F(w)*q2.get(bit,F(0))/2;c4+=F(w)*a4/2
 loads={q:abs(v) for q,v in h.items()}
 for (q,r),v in J.items():loads[q]+=abs(v);loads[r]+=abs(v)
 return {'c2':c2,'c4':c4,'gE':max(loads.values(),default=F(0)),'weight_l1':sum(map(lambda w:abs(F(w)),weights),F(0)),'N':len(nodes)}
def remainder(s,x):
 if x>=1:return None
 return ((1-x)**(-s)+(1+x)**(-s))/2-1-comb(s+1,2)*x*x-comb(s+3,4)*x**4

def certificate(base,new,weights):
 a=local_data(base,weights);b=local_data(new,weights);menu=[F(1,10),F(1,20),F(1,40),F(1,80),F(1,160),F(1,320),F(1,640)];rows=[];best=None
 for T in menu:
  ra=remainder(1,(1+a['gE'])*T);rb=remainder(1,(1+b['gE'])*T)
  if ra is None or rb is None:rows.append({'T':float(T),'status':'local_series_radius'});continue
  center=(a['c2']-b['c2'])*T*T+(a['c4']-b['c4'])*T**4;error=a['weight_l1']*(ra+rb)/2;gap=center-error
  row={'T':float(T),'status':'strict_actual_unconditional_cost_order' if gap>0 else 'inconclusive','cost_improvement_lower_exact':[gap.numerator,gap.denominator],'cost_improvement_lower':float(gap),'center':float(center),'remainder':float(error)};rows.append(row)
  if gap>0 and best is None:best=row
 return {'baseline':{k:([v.numerator,v.denominator] if isinstance(v,F) else v) for k,v in a.items()},'amplified':{k:([v.numerator,v.denominator] if isinstance(v,F) else v) for k,v in b.items()},'menu':rows,'largest_certified_duration':None if best is None else best['T'],'interpretation':'Exact-rational actual rounded-program unconditional original-error mean-cost order. Does not imply syndrome feasibility or optimum decoding success.'}
def main():
 start=time.perf_counter();records=[];OUT=LAB/'results/local_forward';OUT.mkdir(exist_ok=True)
 for path in sorted((LAB/'results/forward_ordinary').glob('*.json')):
  d=json.loads(path.read_text());st=time.perf_counter();r=certificate(d['baseline_program'],d['amplified_program'],d['input']['weights']);r.update(name=d['name'],seconds=time.perf_counter()-st);(OUT/path.name).write_text(json.dumps(r,indent=2)+'\n');records.append({'name':d['name'],'N':len(d['baseline_program']['h']),'largest_certified_duration':r['largest_certified_duration'],'seconds':r['seconds']})
 good=[r for r in records if r['largest_certified_duration'] is not None];out={'status':'pass','instances':len(records),'certified_actual_cost_orders':len(good),'median_certified_duration':statistics.median(r['largest_certified_duration'] for r in good) if good else None,'min_certified_duration':min((r['largest_certified_duration'] for r in good),default=None),'max_certified_duration':max((r['largest_certified_duration'] for r in good),default=None),'median_seconds':statistics.median(r['seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records};(LAB/'results/local_forward_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
