"""Exact-rational actual optimum-event finite-forward bound; no decoding solve."""
from pathlib import Path
from fractions import Fraction as F
from math import comb
import json,time,statistics,hashlib,sys
sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parents[1];LAB=HERE.parent

def parameters(record):
    base=record['baseline_program'];new=record['amplified_program'];n=record['input']['n']
    h0={int(q):F(v) for q,v in base['h']};h1={int(q):F(v) for q,v in new['h']}
    J0={tuple(sorted((int(q),int(r)))):F(v) for q,r,v in base['J'] if v};J1={tuple(sorted((int(q),int(r)))):F(v) for q,r,v in new['J'] if v}
    roots={int(i):int(q) for i,q in base['roots'].items()};roots1={int(i):int(q) for i,q in new['roots'].items()}
    assert h0.keys()==h1.keys() and J0==J1 and roots==roots1
    assert len(set(roots[i] for i in range(n)))==n
    selected={roots[i] for i in range(n)};assert all(h0[q]==h1[q] for q in h0 if q not in selected)
    eta=F(*record['parameters']['eta_difference']);assert eta>0
    weights=list(map(F,record['input']['weights']));rho=sum((abs(h1[roots[i]]-h0[roots[i]]-eta*weights[i]/2) for i in range(n)),F(0))
    D=F(*record['moments']['short_time_cost_advantage_lower_exact']);curvature=eta*D/12-rho/6
    def local(h):
        load={q:abs(v) for q,v in h.items()}
        for (q,r),v in J0.items():load[q]+=abs(v);load[r]+=abs(v)
        return max(load.values(),default=F(0))
    def global_norm(h):return (len(h)+sum(map(abs,h.values()),F(0))+sum(map(abs,J0.values()),F(0)))/2
    return {'n':n,'N':len(h0),'eta':eta,'D':D,'rho':rho,'curvature':curvature,'g0':local(h0),'g1':local(h1),'lambda0':global_norm(h0),'lambda1':global_norm(h1)}

def relative_tail(s,x):
    if not 0<=x<1:return None
    return ((1-x)**(-s)+(1+x)**(-s))/2-1-comb(s+1,2)*x*x

def global_tail(lam,T):
    y=2*lam*T
    if y*y>=30:return None
    return y**4/(24*(1-y*y/30))

def certificate(p,method):
    if p['curvature']<=0:return {'status':'inconclusive_nonpositive_actual_curvature'}
    for k in range(81):
        T=F(1,2**k)
        if method=='local':a=relative_tail(p['n'],(1+p['g0'])*T);b=relative_tail(p['n'],(1+p['g1'])*T)
        else:a=global_tail(p['lambda0'],T);b=global_tail(p['lambda1'],T)
        if a is None or b is None:continue
        gap=p['curvature']*T*T-a-b
        if gap>0:return {'status':'strict_actual_original_optimum_order','duration':float(T),'duration_exact':pair(T),'relative_advantage_lower':float(gap),'relative_advantage_lower_exact':pair(gap),'remainder_exact':pair(a+b),'menu_index':k}
    return {'status':'inconclusive_menu_exhausted'}

def pair(x):return {'numerator_hex':hex(x.numerator),'denominator_hex':hex(x.denominator)}

def main():
    start=time.perf_counter();out=HERE/'results';out.mkdir(exist_ok=True);records=[]
    for path in sorted((LAB/'results/forward_ordinary').glob('*.json')):
        st=time.perf_counter();d=json.loads(path.read_text());p=parameters(d);local=certificate(p,'local');global_actual=certificate(p,'global')
        r={'name':d['name'],'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'parameters':{k:pair(v) if isinstance(v,F) else v for k,v in p.items()},'parent_certificate':d['certificate'],'actual_curvature_global_control':global_actual,'relative_event_local':local,'seconds':time.perf_counter()-st}
        (out/path.name).write_text(json.dumps(r,indent=2)+'\n');row={'name':d['name'],'n':p['n'],'N':p['N'],'seconds':r['seconds'],'parent_duration':d['certificate'].get('duration'),'global_actual_duration':global_actual.get('duration'),'local_duration':local.get('duration')}
        if row['local_duration'] and row['parent_duration']:row['gain_over_parent']=row['local_duration']/row['parent_duration']
        if row['local_duration'] and row['global_actual_duration']:row['gain_over_global_actual']=row['local_duration']/row['global_actual_duration']
        records.append(row)
    good=[r for r in records if r['local_duration']]
    result={'status':'complete','instances':len(records),'local_certified':len(good),'median_local_duration':statistics.median(r['local_duration'] for r in good),'min_local_duration':min(r['local_duration'] for r in good),'max_local_duration':max(r['local_duration'] for r in good),'median_gain_over_parent':statistics.median(r['gain_over_parent'] for r in good),'median_gain_over_global_actual':statistics.median(r['gain_over_global_actual'] for r in good),'median_seconds':statistics.median(r['seconds'] for r in records),'seconds':time.perf_counter()-start,'records':records,'scope':'Actual rounded-program original-root feasible optimum probability order under standard-|+> full physical finite-forward evolution, at a certified generally tiny duration. No decoding optimum/event enumeration is performed.'}
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='records'}))
if __name__=='__main__':main()
