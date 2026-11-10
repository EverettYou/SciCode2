"""Charged feasible kernel-descent witness; no optimality claim or oracle."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import json,time,sys,random,math,statistics,hashlib,argparse
from optimality_lp import root_second,subtract,evaluate
from run import HERE,LAB,read,pair

def witness(inp,m):
 start=time.perf_counter();n=inp['n'];k=m['kernel_dimension'];patterns=[int(v,16) for v in m['kernel_character_hex']];ref=m['particular_solution'];base=sum(int(v)<<i for i,v in enumerate(ref));weights=list(map(F,inp['weights']));den=math.lcm(*(v.denominator for v in weights));iw=[int(w*den) for w in weights];ts=[1<<j for j in range(k)]+[(1<<i)^(1<<j) for i,j in combinations(range(k),2)]
 def error(y):return base^sum(((p&y).bit_count()%2)<<i for i,p in enumerate(patterns))
 moves=[(t,[(i,iw[i]) for i,p in enumerate(patterns) if (p&t).bit_count()%2],error(t)^base) for t in ts];rng=random.Random(165311);starts=[0]+[rng.getrandbits(k) for _ in range(15)];best=None;records=[];evaluations=0
 for y in starts:
  e=error(y);cost=sum(w for i,w in enumerate(iw) if (e>>i)&1);accepted=0
  for it in range(4*n):
   bestdelta=0;move=None
   for t,terms,mask in moves:
    delta=sum(w*(1-2*((e>>i)&1)) for i,w in terms);evaluations+=1
    if delta<bestdelta:bestdelta=delta;move=(t,mask)
   if move is None:break
   y^=move[0];e^=move[1];cost+=bestdelta;accepted+=1
  records.append({'accepted_moves':accepted,'terminal_cost_scaled':cost,'cap_reached':accepted==4*n})
  if best is None or cost<best[0]:best=(cost,e,y)
 cost,e,y=best;assert error(y)==e;assert all(sum((e>>i)&1 for i in row)%2==s for row,s in zip(inp['rows'],inp['syndrome']));assert sum((w*((e>>i)&1) for i,w in enumerate(weights)),F(0))==F(cost,den)
 return {'status':'feasible_upper_witness_not_optimum','cost':F(cost,den),'original_error_mask_hex':hex(e),'kernel_parameter_hex':hex(y),'starts':16,'seed':165311,'per_start_accepted_cap':4*n,'move_count':len(moves),'move_evaluations':evaluations,'scaled_weight_denominator':den,'start_records':records,'seconds':time.perf_counter()-start,'syndrome_verified':True}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--particular',action='store_true');args=ap.parse_args();start=time.perf_counter();out=HERE/('results/particular' if args.particular else 'results/witness');out.mkdir(exist_ok=True);records=[]
 for path in sorted((LAB/'results/certified_mapping').glob('*_standard.json')):
  st=time.perf_counter();d=json.loads(path.read_text());inp=d['input'];m=dict(d['moments']);
  if args.particular:
   ts=time.perf_counter();e=m['particular_solution'];cost=sum((F(w)*v for w,v in zip(inp['weights'],e)),F(0));assert all(sum(e[i] for i in row)%2==s for row,s in zip(inp['rows'],inp['syndrome']));w={'status':'existing_affine_particular_upper_not_optimum','cost':cost,'original_error_mask_hex':hex(sum(v<<i for i,v in enumerate(e))),'seconds':time.perf_counter()-ts,'syndrome_verified':True,'starts':0,'move_evaluations':0}
  else:w=witness(inp,m)
  oldU=F(*m['minimum_cost_upper_exact']);U=min(oldU,w['cost']);m['minimum_cost_upper_exact']=[U.numerator,U.denominator];base=d['comparisons'][0];bp=root_second(inp,base['program'],m);comparisons=[]
  for a in d['comparisons']:
   delta=subtract(bp,root_second(inp,a['program'],m));old=read(a['L2_exact']);r=evaluate(inp,m,delta,'triangles');lower=max(old,r.get('bound',old));curves=[]
   for c in a['curves']:
    T=F(c['T']);gap=None if c['relative_advantage_lower_exact'] is None else read(c['relative_advantage_lower_exact'])+(lower-old)*T*T;curves.append({'T':float(T),'strict':gap is not None and gap>0,'gap_exact':None if gap is None else pair(gap),'gap':None if gap is None else float(gap)})
   comparisons.append({'seed':a['seed'],'N':a['physical_qubits'],'L2_exact':pair(lower),'L2':float(lower),'raw_dual_bound_exact':None if 'bound' not in r else pair(r['bound']),'dual_nonzero':[[row['id'],pair(nu)] for row,nu in zip(r['rows'],r.get('multipliers',[])) if nu],'seconds':r['seconds'],'curves':curves})
  selections=[]
  for j,s in enumerate(d['selections']):
   eligible=[a for a in comparisons if a['N']<=base['physical_qubits'] and a['curves'][j]['strict']];sel=min(eligible,key=lambda a:(a['N'],-read(a['curves'][j]['gap_exact']),a['seed'])) if eligible else comparisons[0];selections.append({'T':s['T'],'selected_seed':sel['seed'],'certified_change':bool(eligible),'baseline_N':base['physical_qubits'],'selected_N':sel['N'],'saved_qubits':base['physical_qubits']-sel['N']})
  ws={k:(pair(v) if isinstance(v,F) else v) for k,v in w.items()};r={'name':d['name'],'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'input':inp,'moments_with_witness_upper':m,'witness':ws,'old_upper_exact':pair(oldU),'new_upper_exact':pair(U),'comparisons':comparisons,'selections':selections,'seconds':time.perf_counter()-st};(out/path.name).write_text(json.dumps(r,indent=2)+'\n');records.append({'name':d['name'],'n':inp['n'],'witness_seconds':w['seconds'],'witness_cost':float(w['cost']),'parent_upper':float(oldU),'new_upper':float(U),'seconds':r['seconds'],'selections':selections});print(json.dumps({'name':d['name'],'witness_seconds':w['seconds'],'costs':[float(oldU),float(U)],'primary':next(s for s in selections if s['T']==1/1024)}),flush=True)
 summary={}
 for k in range(6,13):
  T=1/2**k;rows=[next(s for s in r['selections'] if s['T']==T) for r in records];summary[str(T)]={'certified_changes':sum(s['certified_change'] for s in rows),'strict_qubit_reductions':sum(s['saved_qubits']>0 for s in rows),'mean_qubit_reduction_fraction':statistics.mean(s['saved_qubits']/s['baseline_N'] for s in rows)}
 result={'status':'complete','models':len(records),'candidates':sum(len(json.loads(p.read_text())['comparisons']) for p in out.glob('*.json')),'summary':summary,'witness_median_seconds':statistics.median(r['witness_seconds'] for r in records),'witness_total_seconds':sum(r['witness_seconds'] for r in records),'upper_improved_inputs':sum(r['new_upper']<r['parent_upper'] for r in records),'seconds':time.perf_counter()-start,'records':records};(HERE/('results/particular_summary.json' if args.particular else 'results/witness_summary.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
