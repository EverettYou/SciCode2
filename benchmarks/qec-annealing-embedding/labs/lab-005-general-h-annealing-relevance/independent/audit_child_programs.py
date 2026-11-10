"""Independent actual-coefficient audit of child research program records."""
from pathlib import Path
import sys,json,time,hashlib
sys.dont_write_bytecode=True
from penalty_bound import load_module
LAB=Path(__file__).resolve().parents[1];OLD=LAB.parent/'lab-004-general-h-evaluation-embedding-loop';sys.path.insert(0,str(OLD/'scripts'));sys.path.insert(0,str(LAB.parent/'lab-002-agent-test-general-h/scripts'))
from embedding import graph_from_witness,qubo_to_ising
from numeric_certificate import rational_audit
ia=load_module('independent_prior_witness_reader',OLD/'independent/audit_programs.py')
def main():
    st=time.perf_counter();td=json.loads((LAB/'results/target.json').read_text());target=graph_from_witness(td['target']);groups=[[tuple(e) for e in group] for group in td['coupling_groups']];records=[];seen=set()
    def check(name,label,input,model,emb,program,ising=None):
        emb={int(i):v for i,v in emb.items()}
        if ising is None:
            h,J,c=qubo_to_ising(model['linear'],model['quadratic'],model['offset']);ising={'h':[[i,v] for i,v in sorted(h.items())],'J':[[i,j,v] for (i,j),v in sorted(J.items())],'offset':c}
        entry={'embedding':emb,'program':program};datum={'name':name,'input':input,'model':model,'logical_ising':ising,'selected':{'first':entry}}
        independent=ia.audit(datum,label,entry,target,groups);exact=rational_audit(model,program,emb,target,groups);assert exact['float_projected_ground_states_certified'],(name,label)
        core={'exact_model':model['exact_coefficients'],'embedding':emb,'h':program['h'],'J':program['J'],'scale':program['scale'],'offset':program['offset'],'roots':program['roots'],'trees':program['chain_trees']}
        digest=hashlib.sha256(json.dumps(core,sort_keys=True).encode()).hexdigest();seen.add(digest)
        records.append({'name':name,'selection':label,'core_sha256':digest,'independent':independent,'authoritative_model_audit':exact})
    for path in sorted(list((LAB/'results').glob('*_n*_s*_standard.json'))+list((LAB/'results').glob('*_n*_s*_balanced.json'))):
        data=json.loads(path.read_text())
        if data.get('status')!='ok' or 'selected' not in data:continue
        x=data['selected'];check(data['name'],'main_selected',data['input'],data['model'],x['embedding'],x['program'],data['logical_ising'])
    for path in sorted((LAB/'results/dynamics').glob('*.json')):
        dynamic=json.loads(path.read_text());data=json.loads((LAB/'results'/dynamic['source_file']).read_text());emb=data['selected']['embedding']
        for row in dynamic['curves']:check(data['name'],f"bath_beta{row['beta']}",data['input'],data['model'],emb,row['program'],data['logical_ising'])
    for path in sorted((LAB/'results/relaxation').glob('*.json')):
        data=json.loads(path.read_text())
        for tag in ['before_program','after_program']:check(data['name'],'relaxation_'+tag,data['input'],data['model'],data['embedding'],data[tag])
    for path in sorted((LAB/'results/repair_compilers').glob('*.json')):
        data=json.loads(path.read_text())
        for row in data['curves']:check(data['name'],f"repair_beta{row['beta']}",data['input'],data['model'],data['embedding'],row['program'])
    result={'status':'pass','saved_program_records_checked':len(records),'distinct_core_witnesses':len(seen),'maximum_classical_chain_bound':max(x['independent']['classical_defect_upper'] for x in records),
      'maximum_rounding_tv':max(x['independent']['thermal_rounding_tv_upper'] for x in records),'seconds':time.perf_counter()-st,'records':records}
    (LAB/'results/independent_child_program_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
