"""Remove unnecessary ferromagnetic strength at fixed alpha/nonchain coefficients."""
from copy import deepcopy
import numpy as np,math,time
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from evaluator import rooted_tree,quantum_union_bound
from embedding import edge_key


def relax(p,embedding,groups):
    start=time.perf_counter();out=deepcopy(p);trees={int(i):[tuple(e) for e in es] for i,es in p['chain_trees'].items()};roots={int(i):q for i,q in p['roots'].items()}
    edges=[e for i in sorted(trees) for e in trees[i]];ix={e:k for k,e in enumerate(edges)};ph=dict(p['h']);pj={(q,r):v for q,r,v in p['J']}
    chainset=set(edges);loads={q:abs(v) for q,v in ph.items()}
    for e,v in pj.items():
        if e not in chainset:
            for q in e:loads[q]+=abs(v)
    lower={};d=p['margin_requested'];reserve=1e-8
    for i,ch in embedding.items():
        _,par,order=rooted_tree(trees[i],ch,roots[i]);sub={q:loads[q] for q in ch}
        for q in reversed(order[1:]):sub[par[q]]+=sub[q]
        for q in order[1:]:edge=edge_key(q,par[q]);lower[edge]=min(-pj[edge],sub[q]+d+reserve)
    if not edges:return out,{'status':'no_chains','elapsed_seconds':time.perf_counter()-start}
    rows=[];cols=[];values=[];b=[];glo,ghi=p['ranges']['group']
    for group in groups:
        used=[ix[e] for e in group if e in ix];fixed=sum(pj.get(e,0.) for e in group if e not in chainset)
        if not used:continue
        k=len(b);b.append(ghi-fixed)
        for j in used:rows.append(k);cols.append(j);values.append(-1.)
        k=len(b);b.append(fixed-glo)
        for j in used:rows.append(k);cols.append(j);values.append(1.)
    A=coo_matrix((values,(rows,cols)),shape=(len(b),len(edges))).tocsr()
    strength_limit=-p['ranges']['J'][0]
    sol=linprog(np.ones(len(edges)),A_ub=A,b_ub=b,bounds=[(lower[e],strength_limit) for e in edges],method='highs',options={'primal_feasibility_tolerance':1e-9})
    if not sol.success:return None,{'status':'relaxation_lp_failure','message':sol.message,'elapsed_seconds':time.perf_counter()-start}
    for e,k in ix.items():pj[e]=-float(sol.x[k])
    margins={};branchbounds=[];sizes=[]
    for i,ch in embedding.items():
        _,par,order=rooted_tree(trees[i],ch,roots[i]);sub={q:loads[q] for q in ch}
        for q in reversed(order[1:]):sub[par[q]]+=sub[q]
        logprod=0.
        for q in order[1:]:
            e=edge_key(q,par[q]);margins[e]=-pj[e]-sub[q];logprod+=math.log1p(math.exp(-2*p['beta']*margins[e]))
        if len(ch)>1:branchbounds.append(-math.expm1(-logprod));sizes.append(len(ch))
    gsums=[sum(pj.get(e,0.) for e in g) for g in groups];viol=[]
    for e,v in pj.items():
        if not p['ranges']['J'][0]<=v<=p['ranges']['J'][1]:viol.append(['J',e,v])
    for k,v in enumerate(gsums):
        if not glo<=v<=ghi:viol.append(['group',k,v])
    if min(margins.values())<=0:viol.append(['margin'])
    out.update({'J':[[q,r,v] for (q,r),v in sorted(pj.items())],
      'offset':p['scale']*p['logical_offset']+sum(-pj[e] for e in edges),'chain_offset':sum(-pj[e] for e in edges),
      'edge_margins':[[q,r,v] for (q,r),v in sorted(margins.items())],
      'margin_min':min(margins.values()),'classical_break_bound':-math.expm1(-sum(math.log1p(math.exp(-2*p['beta']*v)) for v in margins.values())),
      'classical_union_bound':min(1.,sum(branchbounds)),'chain_bounds':branchbounds,'chain_sizes':sizes,
      'group_sums':gsums,'quantum_bounds':{str(g):quantum_union_bound(branchbounds,sizes,p['beta'],g) for g in (0.,1e-5,1e-4,1e-3)},
      'allocation':'lp','chain_allocation':'minimum_total_strength','numeric_violations':viol})
    stats={'status':'ok' if not viol else 'numeric_violation','elapsed_seconds':time.perf_counter()-start,
      'original_strength_sum':sum(-v for q,r,v in p['J'] if (q,r) in chainset),'relaxed_strength_sum':sum(-pj[e] for e in chainset),
      'original_break_bound':p['classical_break_bound'],'relaxed_break_bound':out['classical_break_bound'],'changed_edges':sum(abs(pj[e]-dict(((q,r),v) for q,r,v in p['J'])[e])>1e-9 for e in edges)}
    return out,stats
