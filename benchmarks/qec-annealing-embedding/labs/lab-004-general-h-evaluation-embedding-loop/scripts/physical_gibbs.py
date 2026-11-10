"""Supplemental exact classical endpoint Gibbs checks on compiled general H."""
import numpy as np
import time,json
from run_suite import OUT,instance,FAMILIES,one,save
from evaluator import get_groups
from embedding import make_target
from logical_gibbs import logical_gibbs


def enumerate_program(data,model,selected,max_qubits=22):
    p=selected['program'];embedding={int(i):ch for i,ch in selected['embedding'].items()};roots={int(i):q for i,q in p['roots'].items()}
    nodes=sorted(q for ch in embedding.values() for q in ch);N=len(nodes)
    if N>max_qubits:return {'status':'skipped_exact_state_limit','physical_qubits':N,'limit':max_qubits}
    ix={q:k for k,q in enumerate(nodes)};start=time.perf_counter();beta=p['beta'];alpha=p['scale']
    ideal=logical_gibbs(data,model['penalty'],beta*alpha);minimum=alpha*ideal['optimum']
    Z=0.;Zbroken=0.;Zopt=0.;Zconsistentopt=0.;Zconsistentground=0.;mass=np.zeros(2**data['n']);cmass=np.zeros_like(mass)
    for first in range(0,2**N,65536):
        indices=np.arange(first,min(first+65536,2**N),dtype=np.uint64)
        spins=1-2*((indices[:,None]>>np.arange(N,dtype=np.uint64))&1).astype(np.int8)
        E=np.full(len(indices),p['offset'])
        for q,v in p['h']:E+=v*spins[:,ix[q]]
        for q,r,v in p['J']:E+=v*spins[:,ix[q]]*spins[:,ix[r]]
        w=np.exp(-beta*(E-minimum));consistent=np.ones(len(indices),dtype=bool)
        for i,ch in embedding.items():consistent&=np.all(spins[:,[ix[q] for q in ch]]==spins[:,ix[roots[i]],None],axis=1)
        codes=np.zeros(len(indices),dtype=int)
        for i in range(data['n']):codes+=((1+spins[:,ix[roots[i]]])//2)*(2**i)
        optimal=ideal['ground_mask'][codes]
        Z+=float(w.sum());Zbroken+=float(w[~consistent].sum());Zopt+=float(w[optimal].sum());Zconsistentopt+=float(w[consistent&optimal].sum());Zconsistentground+=float(w[consistent&(np.abs(E-minimum)<1e-9)].sum())
        mass+=np.bincount(codes,weights=w,minlength=len(mass));cmass+=np.bincount(codes[consistent],weights=w[consistent],minlength=len(mass))
    actualbreak=Zbroken/Z;actualopt=Zopt/Z;conditional=Zconsistentopt/(Z-Zbroken)
    tv=.5*float(np.abs(mass/Z-ideal['distribution']).sum())
    ctv=.5*float(np.abs(cmass/(Z-Zbroken)-ideal['distribution']).sum())
    if actualbreak>p['classical_break_bound']+1e-10:raise AssertionError('actual chain failure exceeds bound')
    if abs(conditional-ideal['projected_optimum_probability'])>1e-10:raise AssertionError('conditional Gibbs ground mass disagrees')
    if tv>p['classical_break_bound']+1e-10:raise AssertionError('TV guarantee fails')
    return {'status':'exact','physical_qubits':N,'physical_states':2**N,'actual_break_probability':actualbreak,
            'break_bound':p['classical_break_bound'],'actual_root_decoded_optimum_probability':actualopt,
            'actual_consistent_optimum_probability':Zconsistentopt/Z,
            'actual_conditional_optimum_probability':conditional,'predicted_conditional_optimum_probability':ideal['projected_optimum_probability'],
            'actual_consistent_full_model_ground_probability':Zconsistentground/Z,
            'actual_conditional_full_model_ground_probability':Zconsistentground/(Z-Zbroken),
            'predicted_conditional_full_model_ground_probability':ideal['ground_probability'],
            'root_decoded_tv_to_ideal':tv,'conditional_tv_to_ideal':ctv,'elapsed_seconds':time.perf_counter()-start}


def main():
    target=make_target(6,4);groups=get_groups(target);records=[];start=time.perf_counter()
    for family in FAMILIES:
        data=instance(family,6,6607);data['extension']='exact_physical_validation';r=one(data,target,groups,refine=False)
        row={'name':r['name'],'status':r['status'],'selected':{}}
        if r['status']=='ok':
            for label in ['first','guided_pool','size_only_pool']:
                row['selected'][label]=enumerate_program(data,r['model'],r['selected'][label])
        records.append(row);save(OUT/'physical_gibbs_validation.json',{'records':records,'elapsed_seconds':time.perf_counter()-start})
        print(json.dumps(row),flush=True)
if __name__=='__main__':main()
