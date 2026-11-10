"""General sparse-H ordinary and thermally balanced XOR compilers."""
from pathlib import Path
import sys,math
from collections import defaultdict
from fractions import Fraction as F
PRIOR4=Path(__file__).resolve().parents[2]/'lab-004-general-h-evaluation-embedding-loop'
sys.path.insert(0,str(PRIOR4/'scripts'))
import evaluator
import compiler as old
from embedding import qubo_to_ising
EVEN_FLIPS=[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]


def compile_model(rows,n,syndrome,weights,scheme='standard',penalty=None):
    if scheme=='standard':
        m=old.compile_instance(rows,n,syndrome,weights,penalty);m['compiler_scheme']='standard';return m
    if scheme!='balanced':raise ValueError('unknown scheme')
    rows=old.normalize_rows(rows,n);syndrome=list(syndrome);weights=[float(x) for x in weights]
    if len(syndrome)!=len(rows) or len(weights)!=n:raise ValueError('dimension mismatch')
    if any(s not in (0,1) for s in syndrome):raise ValueError('nonbinary syndrome')
    W=math.fsum(abs(w) for w in weights);M=float(W+1 if penalty is None else penalty)
    if not all(math.isfinite(w) for w in weights) or not math.isfinite(M) or M<=W:raise ValueError('require finite M>weight L1')
    lin=list(map(F,weights));quad=defaultdict(F);offset=F(0);vars=[{'kind':'error','column':i} for i in range(n)];constraints=[];structure=set()
    def aux(kind,row,stage,flip=None):
        vars.append({'kind':kind,'row':row,'stage':stage,'flip':flip});lin.append(F(0));return len(lin)-1
    def square(terms,constant,scale,row,stage,flip):
        nonlocal offset
        for i,a in terms.items():lin[i]+=scale*(a*a+2*constant*a)
        pairs=sorted(terms)
        for k,i in enumerate(pairs):
            for j in pairs[k+1:]:quad[i,j]+=2*scale*terms[i]*terms[j];structure.add((i,j))
        offset+=scale*constant*constant
        constraints.append({'kind':'square','terms':sorted(terms.items()),'constant':constant,
                            'scale':[scale.numerator,scale.denominator],'row':row,'stage':stage,'flip':flip})
    for r,(support,s) in enumerate(zip(rows,syndrome)):
        d=len(support)
        if d==0:
            if s:raise ValueError('infeasible empty row')
        elif d==1:square({support[0]:1},-s,F(M),r,0,None)
        else:
            prev=support[0]
            for stage,current in enumerate(support[1:]):
                if stage==d-2:
                    sign=1-2*s;lin[prev]+=F(M)*sign;lin[current]+=F(M)*sign
                    edge=tuple(sorted((prev,current)));quad[edge]-=2*F(M)*sign;structure.add(edge);offset+=F(M)*s
                    constraints.append({'kind':'parity','inputs':[prev,current],'target':s,'row':r,'scale':[F(M).numerator,F(M).denominator]})
                else:
                    p=aux('prefix',r,stage)
                    for flip in EVEN_FLIPS:
                        a,b,c=flip;hidden=aux('balanced_hidden',r,stage,list(flip))
                        square({prev:1-2*a,current:1-2*b,p:-(1-2*c),hidden:-2},a+b-c,F(M)/4,r,stage,list(flip))
                    prev=p
    model={'schema':'balanced-xor-qubo-v1','compiler_scheme':'balanced','n_original':n,'rows':rows,'syndrome':syndrome,'weights':weights,
           'penalty':M,'weight_l1':W,'linear':[float(x) for x in lin],
           'quadratic':[[i,j,float(v)] for (i,j),v in sorted(quad.items()) if v],
           'offset':float(offset),'variables':vars,'constraints':constraints,'structural_edges':[list(e) for e in sorted(structure)]}
    return old.certify_coefficients(model,lin,quad,offset)


def complete(model,e):
    if not old.feasible(model,e):raise ValueError('infeasible error')
    if model['compiler_scheme']=='standard':return old.complete_feasible(model,e)
    y=list(e)+[0]*(len(model['linear'])-len(e))
    for row,support in enumerate(model['rows']):
        prev=e[support[0]] if support else 0
        for stage,current in enumerate(support[1:-1]):
            p=prev^e[current]
            for i,var in enumerate(model['variables']):
                if var.get('row')!=row or var.get('stage')!=stage:continue
                if var['kind']=='prefix':y[i]=p
                elif var['kind']=='balanced_hidden':
                    a,b,c=var['flip'];y[i]=((prev^a)+(e[current]^b)-(p^c))//2
            prev=p
    return y
