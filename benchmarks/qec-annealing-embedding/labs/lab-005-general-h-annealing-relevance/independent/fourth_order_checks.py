"""Exact rational time-polynomial Dyson validation, independent of log recursion."""
from fractions import Fraction as F
from pathlib import Path
import random,json,time
from forward_moments import expansion
LAB=Path(__file__).resolve().parents[1]
def value(poly,state,N):
    return sum((v*((-1)**((mask & (~state & ((1<<N)-1))).bit_count())) for mask,v in poly.items()),F(0))
def main():
    start=time.perf_counter();rng=random.Random(100907);cases=[]
    for trial in range(24):
        N=1+trial%5;S=1<<N;h={i:F(rng.randrange(-3,4),4) for i in range(N)};J={(i,j):F(rng.randrange(-3,4),4) for i in range(N) for j in range(i+1,N) if rng.random()<.6}
        E=[sum((v*(1 if (state>>i)&1 else -1) for i,v in h.items()),F(0))+sum((v*(1 if ((state>>i)^(state>>j))&1==0 else -1) for (i,j),v in J.items()),F(0)) for state in range(S)]
        # b_k(u) real, psi=sum_k(-iT)^k b_k(u), initial amplitude factored out.
        previous=[[F(1)] for x in range(S)];finals=[[F(1)] for x in range(S)]
        for k in range(1,5):
            current=[[F(0)]*(2*k+1) for x in range(S)]
            for x in range(S):
                for p in range(len(previous[x])):
                    driver=-sum((previous[x^(1<<i)][p] for i in range(N)),F(0))
                    current[x][p+1]+=driver/F(p+1)
                    current[x][p+2]+=(E[x]*previous[x][p]-driver)/F(p+2)
            for x in range(S):finals[x].append(sum(current[x],F(0)))
            previous=current
        q2,q4=expansion(h,J,exact=True)
        for x in range(S):
            b0,b1,b2,b3,b4=finals[x];p2=b1*b1-2*b2;p4=2*b4-2*b1*b3+b2*b2
            q2x=value(q2,x,N);q4x=value(q4,x,N);assert p2==q2x,(trial,x,p2,q2x);assert p4==q4x+q2x*q2x/2,(trial,x,p4,q4x)
        assert sum(value(q2,x,N) for x in range(S))==0
        assert sum(value(q4,x,N)+value(q2,x,N)**2/2 for x in range(S))==0
        cases.append({'N':N,'basis_states':S,'q2_terms':len(q2),'q4_terms':len(q4)})
    out={'status':'pass','cases':len(cases),'basis_states_checked':sum(x['basis_states'] for x in cases),'method':'Exact Fraction time-polynomial Dyson recursion through order4; all computational states, normalization and sparse log-expansion coefficients checked.','seconds':time.perf_counter()-start,'records':cases}
    (LAB/'results/fourth_order_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
