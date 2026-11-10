from pathlib import Path
import json,time,statistics
from run_suite import OUT,save
from evaluator import evaluate,json_program,brief
from embedding import graph_from_witness
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit


def main():
    td=json.loads((OUT/'target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in g] for g in td['coupling_groups']]
    folder=OUT/'lp';folder.mkdir(exist_ok=True);records=[];start=time.perf_counter()
    for path in sorted(OUT.glob('*_n*_s*.json')):
        r=json.loads(path.read_text())
        if r['status']!='ok' or r['input']['seed'] not in (1101,2203,3307):continue
        li=r['logical_ising'];h=dict(li['h']);J={(i,j):v for i,j,v in li['J']};c=li['offset'];candidates=[]
        for old in r['candidates']:
            emb={int(i):ch for i,ch in old['embedding'].items()}
            uniform=evaluate(h,J,c,target,emb,groups=groups)
            p=allocate_lp(h,J,c,target,emb,uniform,groups)
            candidates.append({'seed':old['seed'],'embedding':emb,'program':p,'uniform_scale':uniform['scale'],
                               'uniform_reevaluation_seconds':uniform['elapsed_seconds']})
        feasible=[x for x in candidates if x['program']['feasible']]
        eligible=[x for x in feasible if x['program']['scale']>=r['scale_floor']]
        # Include original uniform guided as a safe fallback, so selection is
        # never declared improved when LP failed to satisfy frozen constraints.
        selected=min(eligible,key=lambda x:(x['program']['physical_qubits'],-x['program']['scale'],x['seed'])) if eligible else None
        selout=None
        if selected:
            witness=json_program(selected['program']);audit=rational_audit(r['model'],witness,selected['embedding'],target,groups)
            selout={'seed':selected['seed'],'embedding':selected['embedding'],'program':witness,'numeric_certificate':audit}
        row={'name':r['name'],'input':r['input'],'model':r['model'],'logical_ising':li,'scale_floor':r['scale_floor'],
             'candidates':[{'seed':x['seed'],'embedding':x['embedding'],'evaluation':brief(x['program']),
                             'uniform_scale':x['uniform_scale'],'uniform_reevaluation_seconds':x['uniform_reevaluation_seconds']} for x in candidates],
             'selected':selout,'uniform_guided_qubits':r['selected']['guided_pool']['program']['physical_qubits'],
             'original_first_qubits':r['selected']['first']['program']['physical_qubits'],
             'unconstrained_size_qubits':r['selected']['size_only_pool']['program']['physical_qubits']}
        save(folder/(r['name']+'.json'),row)
        record={'name':r['name'],'split':r['input']['split'],'uniform_guided_qubits':row['uniform_guided_qubits'],
                'original_first_qubits':row['original_first_qubits'],'unconstrained_size_qubits':row['unconstrained_size_qubits'],
                'lp_selected_qubits':selected['program']['physical_qubits'] if selected else row['uniform_guided_qubits'],
                'lp_selected_scale':selected['program']['scale'] if selected else r['selected']['guided_pool']['program']['scale'],
                'fallback':not bool(selected),'lp_failures':sum(not x['program']['feasible'] for x in candidates),
                'total_lp_seconds':sum(x['program']['elapsed_seconds'] for x in candidates),
                'total_uniform_reevaluation_seconds':sum(x['uniform_reevaluation_seconds'] for x in candidates),
                'lp_scale_ratios':[x['program']['scale']/x['uniform_scale'] for x in feasible],
                'numeric_certified':selout['numeric_certificate']['float_projected_ground_states_certified'] if selout else True}
        records.append(record);save(OUT/'lp_progress.json',records);print(json.dumps(record),flush=True)
    result={'records':records,'elapsed_seconds':time.perf_counter()-start,
            'improved_over_uniform_guided_count':sum(x['lp_selected_qubits']<x['uniform_guided_qubits'] for x in records),
            'matches_unconstrained_size_count':sum(x['lp_selected_qubits']==x['unconstrained_size_qubits'] for x in records),
            'mean_reduction_vs_first':statistics.mean(1-x['lp_selected_qubits']/x['original_first_qubits'] for x in records),
            'mean_lp_scale_ratio':statistics.mean(a for x in records for a in x['lp_scale_ratios']),
            'total_lp_seconds':sum(x['total_lp_seconds'] for x in records),'failed_lp_programs':sum(x['lp_failures'] for x in records)}
    save(OUT/'lp_summary.json',result)
if __name__=='__main__':main()
