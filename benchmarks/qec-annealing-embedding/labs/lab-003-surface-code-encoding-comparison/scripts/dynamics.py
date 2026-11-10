"""Reproducible closed-system forward QA; midpoint Strang, with convergence.

H(u)=-(1-u) sum X + u*alpha*(H_P-offset), u=t/T; initial uniform |+>.
Each logical spin is treated as native in this primary encoding comparison.
Hardware embedding is a separate resource comparison and tiny follow-up.
"""
from pathlib import Path
import argparse, json, math, time
import numpy as np
from numba import njit
from models import (make_patch, direct_model, dual_model, reference_error,
                    repair_radius, coefficient_scale, all_bits, ising_diagonal, decode_bits)

LAB=Path(__file__).resolve().parents[1]


@njit(cache=True)
def evolve(diagonal, n, total_time, steps):
    dim=len(diagonal)
    state=np.ones(dim,dtype=np.complex128)/math.sqrt(dim)
    dt=total_time/steps
    for k in range(steps):
        u=(k+0.5)/steps
        for a in range(dim):
            state[a] *= np.exp(-0.5j*dt*u*diagonal[a])
        theta=dt*(1-u)
        co=math.cos(theta)
        si=1j*math.sin(theta)
        for bit in range(n):
            stride=1<<bit
            for base in range(0,dim,2*stride):
                for a in range(base,base+stride):
                    b=a+stride
                    va=state[a]
                    vb=state[b]
                    state[a]=co*va+si*vb
                    state[b]=si*va+co*vb
        for a in range(dim):
            state[a] *= np.exp(-0.5j*dt*u*diagonal[a])
    return state


def ground_truth(patch, syndrome, weights):
    bits=all_bits(patch['n'])
    feasible=np.all((bits @ patch['H'].T)%2==np.asarray(syndrome),axis=1)
    costs=bits @ np.asarray(weights)
    best=float(costs[feasible].min())
    return dict(best_cost=best, optimum_count=int(np.sum(feasible & np.isclose(costs,best))),
                feasible_count=int(np.sum(feasible)))


def masks_for_model(model, patch, syndrome, weights, best_cost):
    bits=all_bits(model['n'])
    errors=decode_bits(model,patch,bits)
    feasible=np.all((errors @ patch['H'].T)%2==np.asarray(syndrome),axis=1)
    costs=errors @ np.asarray(weights)
    success=feasible & np.isclose(costs,best_cost,rtol=0,atol=1e-10)
    diagonal=ising_diagonal(model)
    ground=np.isclose(diagonal,diagonal.min(),rtol=0,atol=1e-10)
    # Optional non-optimizing classical repair, included so a poor feasible
    # fraction is not the only reason direct encoding loses. This is a fixed
    # GF(2) right inverse, independent of weights and of the optimum.
    corrections=np.array([reference_error(patch['H'],s) for s in np.eye(len(patch['H']),dtype=np.uint8)])
    residual=((errors @ patch['H'].T)%2 + np.asarray(syndrome,dtype=np.uint8))%2
    repaired=(errors + residual @ corrections)%2
    assert np.all((repaired @ patch['H'].T)%2==np.asarray(syndrome))
    repaired_success=np.isclose(repaired @ np.asarray(weights),best_cost,rtol=0,atol=1e-10)
    return diagonal,success,feasible,ground,repaired_success


def run_model(model, diagonal, masks, alpha, T, steps_per_time=24., min_steps=96, refine=False):
    steps=max(min_steps,int(math.ceil(T*steps_per_time)))
    diagonal=np.asarray(alpha*(diagonal-diagonal.mean()),dtype=float)
    state=evolve(diagonal,model['n'],float(T),steps)
    prob=np.abs(state)**2
    result=dict(time=float(T),steps=steps,alpha=float(alpha),n_spins=model['n'],
                p_success=float(prob[masks[0]].sum()),p_feasible=float(prob[masks[1]].sum()),
                p_programmed_ground=float(prob[masks[2]].sum()),norm_error=float(abs(prob.sum()-1)))
    if len(masks)>3:
        result['p_repaired_success']=float(prob[masks[3]].sum())
    if refine:
        fine=evolve(diagonal,model['n'],float(T),2*steps)
        p2=np.abs(fine)**2
        fine_scores=[float(p2[m].sum()) for m in masks]
        result['refinement']=dict(steps=2*steps,p_success=fine_scores[0],p_feasible=fine_scores[1],
                                 p_programmed_ground=fine_scores[2],norm_error=float(abs(p2.sum()-1)),
                                 max_score_difference=max(abs(fine_scores[i]-result[k]) for i,k in
                                   enumerate(['p_success','p_feasible','p_programmed_ground']+
                                             (['p_repaired_success'] if len(masks)>3 else []))))
        result['p_success']=fine_scores[0]
        result['p_feasible']=fine_scores[1]
        result['p_programmed_ground']=fine_scores[2]
        if len(masks)>3:
            result['refinement']['p_repaired_success']=fine_scores[3]
            result['p_repaired_success']=fine_scores[3]
        result['norm_error']=float(abs(p2.sum()-1))
        result['reported_steps']=2*steps
    return result


def compare_case(width,height,syndrome,weights,budgets,refine=True):
    patch=make_patch(width,height)
    truth=ground_truth(patch,syndrome,weights)
    e0=reference_error(patch['H'],syndrome)
    direct_global=direct_model(patch,syndrome,weights)
    R=repair_radius(patch,weights)
    direct_local=direct_model(patch,syndrome,weights,penalty=R+1.)
    dual=[dual_model(patch,syndrome,weights,ell,e0) for ell in [0,1]]
    models=[direct_global,direct_local,*dual]
    names=['direct_global','direct_local','dual_0','dual_1']
    alphas=[coefficient_scale([direct_global]),coefficient_scale([direct_local]),
            coefficient_scale(dual),coefficient_scale(dual)]
    times=sorted(set([float(b) for b in budgets]+[float(b)/2 for b in budgets]))
    records={}
    for name,model,alpha in zip(names,models,alphas):
        diagonal,*masks=masks_for_model(model,patch,syndrome,weights,truth['best_cost'])
        required=times if name.startswith('direct') else [float(b)/2 for b in budgets]
        records[name]={str(T):run_model(model,diagonal,masks,alpha,T,refine=refine) for T in required}
    scores=[]
    for C in budgets:
        C=float(C); t=C/2
        p0=records['dual_0'][str(t)]['p_success']
        p1=records['dual_1'][str(t)]['p_success']
        row=dict(total_anneal_time=C,dual_two_sectors=1-(1-p0)*(1-p1))
        for name in names[:2]:
            p_long=records[name][str(C)]['p_success']
            p_half=records[name][str(t)]['p_success']
            row[name+'_one_run']=p_long
            row[name+'_two_runs']=1-(1-p_half)**2
            r_long=records[name][str(C)]['p_repaired_success']
            r_half=records[name][str(t)]['p_repaired_success']
            row[name+'_repaired_one_run']=r_long
            row[name+'_repaired_two_runs']=1-(1-r_half)**2
        scores.append(row)
    return dict(width=width,height=height,syndrome=list(map(int,syndrome)),weights=list(map(float,weights)),
                truth=truth,reference_error=e0.tolist(),repair_radius=R,
                penalties=[direct_global['penalty'],direct_local['penalty']],records=records,scores=scores)


def aggregate(cases):
    budgets=[s['total_anneal_time'] for s in cases[0]['scores']]
    out=[]
    for i,C in enumerate(budgets):
        keys=[k for k in cases[0]['scores'][i] if k!='total_anneal_time']
        row={'total_anneal_time':C}
        for k in keys:
            values=np.array([case['scores'][i][k] for case in cases])
            row[k]={'mean':float(values.mean()),'min':float(values.min()),'max':float(values.max())}
        pdual=np.array([c['scores'][i]['dual_two_sectors'] for c in cases])
        for name in ['direct_global','direct_local']:
            # Deliberately let direct use the better of its one- and two-run
            # strategies as a generous post-hoc comparison, explicitly labeled.
            best=np.array([max(c['scores'][i][name+'_one_run'],c['scores'][i][name+'_two_runs']) for c in cases])
            row['dual_minus_'+name+'_best']={'mean':float(np.mean(pdual-best)),
                'wins':int(np.sum(pdual-best>1e-3)),'losses':int(np.sum(pdual-best< -1e-3)),
                'ties_within_1e-3':int(np.sum(abs(pdual-best)<=1e-3))}
            best_repaired=np.array([max(c['scores'][i][name+'_repaired_one_run'],c['scores'][i][name+'_repaired_two_runs']) for c in cases])
            row['dual_minus_'+name+'_best_repaired']={'mean':float(np.mean(pdual-best_repaired)),
                'wins':int(np.sum(pdual-best_repaired>1e-3)),'losses':int(np.sum(pdual-best_repaired< -1e-3)),
                'ties_within_1e-3':int(np.sum(abs(pdual-best_repaired)<=1e-3))}
        out.append(row)
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--suite',choices=['square2','rectangle23'],default='square2')
    args=parser.parse_args()
    started=time.perf_counter()
    width,height=(2,2) if args.suite=='square2' else (2,3)
    patch=make_patch(width,height)
    weights_sets=[[1.]*patch['n']]
    if args.suite=='square2':
        weights_sets.append([1.,1.25,1.5,.75,1.75])
        budgets=[.5,2.,8.,32.,128.]
    else:
        budgets=[1.,4.,16.]
    cases=[]
    destination=LAB/'results'/('dynamics_'+args.suite+'.json')
    for wi,weights in enumerate(weights_sets):
        for syndrome in all_bits(len(patch['H'])):
            case=compare_case(width,height,syndrome,weights,budgets,refine=True)
            case['weights_label']='uniform' if wi==0 else 'heterogeneous_dyadic'
            cases.append(case)
            print(json.dumps({'suite':args.suite,'case':len(cases),'syndrome':syndrome.tolist(),
                              'last_scores':case['scores'][-1],'elapsed':time.perf_counter()-started}),flush=True)
            result=dict(schema='surface-qa-comparison-v1',suite=args.suite,status='running',
                model='closed system, linear schedule, uniform transverse driver per spin',
                coefficient_limits={'h':[-1,1],'J':[-1,1]},scale_cap=False,
                sector_accounting='two sequential dual sector runs at C/2 each; direct one at C or two at C/2',
                ensemble='all syndromes equally weighted; not a noise-distributed threshold experiment',
                cases=cases,aggregate=aggregate(cases),elapsed_seconds=time.perf_counter()-started)
            destination.write_text(json.dumps(result,indent=2)+'\n')
    result['status']='complete'
    result['elapsed_seconds']=time.perf_counter()-started
    result['max_refinement_score_difference']=max(r['refinement']['max_score_difference']
        for c in cases for variant in c['records'].values() for r in variant.values())
    result['max_norm_error']=max(r['norm_error'] for c in cases for variant in c['records'].values() for r in variant.values())
    destination.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'output':str(destination),'elapsed':result['elapsed_seconds'],
                      'max_refinement':result['max_refinement_score_difference']}),flush=True)


if __name__=='__main__':
    main()
