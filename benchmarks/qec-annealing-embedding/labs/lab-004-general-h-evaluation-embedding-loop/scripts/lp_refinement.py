import json,time,statistics
from run_suite import OUT,FAMILIES,instance,one,removable,save
from evaluator import evaluate,json_program,brief,get_groups
from embedding import make_target
from lp_allocator import allocate_lp
from numeric_certificate import rational_audit


def prune_lp(source,target,initial,h,J,c,groups,floor):
    emb={i:list(ch) for i,ch in initial.items()};start=time.perf_counter();trace=[];evaltime=0.
    for i in sorted(emb,key=lambda i:(-len(emb[i]),i)):
        for q in sorted(emb[i],reverse=True):
            if not removable(source,target,emb,i,q):continue
            cand={v:(ch if v!=i else [p for p in ch if p!=q]) for v,ch in emb.items()}
            u=evaluate(h,J,c,target,cand,groups=groups,validate=False)
            p=allocate_lp(h,J,c,target,cand,u,groups);evaltime+=u['elapsed_seconds']+p['elapsed_seconds']
            accept=p['feasible'] and (floor is None or p['scale']>=floor)
            trace.append({'variable':i,'qubit':q,'accepted':accept,'evaluation':brief(p)})
            if accept:emb=cand
    u=evaluate(h,J,c,target,emb,groups=groups);p=allocate_lp(h,J,c,target,emb,u,groups)
    return emb,p,{'total_seconds':time.perf_counter()-start,'evaluation_seconds':evaltime,
                  'graph_valid_proposals':len(trace),'accepted':sum(x['accepted'] for x in trace),'trace':trace}


def main():
    from compiler import model_graph
    target=make_target(6,4);groups=get_groups(target);folder=OUT/'lp_refinement';folder.mkdir(exist_ok=True);start=time.perf_counter();results=[]
    names=[f'{f}_n{n}_s1101' for f in FAMILIES for n in [16,32,64]]
    names += [f'{f}_n{n}_s7703' for f in FAMILIES for n in [32,64]]
    for name in names:
        path=OUT/(name+'.json');fresh=name.endswith('s7703')
        if fresh:
            parts=name.rsplit('_n',1);f=parts[0];n=int(parts[1].split('_s')[0]);data=instance(f,n,7703);data['split']='new_lp_refinement_held_out';data['extension']='lp_refinement'
            r=one(data,target,groups,refine=False)
        else:r=json.loads(path.read_text())
        if r['status']!='ok':results.append({'name':name,'fresh_held_out':fresh,'status':r['status']});continue
        li=r['logical_ising'];h=dict(li['h']);J={(i,j):v for i,j,v in li['J']};c=li['offset'];source=model_graph(r['model'])
        candidates=[]
        for x in r['candidates']:
            emb={int(i):ch for i,ch in x['embedding'].items()};u=evaluate(h,J,c,target,emb,groups=groups);p=allocate_lp(h,J,c,target,emb,u,groups)
            if p['feasible'] and p['scale']>=r['scale_floor']:candidates.append({'embedding':emb,'program':p,'seed':x['seed']})
        if not candidates:
            results.append({'name':name,'fresh_held_out':fresh,'status':'lp_floor_failure'});continue
        initial=min(candidates,key=lambda x:(x['program']['physical_qubits'],-x['program']['scale'],x['seed']));selected={}
        for label,floor in [('guided',r['scale_floor']),('unconstrained',None)]:
            emb,p,stats=prune_lp(source,target,initial['embedding'],h,J,c,groups,floor)
            pw=json_program(p);audit=rational_audit(r['model'],pw,emb,target,groups)
            selected[label]={'embedding':emb,'program':pw,'pruning':stats,'numeric_certificate':audit}
        obj={'name':name,'fresh_held_out':fresh,'status':'ok','input':r['input'],'model':r['model'],'scale_floor':r['scale_floor'],
             'initial':{'embedding':initial['embedding'],'program':json_program(initial['program'])},'selected':selected,
             'first_uniform':r['selected']['first']['program'],'uniform_guided_pool':r['selected']['guided_pool']['program']}
        save(folder/(name+'.json'),obj)
        row={'name':name,'fresh_held_out':fresh,'status':'ok','first_qubits':obj['first_uniform']['physical_qubits'],
             'uniform_pool_qubits':obj['uniform_guided_pool']['physical_qubits'],'lp_initial_qubits':initial['program']['physical_qubits'],
             'guided_qubits':selected['guided']['program']['physical_qubits'],'unconstrained_qubits':selected['unconstrained']['program']['physical_qubits'],
             'scale_floor':r['scale_floor'],'guided_scale':selected['guided']['program']['scale'],
             'unconstrained_scale':selected['unconstrained']['program']['scale'],
             'guided_proposals':selected['guided']['pruning']['graph_valid_proposals'],
             'unconstrained_proposals':selected['unconstrained']['pruning']['graph_valid_proposals'],
             'guided_seconds':selected['guided']['pruning']['total_seconds'],'unconstrained_seconds':selected['unconstrained']['pruning']['total_seconds'],
             'certified':all(a['numeric_certificate']['float_projected_ground_states_certified'] for a in selected.values())}
        results.append(row);save(OUT/'lp_refinement_progress.json',results);print(json.dumps(row),flush=True)
    save(OUT/'lp_refinement_summary.json',{'records':results,'elapsed_seconds':time.perf_counter()-start})
if __name__=='__main__':main()
