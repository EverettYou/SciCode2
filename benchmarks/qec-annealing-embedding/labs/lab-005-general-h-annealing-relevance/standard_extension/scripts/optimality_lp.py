"""Necessary-optimality character relaxation with exact dual lower bounds."""
from fractions import Fraction as F
from itertools import combinations
import numpy as np
from scipy.optimize import linprog
import time

def root_second(inp,p,m):
    n=inp['n'];ref=m['particular_solution'];patterns=[int(x,16) for x in m['kernel_character_hex']]
    roots={int(q):int(i) for i,q in p['roots'].items() if int(i)<n};out={}
    for q,h in p['h']:
        if q in roots:
            i=roots[q];c=patterns[i];out[c]=out.get(c,F(0))-F(h)*(2*ref[i]-1)/6
    for q,r,J in p['J']:
        if q in roots and r in roots:
            i,j=roots[q],roots[r];c=patterns[i]^patterns[j];out[c]=out.get(c,F(0))-F(J)*(2*ref[i]-1)*(2*ref[j]-1)/3
    return {k:v for k,v in out.items() if v}

def subtract(a,b):return {k:b.get(k,F(0))-a.get(k,F(0)) for k in a.keys()|b.keys() if b.get(k,F(0))!=a.get(k,F(0))}

def constraints(inp,m,delta,method):
    patterns=[int(x,16) for x in m['kernel_character_hex']];ref=m['particular_solution'];cost={}
    for i,p in enumerate(patterns):
        if p:cost[p]=cost.get(p,F(0))+F(inp['weights'][i])*(2*ref[i]-1)/2
    cost={k:v for k,v in cost.items() if v};characters=sorted(set(delta)-{0}|set(patterns)-{0}|set(cost));mean=F(*m['mean_exact']);upper=F(*m['minimum_cost_upper_exact'])
    rows=[{'id':'cost_upper','coefficients':cost,'rhs':upper-mean}];k=m['kernel_dimension'];moves=[1<<j for j in range(k)]
    if method in ['pairs','triangles']:moves.extend((1<<i)^(1<<j) for i,j in combinations(range(k),2))
    for t in moves:
        a={c:v for c,v in cost.items() if (c&t).bit_count()%2}
        if a:rows.append({'id':'kernel_'+hex(t),'coefficients':a,'rhs':F(0)})
    if method=='triangles':
        triples={tuple(sorted([a,b,a^b])) for a,b in combinations(set(patterns)-{0},2) if a^b in characters}
        for a,b,c in sorted(triples):
            for j,signs in enumerate([(-1,-1,-1),(-1,1,1),(1,-1,1),(1,1,-1)]):
                rows.append({'id':'triangle_'+hex(a)+'_'+hex(b)+'_'+hex(c)+'_'+str(j),'coefficients':dict(zip([a,b,c],map(F,signs))),'rhs':F(1)})
    return characters,rows

def exact_dual_bound(delta,rows,multipliers):
    residual={k:v for k,v in delta.items() if k};constant=delta.get(0,F(0))
    for row,nu in zip(rows,multipliers):
        assert nu>=0
        if not nu:continue
        constant-=nu*row['rhs']
        for c,v in row['coefficients'].items():residual[c]=residual.get(c,F(0))+nu*v
    return constant-sum(map(abs,residual.values()),F(0))

def evaluate(inp,m,delta,method):
    start=time.perf_counter();chars,rows=constraints(inp,m,delta,method);index={c:i for i,c in enumerate(chars)}
    if not chars:return {'status':'constant','bound':delta.get(0,F(0)),'seconds':time.perf_counter()-start,'variables':0,'constraints':len(rows),'multipliers':[],'rows':rows}
    A=np.zeros((len(rows),len(chars)));b=np.array([float(r['rhs']) for r in rows]);c=np.array([float(delta.get(k,F(0))) for k in chars])
    for i,row in enumerate(rows):
        for character,v in row['coefficients'].items():A[i,index[character]]=float(v)
    t=time.perf_counter();result=linprog(c,A_ub=A,b_ub=b,bounds=[(-1,1)]*len(chars),method='highs');lp_seconds=time.perf_counter()-t
    if not result.success:return {'status':'lp_failure','message':result.message,'seconds':time.perf_counter()-start,'lp_seconds':lp_seconds,'variables':len(chars),'constraints':len(rows),'rows':rows}
    nu=[F(max(0.,-float(v))) for v in result.ineqlin.marginals];bound=exact_dual_bound(delta,rows,nu)
    return {'status':'exact_dual_lower','bound':bound,'seconds':time.perf_counter()-start,'lp_seconds':lp_seconds,'variables':len(chars),'constraints':len(rows),'multipliers':nu,'rows':rows,'numerical_primal_objective':delta.get(0,F(0))+F(float(result.fun))}
