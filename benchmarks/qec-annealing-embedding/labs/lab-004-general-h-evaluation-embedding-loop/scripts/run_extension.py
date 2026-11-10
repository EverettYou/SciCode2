import json,time,random,sys
from run_suite import instance,FAMILIES,one,save,OUT
from evaluator import get_groups
from embedding import make_target,graph_witness,versions


def main():
    target=make_target(6,4);groups=get_groups(target);results=[]
    for n in [128,256]:
        for family in FAMILIES:
            data=instance(family,n,4409);data['extension']='scaling';data['split']='new_held_out'
            r=one(data,target,groups,refine=False)
            result={k:r[k] for k in ['name','status','total_seconds']}
            if r['status']=='ok':result['selected']={k:{a:r['selected'][k]['program'][a] for a in ['physical_qubits','scale','classical_break_bound']} for k in r['selected']}
            results.append(result);save(OUT/'extension_progress.json',results);print(json.dumps(result),flush=True)
    rng=random.Random(7523);defect=target.copy()
    deleted_nodes=rng.sample(sorted(defect),round(.05*len(defect)));defect.remove_nodes_from(deleted_nodes)
    deleted_edges=rng.sample(sorted(defect.edges),round(.01*defect.number_of_edges()));defect.remove_edges_from(deleted_edges)
    dg=get_groups(defect)
    save(OUT/'defect_target.json',{'target':graph_witness(defect),'coupling_groups':dg,
                                  'deleted_nodes':deleted_nodes,'deleted_edges':deleted_edges,'seed':7523})
    for family in FAMILIES:
        data=instance(family,64,5501);data['extension']='synthetic_defects';data['split']='new_held_out'
        r=one(data,defect,dg,refine=False)
        result={k:r[k] for k in ['name','status','total_seconds']}
        if r['status']=='ok':result['selected']={k:{a:r['selected'][k]['program'][a] for a in ['physical_qubits','scale','classical_break_bound']} for k in r['selected']}
        results.append(result);save(OUT/'extension_progress.json',results);print(json.dumps(result),flush=True)
    save(OUT/'extension_summary.json',results)
if __name__=='__main__':main()
