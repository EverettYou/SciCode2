"""Matched actual-physical forward anchors; reference optimum only scores outputs."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,time,random,subprocess,math
sys.dont_write_bytecode=True
from penalty_bound import witness,compile_with_bound,load_module
from forward_certificate import cost_moments,amplify,certificate
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'))
from evaluator import evaluate,json_program
from embedding import graph_from_witness,qubo_to_ising,find_automatic_embedding
from compiler import model_graph
from numeric_certificate import rational_audit
OUT=LAB/'results/forward_anchors';OUT.mkdir(exist_ok=True)
FAMILIES=['random_triples','irregular_pairs_triples','rewired_triple_band','dependent_mixed']

def instance(family,n,seed):
    rng=random.Random(seed+n*1009+FAMILIES.index(family)*10007);m=n//2
    if family=='random_triples':rows=[sorted(rng.sample(range(n),3)) for _ in range(m)]
    elif family=='irregular_pairs_triples':
        rows=[]
        for i in range(m):
            support=set(rng.sample(range(n),rng.choice([2,3])))
            if i%2==0:support.discard(max(support));support.add(0)
            rows.append(sorted(support))
    elif family=='rewired_triple_band':
        rows=[sorted({(2*i+j)%n for j in [0,1,3]}) for i in range(m)]
        rows[-1]=sorted(set(rows[-1][:-1]+[rng.randrange(n)]))
    else:
        rows=[sorted(rng.sample(range(n),rng.choice([2,3]))) for _ in range(m-1)];rows.append(sorted(set(rows[0])^set(rows[1])))
    truth=[rng.randrange(2) for _ in range(n)];s=[sum(truth[i] for i in row)%2 for row in rows];w=[rng.randrange(-2,7)/4 for _ in range(n)];w[0]=0;w[1]=-.5
    return {'family':family,'n':n,'seed':seed,'rows':rows,'syndrome':s,'weights':w,'split':'physical_forward_validation_anchors'}

def reference(data):
    st=time.perf_counter();best=None;patterns=[]
    for state in range(1<<data['n']):
        bits=[(state>>i)&1 for i in range(data['n'])]
        if any(sum(bits[i] for i in row)%2!=s for row,s in zip(data['rows'],data['syndrome'])):continue
        cost=sum(F(w)*bits[i] for i,w in enumerate(data['weights']))
        if best is None or cost<best:best=cost;patterns=[state]
        elif cost==best:patterns.append(state)
    return {'minimum_cost_exact':[best.numerator,best.denominator],'optimal_patterns':patterns,'seconds':time.perf_counter()-st}

def write_input(path,program,embedding,n,patterns):
    nodes=sorted(q for q,v in program['h']);idx={q:i for i,q in enumerate(nodes)};h=dict(program['h']);roots={int(i):q for i,q in program['roots'].items()};owners={q:i for i,ch in embedding.items() for q in ch}
    assert sorted(roots)==list(range(len(roots)))
    lines=[f"{len(nodes)} {len(program['J'])} {n} {len(roots)} {len(patterns)}",' '.join(format(h[q],'.17g') for q in nodes)]
    lines += [f'{idx[q]} {idx[r]} {v:.17g}' for q,r,v in program['J']]
    lines+=[' '.join(str(idx[roots[i]]) for i in range(n)),' '.join(str(idx[roots[i]]) for i in range(len(roots))),' '.join(str(owners[q]) for q in nodes),' '.join(map(str,patterns))]
    path.write_text('\n'.join(lines)+'\n')

def propagate(path,T,budget_start):
    steps=128
    while steps<64*T:steps*=2
    levels=[]
    while steps<=8192:
        if time.perf_counter()-budget_start>2700:return {'status':'overall_backend_budget','levels':levels}
        st=time.perf_counter()
        try:r=subprocess.run([str(LAB/'independent/quantum_forward_backend'),str(path),str(T),str(steps)],capture_output=True,text=True,timeout=180)
        except subprocess.TimeoutExpired:return {'status':'propagation_timeout','steps':steps,'levels':levels,'call_seconds':time.perf_counter()-st}
        if r.returncode:return {'status':'backend_error','steps':steps,'stderr':r.stderr,'levels':levels}
        data=json.loads(r.stdout);levels.append(data)
        if len(levels)>1:
            delta=max(abs(levels[-1][key]-levels[-2][key]) for key in ['original_optimal','chain_broken','full_ground'])
            if delta<=2e-5 and abs(data['norm']-1)<1e-8:return {'status':'converged','final':data,'last_probability_change':delta,'levels':levels}
        steps*=2
    return {'status':'step_cap_unresolved','levels':levels,'final':levels[-1]}

def main():
    start=time.perf_counter();td=json.loads((OLD/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in group] for group in td['coupling_groups']];summary=[]
    for family in FAMILIES:
        for n in [6,8]:
            for seed in [9611,9623]:
                name=f'{family}_n{n}_s{seed}';file=OUT/(name+'.json')
                if file.exists():
                    result=json.loads(file.read_text());summary.append(result);continue
                data=instance(family,n,seed);cert=witness(data['rows'],n,data['weights']);old=compile_with_bound(data['rows'],n,data['syndrome'],data['weights'],cert,'global');new=compile_with_bound(data['rows'],n,data['syndrome'],data['weights'],cert,'repair')
                h,J,c=qubo_to_ising(old['linear'],old['quadratic'],old['offset']);embedding=None;search=[]
                for mmseed in [11,29,47]:
                    r=find_automatic_embedding(model_graph(old),target,seed=mmseed,timeout=5.,tries=2);search.append({k:v for k,v in r.items() if k!='embedding'})
                    if r['status']=='valid':embedding=r['embedding'];break
                if embedding is None:result={'name':name,'input':data,'status':'embedding_failed','search':search};file.write_text(json.dumps(result,indent=2)+'\n');summary.append(result);continue
                p0=json_program(evaluate(h,J,c,target,embedding,groups=groups));eta=F(p0['scale'])*F(old['penalty'])/F(new['penalty']);p1,params=amplify(p0,data['weights'],eta)
                audits=[rational_audit(model,p,embedding,target,groups) for model,p in [(old,p0),(new,p1)]];assert all(x['float_projected_ground_states_certified'] for x in audits)
                moments=cost_moments(data['rows'],n,data['syndrome'],data['weights'],cert);short=certificate(moments,params)
                result={'name':name,'input':data,'status':'prepared','embedding':embedding,'old_model':old,'new_model':new,'baseline_program':p0,'amplified_program':p1,'static_audits':audits,
                  'cost_moments':moments,'short_certificate':short,'parameters':{k:[v.numerator,v.denominator] for k,v in params.items()},'search':search,'dynamics':{}}
                if len(p0['h'])>20:result['status']='state_cap_skipped';file.write_text(json.dumps(result,indent=2)+'\n');summary.append(result);continue
                ref=reference(data);result['reference']=ref;paths={}
                for label,p in [('baseline',p0),('amplified',p1)]:
                    paths[label]=OUT/(name+'_'+label+'.dat');write_input(paths[label],p,embedding,n,ref['optimal_patterns'])
                for T in [.05,.25,1.,4.,16.]:
                    result['dynamics'][str(T)]={}
                    for label in ['baseline','amplified']:
                        result['dynamics'][str(T)][label]=propagate(paths[label],T,start)
                        file.write_text(json.dumps(result,indent=2)+'\n')
                    print(json.dumps({'name':name,'T':T,'N':len(p0['h']),'statuses':{k:v['status'] for k,v in result['dynamics'][str(T)].items()},'probabilities':{k:v.get('final',{}).get('original_optimal') for k,v in result['dynamics'][str(T)].items()}}),flush=True)
                result['status']='completed';file.write_text(json.dumps(result,indent=2)+'\n');summary.append(result)
                (LAB/'results/forward_anchor_progress.json').write_text(json.dumps({'finished':len(summary),'total':16,'elapsed_seconds':time.perf_counter()-start})+'\n')
    out={'status':'completed','instances':len(summary),'seconds':time.perf_counter()-start,'records':[{'name':d['name'],'status':d['status'],'physical_spins':len(d.get('baseline_program',{}).get('h',[])),'dynamics':d.get('dynamics',{})} for d in summary]}
    (LAB/'results/forward_anchor_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'instances':out['instances'],'seconds':out['seconds']}))
if __name__=='__main__':main()
