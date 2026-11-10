"""Tree repair evaluation for general embedded Ising models.

Terminal Gibbs equilibrium certificate, not a finite-time QA success model.
Public API evaluate(h,J,offset,target,embedding,beta=20,epsilon=.05,...).
"""
from __future__ import annotations
from collections import defaultdict
import math, time, sys
from pathlib import Path
import networkx as nx
PRIOR=Path(__file__).resolve().parents[2]/'lab-002-agent-test-general-h'/'scripts'
sys.path.insert(0,str(PRIOR))
from embedding import tree_edges, edge_key, verify_embedding, interaction_graph


def rooted_tree(edges, nodes, root):
    adj={q:[] for q in nodes}
    for q,r in edges: adj[q].append(r); adj[r].append(q)
    parent={root:None}; order=[root]
    for q in order:
        for r in sorted(adj[q]):
            if r not in parent: parent[r]=q; order.append(r)
    if len(order)!=len(nodes): raise ValueError('disconnected chain tree')
    return adj,parent,order


def centroid(edges,nodes,loads):
    adj,parent,order=rooted_tree(edges,nodes,min(nodes))
    sub={q:loads.get(q,0.) for q in nodes}
    for q in reversed(order[1:]): sub[parent[q]]+=sub[q]
    total=sub[order[0]]
    worst={q:max([total-sub[q]]+[sub[r] for r in adj[q] if parent.get(r)==q]) for q in nodes}
    return min(nodes,key=lambda q:(worst[q],q))


def get_groups(target):
    from dwave.system.coupling_groups import coupling_groups
    return [[edge_key(q,r) for q,r in group] for group in coupling_groups(target)]


def _constrain_interval(lo,hi,a,b,bounds):
    lower,upper=bounds
    if a==0:
        if not lower<=b<=upper: return 1.,0.
        return lo,hi
    x,y=(lower-b)/a,(upper-b)/a
    if x>y:x,y=y,x
    return max(lo,x),min(hi,y)


def quantum_union_bound(chain_bounds,chain_sizes,beta,gamma):
    """Local driver removal; cosh correction plus rigorous trace-distance alternative."""
    corrections=[]
    for size in chain_sizes:
        x=beta*abs(gamma)*size
        # Relative entropy and Pinsker give sqrt(beta*v), the optional
        # independent beta*v linear Lipschitz proof is not assumed here.
        cosh=2*math.sinh(x/2)**2 if x<700 else math.inf
        corrections.append(min(1.,cosh,math.sqrt(x)))
    return min(1.,sum(min(1.,b+c) for b,c in zip(chain_bounds,corrections)))


def evaluate(h,J,offset,target,embedding,beta=20.,epsilon=.05,groups=None,
             h_range=(-4.,4.),j_range=(-1.,1.),group_range=(-13.,10.),
             allocation='cut',validate=True):
    start=time.perf_counter()
    if beta<=0 or not 0<epsilon<1: raise ValueError('beta>0 and 0<epsilon<1 required')
    if allocation not in ('cut','total'): raise ValueError('unknown allocation')
    if validate:
        valid=verify_embedding(interaction_graph(h,J),target,embedding)
        if not valid['valid']: raise ValueError(valid)
    owner={q:i for i,c in embedding.items() for q in c}
    contacts=defaultdict(list)
    for q in sorted(owner):
        for r in sorted(target[q]):
            if q<r and r in owner and owner[q]!=owner[r]:
                pair=edge_key(owner[q],owner[r])
                if pair in J: contacts[pair].append((q,r))
    ext={}
    extload={q:0. for q in owner}
    for pair,value in sorted(J.items()):
        sites=contacts[pair]
        if not sites: raise ValueError('missing coupler')
        for edge in sites:
            ext[edge]=value/len(sites)
            for q in edge: extload[q]+=abs(ext[edge])
    trees={i:tree_edges(target,c) for i,c in embedding.items()}
    K=sum(map(len,trees.values()))
    # Union exp bound is slightly weaker than product bound; frozen budget.
    d=math.log(K/epsilon)/(2*beta) if K else 0.
    roots={}; subtree={}; fields={q:0. for q in owner}; chain={}; chain_variable={}
    for i,nodes in sorted(embedding.items()):
        root=centroid(trees[i],nodes,extload); roots[i]=root; fields[root]=float(h[i])
        adj,parent,order=rooted_tree(trees[i],nodes,root)
        sub={q:extload[q] for q in nodes}
        for q in reversed(order[1:]): sub[parent[q]]+=sub[q]
        total=abs(h[i])+sum(extload[q] for q in nodes)
        for q in order[1:]:
            edge=edge_key(q,parent[q]); subtree[edge]=sub[q]
            chain[edge]=sub[q] if allocation=='cut' else total
            chain_variable[edge]=i
    slopes=dict(ext); intercept={edge:0. for edge in ext}
    for edge,load in chain.items(): slopes[edge]=-load; intercept[edge]=-d
    lo,hi=0.,1.
    for a in fields.values():lo,hi=_constrain_interval(lo,hi,a,0.,h_range)
    for edge,a in slopes.items():lo,hi=_constrain_interval(lo,hi,a,intercept[edge],j_range)
    groups=get_groups(target) if groups is None else groups
    group_affine=[]
    for group in groups:
        a=sum(slopes.get(e,0.) for e in group); b=sum(intercept.get(e,0.) for e in group)
        group_affine.append((a,b))
        if group_range is not None:lo,hi=_constrain_interval(lo,hi,a,b,group_range)
    if hi<=0 or hi<lo:
        return {'feasible':False,'reason':'certificate margin incompatible with programming limits',
                'physical_qubits':len(owner),'chain_edges_count':K,'margin_requested':d,
                'elapsed_seconds':time.perf_counter()-start}
    alpha=hi*(1-1e-12)
    ph={q:alpha*a for q,a in fields.items()}
    pj={e:alpha*a+intercept[e] for e,a in slopes.items()}
    actual_load={q:abs(ph[q]) for q in owner}
    for e in ext:
        for q in e:actual_load[q]+=abs(pj[e])
    margins={}; chainbounds=[]; sizes=[]
    for i,nodes in sorted(embedding.items()):
        _,parent,order=rooted_tree(trees[i],nodes,roots[i])
        sub={q:actual_load[q] for q in nodes}
        for q in reversed(order[1:]):sub[parent[q]]+=sub[q]
        logprod=0.
        for q in order[1:]:
            edge=edge_key(q,parent[q]); margins[edge]=-pj[edge]-sub[q]
            logprod+=math.log1p(math.exp(-2*beta*margins[edge]))
        if len(nodes)>1:
            chainbounds.append(-math.expm1(-logprod)); sizes.append(len(nodes))
    logprod=sum(math.log1p(math.exp(-2*beta*v)) for v in margins.values())
    allbreak=-math.expm1(-logprod)
    chain_offset=sum(-pj[e] for e in chain)
    return {'feasible':True,'scale':alpha,'physical_qubits':len(owner),'logical_variables':len(h),
            'chain_edges_count':K,'chain_max':max(map(len,embedding.values()),default=0),
            'beta':beta,'epsilon_requested':epsilon,'margin_requested':d,
            'margin_min':min(margins.values(),default=None),'classical_break_bound':allbreak,
            'classical_union_bound':min(1.,sum(chainbounds)),
            'quantum_bounds':{str(g):quantum_union_bound(chainbounds,sizes,beta,g) for g in (0.,1e-5,1e-4,1e-3)},
            'roots':roots,'chain_trees':trees,'subtree_loads_logical':subtree,
            'edge_margins':margins,'chain_bounds':chainbounds,'chain_sizes':sizes,
            'h':ph,'J':pj,'offset':alpha*offset+chain_offset,
            'logical_offset':offset,'chain_offset':chain_offset,
            'allocation':allocation,'ranges':{'h':h_range,'J':j_range,'group':group_range},
            'group_sums':[alpha*a+b for a,b in group_affine],
            'elapsed_seconds':time.perf_counter()-start}


def json_program(p):
    out=dict(p)
    for key in ('h',):
        if key in out:out[key]=[[q,v] for q,v in sorted(out[key].items())]
    for key in ('J','edge_margins','subtree_loads_logical'):
        if key in out:out[key]=[[*edge,v] for edge,v in sorted(out[key].items())]
    return out


def brief(p):
    return {k:v for k,v in p.items() if k not in ('h','J','offset','roots','chain_trees',
        'subtree_loads_logical','edge_margins','group_sums','chain_bounds','chain_sizes')}
