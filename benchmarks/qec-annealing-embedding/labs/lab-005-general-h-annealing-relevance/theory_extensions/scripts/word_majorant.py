"""Schedule-aware relative-event mixed driver/diagonal commutator majorant."""
from fractions import Fraction as F
from math import comb
from pathlib import Path
import json,time,statistics,sys
from relative_event import parameters,pair,HERE,LAB
sys.set_int_max_str_digits(0)
ORDER=12

def add(a,b):
    c=[F(0)]*max(len(a),len(b))
    for i,v in enumerate(a):c[i]+=v
    for i,v in enumerate(b):c[i]+=v
    return c

def scale(a,v):return [x*v for x in a]
def shift(a):return [F(0),*a]
def integrate_from_u_to_one(a):
    b=[F(0)]*(len(a)+1)
    for i,v in enumerate(a):b[i+1]=-v/(i+1)
    b[0]=-sum(b[1:],F(0));return b

def u_integral(a):return sum((v/F(i+2) for i,v in enumerate(a)),F(0))

def schedule_coefficients(s,K=ORDER):
    # B[d,m](u) majorizes inner-later words at times in[u,1], divided by gE**m.
    B={(0,0):[F(1)]};C={}
    for k in range(1,K+1):
        for d in range(k+1):
            m=k-d;p=[F(0)]
            if d:
                prev=B[d-1,m];p=add(p,scale(add(prev,scale(shift(prev),-1)),2*(s+m)))
            if m:p=add(p,scale(shift(B[d,m-1]),2*d))
            B[d,m]=integrate_from_u_to_one(p)
        if k%2==0:
            C[k]=[(m,2*d*u_integral(B[d,m-1])) for d in range(1,k) for m in [k-d]]
            assert all(v>=0 for m,v in C[k])
    assert C[2]==[(1,F(s,6))]
    return C

def remainder(n,g,T,C,K=ORDER,through_order=2):
    if through_order not in range(2,K+1,2):raise ValueError("through_order must be even in[2,K]")
    x=(1+g)*T
    if not 0<=x<1:return None
    generic=((1-x)**(-n)+(1+x)**(-n))/2
    for k in range(0,K+1,2):generic-=comb(n+k-1,k)*x**k
    low=F(0)
    for k in range(through_order+2,K+1,2):
        special=sum((v*g**m for m,v in C[k]),F(0))*T**k
        ordinary=comb(n+k-1,k)*x**k
        low+=min(special,ordinary)
    assert generic>=0
    return low+generic

def certificate(p,C):
    if p['curvature']<=0:return {'status':'inconclusive_nonpositive_actual_curvature'}
    for k in range(81):
        T=F(1,2**k);a=remainder(p['n'],p['g0'],T,C);b=remainder(p['n'],p['g1'],T,C)
        if a is None or b is None:continue
        gap=p['curvature']*T*T-a-b
        if gap>0:return {'status':'strict_actual_original_optimum_order','duration':float(T),'duration_exact':pair(T),'relative_advantage_lower':float(gap),'relative_advantage_lower_exact':pair(gap),'remainder_exact':pair(a+b),'menu_index':k}
    return {'status':'inconclusive_menu_exhausted'}

def main():
    start=time.perf_counter();records=[];cache={};out=HERE/'results/word_majorant';out.mkdir(exist_ok=True)
    for path in sorted((LAB/'results/forward_ordinary').glob('*.json')):
        st=time.perf_counter();d=json.loads(path.read_text());p=parameters(d)
        if p['n'] not in cache:cache[p['n']]=schedule_coefficients(p['n'])
        C=cache[p['n']];cert=certificate(p,C);old=json.loads((HERE/'results'/path.name).read_text());r={'name':d['name'],'parameters':{k:pair(v) if isinstance(v,F) else v for k,v in p.items()},'certificate':cert,'schedule_coefficients':{k:[[m,pair(v)] for m,v in a] for k,a in C.items()},'seconds':time.perf_counter()-st};(out/path.name).write_text(json.dumps(r,indent=2)+'\n')
        row={'name':d['name'],'n':p['n'],'N':p['N'],'seconds':r['seconds'],'duration':cert.get('duration'),'parent_duration':d['certificate'].get('duration'),'local_support_duration':old['relative_event_local'].get('duration')}
        for oldname in ['parent','local_support']:
            if row['duration'] and row[oldname+'_duration']:row['gain_over_'+oldname]=row['duration']/row[oldname+'_duration']
        records.append(row)
    good=[r for r in records if r['duration']];result={'status':'complete','instances':len(records),'certified':len(good),'order':ORDER,'median_duration':statistics.median(r['duration'] for r in good),'min_duration':min(r['duration'] for r in good),'max_duration':max(r['duration'] for r in good),'median_gain_over_parent':statistics.median(r['gain_over_parent'] for r in good),'median_gain_over_local_support':statistics.median(r['gain_over_local_support'] for r in good),'median_seconds':statistics.median(r['seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records,'scope':'Actual original-error optimum finite-forward event; certified interval remains conservative, not moderate-time evidence.'};(HERE/'results/word_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
