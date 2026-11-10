"""Exact rational backend: all finite binary64 input weights are supported.

It emits mathematical QUBO and programmed Ising coefficients as rational pairs.
Physical ranges are parametric exact rationals. No lossy coefficient conversion
is required by this path; a digital hardware export needs a separate precision
certificate (provided for the ordinary regime by embedding.py).
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction as F
import math
from compiler import normalize_rows
from embedding import verify_embedding, tree_edges, edge_key
import networkx as nx


def ratio(x): return [x.numerator,x.denominator]


def compile_exact_instance(rows,n,syndrome,weights,penalty=None):
    if not isinstance(n,int) or n<0:raise ValueError("n must be a nonnegative integer")
    rows=normalize_rows(rows,n);syndrome=list(syndrome);weights=list(weights)
    if len(rows)!=len(syndrome) or len(weights)!=n or any(s not in (0,1) for s in syndrome):
        raise ValueError("Input dimensions/syndrome invalid")
    syndrome=list(map(int,syndrome))
    if any(not math.isfinite(float(w)) for w in weights):
        raise ValueError("Weights must be finite")
    w=list(map(F,weights));W=sum(map(abs,w),F(0));P=W+1 if penalty is None else F(penalty)
    if P<=W: raise ValueError("Need exact penalty greater than weight L1 norm")
    linear=list(w);quad=defaultdict(F);constant=F(0);edges=set();constraints=[]
    variables=[{"kind":"error","column":i} for i in range(n)]
    def new(kind,r,stage):
        v=len(linear);linear.append(F(0));variables.append({"kind":kind,"row":r,"stage":stage});return v
    def square(terms,c,r):
        nonlocal constant
        terms=sorted(terms.items());constant+=P*c*c
        for i,a in terms:linear[i]+=P*(a*a+2*a*c)
        for pos,(i,a) in enumerate(terms):
            for j,b in terms[pos+1:]:quad[i,j]+=2*P*a*b;edges.add((i,j))
        constraints.append({"kind":"xor" if len(terms)==4 else "final","row":r,"terms":terms,"constant":c})
    for r,(row,s) in enumerate(zip(rows,syndrome)):
        if not row:
            if s:raise ValueError("Nonzero empty check is infeasible")
        elif len(row)==1:square({row[0]:1},-s,r)
        else:
            prev=row[0]
            for stage,current in enumerate(row[1:]):
                if stage==len(row)-2:
                    sign=1-2*s;linear[prev]+=P*sign;linear[current]+=P*sign
                    pair=edge_key(prev,current);quad[pair]-=2*P*sign;edges.add(pair);constant+=P*s
                    constraints.append({"kind":"parity","row":r,"inputs":[prev,current],"target":s})
                else:
                    carry=new("carry",r,stage);parity=new("prefix",r,stage)
                    square({prev:1,current:1,parity:-1,carry:-2},0,r);prev=parity
    denominator=math.lcm(*(q.denominator for q in w))
    step_num=math.gcd(*(abs(q.numerator)*(denominator//q.denominator) for q in w))
    step=F(step_num,denominator) if step_num else None
    gap=min(P-W,step) if step else P-W
    return {"schema":"xor-chain-exact-rational-v1","n_original":n,"rows":rows,"syndrome":syndrome,
            "weights_exact":[ratio(x) for x in w],"penalty_exact":ratio(P),"variables":variables,
            "structural_edges":[list(e) for e in sorted(edges)],"constraints":constraints,
            "exact_coefficients":{"linear":[ratio(a) for a in linear],
              "quadratic":[[i,j,*ratio(a)] for (i,j),a in sorted(quad.items()) if a],"offset":ratio(constant)},
            "numeric_certificate":{"float_ground_states_certified":False,"status":"exact_only",
              "nonoptimal_gap_lower_bound_exact":ratio(gap),"exact_penalty_margin":ratio(P-W),
              "weight_lattice_step_exact":None if step is None else ratio(step)}}


def exact_graph(model,structural=True):
    graph=nx.Graph();graph.add_nodes_from(range(len(model["variables"])))
    graph.add_edges_from(model["structural_edges"] if structural else
                         [(i,j) for i,j,a,b in model["exact_coefficients"]["quadratic"] if a])
    return graph


def exact_ising(model):
    coeff=model["exact_coefficients"];linear=[F(*q) for q in coeff["linear"]]
    h={i:a/2 for i,a in enumerate(linear)};J={};c=F(*coeff["offset"])+sum(linear,F(0))/2
    for i,j,a,b in coeff["quadratic"]:
        q=F(a,b);J[i,j]=q/4;h[i]+=q/4;h[j]+=q/4;c+=q/4
    return h,J,c


def allocate_symbolic(model,target,embedding,chain_margin=1,chain_factor=1,
                      h_range=(-4,4),j_range=(-1,1),group_range=(-13,10),coupling_groups=None):
    """Exact static embedding and signed coupling-group compliant rescaling."""
    source=exact_graph(model,structural=False)
    check=verify_embedding(source,target,embedding)
    if not check["valid"]:raise ValueError("Invalid embedding")
    margin,factor=F(chain_margin),F(chain_factor)
    if margin<=0 or factor<1:raise ValueError("Need factor>=1,margin>0")
    h,J,c=exact_ising(model);owners={q:i for i,b in embedding.items() for q in b};contacts={}
    for q,r in sorted(edge_key(q,r) for q,r in target.edges):
        if q in owners and r in owners and owners[q]!=owners[r]:
            contacts.setdefault(edge_key(owners[q],owners[r]),(q,r))
    ph={q:h[i]/len(branch) for i,branch in embedding.items() for q in branch}
    pj={};load={i:abs(v) for i,v in h.items()}
    for (i,j),v in J.items():
        pj[edge_key(*contacts[i,j])]=v;load[i]+=abs(v);load[j]+=abs(v)
    trees={i:tree_edges(target,b) for i,b in embedding.items()}
    strengths={i:factor*load[i]+margin for i in embedding if trees[i]}
    raw_offset=c
    for i,edges in trees.items():
        for edge in edges:pj[edge]=-strengths[i];raw_offset+=strengths[i]
    if coupling_groups is None:
        from dwave.system.coupling_groups import coupling_groups as make_groups
        groups=list(make_groups(target))
    else:groups=[list(g) for g in coupling_groups]
    sums=[sum((pj.get(edge_key(q,r),F(0)) for q,r in g),F(0)) for g in groups]
    def bound(value,bounds):
        lo,hi=map(F,bounds)
        if not lo<0<hi:raise ValueError("Ranges must strictly contain zero")
        return hi/value if value>0 else lo/value if value<0 else None
    limits=[F(1)]
    for values,bounds in [(ph.values(),h_range),(pj.values(),j_range),(sums,group_range)]:
        for value in values:
            lim=bound(value,bounds)
            if lim is not None:limits.append(lim)
    alpha=min(limits)
    gap=F(*model["numeric_certificate"]["nonoptimal_gap_lower_bound_exact"])*alpha
    if strengths:gap=min(gap,2*alpha*min(strengths[i]-load[i] for i in strengths))
    return {"schema":"exact-rational-physical-v1","embedding":{str(i):list(b) for i,b in embedding.items()},
            "h":[[q,*ratio(alpha*v)] for q,v in sorted(ph.items())],
            "J":[[q,r,*ratio(alpha*v)] for (q,r),v in sorted(pj.items())],
            "offset":ratio(alpha*raw_offset),"scale":ratio(alpha),
            "nonoptimal_gap_lower_bound":ratio(gap),
            "chain_strength_raw":{str(i):ratio(v) for i,v in strengths.items()},
            "chain_edges":{str(i):[list(e) for e in es] for i,es in trees.items()},
            "ranges":{"h":list(h_range),"J":list(j_range),"coupling_group":list(group_range)},
            "group_sums":[ratio(alpha*s) for s in sums],"coupling_groups":groups,
            "validation":check,"fidelity":"exact rational arithmetic; no coefficient rounding"}
