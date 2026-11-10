"""Parent independent reconstruction of saved optimal-set dual certificates."""
from pathlib import Path
from fractions import Fraction as F
import json,time,hashlib,sys
sys.dont_write_bytecode=True
from event_fourth import projected_fourth
from certified_mapping import difference
from exact_json import decode
LAB=Path(__file__).resolve().parents[1];ROOT=LAB/'standard_extension/results'
def dual(delta,m,inp,multipliers):
 cost={}
 for i,text in enumerate(m['kernel_character_hex']):
  char=int(text,16)
  if char:cost[char]=cost.get(char,F(0))+F(inp['weights'][i])*(2*m['particular_solution'][i]-1)/2
 residual={k:v for k,v in delta.items() if k};const=delta.get(0,F(0));count=0
 for label,value in multipliers:
  nu=decode(value);assert nu>=0
  if label=='cost_upper':coeff=cost;rhs=F(*m['minimum_cost_upper_exact'])-F(*m['mean_exact'])
  elif label.startswith('kernel_'):
   t=int(label.split('_')[1],16);assert 0<t<(1<<m['kernel_dimension']);coeff={a:v for a,v in cost.items() if (a&t).bit_count()%2};rhs=F(0)
  elif label.startswith('triangle_'):
   _,aa,bb,cc,j=label.split('_');a,b,c=map(lambda v:int(v,16),[aa,bb,cc]);assert a and b and c and a^b^c==0;sgn=[(-1,-1,-1),(-1,1,1),(1,-1,1),(1,1,-1)][int(j)];assert sgn[0]*sgn[1]*sgn[2]==-1;coeff=dict(zip([a,b,c],map(F,sgn)));rhs=F(1)
  else:raise ValueError(label)
  const-=nu*rhs
  for a,v in coeff.items():residual[a]=residual.get(a,F(0))+nu*v
  count+=1
 return const-sum(map(abs,residual.values()),F(0)),count

def main():
 start=time.perf_counter();checks=projections=witnesses=nonzero=gapchecks=selectionchecks=0;records=[]
 for path in sorted(ROOT.glob('*_standard.json')):
  initial=json.loads(path.read_text());sourcepath=LAB/'results/certified_mapping'/path.name;source=json.loads(sourcepath.read_text());assert hashlib.sha256(sourcepath.read_bytes()).hexdigest()==initial['source_sha256'];inp=source['input'];m=source['moments'];base=source['comparisons'][0];base2=projected_fourth(inp,base['program'],m,orders=True)[0];delta_by_seed={}
  for a,c in zip(source['comparisons'],initial['comparisons']):
   assert a['seed']==c['seed'];p2=projected_fourth(inp,a['program'],m,orders=True)[0];delta=difference(base2,p2);assert delta=={int(k,16):decode(v) for k,v in c['delta_second_exact']};delta_by_seed[a['seed']]=delta;projections+=1;best=decode(c['cost_only_lower_exact'])
   for method in ['basis','pairs','triangles']:
    row=c['methods'][method];bound,count=dual(delta,m,inp,row['dual_nonzero']);assert bound==decode(row['raw_dual_bound_exact']);best=max(best,bound);assert best==decode(row['bound_exact']);checks+=1;nonzero+=count
  for folder in ['particular','witness']:
   d=json.loads((ROOT/folder/path.name).read_text());assert d['source_sha256']==initial['source_sha256'];mm=d['moments_with_witness_upper'];w=d['witness'];mask=int(w['original_error_mask_hex'],16);assert mask>>inp['n']==0;bits=[(mask>>i)&1 for i in range(inp['n'])];assert all(sum(bits[i] for i in row)%2==s for row,s in zip(inp['rows'],inp['syndrome']));cost=sum((F(wi)*b for wi,b in zip(inp['weights'],bits)),F(0));assert cost==decode(w['cost']);assert F(*mm['minimum_cost_upper_exact'])==min(F(*m['minimum_cost_upper_exact']),cost);witnesses+=1
   for a,c in zip(source['comparisons'],d['comparisons']):
    assert a['seed']==c['seed'];bound,count=dual(delta_by_seed[a['seed']],mm,inp,c['dual_nonzero']);assert bound==decode(c['raw_dual_bound_exact']);lower=max(decode(a['L2_exact']),bound);assert lower==decode(c['L2_exact']);checks+=1;nonzero+=count
    for old,new in zip(a['curves'],c['curves']):
     if old['relative_advantage_lower_exact'] is None:assert new['gap_exact'] is None;continue
     T=F(old['T']);gap=decode(old['relative_advantage_lower_exact'])+(lower-decode(a['L2_exact']))*T*T;assert gap==decode(new['gap_exact']);assert new['strict']==(gap>0);gapchecks+=1
   for j,s in enumerate(d['selections']):
    eligible=[c for c in d['comparisons'] if c['N']<=base['physical_qubits'] and c['curves'][j]['strict']];sel=min(eligible,key=lambda c:(c['N'],-decode(c['curves'][j]['gap_exact']),c['seed'])) if eligible else d['comparisons'][0];assert sel['seed']==s['selected_seed'];selectionchecks+=1
  records.append({'name':source['name'],'projections_checked':len(source['comparisons'])})
 out={'status':'pass','physical_program_root_polynomials_checked':projections,'saved_exact_dual_bounds_reconstructed':checks,'nonzero_multipliers_checked':nonzero,'ordinary_feasible_witnesses_checked':witnesses,'exact_gap_updates_checked':gapchecks,'exact_selections_checked':selectionchecks,'seconds':time.perf_counter()-start,'records':records,'scope':'Parent reconstructs root coefficients with its independent exact Walsh projection, then rebuilds each nonzero kernel/cost/triangle row directly from mathematical identities. No ordinary optimum oracle or LP run.'};(LAB/'results/independent_standard_extension_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
