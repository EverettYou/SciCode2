"""Frozen parent penalty study: matched mappings, exact actual-program audits, Gibbs intervals."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy
import sys,json,time,statistics,math
sys.dont_write_bytecode=True
from penalty_bound import witness,compile_with_bound,load_module
LAB=Path(__file__).resolve().parents[1];BENCH=LAB.parents[1];OLD=BENCH/'labs/lab-004-general-h-evaluation-embedding-loop'
sys.path.insert(0,str(OLD/'scripts'))
from evaluator import evaluate,json_program
from numeric_certificate import rational_audit
from embedding import graph_from_witness,qubo_to_ising,find_automatic_embedding
from compiler import model_graph
from run_suite import instance,FAMILIES
ia=load_module('independent_actual_program_audit',OLD/'independent/audit_programs.py')
gi=load_module('independent_logical_interval',OLD/'independent/logical_gibbs_intervals.py')
OUT=LAB/'results/penalty';OUT.mkdir(exist_ok=True)

def process(data,mappings,target,groups,name,search_seconds=0.):
    start=time.perf_counter();st=time.perf_counter();cert=witness(data['rows'],data['n'],data['weights']);basis_seconds=time.perf_counter()-st
    records={};models={};logicals={};cert_seconds=0.;eval_seconds=0.;compile_seconds=0.
    for mode in ['global','basis','repair']:
        st=time.perf_counter();model=compile_with_bound(data['rows'],data['n'],data['syndrome'],data['weights'],cert,mode);compile_seconds+=time.perf_counter()-st
        h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);models[mode]=model
        logicals[mode]={'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c}
        for maplabel,embedding in mappings.items():
            p=evaluate(h,J,c,target,embedding,groups=groups);eval_seconds+=p['elapsed_seconds'];assert p['feasible']
            saved=json_program(p);st=time.perf_counter();audit=rational_audit(model,saved,embedding,target,groups);cert_seconds+=time.perf_counter()-st
            assert audit['float_projected_ground_states_certified'],(name,mode,maplabel,audit)
            records[mode+'_'+maplabel]={'embedding':embedding,'program':saved,'numeric_certificate':audit}
    cache={};masses={}
    for label,entry in records.items():
        mode=label.split('_')[0];datum={'name':name,'input':data,'model':models[mode],'logical_ising':logicals[mode],'selected':{'first':records['global_first']}}
        st=time.perf_counter();aud=ia.audit(datum,label,entry,target,groups);cert_seconds+=time.perf_counter()-st
        entry['independent_audit']=aud
        if data['n']==16:
            alpha=F(entry['program']['scale']);penalty=F(models[mode]['penalty']);key=(alpha,penalty)
            if key not in cache:cache[key]=gi.interval_mass(data['rows'],data['n'],data['syndrome'],data['weights'],penalty,20*alpha)
            mass=cache[key];u=aud['classical_defect_upper'];tv=aud['thermal_rounding_tv_upper']
            masses[label]={'logical_interval':mass,'root_decoded_lower':max(0.,math.nextafter((1-u)*max(0.,mass['decoded_error_lower']-tv),-math.inf)),
              'root_decoded_upper':min(1.,math.nextafter(mass['decoded_error_upper']+tv+u,math.inf)),
              'consistent_full_ground_lower':max(0.,math.nextafter((1-u)*max(0.,mass['lower']-tv),-math.inf)),
              'consistent_full_ground_upper':min(1.,math.nextafter(mass['upper']+tv,math.inf))}
    comparisons={}
    for maplabel in mappings:
        old=masses.get('global_'+maplabel)
        for mode in ['basis','repair']:
            new=masses.get(mode+'_'+maplabel)
            a=records['global_'+maplabel]['program']['scale'];b=records[mode+'_'+maplabel]['program']['scale']
            cmp={'scale_ratio':b/a,'penalty_ratio':models[mode]['penalty']/models['global']['penalty']}
            if old:
                cmp.update({'strict_root_decoded_improvement':new['root_decoded_lower']>old['root_decoded_upper'],
                  'strict_root_decoded_reversal':new['root_decoded_upper']<old['root_decoded_lower'],
                  'strict_consistent_full_ground_improvement':new['consistent_full_ground_lower']>old['consistent_full_ground_upper'],
                  'conditional_original_optimum_ratio_lower':new['logical_interval']['decoded_error_lower']/old['logical_interval']['decoded_error_upper']})
            comparisons[mode+'_'+maplabel]=cmp
    result={'name':name,'status':'ok','input':data,'repair_witness':cert,'models':models,'logical_ising':logicals,'selected':records,'terminal_masses':masses,'comparisons':comparisons,
      'costs':{'basis_seconds':basis_seconds,'compilation_seconds':compile_seconds,'physical_evaluation_seconds':eval_seconds,'final_audit_seconds':cert_seconds,'search_seconds':search_seconds,'total_seconds':time.perf_counter()-start+search_seconds}}
    (OUT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    start=time.perf_counter();td=json.loads((OLD/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in group] for group in td['coupling_groups']];allresults=[]
    for family in FAMILIES:
        for n in [16,32,64]:
            for seed in [1101,2203,3307]:
                name=f'{family}_n{n}_s{seed}';d=json.loads((OLD/'results'/(name+'.json')).read_text());data=d['input'];data={**data,'split':'historical_main_reuse'}
                embeddings={k:{int(i):v for i,v in d['selected'][label]['embedding'].items()} for k,label in [('first','first'),('guided','guided_pruned')]}
                result=process(data,embeddings,target,groups,name);allresults.append(result)
                print(json.dumps({'name':name,'rank':result['repair_witness']['rank'],'repair_scale_ratio':result['comparisons']['repair_first']['scale_ratio']}),flush=True)
    for family in FAMILIES:
        for n in [16,32,64]:
            name=f'{family}_n{n}_s8809';data=instance(family,n,8809);data['split']='fresh_penalty_validation';model=compile_with_bound(data['rows'],n,data['syndrome'],data['weights'],witness(data['rows'],n,data['weights']),'global')
            emb=None;search_seconds=0.;failures=[]
            for seed in [11,29,47]:
                found=find_automatic_embedding(model_graph(model),target,seed=seed,timeout=5.,tries=2);search_seconds+=found['elapsed_seconds']
                if found['status']=='valid':emb=found['embedding'];break
                failures.append({k:v for k,v in found.items() if k!='embedding'})
            if emb is None:
                result={'name':name,'status':'all_search_failures','input':data,'failures':failures,'search_seconds':search_seconds};(OUT/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n')
            else:result=process(data,{'first':emb},target,groups,name,search_seconds)
            allresults.append(result);print(json.dumps({'fresh':name,'status':result['status']}),flush=True)
    rows=[]
    for d in allresults:
        if d['status']!='ok':rows.append({'name':d['name'],'status':d['status']});continue
        cert=d['repair_witness'];cmp=d['comparisons']['repair_first'];rows.append({'name':d['name'],'status':'ok','split':d['input']['split'],'n':d['input']['n'],'repair_penalty':d['models']['repair']['penalty'],
           'global_penalty':d['models']['global']['penalty'],'basis_total':float(F(*cert['basis_total_exact'])),'repair_bound':float(F(*cert['repair_bound_exact'])),**cmp,**d['costs']})
    def summary(split):
        a=[x for x in rows if x['status']=='ok' and x['split']==split];small=[x for x in a if x['n']==16]
        return {'instances':len(a),'mean_scale_ratio':statistics.mean(x['scale_ratio'] for x in a),'median_scale_ratio':statistics.median(x['scale_ratio'] for x in a),
         'mean_penalty_ratio':statistics.mean(x['penalty_ratio'] for x in a),'basis_median_seconds':statistics.median(x['basis_seconds'] for x in a),
         'small_original_error_orders':sum(x['strict_root_decoded_improvement'] for x in small),'small_original_error_reversals':sum(x['strict_root_decoded_reversal'] for x in small),'small_instances':len(small),
         'small_consistent_ground_orders':sum(x['strict_consistent_full_ground_improvement'] for x in small)}
    out={'status':'pass','historical':summary('historical_main_reuse'),'fresh':summary('fresh_penalty_validation'),'elapsed_seconds':time.perf_counter()-start,'records':rows}
    (LAB/'results/penalty_summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}),flush=True)
if __name__=='__main__':main()
