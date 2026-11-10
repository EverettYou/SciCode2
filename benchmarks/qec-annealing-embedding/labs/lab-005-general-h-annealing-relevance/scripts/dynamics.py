"""Conductance limitation for a declared classical late-hold local-bath model."""
from pathlib import Path
import sys,json,math,time
import numpy as np
from models import compile_model
from evaluator import evaluate,json_program,get_groups
from lp_allocator import allocate_lp
from embedding import graph_from_witness,qubo_to_ising
LAB=Path(__file__).resolve().parents[1];OUT=LAB/'results'


def kernel_candidates(data,witness):
    B=set(witness['basis_columns']);R=witness['basis_rows'];deltas=[set(x) for x in witness['repair_columns']];fundamental=[]
    for i in range(data['n']):
        if i in B:continue
        v={i}
        for row,delta in zip(R,deltas):
            if i in data['rows'][row]:v^=delta
        if not all(sum(j in v for j in row)%2==0 for row in data['rows']):raise AssertionError('not a kernel vector')
        cost=sum(abs(data['weights'][j]) for j in v)
        fundamental.append({'free_origin':i,'kernel_support':sorted(v),'absolute_weight_cost':cost})
    result=[]
    for i in range(data['n']):
        candidates=[v for v in fundamental if i in v['kernel_support']]
        if candidates:result.append({'original_variable':i,**min(candidates,key=lambda v:(v['absolute_weight_cost'],len(v['kernel_support']),v['free_origin']))})
    return result


def certificate(data,witness,embedding,p,rounding_tv=1e-10):
    roots={int(i):q for i,q in p['roots'].items()};trees={int(i):[tuple(e) for e in es] for i,es in p['chain_trees'].items()}
    margins={(q,r):v for q,r,v in p['edge_margins']} if isinstance(p['edge_margins'],list) else p['edge_margins']
    N=p['physical_qubits'];beta=p['beta'];t=beta*p['scale'];epsilon=p['classical_break_bound'];entries=[]
    for kv in kernel_candidates(data,witness):
        i=kv['original_variable']
        if len(embedding[i])<=1:continue
        logical_min=math.exp(-float(np.logaddexp(0.,t*kv['absolute_weight_cost'])))
        lower=max(0.,logical_min-epsilon-rounding_tv)
        ep=-math.expm1(-sum(math.log1p(math.exp(-2*beta*margins[e])) for e in trees[i]))
        row={**kv,'branch_size':len(embedding[i]),'branch_defect_bound':ep,'logical_marginal_min':logical_min,
             'physical_marginal_min':lower,'root':roots[i]}
        if lower<=0:row['status']='inconclusive_variance'
        else:
            gap=min(1.,ep/(N*lower*(1-lower)));row.update({'status':'certified','gap_upper_per_attempt':gap,
              'mixing_time_lower_attempts_tv_quarter':math.log(2)/(-math.log1p(-gap)) if 0<gap<1 else (math.inf if gap==0 else 0.)})
            row['mixing_time_lower_sweeps_tv_quarter']=row['mixing_time_lower_attempts_tv_quarter']/N
        entries.append(row)
    finite=[e for e in entries if e['status']=='certified']
    strongest=max(finite,key=lambda e:e['mixing_time_lower_sweeps_tv_quarter']) if finite else None
    return {'status':'certified' if strongest else 'inconclusive','entries':entries,'strongest':strongest,
            'model':'random-scan single-site heat-bath at fixed beta, Gamma=0; one physical-site attempt per step',
            'interpretation':'worst-case mixing-time lower bound, not decoding-success ordering'}


def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']]
    folder=OUT/'dynamics';folder.mkdir(exist_ok=True);rows=[];start=time.perf_counter()
    for path in sorted(OUT.glob('*_balanced.json')):
        r=json.loads(path.read_text())
        if r['status']!='ok':continue
        emb={int(i):c for i,c in r['selected']['embedding'].items()};m=r['model'];h,J,c=qubo_to_ising(m['linear'],m['quadratic'],m['offset']);curves=[]
        for beta in [10.,20.,40.,80.]:
            u=evaluate(h,J,c,target,emb,groups=groups,beta=beta);p=allocate_lp(h,J,c,target,emb,u,groups)
            if not p['feasible'] or p['scale']<u['scale']:p=u
            pw=json_program(p);cert=certificate(r['input'],r['repair_witness'],emb,pw)
            curves.append({'beta':beta,'program':pw,'certificate':cert})
            rows.append({'name':r['name'],'beta':beta,'status':cert['status'],'strongest':cert['strongest']})
        (folder/(r['name']+'.json')).write_text(json.dumps({'name':r['name'],'source_file':path.name,'curves':curves},indent=2)+'\n')
    (OUT/'dynamics_summary.json').write_text(json.dumps({'records':rows,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n')
    print('models',len(rows)//4,'certified',sum(r['status']=='certified' for r in rows))
if __name__=='__main__':main()
