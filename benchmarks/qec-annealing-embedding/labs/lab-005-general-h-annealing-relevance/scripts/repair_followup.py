from pathlib import Path
from copy import deepcopy
from fractions import Fraction as F
import json,time,math
from models import compile_model
from evaluator import evaluate,json_program
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit
from embedding import graph_from_witness,qubo_to_ising
from thermal import row_envelopes,syndrome_certificate,exact_original_gibbs
OUT=Path(__file__).resolve().parents[1]/'results'


def rescale_balanced(model,witness,slack=1.):
    out=deepcopy(model);C=F(*witness['repair_bound_exact']);M=F(float(C+F(slack)));ratio=M/F(model['penalty']);n=model['n_original'];w=list(map(F,model['weights']))
    lin=[F(*a) for a in model['exact_coefficients']['linear']];lin=[w[i]+(a-w[i])*ratio if i<n else a*ratio for i,a in enumerate(lin)]
    quad={(i,j):F(a,b)*ratio for i,j,a,b in model['exact_coefficients']['quadratic']};offset=F(*model['exact_coefficients']['offset'])*ratio
    out.update({'linear':list(map(float,lin)),'quadratic':[[i,j,float(v)] for (i,j),v in sorted(quad.items()) if v],'offset':float(offset),'penalty':float(M)})
    for c in out['constraints']:
        if 'scale' in c:
            a=F(*c['scale'])*ratio;c['scale']=[a.numerator,a.denominator]
    rho=sum((abs(F(a)-b) for a,b in zip(out['linear'],lin)),F(0))+sum((abs(F(float(v))-v) for v in quad.values()),F(0))
    lattice=model['numeric_certificate']['weight_lattice_step_exact'];lattice=F(*lattice) if lattice else None;gap=min(M-C,lattice) if lattice else M-C
    pair=lambda v:[v.numerator,v.denominator]
    out['exact_coefficients']={'linear':[pair(v) for v in lin],'quadratic':[[i,j,*pair(v)] for (i,j),v in sorted(quad.items()) if v],'offset':pair(offset),
      'interpretation':'balanced polynomial exact rescaling with independently verified general-H repair penalty'}
    out['numeric_certificate']={'float_ground_states_certified':2*rho<gap,'coefficient_error_l1_exact':pair(rho),'nonoptimal_gap_lower_bound_exact':pair(gap),
      'weight_lattice_step_exact':pair(lattice) if lattice else None,'exact_penalty_margin':pair(M-C),'offset_error_exact':pair(abs(F(out['offset'])-offset)),
      'condition':'2rho<min(weight lattice,M-C); every violated original row costs at least M; C from parent verified repair witness'}
    out['repair_penalty_certificate']={'mode':'repair','slack':slack,'witness':witness}
    if not out['numeric_certificate']['float_ground_states_certified']:raise AssertionError('repair model numeric fidelity')
    return out


def main():
    from repair_api import REPAIR
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']]
    folder=OUT/'repair_compilers';folder.mkdir(exist_ok=True);records=[];start=time.perf_counter()
    for path in sorted(OUT.glob('*_s*_*.json')):
        if not (path.stem.endswith('_standard') or path.stem.endswith('_balanced')):continue
        r=json.loads(path.read_text())
        if r['status']!='ok':records.append({'name':r['name'],'status':'original_search_failure_retained'});continue
        data=r['input'];wit=r['repair_witness'];scheme=r['scheme'];emb={int(i):ch for i,ch in r['selected']['embedding'].items()}
        if scheme=='standard':m=REPAIR.compile_with_bound(data['rows'],data['n'],data['syndrome'],data['weights'],wit,mode='repair');m['compiler_scheme']='standard'
        else:m=rescale_balanced(r['model'],wit)
        h,J,c=qubo_to_ising(m['linear'],m['quadratic'],m['offset']);loads=[float(F(*a)) for a in wit['repair_loads_exact']];curves=[]
        for beta in [10.,20.,40.,80.]:
            u=evaluate(h,J,c,target,emb,groups=groups,beta=beta);p=allocate_lp(h,J,c,target,emb,u,groups)
            if not p['feasible'] or p['scale']<u['scale']:p=u
            pw=json_program(p);audit=rational_audit(m,pw,emb,target,groups)
            if not audit['float_projected_ground_states_certified']:raise AssertionError('repair program numeric fidelity')
            t=beta*p['scale'];env=row_envelopes(data['rows'],data['syndrome'],t*m['penalty'],scheme);cert=syndrome_certificate(env,wit['basis_rows'],loads,t)
            row={'beta':beta,'program':pw,'numeric_certificate':audit,'syndrome_certificate':cert,
                 'root_readout_tv_bound':min(1.,p['classical_break_bound']+cert['syndrome_defect_bound']+cert['conditional_feasible_tv_bound'])}
            if data['n']==16:
                row['exact_reference']=exact_original_gibbs(data,m['penalty'],t,scheme)
                if row['exact_reference']['feasible_probability']+1e-9<cert['feasible_probability_lower']:raise AssertionError('repair probability certificate')
            curves.append(row)
        obj={'name':r['name'],'input':data,'scheme':scheme,'model':m,'embedding':emb,'repair_witness':wit,'curves':curves,'global_model_file':path.name}
        (folder/(r['name']+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
        records.append({'name':r['name'],'status':'ok','scheme':scheme,'global_penalty':r['model']['penalty'],'repair_penalty':m['penalty'],
          'curves':[{'beta':x['beta'],'scale':x['program']['scale'],'root_readout_tv_bound':x['root_readout_tv_bound'],
                     **({'exact_reference':x['exact_reference']} if 'exact_reference' in x else {})} for x in curves]})
    (OUT/'repair_compiler_summary.json').write_text(json.dumps({'records':records,'elapsed_seconds':time.perf_counter()-start},indent=2)+'\n');print('repair followup done',len(records))
if __name__=='__main__':main()
