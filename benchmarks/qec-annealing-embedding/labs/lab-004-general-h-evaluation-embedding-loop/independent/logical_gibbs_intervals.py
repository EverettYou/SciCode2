"""Outward interval sum of the complete XOR-compiled logical Gibbs model.

Enumerates only original errors; each row's auxiliary partition function is
summed by an independent two-state transfer matrix. No compiler/evaluator import.
"""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext,ROUND_FLOOR,ROUND_CEILING
import numpy as np
import json,math,time
LAB=Path(__file__).resolve().parents[1]

def exp_interval(exponent):
    if not exponent:return 1.,1.
    with localcontext() as c:
        c.prec=70;c.rounding=ROUND_FLOOR;lo=D(exponent.numerator)/D(exponent.denominator)
        c.rounding=ROUND_CEILING;hi=D(exponent.numerator)/D(exponent.denominator)
        elo=lo.exp().next_minus();ehi=hi.exp().next_plus()
        a=float(elo);b=float(ehi)
        if D.from_float(a)>elo:a=math.nextafter(a,-math.inf)
        if D.from_float(b)<ehi:b=math.nextafter(b,math.inf)
        return max(0.,a),b

def mul(a,b,up):return np.nextafter(a*b,np.inf if up else -np.inf).clip(min=0.)
def add(a,b,up):return np.nextafter(a+b,np.inf if up else -np.inf).clip(min=0.)

def interval_mass(rows,n,syndrome,weights,penalty,t):
    assert n<=20
    t=F(t);penalty=F(penalty)
    w4=[F(w)*4 for w in weights];assert all(w.denominator==1 for w in w4)
    w4=np.array([int(w) for w in w4],dtype=np.int64)
    ids=np.arange(1<<n,dtype=np.uint64);bits=((ids[:,None]>>np.arange(n,dtype=np.uint64))&1).astype(np.int8)
    costs=bits@w4;min_unconstrained=int(sum(min(0,int(w)) for w in w4))
    feasible=np.ones(len(ids),dtype=bool)
    for row,s in zip(rows,syndrome):feasible &= ((bits[:,row].sum(axis=1)%2)==s)
    e0=int(costs[feasible].min());g0=int(np.sum(feasible & (costs==e0)))
    elos=[];ehis=[]
    for q in range(10):
        a,b=exp_interval(-t*penalty*q);elos.append(a);ehis.append(b)
    elos=np.array(elos);ehis=np.array(ehis)
    denlo=np.ones(len(ids));denhi=np.ones(len(ids))
    for row,s in zip(rows,syndrome):
        d=len(row)
        if d==0:assert s==0;continue
        if d==1:
            idx=bits[:,row[0]]^s;rlo=elos[idx];rhi=ehis[idx]
        elif d==2:
            idx=bits[:,row[0]]^bits[:,row[1]]^s;rlo=elos[idx];rhi=ehis[idx]
        else:
            vslo=[(bits[:,row[0]]==p).astype(float) for p in (0,1)];vshi=[x.copy() for x in vslo]
            for col in row[1:-1]:
                b=bits[:,col];newlo=[];newhi=[]
                for p in (0,1):
                    lower=np.zeros(len(ids));upper=np.zeros(len(ids))
                    for a in (0,1):
                        q0=(a+b-p)**2;q1=(a+b-p-2)**2
                        k_lo=add(elos[q0],elos[q1],False);k_hi=add(ehis[q0],ehis[q1],True)
                        lower=add(lower,mul(vslo[a],k_lo,False),False)
                        upper=add(upper,mul(vshi[a],k_hi,True),True)
                    newlo.append(lower);newhi.append(upper)
                vslo,vshi=newlo,newhi
            last=bits[:,row[-1]]
            rlo=add(mul(vslo[0],elos[last^s],False),mul(vslo[1],elos[(1-last)^s],False),False)
            rhi=add(mul(vshi[0],ehis[last^s],True),mul(vshi[1],ehis[(1-last)^s],True),True)
        denlo=mul(denlo,rlo,False);denhi=mul(denhi,rhi,True)
    costvals={int(x) for x in costs};exps={c:exp_interval(-t*F(c-min_unconstrained,4)) for c in costvals}
    clo=np.array([exps[int(c)][0] for c in costs]);chi=np.array([exps[int(c)][1] for c in costs])
    denlo=mul(denlo,clo,False);denhi=mul(denhi,chi,True)
    assert np.all(np.isfinite(denhi)) and denlo.sum()>0
    # Any order of positive additions obeys the standard gamma_(N-1) bound.
    u=np.finfo(float).eps;g=(len(ids)*u)/(1-len(ids)*u)
    zlo=math.nextafter(float(denlo.sum())/(1+g),-math.inf)
    zhi=math.nextafter(float(denhi.sum())/(1-g),math.inf)
    nlo,nhi=exp_interval(-t*F(e0-min_unconstrained,4))
    nlo=math.nextafter(nlo*g0,-math.inf);nhi=math.nextafter(nhi*g0,math.inf)
    plo=max(0.,math.nextafter(nlo/zhi,-math.inf));phi=min(1.,math.nextafter(nhi/zlo,math.inf))
    error_nlo=math.nextafter(float(denlo[feasible & (costs==e0)].sum())/(1+g),-math.inf)
    error_nhi=math.nextafter(float(denhi[feasible & (costs==e0)].sum())/(1-g),math.inf)
    error_plo=max(0.,math.nextafter(error_nlo/zhi,-math.inf));error_phi=min(1.,math.nextafter(error_nhi/zlo,math.inf))
    return {'lower':plo,'upper':phi,'decoded_error_lower':error_plo,'decoded_error_upper':error_phi,'ground_cost':e0/4,'ground_degeneracy':g0,'auxiliary_partition_summed':True,'original_patterns':len(ids),'relative_interval_width':(phi-plo)/max(phi,1e-300)}

def self_check():
    rows=[[0,1,2],[1,2,3]];n=4;syndrome=[1,0];weights=[-.5,.25,1.,0.];penalty=F(11,4);t=F(7,5)
    bound=interval_mass(rows,n,syndrome,weights,penalty,t)
    vals=[];ground=[]
    for state in range(256):
        b=[(state>>i)&1 for i in range(8)];en=sum(F(w)*b[i] for i,w in enumerate(weights))
        for rid,(row,s) in enumerate(zip(rows,syndrome)):
            p,c=b[4+2*rid],b[5+2*rid];a,x,y=[b[i] for i in row]
            en+=penalty*((a+x-p-2*c)**2+(s^p^y))
        vals.append(en)
    eg=min(vals)
    with localcontext() as c:
        c.prec=60;weightsD=[(-D(t.numerator)/D(t.denominator)*D((v-eg).numerator)/D((v-eg).denominator)).exp() for v in vals]
        prob=D(sum(v==eg for v in vals))/sum(weightsD)
        assert D.from_float(bound['lower'])<=prob<=D.from_float(bound['upper']),(bound,prob)
        errors=[[(state>>i)&1 for i in range(4)] for state in range(256)]
        decoded_mask=[all(sum(e[i] for i in row)%2==s for row,s in zip(rows,syndrome)) and sum(F(w)*e[i] for i,w in enumerate(weights))==eg for e in errors]
        decoded_prob=sum(v for v,ok in zip(weightsD,decoded_mask) if ok)/sum(weightsD)
        assert D.from_float(bound['decoded_error_lower'])<=decoded_prob<=D.from_float(bound['decoded_error_upper'])
    return {'status':'pass','expanded_assignments':256,'interval':bound,'dense_probability':str(prob),'dense_decoded_error_probability':str(decoded_prob)}

def main():
    start=time.perf_counter();test=self_check()
    audited=json.loads((LAB/'results/independent_program_audit.json').read_text())['records']
    lookup={(r['instance'],r['selection']):r for r in audited}
    results=[]
    for path in sorted((LAB/'results').glob('*_n16_s*.json')):
        data=json.loads(path.read_text());cache={};records={}
        lp_path=LAB/'results/lp'/path.name
        if lp_path.exists():data['selected']['lp_selected']=json.loads(lp_path.read_text())['selected']
        for label,entry in data['selected'].items():
            p=entry['program'];a=F(p['scale']);t=a*int(p['beta'])
            if a not in cache:cache[a]=interval_mass(data['model']['rows'],data['input']['n'],data['model']['syndrome'],data['model']['weights'],data['model']['penalty'],t)
            mass=cache[a];audit=lookup[data['name'],label];tv=audit['thermal_rounding_tv_upper'];defect=audit['classical_defect_upper']
            lower=math.nextafter((1-defect)*max(0.,mass['lower']-tv),-math.inf)
            upper=min(1.,math.nextafter(mass['upper']+tv,math.inf))
            decoded_upper=min(1.,math.nextafter(mass['decoded_error_upper']+tv+defect,math.inf))
            decoded_lower=max(0.,math.nextafter((1-defect)*max(0.,mass['decoded_error_lower']-tv),-math.inf))
            records[label]={'scale':float(a),'logical_gibbs_ground_mass':mass,'consistent_optimal_lower':max(0.,lower),'consistent_optimal_upper':upper,'root_decoded_optimal_upper':decoded_upper,'root_decoded_optimal_lower':decoded_lower}
        first=records['first'];guided=records['guided_pruned']
        results.append({'instance':data['name'],'split':data['input']['split'],'records':records,'conditional_mass_ratio_lower':guided['logical_gibbs_ground_mass']['lower']/first['logical_gibbs_ground_mass']['upper'],'strict_consistent_order_proved':guided['consistent_optimal_lower']>first['consistent_optimal_upper'],'root_decoded_order_proved':guided['root_decoded_optimal_lower']>first['root_decoded_optimal_upper'],'lp_strict_consistent_order_proved':records.get('lp_selected',guided)['consistent_optimal_lower']>first['consistent_optimal_upper']})
    out={'status':'pass','instances':len(results),'self_check':test,'consistent_optimal_improvement_certificates':sum(x['strict_consistent_order_proved'] for x in results),'root_decoded_improvement_certificates':sum(x['root_decoded_order_proved'] for x in results),'lp_consistent_optimal_improvement_certificates':sum(x['lp_strict_consistent_order_proved'] for x in results),'seconds':time.perf_counter()-start,'interpretation':'Certified endpoint Gibbs comparisons for explicitly distinguished readout events. Logical Gibbs mass includes all auxiliary excited states. Full-QUBO ground and decoded original-error optimum events are distinct; excited auxiliaries count for the latter. Exact original-error enumeration is validation only, not construction or selection. Interval enclosures use positive transfer arithmetic and Decimal-enclosed exponential constants.','records':results}
    (LAB/'results/independent_logical_gibbs_intervals.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['records','self_check']},indent=2))
if __name__=='__main__':main()
