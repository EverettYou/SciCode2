"""Sparse LP optimizes same-sign contacts for fixed branch roots and trees."""
import time,math
from collections import defaultdict
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix
from evaluator import rooted_tree,quantum_union_bound
from embedding import edge_key


def allocate_lp(h,J,c,target,embedding,uniform,groups):
    start=time.perf_counter();owner={q:i for i,ch in embedding.items() for q in ch}
    trees={int(i):[tuple(e) for e in es] for i,es in uniform['chain_trees'].items()};roots={int(i):q for i,q in uniform['roots'].items()}
    contacts=[];bypair=defaultdict(list)
    for q in sorted(owner):
        for r in sorted(target[q]):
            if q<r and r in owner:
                pair=edge_key(owner[q],owner[r])
                if pair in J:
                    k=len(contacts);contacts.append((q,r,pair,1 if J[pair]>0 else -1));bypair[pair].append(k)
    K=sum(map(len,trees.values()));edges=[e for i in sorted(trees) for e in trees[i]]
    edgeix={e:len(contacts)+k for k,e in enumerate(edges)};N=len(contacts)+K+1;ai=N-1
    d=uniform['margin_requested'];reserve=1e-8;dlp=d+reserve if K else 0.
    ur=[];uc=[];uv=[];ub=[];er=[];ec=[];ev=[];eb=[]
    def inequality(row,b):
        idx=len(ub);ub.append(b)
        for col,v in row.items():
            if v:ur.append(idx);uc.append(col);uv.append(v)
    for pair,indices in bypair.items():
        idx=len(eb);eb.append(0.)
        for k in indices:er.append(idx);ec.append(k);ev.append(1.)
        er.append(idx);ec.append(ai);ev.append(-abs(J[pair]))
    paths={}
    for i,ch in embedding.items():
        _,parent,order=rooted_tree(trees[i],ch,roots[i]);paths[roots[i]]=[]
        for q in order[1:]:paths[q]=paths[parent[q]]+[edge_key(q,parent[q])]
    loads={e:defaultdict(float) for e in edges}
    for k,(q,r,_,_) in enumerate(contacts):
        for site in [q,r]:
            for edge in paths[site]:loads[edge][k]+=1.
    for edge,row in loads.items():
        row=dict(row);row[edgeix[edge]]=-1.;inequality(row,-dlp)
    physicalvars={edge_key(q,r):(k,sign) for k,(q,r,_,sign) in enumerate(contacts)}
    physicalvars.update({e:(k,-1) for e,k in edgeix.items()})
    hlo,hhi=uniform['ranges']['h'];jlo,jhi=uniform['ranges']['J'];glo,ghi=uniform['ranges']['group']
    for group in groups:
        row=defaultdict(float)
        for edge in group:
            if edge in physicalvars:
                k,sign=physicalvars[edge];row[k]+=sign
        if row:
            inequality(row,ghi);inequality({k:-v for k,v in row.items()},-glo)
    amax=1.
    for value in h.values():
        if value>0:amax=min(amax,hhi/value)
        elif value<0:amax=min(amax,hlo/value)
    bounds=[(0.,jhi if sign>0 else -jlo) for _,_,_,sign in contacts]+[(0.,-jlo)]*K+[(0.,amax)]
    A=coo_matrix((uv,(ur,uc)),shape=(len(ub),N)).tocsr();AE=coo_matrix((ev,(er,ec)),shape=(len(eb),N)).tocsr()
    objective=np.zeros(N);objective[ai]=-1.
    sol=linprog(objective,A_ub=A,b_ub=ub,A_eq=AE,b_eq=eb,bounds=bounds,method='highs',
                options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
    meta={'lp_status':int(sol.status),'lp_message':sol.message,'lp_variables':N,'lp_inequalities':len(ub),'lp_equalities':len(eb),
          'lp_nonzeros':len(uv)+len(ev),'lp_iterations':sol.nit,'elapsed_seconds':time.perf_counter()-start}
    if not sol.success or sol.x[ai]<=0:return {'feasible':False,**meta}
    alpha=float(sol.x[ai])*(1-1e-8);ratio=alpha/float(sol.x[ai]);ph={q:0. for q in owner};pj={}
    for i,root in roots.items():ph[root]=alpha*h[i]
    for k,(q,r,_,sign) in enumerate(contacts):pj[q,r]=sign*float(sol.x[k])*ratio
    for edge,k in edgeix.items():pj[edge]=-(dlp+(float(sol.x[k])-dlp)*ratio)
    actual={q:abs(ph[q]) for q in owner}
    for q,r,_,_ in contacts:
        for site in [q,r]:actual[site]+=abs(pj[q,r])
    margins={};chainbounds=[];sizes=[];logicalsub={}
    for i,ch in embedding.items():
        _,parent,order=rooted_tree(trees[i],ch,roots[i]);sub={q:actual[q] for q in ch}
        for q in reversed(order[1:]):sub[parent[q]]+=sub[q]
        logprod=0.
        for q in order[1:]:
            e=edge_key(q,parent[q]);margins[e]=-pj[e]-sub[q];logicalsub[e]=sub[q]/alpha
            logprod+=math.log1p(math.exp(-2*uniform['beta']*margins[e]))
        if len(ch)>1:chainbounds.append(-math.expm1(-logprod));sizes.append(len(ch))
    gsums=[sum(pj.get(e,0.) for e in group) for group in groups]
    violations=[]
    for q,v in ph.items():
        if not hlo<=v<=hhi:violations.append(['h',q,v])
    for e,v in pj.items():
        if not jlo<=v<=jhi:violations.append(['J',e,v])
    for k,v in enumerate(gsums):
        if not glo<=v<=ghi:violations.append(['group',k,v])
    budget=-math.expm1(-sum(math.log1p(math.exp(-2*uniform['beta']*v)) for v in margins.values()))
    if margins and min(margins.values())<d*(1-1e-10):violations.append(['margin',min(margins.values()),d])
    p={'feasible':not violations,'scale':alpha,'physical_qubits':len(owner),'logical_variables':len(h),'chain_edges_count':K,
       'chain_max':max(map(len,embedding.values())),'beta':uniform['beta'],'epsilon_requested':uniform['epsilon_requested'],
       'margin_requested':d,'margin_min':min(margins.values(),default=None),'classical_break_bound':budget,
       'classical_union_bound':min(1.,sum(chainbounds)),
       'quantum_bounds':{str(g):quantum_union_bound(chainbounds,sizes,uniform['beta'],g) for g in (0.,1e-5,1e-4,1e-3)},
       'roots':roots,'chain_trees':trees,'subtree_loads_logical':logicalsub,'edge_margins':margins,
       'chain_bounds':chainbounds,'chain_sizes':sizes,'h':ph,'J':pj,'offset':alpha*c+sum(-pj[e] for e in edges),
       'logical_offset':c,'chain_offset':sum(-pj[e] for e in edges),'allocation':'lp','ranges':uniform['ranges'],
       'group_sums':gsums,'numeric_violations':violations,**meta}
    p['elapsed_seconds']=time.perf_counter()-start
    return p
