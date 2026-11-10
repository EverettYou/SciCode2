"""Independent adaptive ODE check plus no-annealing baselines."""
import json,time
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from models import *
from dynamics import evolve,ground_truth,masks_for_model

LAB=Path(__file__).resolve().parents[1]


def ode_check():
    patch=make_patch(2); weights=[1.]*patch['n']; syndrome=[1,1]
    variants=[('direct_local',direct_model(patch,syndrome,weights,2.)),
              ('dual_0',dual_model(patch,syndrome,weights,0))]
    result=[]
    for name,model in variants:
        best=ground_truth(patch,syndrome,weights)['best_cost']
        diagonal,*masks=masks_for_model(model,patch,syndrome,weights,best)
        alpha=coefficient_scale([model])
        diagonal=alpha*(diagonal-diagonal.mean())
        n=model['n']; dim=1<<n; T=16.
        indices=np.arange(dim)
        flips=[indices^(1<<bit) for bit in range(n)]
        def rhs(t,psi):
            u=t/T
            hop=sum((psi[f] for f in flips),np.zeros_like(psi))
            return -1j*(u*diagonal*psi-(1-u)*hop)
        start=time.perf_counter()
        sol=solve_ivp(rhs,(0,T),np.ones(dim,dtype=complex)/np.sqrt(dim),method='DOP853',
                      rtol=2e-11,atol=2e-12,t_eval=[T])
        assert sol.success
        exact=sol.y[:,-1]
        strang=evolve(diagonal,n,T,768)
        overlap=abs(np.vdot(exact,strang))
        scores_ode=[float((abs(exact)**2)[m].sum()) for m in masks]
        scores_strang=[float((abs(strang)**2)[m].sum()) for m in masks]
        diff=max(abs(a-b) for a,b in zip(scores_ode,scores_strang))
        assert diff<1e-4
        result.append({'variant':name,'T':T,'alpha':alpha,'n':n,'method':'DOP853',
                       'rtol':2e-11,'atol':2e-12,'nfev':sol.nfev,'norm_error':float(abs(np.vdot(exact,exact)-1)),
                       'strang_steps':768,'overlap_abs':float(overlap),'max_score_difference':diff,
                       'scores_ode':scores_ode,'scores_strang':scores_strang,'elapsed_seconds':time.perf_counter()-start})
    return result


def baselines_for_file(path):
    data=json.loads(path.read_text())
    cases=[]
    for case in data['cases']:
        patch=make_patch(case['width'],case['height'])
        weights=case['weights']; syndrome=case['syndrome']
        best=case['truth']['best_cost']
        direct=direct_model(patch,syndrome,weights)
        _,*m=masks_for_model(direct,patch,syndrome,weights,best)
        p=float(m[0].mean()); pr=float(m[3].mean())
        ps=[]
        for ell in [0,1]:
            model=dual_model(patch,syndrome,weights,ell)
            _,*ms=masks_for_model(model,patch,syndrome,weights,best)
            ps.append(float(ms[0].mean()))
        pd=1-(1-ps[0])*(1-ps[1])
        repaired2=1-(1-pr)**2
        assert abs(pd-repaired2-(ps[0]-ps[1])**2/4)<1e-12
        cases.append({'width':case['width'],'height':case['height'],'weights':weights,
                      'syndrome':syndrome,'raw_direct_one_sample':p,'raw_direct_two_samples':1-(1-p)**2,
                      'repaired_direct_one_sample':pr,'repaired_direct_two_samples':repaired2,
                      'dual_one_sample_per_sector':pd,'dual_sector_stratification_advantage':pd-repaired2})
    return {'source':path.name,'cases':cases,'means':{k:float(np.mean([c[k] for c in cases])) for k in
        ['raw_direct_one_sample','raw_direct_two_samples','repaired_direct_one_sample',
         'repaired_direct_two_samples','dual_one_sample_per_sector','dual_sector_stratification_advantage']}}


def main():
    baselines=[]
    for suite in ['square2','rectangle23']:
        path=LAB/'results'/f'dynamics_{suite}.json'
        if path.exists() and json.loads(path.read_text())['status']=='complete':
            baselines.append(baselines_for_file(path))
    result={'status':'pass','ode_checks':ode_check(),'zero_time_baselines':baselines,
            'score_order':['raw_decoded_optimum','syndrome_feasible','programmed_ground','fixed_repair_optimum'],
            'interpretation':'Dual stratifies sectors and samples feasible states already at T=0; baseline gain is not quantum speedup.'}
    (LAB/'results'/'dynamics_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
