from pathlib import Path
import json,time,sys,statistics
sys.dont_write_bytecode=True
from forward_certificate import cost_moments
from forward_moments import evaluate_moments
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'));sys.path.insert(0,str(LAB.parent/'lab-002-agent-test-general-h/scripts'))
from evaluator import evaluate,json_program
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit
from embedding import graph_from_witness,qubo_to_ising
OUT=LAB/'results/moment_selection';OUT.mkdir(exist_ok=True)
def main():
 start=time.perf_counter();td=json.loads((LAB/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];records=[]
 for path in sorted((LAB/'results').glob('*_n*_s*_standard.json')):
  d=json.loads(path.read_text());st=time.perf_counter();inp=d['input'];m=cost_moments(inp['rows'],inp['n'],inp['syndrome'],inp['weights']);h,J,c=qubo_to_ising(d['model']['linear'],d['model']['quadratic'],d['model']['offset']);candidates=[]
  for old in d['candidates']:
   emb={int(i):v for i,v in old['embedding'].items()};u=evaluate(h,J,c,target,emb,groups=groups);p=allocate_lp(h,J,c,target,emb,u,groups)
   if not p['feasible'] or p['scale']<u['scale']:p=u
   p=json_program(p);ts=time.perf_counter();q=evaluate_moments(inp,p,m);seconds=time.perf_counter()-ts;T=.25
   a={'seed':old['seed'],'embedding':emb,'program':p,'moments':q,'moment_seconds':seconds,'feasible_prediction':q['feasible_probability_at_zero']*(1+q['feasibility_relative_T2']*T*T+q['feasibility_relative_T4']*T**4),'cost_prediction':q['uniform_feasible_cost']+q['conditional_cost_T2']*T*T+q['conditional_cost_T4']*T**4};candidates.append(a)
  base=candidates[0];eligible=[a for a in candidates if len(a['program']['h'])<=len(base['program']['h']) and a['feasible_prediction']>=base['feasible_prediction']-1e-12 and a['cost_prediction']<=base['cost_prediction']+1e-12 and (a['feasible_prediction']>base['feasible_prediction']+1e-10 or a['cost_prediction']<base['cost_prediction']-1e-10)]
  selected=min(eligible,key=lambda a:(len(a['program']['h']),-a['feasible_prediction'],a['cost_prediction'],a['seed'])) if eligible else base
  audit=rational_audit(d['model'],selected['program'],selected['embedding'],target,groups);assert audit['float_projected_ground_states_certified']
  result={'name':d['name'],'input':inp,'T':T,'baseline_seed':base['seed'],'selected_seed':selected['seed'],'prior_alpha_compactness_seed':d['selected']['seed'],'selected_static_audit':audit,'candidates':candidates,'seconds':time.perf_counter()-st};(OUT/path.name).write_text(json.dumps(result,indent=2)+'\n')
  record={'name':d['name'],'changed':selected['seed']!=base['seed'],'baseline_qubits':len(base['program']['h']),'selected_qubits':len(selected['program']['h']),'saved_qubits':len(base['program']['h'])-len(selected['program']['h']),'feasible_prediction_ratio':selected['feasible_prediction']/base['feasible_prediction'],'conditional_cost_change':selected['cost_prediction']-base['cost_prediction'],'candidate_count':len(candidates),'moment_median_seconds':statistics.median(a['moment_seconds'] for a in candidates),'seconds':result['seconds']};records.append(record);print(json.dumps(record),flush=True)
 out={'status':'completed','instances':len(records),'changed_selections':sum(r['changed'] for r in records),'strict_qubit_reductions':sum(r['saved_qubits']>0 for r in records),'mean_qubit_reduction_fraction':statistics.mean(r['saved_qubits']/r['baseline_qubits'] for r in records),'median_moment_seconds':statistics.median(r['moment_median_seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records,'interpretation':'Expansion-guided compact mapping decisions; not certified moderate-time or actual optimum improvements.'};(LAB/'results/moment_selection_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
