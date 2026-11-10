"""Actual original-optimum certificate-guided mapping, no decoding oracle."""
from pathlib import Path
from fractions import Fraction as F
import json,time,sys,statistics,hashlib
sys.dont_write_bytecode=True
from event_fourth import projected_fourth,tail_after_fourth,schedule_coefficients
from forward_certificate import cost_moments
from exact_json import encode,decode
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'));sys.path.insert(0,str(LAB.parent/'lab-002-agent-test-general-h/scripts'))
from evaluator import evaluate,json_program
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit
from embedding import graph_from_witness,qubo_to_ising
OUT=LAB/'results/certified_mapping';OUT.mkdir(exist_ok=True)
MENU=[F(1,2**k) for k in range(6,13)]
def pair(v):return encode(v)
def local_strength(p):
 loads={q:abs(F(v)) for q,v in p['h']}
 for q,r,v in p['J']:loads[q]+=abs(F(v));loads[r]+=abs(F(v))
 return max(loads.values(),default=F(0))
def difference(a,b):return {k:b.get(k,F(0))-a.get(k,F(0)) for k in a.keys()|b.keys() if b.get(k,F(0))!=a.get(k,F(0))}
def second_bound(delta,inp,m):
 cost={};chars=[int(v,16) for v in m['kernel_character_hex']];ref=m['particular_solution']
 for i,c in enumerate(chars):
  if c:cost[c]=cost.get(c,F(0))+F(inp['weights'][i])*(2*ref[i]-1)/2
 cost={k:v for k,v in cost.items() if v};mean=F(*m['mean_exact']);upper=F(*m['minimum_cost_upper_exact']);points={F(0)}
 for k,c in cost.items():
  p=-delta.get(k,F(0))/c
  if p>=0:points.add(p)
 def bound(lam):return delta.get(0,F(0))+lam*(mean-upper)-sum((abs(delta.get(k,F(0))+lam*cost.get(k,F(0))) for k in (delta.keys()|cost.keys()) if k),F(0))
 best=max(points,key=lambda p:(bound(p),-p));return bound(best),best,len(points)
def main():
 start=time.perf_counter();td=json.loads((LAB/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']];records=[];cache={}
 for path in sorted(list((LAB/'results').glob('*_n*_s*_standard.json'))+list((LAB/'results').glob('*_n*_s*_balanced.json'))):
  d=json.loads(path.read_text())
  if 'selected' not in d:continue
  st=time.perf_counter();inp=d['input'];n=inp['n'];m=cost_moments(inp['rows'],n,inp['syndrome'],inp['weights']);h,J,c=qubo_to_ising(d['model']['linear'],d['model']['quadratic'],d['model']['offset']);candidates=[];program_seconds=0;criterion_seconds=0
  if n not in cache:cache[n]=schedule_coefficients(n)
  saved=LAB/'results/moment_selection'/path.name;saved_programs={a['seed']:a['program'] for a in json.loads(saved.read_text())['candidates']} if saved.exists() else {}
  for old in d['candidates']:
   emb={int(i):v for i,v in old['embedding'].items()};ps=time.perf_counter()
   if old['seed'] in saved_programs:p=saved_programs[old['seed']]
   else:
    u=evaluate(h,J,c,target,emb,groups=groups);q=allocate_lp(h,J,c,target,emb,u,groups);p=json_program(q if q['feasible'] and q['scale']>=u['scale'] else u)
   program_seconds+=time.perf_counter()-ps;ts=time.perf_counter();orders=projected_fourth(inp,p,m,orders=True);g=local_strength(p);criterion_seconds+=time.perf_counter()-ts;candidates.append({'seed':old['seed'],'embedding':emb,'program':p,'orders':orders,'g':g})
  base=candidates[0];tail_cache={};comparisons=[]
  for a in candidates:
   ts=time.perf_counter();delta2=difference(base['orders'][0],a['orders'][0]);delta4=difference(base['orders'][1],a['orders'][1]);L2,lam,pointcount=second_bound(delta2,inp,m);L4=delta4.get(0,F(0))-sum((abs(v) for k,v in delta4.items() if k),F(0));curves=[]
   for T in MENU:
    rs=[]
    for g in [base['g'],a['g']]:
     key=(g,T)
     if key not in tail_cache:tail_cache[key]=tail_after_fourth(n,g,T,cache[n])
     rs.append(tail_cache[key])
    gap=None if any(r is None for r in rs) else L2*T*T+L4*T**4-sum(rs,F(0));curves.append({'T':float(T),'status':'strict_order' if gap is not None and gap>0 else 'inconclusive','relative_advantage_lower_exact':None if gap is None else pair(gap),'relative_advantage_lower':None if gap is None else float(gap)})
   criterion_seconds+=time.perf_counter()-ts;comparisons.append({'seed':a['seed'],'physical_qubits':len(a['program']['h']),'program':a['program'],'embedding':a['embedding'],'L2_exact':pair(L2),'L4_exact':pair(L4),'lambda_exact':pair(lam),'lambda_candidates':pointcount,'curves':curves})
  selections=[]
  for j,T in enumerate(MENU):
   eligible=[a for a in comparisons if a['physical_qubits']<=len(base['program']['h']) and a['curves'][j]['status']=='strict_order'];sel=min(eligible,key=lambda a:(a['physical_qubits'],-decode(a['curves'][j]['relative_advantage_lower_exact']),a['seed'])) if eligible else comparisons[0];selections.append({'T':float(T),'selected_seed':sel['seed'],'baseline_seed':base['seed'],'certified_change':bool(eligible),'baseline_qubits':len(base['program']['h']),'selected_qubits':sel['physical_qubits'],'saved_qubits':len(base['program']['h'])-sel['physical_qubits'],'relative_advantage_lower':sel['curves'][j]['relative_advantage_lower'] if eligible else None})
  selected_seeds={s['selected_seed'] for s in selections}|{base['seed']};audits={}
  for a in comparisons:
   if a['seed'] in selected_seeds:
    audit=rational_audit(d['model'],a['program'],a['embedding'],target,groups);assert audit['float_projected_ground_states_certified'];audits[str(a['seed'])]=audit
  result={'name':d['name'],'scheme':d['scheme'],'input':inp,'moments':m,'baseline_seed':base['seed'],'comparisons':comparisons,'selections':selections,'selected_static_audits':audits,'program_seconds':program_seconds,'criterion_seconds':criterion_seconds,'seconds':time.perf_counter()-st};(OUT/path.name).write_text(json.dumps(result,indent=2)+'\n');records.append({'name':d['name'],'scheme':d['scheme'],'selections':selections,'candidate_count':len(candidates),'program_seconds':program_seconds,'criterion_seconds':criterion_seconds,'seconds':result['seconds']});print(json.dumps({'name':d['name'],'primary':next(s for s in selections if s['T']==float(F(1,1024))),'seconds':result['seconds']}),flush=True)
 summary={}
 for scheme in ['standard','balanced','all']:
  a=[r for r in records if scheme=='all' or r['scheme']==scheme];summary[scheme]={}
  for T in MENU:
   s=[next(s for s in r['selections'] if s['T']==float(T)) for r in a];summary[scheme][str(float(T))]={'models':len(a),'certified_changes':sum(x['certified_change'] for x in s),'strict_qubit_reductions':sum(x['saved_qubits']>0 for x in s),'mean_qubit_reduction_fraction':statistics.mean(x['saved_qubits']/x['baseline_qubits'] for x in s)}
 out={'status':'completed','models':len(records),'candidate_count':sum(r['candidate_count'] for r in records),'primary_T':float(F(1,1024)),'summary':summary,'median_criterion_seconds_per_pool':statistics.median(r['criterion_seconds'] for r in records),'total_criterion_seconds':sum(r['criterion_seconds'] for r in records),'total_program_seconds':sum(r['program_seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records,'interpretation':'Actual original-optimum finite-forward certificates across mappings and physical sizes. Early-time regime, reused exploratory pools, no decoding optimum or full-state simulation in selection.'};(LAB/'results/certified_mapping_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['records','summary']}))
if __name__=='__main__':main()
