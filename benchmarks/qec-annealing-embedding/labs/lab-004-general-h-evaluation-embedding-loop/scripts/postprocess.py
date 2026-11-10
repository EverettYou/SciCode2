from pathlib import Path
import json,time,statistics,math
from run_suite import OUT,removable,save
from evaluator import evaluate,brief
from embedding import graph_from_witness,interaction_graph
from numeric_certificate import rational_audit


def main():
    targetdata=json.loads((OUT/'target.json').read_text());target=graph_from_witness(targetdata['target'])
    groups=[[tuple(e) for e in group] for group in targetdata['coupling_groups']]
    audits=[];common=[];rows=[]
    for path in sorted(OUT.glob('*_n*_s*.json')):
        r=json.loads(path.read_text())
        if r['status']!='ok' or r['input']['seed'] not in (1101,2203,3307):continue
        li=r['logical_ising'];h=dict(li['h']);J={(i,j):v for i,j,v in li['J']};c=li['offset']
        source=interaction_graph(h,J)
        for label,sel in r['selected'].items():
            emb={int(i):ch for i,ch in sel['embedding'].items()}
            a=rational_audit(r['model'],sel['program'],emb,target,groups)
            audits.append({'name':r['name'],'label':label,**a})
        sel=r['selected']['guided_pool'];emb={int(i):ch for i,ch in sel['embedding'].items()}
        start=time.perf_counter();pool=[]
        for i in sorted(emb,key=lambda i:(-len(emb[i]),i)):
            for q in sorted(emb[i],reverse=True):
                if not removable(source,target,emb,i,q):continue
                candidate={v:(ch if v!=i else [p for p in ch if p!=q]) for v,ch in emb.items()}
                p=evaluate(h,J,c,target,candidate,groups=groups,validate=False)
                pool.append({'variable':i,'qubit':q,'evaluation':brief(p)})
        feas=[x for x in pool if x['evaluation']['feasible']]
        safe=[x for x in feas if x['evaluation']['scale']>=r['scale_floor']]
        common.append({'name':r['name'],'common_graph_valid_candidates':len(pool),
                       'size_only_accepts':bool(feas),'guided_accepts':bool(safe),
                       'size_only_selected':feas[0] if feas else None,
                       'guided_selected':safe[0] if safe else None,
                       'candidates':pool,'elapsed_seconds':time.perf_counter()-start})
        first=r['selected']['first']['program'];guided=r['selected']['guided_pruned']['program']
        raw=r['selected']['size_only_pool']['program'];total=r['standard_total_load']
        cand=r['candidates'];profile=[x['evaluation']['elapsed_seconds'] for x in cand]
        row={'name':r['name'],'family':r['input']['family'],'n':r['input']['n'],'split':r['input']['split'],
             'logical_variables':first['logical_variables'],'logical_edges':len(J),
             'first_qubits':first['physical_qubits'],'guided_pool_qubits':sel['program']['physical_qubits'],
             'guided_qubits':guided['physical_qubits'],'size_only_qubits':raw['physical_qubits'],
             'first_scale':first['scale'],'guided_scale':guided['scale'],'size_only_scale':raw['scale'],
             'standard_scale':total.get('scale'),'guided_reduction_fraction':1-guided['physical_qubits']/first['physical_qubits'],
             'size_only_reduction_fraction':1-raw['physical_qubits']/first['physical_qubits'],
             'size_only_loses_scale':raw['scale']<first['scale'],
             'scale_ratio_cut_vs_total':first['scale']/total['scale'] if total.get('scale') else None,
             'classical_bound':guided['classical_break_bound'],'quantum_bounds':guided['quantum_bounds'],
             'first_eval_seconds':first['elapsed_seconds'],'evaluation_seconds_pool':sum(profile),
             'embedding_seconds_pool':sum(x['embedding_seconds'] for x in cand),
             'compile_seconds':r['compile_seconds'],'total_seconds':r['total_seconds'],
             'guided_prune_seconds':r['selected']['guided_pruned']['pruning']['total_seconds'],
             'guided_prune_proposals':r['selected']['guided_pruned']['pruning']['graph_valid_proposals'],
             'size_prune_proposals':r['selected']['size_only_pruned']['pruning']['graph_valid_proposals']}
        rows.append(row)
    save(OUT/'numeric_certificates.json',audits);save(OUT/'common_deletion_pool.json',common)
    def agg(rs):
        return {'instances':len(rs),'compactness_improved':sum(x['guided_reduction_fraction']>0 for x in rs),
           'mean_qubit_reduction':statistics.mean(x['guided_reduction_fraction'] for x in rs),
           'median_qubit_reduction':statistics.median(x['guided_reduction_fraction'] for x in rs),
           'size_only_scale_losses':sum(x['size_only_loses_scale'] for x in rs),
           'mean_cut_total_scale_ratio':statistics.mean(x['scale_ratio_cut_vs_total'] for x in rs),
           'median_evaluator_seconds':statistics.median(x['first_eval_seconds'] for x in rs),
           'embedding_seconds_pool':sum(x['embedding_seconds_pool'] for x in rs),
           'evaluation_seconds_pool':sum(x['evaluation_seconds_pool'] for x in rs),
           'total_seconds':sum(x['total_seconds'] for x in rs),
           'quantum_bound_max':{g:max(x['quantum_bounds'][g] for x in rs) for g in ['0.0','1e-05','0.0001','0.001']}}
    summary={'all':agg(rows),'development':agg([x for x in rows if x['split']=='development']),
      'held_out':agg([x for x in rows if x['split']=='held_out']),
      'by_family':{f:agg([x for x in rows if x['family']==f]) for f in sorted(set(x['family'] for x in rows))},
      'numeric_audits':{'count':len(audits),'passed':sum(a['float_projected_ground_states_certified'] for a in audits),
       'maximum_rho':max(a['coefficient_error_l1'] for a in audits),
       'max_thermal_rounding_correction':max(a['logical_gibbs_tv_rounding_correction'] for a in audits)},
      'common_deletion_control':{'instances_with_proposals':sum(bool(x['candidates']) for x in common),
        'total_candidates':sum(len(x['candidates']) for x in common),'guided_accepts':sum(x['guided_accepts'] for x in common),
        'size_only_accepts':sum(x['size_only_accepts'] for x in common)},'rows':rows}
    save(OUT/'analysis_summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
