"""Exact feasible-pointwise fourth coefficient; original optimum never solved."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import json,time,statistics,sys
sys.dont_write_bytecode=True
from forward_certificate import cost_moments
from forward_moments import expansion
from exact_json import encode
LAB=Path(__file__).resolve().parents[1];sys.path.insert(0,str(LAB/'theory_extensions/scripts'))
from word_majorant import schedule_coefficients
from relative_event import parameters

def projected_fourth(inp,p,moments,orders=False):
 nodes=sorted(q for q,v in p['h']);idx={q:i for i,q in enumerate(nodes)};h={idx[q]:F(v) for q,v in p['h']};J={(idx[q],idx[r]):F(v) for q,r,v in p['J'] if v};q2,q4=expansion(h,J,exact=True);roots={idx[q]:int(i) for i,q in p['roots'].items() if int(i)<inp['n']};characters=[int(v,16) for v in moments['kernel_character_hex']];ref=moments['particular_solution']
 def groups(poly):
  out={}
  for mask,value in poly.items():
   unobs=character=0;sign=1;m=mask
   while m:
    bit=m&-m;q=bit.bit_length()-1;m^=bit
    if q in roots:i=roots[q];character^=characters[i];sign*=2*ref[i]-1
    else:unobs|=bit
   key=(unobs,character);out[key]=out.get(key,F(0))+sign*value
  return out
 g2=groups(q2);g4=groups(q4);out={c:v for (u,c),v in g4.items() if u==0};byunobs={}
 for (u,c),v in g2.items():
  if v:byunobs.setdefault(u,[]).append((c,v))
 for poly in byunobs.values():
  for i,(c,v) in enumerate(poly):
   out[0]=out.get(0,F(0))+v*v/2
   for d,w in poly[:i]:out[c^d]=out.get(c^d,F(0))+v*w
 out={k:v for k,v in out.items() if v}
 return ({c:v for (u,c),v in g2.items() if u==0 and v},out) if orders else out

def tail_after_fourth(n,g,T,C):
 x=(1+g)*T
 if x>=1:return None
 total=((1-x)**(-n)+(1+x)**(-n))/2-sum((comb(n+k-1,k)*x**k for k in range(0,13,2)),F(0))
 for k in range(6,13,2):total+=min(sum((v*g**m for m,v in C[k]),F(0))*T**k,comb(n+k-1,k)*x**k)
 assert total>=0;return total

def certificate(inp,p0,p1,moments,params,C):
 a=projected_fourth(inp,p0,moments);b=projected_fourth(inp,p1,moments);diff={k:b.get(k,F(0))-a.get(k,F(0)) for k in a.keys()|b.keys()};diff={k:v for k,v in diff.items() if v};L4=diff.get(0,F(0))-sum((abs(v) for k,v in diff.items() if k),F(0));best=None
 for k in range(81):
  T=F(1,2**k);r0=tail_after_fourth(params['n'],params['g0'],T,C);r1=tail_after_fourth(params['n'],params['g1'],T,C)
  if r0 is None or r1 is None:continue
  gap=params['curvature']*T*T+L4*T**4-r0-r1
  if gap>0:best={'duration':float(T),'duration_exact':[T.numerator,T.denominator],'relative_advantage_lower':float(gap),'relative_advantage_lower_exact':encode(gap),'remainder_upper':float(r0+r1)};break
 return {'status':'strict_actual_original_optimum_order' if best else 'inconclusive','certificate':best,'fourth_lower':float(L4),'fourth_lower_exact':encode(L4),'difference_terms':len(diff),'difference_walsh_exact':[[hex(k),encode(v)] for k,v in sorted(diff.items())]}
def main():
 start=time.perf_counter();out=LAB/'results/event_fourth';out.mkdir(exist_ok=True);records=[];cache={}
 for path in sorted((LAB/'results/forward_ordinary').glob('*.json')):
  d=json.loads(path.read_text());st=time.perf_counter();p=parameters(d)
  if p['n'] not in cache:cache[p['n']]=schedule_coefficients(p['n'])
  r=certificate(d['input'],d['baseline_program'],d['amplified_program'],d['moments'],p,cache[p['n']]);r.update(name=d['name'],seconds=time.perf_counter()-st);(out/path.name).write_text(json.dumps(r,indent=2)+'\n');word=json.loads((LAB/'theory_extensions/results/word_majorant'/path.name).read_text())['certificate'];old=d['certificate'];duration=r['certificate']['duration'] if r['certificate'] else None
  row={'name':d['name'],'n':p['n'],'status':r['status'],'duration':duration,'fourth_lower':r['fourth_lower'],'difference_terms':r['difference_terms'],'seconds':r['seconds'],'word_duration':word.get('duration'),'global_duration':old.get('duration')}
  if duration and row['word_duration']:row['gain_over_word']=duration/row['word_duration']
  if duration and row['global_duration']:row['gain_over_global']=duration/row['global_duration']
  records.append(row);print(json.dumps(row),flush=True)
 good=[r for r in records if r['duration']];summary={'status':'completed','instances':len(records),'certified':len(good),'median_duration':statistics.median(r['duration'] for r in good),'min_duration':min(r['duration'] for r in good),'max_duration':max(r['duration'] for r in good),'median_gain_over_word':statistics.median(r['gain_over_word'] for r in good if 'gain_over_word' in r),'median_gain_over_global':statistics.median(r['gain_over_global'] for r in good if 'gain_over_global' in r),'median_seconds':statistics.median(r['seconds'] for r in records),'max_seconds':max(r['seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records};(LAB/'results/event_fourth_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='records'}))
if __name__=='__main__':main()
