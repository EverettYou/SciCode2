from pathlib import Path
import sys,json,time,importlib.util,hashlib,math,random
from fractions import Fraction as F
from models import compile_model,PRIOR4
from thermal import row_envelopes,syndrome_certificate,exact_original_gibbs
from evaluator import evaluate,get_groups,json_program,brief
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit
from compiler import model_graph
from embedding import make_target,graph_witness,find_automatic_embedding,qubo_to_ising,versions
LAB=Path(__file__).resolve().parents[1];OUT=LAB/'results';FAMILIES=['random_regular','irregular_hubs','rewired_band','mixed_hypergraph'];SEEDS=[11,29,47,71,101,137,173,211]
sys.dont_write_bytecode=True

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
GENERATOR=load('lab4_generator_readonly',PRIOR4/'scripts'/'run_suite.py')
REPAIR=load('parent_repair_witness',LAB/'independent'/'penalty_bound.py')

def save(path,data):path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')

def clean_envelope(e):
    if e['status']!='ok':return e
    e=dict(e);e['rows']=[{k:(v if not isinstance(v,float) or math.isfinite(v) else None) for k,v in row.items()} for row in e['rows']];return e


def do_model(data,scheme,target,groups):
    start=time.perf_counter();M=sum(map(abs,data['weights']))+1;model=compile_model(data['rows'],data['n'],data['syndrome'],data['weights'],scheme,M)
    h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);source=model_graph(model)
    wit=REPAIR.witness(data['rows'],data['n'],data['weights']);loads=[float(F(*a)) for a in wit['repair_loads_exact']]
    candidates=[];failures=[];floor=None
    for seed in SEEDS:
        found=find_automatic_embedding(source,target,seed=seed,timeout=5.,tries=2)
        if found['status']!='valid':failures.append({'seed':seed,**{k:v for k,v in found.items() if k!='embedding'}});continue
        emb=found['embedding'];u=evaluate(h,J,c,target,emb,groups=groups)
        if not u['feasible']:failures.append({'seed':seed,'status':'uniform_certificate_inconclusive','evaluation':u});continue
        if floor is None:floor=u['scale']
        p=allocate_lp(h,J,c,target,emb,u,groups)
        if not p['feasible'] or p['scale']<u['scale']:p=u
        candidates.append({'seed':seed,'embedding':emb,'program':p,'uniform_scale':u['scale'],'embedding_seconds':found['elapsed_seconds']})
    eligible=[a for a in candidates if a['program']['scale']>=floor] if floor is not None else []
    name=f"{data['family']}_n{data['n']}_s{data['seed']}_{scheme}"
    if not eligible:
        r={'name':name,'status':'no_certified_mapping','input':data,'scheme':scheme,'model':model,'failures':failures,'repair_witness':wit,'total_seconds':time.perf_counter()-start}
        save(OUT/(name+'.json'),r);return r
    sel=min(eligible,key=lambda a:(a['program']['physical_qubits'],-a['program']['scale'],a['seed']))
    selected=json_program(sel['program']);audit=rational_audit(model,selected,sel['embedding'],target,groups)
    if not audit['float_projected_ground_states_certified']:raise AssertionError(('numeric fidelity',name,audit))
    curve=[]
    for beta in [10.,20.,40.,80.]:
        u=evaluate(h,J,c,target,sel['embedding'],groups=groups,beta=beta);p=allocate_lp(h,J,c,target,sel['embedding'],u,groups)
        if not p['feasible'] or p['scale']<u['scale']:p=u
        t=beta*p['scale'];env=row_envelopes(data['rows'],data['syndrome'],t*M,scheme)
        cert=syndrome_certificate(env,wit['basis_rows'],loads,t)
        row={'beta':beta,'scale':p['scale'],'physical_qubits':p['physical_qubits'],'chain_defect_bound':p['classical_break_bound'],
             'row_envelope':clean_envelope(env),'syndrome_certificate':cert,
             'root_readout_tv_bound':min(1.,p['classical_break_bound']+cert.get('syndrome_defect_bound',1.)+cert.get('conditional_feasible_tv_bound',1.))}
        if data['n']==16:
            rstart=time.perf_counter();ref=exact_original_gibbs(data,M,t,scheme);row['exact_reference']=ref;row['reference_seconds']=time.perf_counter()-rstart
            if cert['feasible_probability_lower']>ref['feasible_probability']+1e-9:raise AssertionError('syndrome feasibility bound fails')
            if cert['conditional_feasible_tv_bound']+1e-10<ref['conditional_feasible_tv']:raise AssertionError('auxiliary distortion bound fails')
            row['optimal_error_probability_lower']=max(0.,(1-p['classical_break_bound'])*cert['feasible_probability_lower']*max(0.,ref['intended_conditional_original_optimum_probability']-cert['conditional_feasible_tv_bound']))
        curve.append(row)
    r={'name':name,'status':'ok','input':data,'scheme':scheme,'model':model,'repair_witness':wit,
       'logical_ising':{'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c},
       'source_graph':graph_witness(source),'scale_floor':floor,'selected':{'seed':sel['seed'],'embedding':sel['embedding'],'program':selected,'numeric_certificate':audit},
       'candidates':[{'seed':a['seed'],'embedding':a['embedding'],'evaluation':brief(a['program']),'uniform_scale':a['uniform_scale'],'embedding_seconds':a['embedding_seconds']} for a in candidates],
       'failures':failures,'thermal_curves':curve,'total_seconds':time.perf_counter()-start}
    save(OUT/(name+'.json'),r);return r


def main():
    OUT.mkdir(exist_ok=True);target=make_target(6,4);groups=get_groups(target)
    save(OUT/'target.json',{'target':graph_witness(target),'coupling_groups':groups,'versions':versions()})
    paths=[PRIOR4/'scripts'/'evaluator.py',PRIOR4/'scripts'/'lp_allocator.py',PRIOR4/'scripts'/'numeric_certificate.py',PRIOR4/'scripts'/'run_suite.py',LAB/'independent'/'penalty_bound.py']
    save(OUT/'source_provenance.json',{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    progress=[]
    for family in FAMILIES:
        for n in [16,32,64]:
            for seed in [8807,9901]:
                data=GENERATOR.instance(family,n,seed);data['split']='development' if seed==8807 else 'held_out'
                for scheme in ['standard','balanced']:
                    name=f'{family}_n{n}_s{seed}_{scheme}';path=OUT/(name+'.json')
                    if path.exists():r=json.loads(path.read_text())
                    else:r=do_model(data,scheme,target,groups)
                    summary={k:r[k] for k in ['name','status','scheme','total_seconds']}
                    if r['status']=='ok':
                        p=r['selected']['program'];summary.update({'logical_variables':len(r['model']['linear']),'logical_edges':len(r['model']['quadratic']),
                            'qubits':p['physical_qubits'],'scale':p['scale'],'readout_curves':[{k:x[k] for k in ['beta','scale','root_readout_tv_bound','syndrome_certificate']} for x in r['thermal_curves']]})
                    progress.append(summary);save(OUT/'suite_progress.json',progress);print(json.dumps(summary),flush=True)
    save(OUT/'suite_summary.json',progress)
if __name__=='__main__':main()
