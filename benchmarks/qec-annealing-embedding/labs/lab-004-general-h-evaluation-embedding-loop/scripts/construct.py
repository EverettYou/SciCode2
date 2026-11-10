"""Reusable general sparse-H constructor; no family metadata or decoding solve.

Input JSON: n,rows,syndrome,weights; optionally target witness and coupling_groups.
Default target is ideal Zephyr g6,t4. Output includes full model/target/program.
"""
import argparse,json,time
from pathlib import Path
from evaluator import evaluate,get_groups,json_program,brief
from compiler import compile_instance,model_graph
from embedding import make_target,graph_witness,graph_from_witness,find_automatic_embedding,qubo_to_ising,versions
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit


def construct(data,g=6,seeds=(11,29,47,71,101,137,173,211),timeout=5.,beta=20.,epsilon=.05,use_lp=True):
    start=time.perf_counter();model=compile_instance(data['rows'],data['n'],data['syndrome'],data['weights'],penalty=data.get('penalty'))
    if 'target' in data:
        target=graph_from_witness(data['target'])
        if 'coupling_groups' not in data:raise ValueError('custom target requires explicit coupling_groups')
        groups=[[tuple(e) for e in group] for group in data['coupling_groups']]
    else:target=make_target(g,4);groups=get_groups(target)
    ranges=data.get('ranges',{});hr=tuple(ranges.get('h',[-4.,4.]));jr=tuple(ranges.get('J',[-1.,1.]));gr=tuple(ranges.get('group',[-13.,10.]))
    source=model_graph(model);h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);candidates=[];failures=[];floor=None
    for seed in seeds:
        found=find_automatic_embedding(source,target,seed=int(seed),timeout=timeout,tries=2)
        if found['status']!='valid':failures.append({k:v for k,v in found.items() if k!='embedding'});continue
        emb=found['embedding'];u=evaluate(h,J,c,target,emb,beta=beta,epsilon=epsilon,groups=groups,h_range=hr,j_range=jr,group_range=gr)
        if not u['feasible']:
            failures.append({'seed':seed,'status':'uniform_certificate_inconclusive','evaluation':u});continue
        if floor is None:floor=u['scale']
        p=allocate_lp(h,J,c,target,emb,u,groups) if use_lp and h else u
        if not p['feasible']:p=u
        witness=json_program(p);audit=rational_audit(model,witness,emb,target,groups)
        candidates.append({'seed':seed,'embedding':emb,'program':p,'numeric_certificate':audit,
                           'embedding_seconds':found['elapsed_seconds'],'uniform_scale':u['scale']})
    eligible=[x for x in candidates if x['numeric_certificate']['float_projected_ground_states_certified']
              and x['program']['scale']>=floor and x['program']['classical_break_bound']<=epsilon] if floor is not None else []
    # LP backoff can lose a tied floor; restore a certified uniform program.
    if not eligible and candidates:
        x=candidates[0];p=evaluate(h,J,c,target,x['embedding'],beta=beta,epsilon=epsilon,groups=groups,h_range=hr,j_range=jr,group_range=gr)
        audit=rational_audit(model,json_program(p),x['embedding'],target,groups)
        if audit['float_projected_ground_states_certified'] and p['classical_break_bound']<=epsilon:
            eligible=[{**x,'program':p,'numeric_certificate':audit}]
    selected=min(eligible,key=lambda x:(x['program']['physical_qubits'],-x['program']['scale'],x['seed'])) if eligible else None
    return {'schema':'general-h-certified-thermal-embedding-v1','status':'certified_program' if selected else 'no_certified_program_found',
      'input':{k:data[k] for k in ['n','rows','syndrome','weights']},'model':model,
      'logical_ising':{'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c},
      'target':graph_witness(target),'coupling_groups':groups,'versions':versions(),'scale_floor':floor,
      'selected':{'seed':selected['seed'],'embedding':selected['embedding'],'program':json_program(selected['program']),
                   'numeric_certificate':selected['numeric_certificate']} if selected else None,
      'candidate_summaries':[{'seed':x['seed'],'embedding_seconds':x['embedding_seconds'],'evaluation':brief(x['program'])} for x in candidates],
      'failures':failures,'total_seconds':time.perf_counter()-start,
      'guarantee_scope':'static projected ground-state fidelity and conditional terminal Gibbs robustness; no finite-time QA success ordering'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--g',type=int,default=6);ap.add_argument('--beta',type=float,default=20.);ap.add_argument('--epsilon',type=float,default=.05)
    ap.add_argument('--uniform',action='store_true');args=ap.parse_args()
    result=construct(json.loads(args.input.read_text()),g=args.g,beta=args.beta,epsilon=args.epsilon,use_lp=not args.uniform)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'total_seconds':result['total_seconds'],
                     'qubits':result['selected']['program']['physical_qubits'] if result['selected'] else None}))
if __name__=='__main__':main()
