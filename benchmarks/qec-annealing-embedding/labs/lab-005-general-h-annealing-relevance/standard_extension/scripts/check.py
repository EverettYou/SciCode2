"""Small arbitrary-affine-space validation; reference optima never used in suite."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,random,time
from itertools import combinations
from optimality_lp import evaluate,constraints
from witness_followup import witness
HERE=Path(__file__).resolve().parents[1];LAB=HERE.parent;sys.path.insert(0,str(LAB/'independent'))
from forward_certificate import cost_moments

def main():
 start=time.perf_counter();rng=random.Random(165319);records=[];optimal_patterns=0;row_checks=0;dual_checks=0
 for case in range(60):
  n=[4,6,8][case%3];rows=[sorted(rng.sample(range(n),rng.randint(1,min(n,4)))) for _ in range(n//2)];rows.append(rows[0]);hidden=[rng.randrange(2) for _ in range(n)];s=[sum(hidden[i] for i in row)%2 for row in rows];w=[F(rng.randint(-4,4),4) for _ in range(n)];inp={'n':n,'rows':rows,'syndrome':s,'weights':[float(v) for v in w]};m=cost_moments(rows,n,s,inp['weights']);pats=[int(v,16) for v in m['kernel_character_hex']];ref=m['particular_solution'];k=m['kernel_dimension'];chars=set(pats)-{0};chars|={a^b for a,b in combinations(chars,2) if rng.random()<.3};chars.discard(0);delta={c:F(rng.randint(-5,5),7) for c in chars};delta[0]=F(rng.randint(-5,5),7)
  samples=[]
  for y in range(1<<k):
   error=[ref[i]^((pats[i]&y).bit_count()%2) for i in range(n)];assert all(sum(error[i] for i in row)%2==t for row,t in zip(rows,s));cost=sum((v*e for v,e in zip(w,error)),F(0));dval=delta[0]+sum((v*(-1)**((c&y).bit_count()%2) for c,v in delta.items() if c),F(0));samples.append((y,cost,dval))
  optimum=min(c for y,c,v in samples);true=[(y,v) for y,c,v in samples if c==optimum];optimal_patterns+=len(true);assert optimum<=F(*m['minimum_cost_upper_exact'])
  for method in ['basis','pairs','triangles']:
   _,cons=constraints(inp,m,delta,method)
   for y,v in true:
    for row in cons:
     lhs=sum((coef*(-1)**((c&y).bit_count()%2) for c,coef in row['coefficients'].items()),F(0));assert lhs<=row['rhs'];row_checks+=1
   lower=evaluate(inp,m,delta,method);upper=evaluate(inp,m,{c:-v for c,v in delta.items()},method);assert lower['status']=='exact_dual_lower' and upper['status']=='exact_dual_lower';assert lower['bound']<=min(v for y,v in true);assert -upper['bound']>=max(v for y,v in true);dual_checks+=2
  witness_result=witness(inp,m);assert witness_result['cost']>=optimum;mw=dict(m);u=min(F(*m['minimum_cost_upper_exact']),witness_result['cost']);mw['minimum_cost_upper_exact']=[u.numerator,u.denominator]
  lower=evaluate(inp,mw,delta,'triangles');upper=evaluate(inp,mw,{c:-v for c,v in delta.items()},'triangles');assert lower['bound']<=min(v for y,v in true);assert -upper['bound']>=max(v for y,v in true);dual_checks+=2
  records.append({'case':case,'n':n,'rank':m['rank'],'kernel_dimension':k,'optimum_patterns':len(true),'delta_terms':len(delta)})
 out={'status':'pass','matrices':len(records),'original_optimal_patterns':optimal_patterns,'necessary_constraint_checks':row_checks,'exact_dual_bound_checks':dual_checks,'feasible_search_witnesses_checked':60,'seconds':time.perf_counter()-start,'scope':'Reference optimum enumeration only on small arbitrary matrices to validate constraints and bounds; never used in ordinary selection','records':records};(HERE/'results/check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
