"""Full tiny embedded forward QA, using saved seed11 Zephyr placements.

Includes physical chain spins and a majority readout (tie -> bit0). All actual
programmed coefficients satisfy the same parametric hardware limits as the
resource sweep. No QPU schedule or open-system simulation is claimed.
"""
import json, importlib.util, time, argparse
from pathlib import Path
import numpy as np
from models import *
from dynamics import run_model, ground_truth, aggregate

LAB=Path(__file__).resolve().parents[1]
prev=Path(__file__).resolve().parents[2]/'lab-002-agent-test-general-h'/'scripts'/'embedding.py'
spec=importlib.util.spec_from_file_location('previous_embedding',prev)
emb=importlib.util.module_from_spec(spec)
spec.loader.exec_module(emb)


def program(logical,target,embedding):
    allocation=emb.allocate_physical(dict(enumerate(logical['h'])),
        {(i,j):c for i,j,c in logical['J']},logical['offset'],target,embedding,
        h_range=(-1.,1.),j_range=(-1.,1.),group_range=(-13.,10.),cap_scale=False)
    nodes=sorted(allocation['h_raw'])
    order={q:i for i,q in enumerate(nodes)}
    physical=dict(n=len(nodes),h=[allocation['h_raw'][q] for q in nodes],
        J=[(order[q],order[r],v) for (q,r),v in allocation['J_raw'].items()],
        offset=allocation['offset_raw'],kind='physical')
    return physical,allocation,nodes,order


def masks(logical,physical,patch,syndrome,weights,best_cost,embedding,order):
    bits=all_bits(physical['n'])
    decoded=np.zeros((len(bits),logical['n']),dtype=np.uint8)
    consistent=np.ones(len(bits),dtype=bool)
    for i,branch in embedding.items():
        positions=[order[q] for q in branch]
        ones=bits[:,positions].sum(axis=1)
        decoded[:,i]=ones>len(branch)/2
        consistent &= (ones==0)|(ones==len(branch))
    errors=decode_bits(logical,patch,decoded)
    residual=((errors @ patch['H'].T)%2+np.asarray(syndrome,dtype=np.uint8))%2
    feasible=np.all(residual==0,axis=1)
    success=feasible & np.isclose(errors @ np.asarray(weights),best_cost,rtol=0,atol=1e-10)
    corrections=np.array([reference_error(patch['H'],s) for s in np.eye(len(patch['H']),dtype=np.uint8)])
    repaired=(errors+residual @ corrections)%2
    repaired_success=np.isclose(repaired @ np.asarray(weights),best_cost,rtol=0,atol=1e-10)
    diagonal=ising_diagonal(physical)
    ground=np.isclose(diagonal,diagonal.min(),rtol=0,atol=1e-10)
    assert np.all(feasible[ground])
    if logical['kind']=='direct':
        assert np.all(success[ground])
    else:
        # A losing logical sector has its own valid ground state, which is not
        # a global decoding optimum; do not incorrectly require it to win.
        sector_errors=decode_bits(logical,patch,all_bits(logical['n']))
        sector_best=float((sector_errors @ np.asarray(weights)).min())
        assert np.allclose((errors @ np.asarray(weights))[ground],sector_best)
    assert np.all(consistent[ground])
    return diagonal,[success,feasible,ground,repaired_success],consistent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=11)
    args=parser.parse_args()
    start=time.perf_counter()
    target=emb.make_target(6)
    placements={}
    for name in ['direct','dual']:
        witness=json.loads((LAB/'results'/f'resource_witness_d2_{name}_seed{args.seed}.json').read_text())
        placements[name]={int(k):v for k,v in witness['embedding'].items()}
    patch=make_patch(2)
    budgets=[.5,2.,8.,32.,128.]
    times=sorted(set(budgets+[t/2 for t in budgets]))
    cases=[]
    for wi,weights in enumerate([[1.]*patch['n'],[1.,1.25,1.5,.75,1.75]]):
        for syndrome in all_bits(len(patch['H'])):
            truth=ground_truth(patch,syndrome,weights)
            R=repair_radius(patch,weights)
            logicals=[direct_model(patch,syndrome,weights),
                      direct_model(patch,syndrome,weights,R+1),
                      dual_model(patch,syndrome,weights,0),dual_model(patch,syndrome,weights,1)]
            names=['direct_global','direct_local','dual_0','dual_1']
            programs=[program(m,target,placements[m['kind']]) for m in logicals]
            scales=[p[1]['scale'] for p in programs]
            scales[2]=scales[3]=min(scales[2:])
            records={}; witnesses={}; baselines={}
            for name,logical,(physical,allocation,nodes,order),alpha in zip(names,logicals,programs,scales):
                diagonal,mask,consistent=masks(logical,physical,patch,syndrome,weights,
                                               truth['best_cost'],placements[logical['kind']],order)
                required=times if name.startswith('direct') else [t/2 for t in budgets]
                records[name]={str(T):run_model(physical,diagonal,mask,alpha,T,refine=True) for T in required}
                baselines[name]={'p_success':float(mask[0].mean()),'p_repaired_success':float(mask[3].mean()),
                                 'p_chain_consistent':float(consistent.mean())}
                witnesses[name]={'logical_model':logical,'physical_raw':physical,'alpha':alpha,
                                 'physical_nodes':nodes,'embedding':placements[logical['kind']],
                                 'chain_strength_raw':allocation['chain_strength_raw'],
                                 'ranges':allocation['ranges']}
            scores=[]
            for C in budgets:
                t=C/2
                p0=records['dual_0'][str(t)]['p_success']
                p1=records['dual_1'][str(t)]['p_success']
                row={'total_anneal_time':C,'dual_two_sectors':1-(1-p0)*(1-p1)}
                for name in names[:2]:
                    p=records[name][str(C)]['p_success']; q=records[name][str(t)]['p_success']
                    r=records[name][str(C)]['p_repaired_success']; s=records[name][str(t)]['p_repaired_success']
                    row.update({name+'_one_run':p,name+'_two_runs':1-(1-q)**2,
                                name+'_repaired_one_run':r,name+'_repaired_two_runs':1-(1-s)**2})
                scores.append(row)
            cases.append({'width':2,'height':2,'weights_label':'uniform' if wi==0 else 'heterogeneous_dyadic',
                          'weights':weights,'syndrome':syndrome.tolist(),'truth':truth,'records':records,
                          'scores':scores,'physical_witnesses':witnesses,'random_readout_baselines':baselines})
            print(json.dumps({'case':len(cases),'last_scores':scores[-1],'elapsed':time.perf_counter()-start}),flush=True)
    result={'status':'complete','schema':'surface-physical-qa-v1','geometry':'2x2 planar patch',
        'target':'ideal Zephyr Z6','embedding_seed':args.seed,'schedule':'H=-(1-u)sumX+u*Hprogrammed',
        'readout':'chain majority, tie->bit0; optional fixed GF2 right-inverse syndrome repair',
        'sector_accounting':'two dual runs C/2 each; direct one C or two C/2; equal total anneal time',
        'cases':cases,'aggregate':aggregate(cases),'elapsed_seconds':time.perf_counter()-start,
        'max_refinement_score_difference':max(r['refinement']['max_score_difference'] for c in cases
              for variant in c['records'].values() for r in variant.values()),
        'max_norm_error':max(r['norm_error'] for c in cases for variant in c['records'].values() for r in variant.values())}
    destination=LAB/'results'/('dynamics_physical_square2'+('' if args.seed==11 else f'_seed{args.seed}')+'.json')
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'output':str(destination),'elapsed':result['elapsed_seconds'],
                     'max_refinement':result['max_refinement_score_difference']}),flush=True)


if __name__=='__main__': main()
