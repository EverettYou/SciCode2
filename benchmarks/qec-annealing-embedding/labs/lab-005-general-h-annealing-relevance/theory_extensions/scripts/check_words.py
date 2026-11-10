"""Independent exact operator-Dyson validation of event-relative word bounds."""
from fractions import Fraction as F
from pathlib import Path
import random,json,time
from word_majorant import schedule_coefficients
HERE=Path(__file__).resolve().parents[1]
# An operator is represented independently as displacement-indexed matrix diagonals:
# A[z,z xor v]=f_v(z). Polynomial coefficients are lists of these exact arrays.
def plus(a,b):
    out={v:list(f) for v,f in a.items()}
    for v,f in b.items():
        if v not in out:out[v]=[F(0)]*len(f)
        out[v]=[x+y for x,y in zip(out[v],f)]
    return {v:f for v,f in out.items() if any(f)}
def times(a,c):return {v:[c*x for x in f] for v,f in a.items() if c and any(f)}
def driver(a,N):
    out={}
    for v,f in a.items():
        for q in range(N):out=plus(out,{v^(1<<q):[-(f[z^(1<<q)]-f[z]) for z in range(1<<N)]})
    return out

def diag(a,E):return {v:[f[z]*(E[z]-E[z^v]) for z in range(len(E))] for v,f in a.items() if v}
def step(poly,N,E):
    new=[{} for _ in range(len(poly)+1)]
    for i,a in enumerate(poly):
        d=driver(a,N);e=diag(a,E);new[i]=plus(new[i],d);new[i+1]=plus(new[i+1],plus(e,times(d,-1)))
    integrated=[{} for _ in range(len(new)+1)]
    for i,a in enumerate(new):integrated[i+1]=times(a,-F(1,i+1));integrated[0]=plus(integrated[0],times(a,F(1,i+1)))
    return integrated

def expectation(a,N):return sum((sum(f,F(0)) for f in a.values()),F(0))/(1<<N)
def main():
    start=time.perf_counter();rng=random.Random(16531);records=[]
    for case in range(16):
        N=2+case%3;n=1+case%N
        h=[F(rng.randint(-3,3),4) for _ in range(N)];J={(q,r):F(rng.randint(-3,3),4) for q in range(N) for r in range(q+1,N) if rng.random()<.6}
        E=[]
        for z in range(1<<N):
            spins=[2*((z>>q)&1)-1 for q in range(N)];E.append(sum((h[q]*spins[q] for q in range(N)),F(0))+sum((v*spins[q]*spins[r] for (q,r),v in J.items()),F(0)))
        load=[abs(v) for v in h]
        for (q,r),v in J.items():load[q]+=abs(v);load[r]+=abs(v)
        g=max(load);events={z for z in range(1<<n) if rng.random()<.4};events=events or {rng.randrange(1<<n)}
        event=[F(int((z&((1<<n)-1)) in events)) for z in range(1<<N)];p0=sum(event,F(0))/(1<<N);poly=[{0:event}];C=schedule_coefficients(n,8);rows=[]
        direct2=sum((event[z]*sum((E[z^(1<<q)]-E[z] for q in range(N)),F(0)) for z in range(1<<N)),F(0))/(12*(1<<N)*p0)
        for k in range(1,9):
            poly=step(poly,N,E);v=expectation(poly[0],N)/p0
            if k%2:
                assert v==0;continue
            coefficient=(-1)**(k//2)*v;bound=sum((a*g**m for m,a in C[k]),F(0));assert abs(coefficient)<=bound
            if k==2:assert coefficient==direct2
            rows.append({'order':k,'coefficient_exact':[coefficient.numerator,coefficient.denominator],'majorant_exact':[bound.numerator,bound.denominator]})
        records.append({'case':case,'N':N,'n':n,'uniform_event_mass_exact':[p0.numerator,p0.denominator],'event_patterns':sorted(events),'orders':rows})
    out={'status':'pass','models':len(records),'even_coefficients_checked':sum(len(r['orders']) for r in records),'odd_coefficients_zero':64,'method':'Independent exact displacement-matrix Heisenberg Dyson integration, through order8; does not use majorant recurrence to obtain coefficients. Checks second-order schedule orientation against neighbor-energy formula.','seconds':time.perf_counter()-start,'records':records};(HERE/'results/exact_word_checks.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='records'}))
if __name__=='__main__':main()
