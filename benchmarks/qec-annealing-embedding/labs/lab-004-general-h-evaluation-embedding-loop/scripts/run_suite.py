from __future__ import annotations
import sys,json,time,random,hashlib,argparse,math
from pathlib import Path
from collections import defaultdict
import networkx as nx
from evaluator import PRIOR,evaluate,get_groups,json_program,brief
from compiler import compile_instance,model_graph
from embedding import make_target,graph_witness,find_automatic_embedding,qubo_to_ising,verify_embedding,versions
LAB=Path(__file__).resolve().parents[1]; OUT=LAB/'results'
FAMILIES=['random_regular','irregular_hubs','rewired_band','mixed_hypergraph']
SEEDS=[11,29,47,71,101,137,173,211]


def instance(family,n,seed):
    rng=random.Random(seed+n*101+FAMILIES.index(family)*10007);m=n//2
    if family=='random_regular':rows=[sorted(rng.sample(range(n),4)) for _ in range(m)]
    elif family=='irregular_hubs':
        rows=[]
        for r in range(m):
            d=rng.randint(2,min(7,n)); pool=list(range(n))
            support=set(rng.sample(pool,d))
            if r%2==0:support.discard(max(support));support.add(r%3)
            rows.append(sorted(support))
    elif family=='rewired_band':
        rows=[]
        for r in range(m):
            support={(2*r+j)%n for j in range(4)}
            if r%3==0:support.discard((2*r+3)%n);support.add(rng.randrange(n))
            rows.append(sorted(support))
    else:
        # graphlike columns plus higher-column-degree hyperchecks and dependence
        rows=[set() for _ in range(m)]
        for col in range(n):
            for row in rng.sample(range(m),2):rows[row].add(col)
        for r in range(0,m,3):rows[r].update(rng.sample(range(n),rng.randint(3,6)))
        rows=[sorted(x) for x in rows]
        if m>=4:rows[-1]=sorted(set(rows[0])^set(rows[1]))
    truth=[rng.randrange(2) for _ in range(n)]
    syndrome=[sum(truth[i] for i in row)%2 for row in rows]
    w=[rng.randint(-2,6)/4 for _ in range(n)];w[0]=0.;w[1]=-.5
    return {'family':family,'n':n,'seed':seed,'split':'development' if seed==1101 else 'held_out',
            'rows':rows,'syndrome':syndrome,'weights':w,'hidden_feasibility_witness':truth}


def removable(source,target,emb,i,q):
    c=set(emb[i]);c.remove(q)
    if not c or (len(c)>1 and not nx.is_connected(target.subgraph(c))):return False
    for j in source[i]:
        if not any(r in target[p] for p in c for r in emb[j]):return False
    return True


def prune(source,target,emb,h,J,c,groups,floor=None):
    start=time.perf_counter();emb={i:list(ch) for i,ch in emb.items()}
    proposals=0;accepted=0;evaltime=0.;trace=[]
    for i in sorted(emb,key=lambda i:(-len(emb[i]),i)):
        for q in sorted(emb[i],reverse=True):
            if not removable(source,target,emb,i,q):continue
            proposals+=1
            candidate={v:(list(ch) if v!=i else [p for p in ch if p!=q]) for v,ch in emb.items()}
            p=evaluate(h,J,c,target,candidate,groups=groups,validate=False)
            evaltime+=p['elapsed_seconds']
            take=p['feasible'] and (floor is None or p['scale']>=floor*(1-1e-10))
            trace.append({'variable':i,'qubit':q,'accepted':take,'scale':p.get('scale'),
                          'qubits':p['physical_qubits']})
            if take:emb=candidate;accepted+=1
    final=evaluate(h,J,c,target,emb,groups=groups)
    return emb,final,{'graph_valid_proposals':proposals,'accepted':accepted,'evaluation_seconds':evaltime,
                      'total_seconds':time.perf_counter()-start,'trace':trace}


def save(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')


def one(data,target,groups,refine=True):
    name=f"{data['family']}_n{data['n']}_s{data['seed']}";start=time.perf_counter()
    cstart=time.perf_counter();model=compile_instance(data['rows'],data['n'],data['syndrome'],data['weights']);
    h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);comp=time.perf_counter()-cstart
    source=model_graph(model);candidates=[];failed=[]
    for seed in SEEDS:
        r=find_automatic_embedding(source,target,seed=seed,timeout=5.,tries=2)
        if r['status']!='valid':failed.append({k:v for k,v in r.items() if k!='embedding'});continue
        emb=r['embedding'];p=evaluate(h,J,c,target,emb,groups=groups)
        candidates.append({'seed':seed,'embedding':emb,'program':p,'embedding_seconds':r['elapsed_seconds']})
    if not candidates:
        result={'name':name,'input':data,'status':'all_heuristic_failures','failures':failed,'total_seconds':time.perf_counter()-start}
        save(OUT/(name+'.json'),result);return result
    feasible=[a for a in candidates if a['program']['feasible']]
    if not feasible:
        result={'name':name,'input':data,'status':'all_certificate_failures','failures':failed,
                'candidates':[{'seed':a['seed'],'embedding':a['embedding'],'evaluation':brief(a['program'])} for a in candidates],
                'total_seconds':time.perf_counter()-start}
        save(OUT/(name+'.json'),result);return result
    first=feasible[0];floor=first['program']['scale']
    size=min(feasible,key=lambda a:(a['program']['physical_qubits'],-a['program']['scale'],a['seed']))
    guided=min([a for a in feasible if a['program']['scale']>=floor*(1-1e-10)],
               key=lambda a:(a['program']['physical_qubits'],-a['program']['scale'],a['seed']))
    selected={'first':first,'size_only_pool':size,'guided_pool':guided}
    if refine:
        # Matched starting mapping isolates the effect of the acceptance rule.
        for label,threshold in [('guided_pruned',floor),('size_only_pruned',None)]:
            emb,p,stats=prune(source,target,guided['embedding'],h,J,c,groups,threshold)
            selected[label]={'seed':guided['seed'],'embedding':emb,'program':p,'pruning':stats}
    standard=evaluate(h,J,c,target,first['embedding'],groups=groups,allocation='total')
    sensitivity={str(beta):brief(evaluate(h,J,c,target,guided['embedding'],groups=groups,beta=beta)) for beta in [5.,10.,20.,40.]}
    # Fixed physical program temperature sweep, distinct from reprogramming above.
    fixed_temperature={}
    margins=list(guided['program']['edge_margins'].values())
    for beta in [5.,10.,20.,40.]:
        fixed_temperature[str(beta)]=-math.expm1(-sum(math.log1p(math.exp(-2*beta*v)) for v in margins))
    result={'name':name,'status':'ok','input':data,'model':model,
      'logical_ising':{'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c},
      'compile_seconds':comp,'failures':failed,'scale_floor':floor,
      'candidates':[{'seed':a['seed'],'embedding':a['embedding'],'evaluation':brief(a['program']),
                     'embedding_seconds':a['embedding_seconds']} for a in candidates],
      'selected':{label:{'seed':a['seed'],'embedding':a['embedding'],'program':json_program(a['program']),
                         **({'pruning':a['pruning']} if 'pruning' in a else {})} for label,a in selected.items()},
      'standard_total_load':brief(standard),'temperature_reprogrammed':sensitivity,
      'temperature_fixed_program':fixed_temperature,'total_seconds':time.perf_counter()-start}
    save(OUT/(name+'.json'),result)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pilot',action='store_true');ap.add_argument('--resume',action='store_true');args=ap.parse_args()
    target=make_target(6,4);groups=get_groups(target);OUT.mkdir(exist_ok=True)
    save(OUT/'target.json',{'target':graph_witness(target),'coupling_groups':groups,'versions':versions()})
    save(OUT/'source_provenance.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [PRIOR/'compiler.py',PRIOR/'embedding.py']})
    inputs=[instance(f,n,s) for f in FAMILIES for n in [16,32,64] for s in [1101,2203,3307]]
    if args.pilot:inputs=inputs[:1]
    summaries=[]
    for data in inputs:
        name=f"{data['family']}_n{data['n']}_s{data['seed']}";path=OUT/(name+'.json')
        if args.resume and path.exists():r=json.loads(path.read_text())
        else:r=one(data,target,groups)
        summary={k:r[k] for k in ['name','status','total_seconds']}
        if r['status']=='ok':summary['selected']={label:brief(a['program']) for label,a in r['selected'].items()}
        summaries.append(summary);save(OUT/'suite_progress.json',summaries)
        print(json.dumps(summary),flush=True)
    save(OUT/'suite_summary.json',summaries)
if __name__=='__main__':main()
