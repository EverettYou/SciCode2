"""Recompute saved exact dual witnesses and gap updates without solving LPs."""
from pathlib import Path
from fractions import Fraction as F
import json,time
from optimality_lp import constraints,exact_dual_bound,root_second,subtract
from run import HERE,LAB,read

def main():
 start=time.perf_counter();duals=0;gaps=0;witnesses=0
 for folder in [HERE/'results',HERE/'results/particular_nested',HERE/'results/witness_nested']:
  for path in folder.glob('*_standard.json'):
   d=json.loads(path.read_text());inp=d['input'];m=d['moments'];source=json.loads((LAB/'results/certified_mapping'/path.name).read_text());parents={a['seed']:a for a in source['comparisons']}
   for a in d['comparisons']:
    delta={int(c,16):read(v) for c,v in a['delta_second_exact']};bound=read(a['cost_only_lower_exact'])
    for method,r in a['methods'].items():
     _,rows=constraints(inp,m,delta,method);multipliers={key:read(v) for key,v in r['dual_nonzero']};nu=[multipliers.get(row['id'],F(0)) for row in rows];assert all(v>=0 for v in nu);raw=exact_dual_bound(delta,rows,nu);assert raw==read(r['raw_dual_bound_exact']);bound=max(bound,raw);assert bound==read(r['bound_exact']);duals+=1
     p=parents[a['seed']];old=read(p['L2_exact'])
     for c,pc in zip(r['curves'],p['curves']):
      if c['gap_exact'] is None:assert pc['relative_advantage_lower_exact'] is None;continue
      gap=read(pc['relative_advantage_lower_exact'])+(bound-old)*F(c['T'])**2;assert gap==read(c['gap_exact']);assert c['strict']==(gap>0);gaps+=1
 for variant in ['particular','witness']:
  for path in (HERE/'results'/variant).glob('*.json'):
   d=json.loads(path.read_text());inp=d['input'];m=d['moments_with_witness_upper'];e=int(d['witness']['original_error_mask_hex'],16);assert all(sum((e>>i)&1 for i in row)%2==s for row,s in zip(inp['rows'],inp['syndrome']));cost=sum((F(w)*((e>>i)&1) for i,w in enumerate(inp['weights'])),F(0));assert cost==read(d['witness']['cost']);assert F(*m['minimum_cost_upper_exact'])==min(cost,read(d['old_upper_exact']));witnesses+=1
 out={'status':'pass','exact_dual_certificates_checked':duals,'exact_gap_updates_checked':gaps,'ordinary_feasible_witnesses_checked':witnesses,'no_lp_or_optimum_solve':True,'seconds':time.perf_counter()-start};(HERE/'results/exact_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
