"""Audit every actual candidate plus exact rational selection tie ordering."""
from pathlib import Path
from fractions import Fraction as F
import json,time,sys
sys.dont_write_bytecode=True
from penalty_bound import load_module
from exact_json import decode
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'));sys.path.insert(0,str(LAB.parent/'lab-002-agent-test-general-h/scripts'))
from embedding import graph_from_witness,qubo_to_ising
from numeric_certificate import rational_audit
ia=load_module('independent_mapping_witness_audit',OLD/'independent/audit_programs.py')
def main():
 st=time.perf_counter();td=json.loads((LAB/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];records=[];selection_checks=0
 for path in sorted((LAB/'results/certified_mapping').glob('*.json')):
  d=json.loads(path.read_text());source=json.loads((LAB/'results'/path.name).read_text());h,J,c=qubo_to_ising(source['model']['linear'],source['model']['quadratic'],source['model']['offset']);ising={'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c};base=d['comparisons'][0]
  for a in d['comparisons']:
   emb={int(i):v for i,v in a['embedding'].items()};entry={'embedding':emb,'program':a['program']};datum={'name':d['name'],'input':d['input'],'model':source['model'],'logical_ising':ising,'selected':{'first':{'embedding':{int(i):v for i,v in base['embedding'].items()},'program':base['program']}}};audit=ia.audit(datum,'candidate_'+str(a['seed']),entry,target,groups);exact=rational_audit(source['model'],a['program'],emb,target,groups);assert exact['float_projected_ground_states_certified'];records.append({'name':d['name'],'seed':a['seed'],'independent':audit,'exact_model':exact})
  for j,s in enumerate(d['selections']):
   eligible=[a for a in d['comparisons'] if a['physical_qubits']<=base['physical_qubits'] and a['curves'][j]['status']=='strict_order'];sel=min(eligible,key=lambda a:(a['physical_qubits'],-decode(a['curves'][j]['relative_advantage_lower_exact']),a['seed'])) if eligible else base;assert sel['seed']==s['selected_seed'];selection_checks+=1
  print(json.dumps({'name':d['name'],'audited':len(records)}),flush=True)
 result={'status':'pass','actual_programs_checked':len(records),'exact_rational_selections_checked':selection_checks,'sorting_mismatches':0,'seconds':time.perf_counter()-st,'records':records,'scope':'Every saved successful actual program in the47model candidate pools, including all baselines. Independent graph/range/repair/rounding reader plus authoritative exact reduction audit.'};(LAB/'results/independent_certified_mapping_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
