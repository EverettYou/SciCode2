"""Exact row marginals and original-error terminal Gibbs references."""
import math
import numpy as np
from scipy.special import logsumexp


def balanced_row_logs(d,u):
    if d==0:return (0.,-math.inf)
    if d<=2:return (0.,-u)
    r=math.exp(-u);loga=4*math.log1p(r);logb=math.log(8)-u+math.log1p(r*r)
    lv,li=0.,-u
    for _ in range(d-2):lv,li=np.logaddexp(loga+lv,logb+li),np.logaddexp(loga+li,logb+lv)
    return float(lv),float(li)


def row_log_factor(bits,syndrome,u,scheme):
    d=bits.shape[1];N=len(bits)
    if d==0:return np.zeros(N) if syndrome==0 else np.full(N,-u)
    violation=(bits.sum(axis=1)%2!=syndrome)
    if d<=2:return -u*violation.astype(float)
    if scheme=='balanced':
        a,b=balanced_row_logs(d,u);return np.where(violation,b,a)
    x=bits[:,0];f0=np.where(x==0,0.,-np.inf);f1=np.where(x==1,0.,-np.inf)
    for col in range(1,d-1):
        x=bits[:,col];new=[]
        for p in [0,1]:
            a0=np.logaddexp(-u*(x-p)**2,-u*(x-p-2)**2)
            a1=np.logaddexp(-u*(1+x-p)**2,-u*(1+x-p-2)**2)
            new.append(np.logaddexp(f0+a0,f1+a1))
        f0,f1=new
    x=bits[:,-1]
    return np.logaddexp(f0-u*(x!=syndrome),f1-u*((1^x)!=syndrome))


def row_envelopes(rows,syndrome,u,scheme,max_degree=20):
    envelopes=[]
    for support,s in zip(rows,syndrome):
        d=len(support)
        if d>max_degree and scheme=='standard':return {'status':'inconclusive_degree_limit','degree':d}
        if d==0:envelopes.append({'degree':0,'kappa':math.inf,'valid_log_range':0.,'valid_log_min':0.,'valid_log_max':0.});continue
        if scheme=='balanced':
            a,b=balanced_row_logs(d,u);envelopes.append({'degree':d,'kappa':a-b,'valid_log_range':0.,'valid_log_min':a,'valid_log_max':a,'invalid_log_min':b,'invalid_log_max':b})
        else:
            bits=((np.arange(2**d,dtype=np.uint64)[:,None]>>np.arange(d,dtype=np.uint64))&1).astype(np.int16)
            logf=row_log_factor(bits,s,u,scheme);valid=(bits.sum(axis=1)%2==s);a=float(logf[valid].min());b=float(logf[valid].max());c=float(logf[~valid].min());e=float(logf[~valid].max())
            envelopes.append({'degree':d,'kappa':b-e,'valid_log_range':b-a,'valid_log_min':a,'valid_log_max':b,'invalid_log_min':c,'invalid_log_max':e})
    R=sum(x['valid_log_range'] for x in envelopes)
    return {'status':'ok','rows':envelopes,'valid_log_factor_range':R,'conditional_feasible_tv_bound':math.tanh(R/4)}


def syndrome_certificate(envelopes,basis_rows,repair_loads,t):
    if envelopes['status']!='ok':return {'status':envelopes['status'],'feasible_probability_lower':0.}
    rows=envelopes['rows'];basis=set(basis_rows);R=envelopes['valid_log_factor_range']
    correction=R+sum(max(0.,-x['kappa']) for i,x in enumerate(rows) if i not in basis and math.isfinite(x['kappa']))
    logs=[]
    for row,load in zip(basis_rows,repair_loads):logs.append(float(np.logaddexp(0.,t*load-rows[row]['kappa'])))
    logproduct=sum(logs)
    if logproduct==0:logextra=-math.inf
    elif logproduct<700:logextra=correction+math.log(math.expm1(logproduct))
    else:logextra=correction+logproduct
    logden=float(np.logaddexp(0.,logextra));p=math.exp(-logden) if logden<745 else 0.
    return {'status':'ok','feasible_probability_lower':p,'syndrome_defect_bound':-math.expm1(-logden),
            'conditional_feasible_tv_bound':envelopes['conditional_feasible_tv_bound'],
            'row_log_factor_range':R,'repair_log_product':logproduct,'repair_correction':correction,
            'minimum_repair_margin':min((rows[row]['kappa']-t*load for row,load in zip(basis_rows,repair_loads)),default=None)}


def exact_original_gibbs(data,M,t,scheme):
    n=data['n'];bits=((np.arange(2**n,dtype=np.uint64)[:,None]>>np.arange(n,dtype=np.uint64))&1).astype(np.int16)
    cost=bits@np.asarray(data['weights']);valid=np.ones(len(bits),dtype=bool);logw=-t*cost
    for row,s in zip(data['rows'],data['syndrome']):
        valid&=(bits[:,row].sum(axis=1)%2==s);logw+=row_log_factor(bits[:,row],s,t*M,scheme)
    lZ=float(logsumexp(logw));p=np.exp(logw-lZ);feasp=float(p[valid].sum());minimum=float(cost[valid].min());opt=valid&(cost==minimum)
    cond=p[valid]/feasp;ideal=np.exp(-t*cost[valid]-logsumexp(-t*cost[valid]));g=float(ideal[cost[valid]==minimum].sum())
    return {'original_optimum_probability':float(p[opt].sum()),'feasible_probability':feasp,
            'conditional_original_optimum_probability':float(p[opt].sum()/feasp),
            'intended_conditional_original_optimum_probability':g,'conditional_feasible_tv':.5*float(np.abs(cond-ideal).sum()),
            'full_qubo_ground_probability':int(opt.sum())*math.exp(-t*minimum-lZ),
            'ground_degeneracy':int(opt.sum()),'minimum_cost':minimum,'log_partition':lZ,
            'original_states':len(bits),'feasible_errors':int(valid.sum())}
