"""Cheap exact-rational standard-|+> short-forward comparison. No decoding solve."""
from fractions import Fraction as F
from copy import deepcopy
from penalty_bound import witness,xor_selected,compiler

def cost_moments(rows,n,syndrome,weights,cert=None):
    rows=compiler.normalize_rows(rows,n)
    cert=cert or witness(rows,n,weights);B=cert['basis_columns'];R=cert['basis_rows'];inverse=[int(v,16) for v in cert['inverse_columns_hex']]
    selected=set(B);Rbits={row:set(rows[row]) for row in R}
    restricted=sum(int(syndrome[row])<<k for k,row in enumerate(R));coeff=xor_selected(restricted,inverse)
    particular=[0]*n
    for k,j in enumerate(B):particular[j]=(coeff>>k)&1
    if any(sum(particular[j] for j in row)%2!=s for row,s in zip(rows,syndrome)):raise ValueError('infeasible syndrome')
    patterns=[0]*n;free=[j for j in range(n) if j not in selected]
    for k,j in enumerate(free):
        restricted=sum(int(j in Rbits[row])<<p for p,row in enumerate(R));c=xor_selected(restricted,inverse)
        patterns[j]|=1<<k
        for p,i in enumerate(B):
            if (c>>p)&1:patterns[i]|=1<<k
    w=list(map(F,weights));mean=F(0);upper=F(0);groups={}
    for i,pat in enumerate(patterns):
        if pat:
            mean+=w[i]/2;upper+=max(F(0),w[i]);groups[pat]=groups.get(pat,F(0))+w[i]*(2*particular[i]-1)
        else:mean+=w[i]*particular[i];upper+=w[i]*particular[i]
    variance=sum((v*v/4 for v in groups.values()),F(0));assert upper>=mean
    minimum_upper=mean-variance/(upper-mean) if upper>mean else mean
    d_lower=sum(w,F(0))-2*minimum_upper
    pair=lambda v:[v.numerator,v.denominator]
    return {'rank':len(B),'kernel_dimension':len(free),'fixed_coordinates':[i for i,p in enumerate(patterns) if not p],
      'particular_solution':particular,'kernel_character_hex':[hex(p) for p in patterns],
      'mean_exact':pair(mean),'variance_exact':pair(variance),'cost_upper_exact':pair(upper),'minimum_cost_upper_exact':pair(minimum_upper),
      'short_time_cost_advantage_lower_exact':pair(d_lower),'short_time_cost_advantage_lower':float(d_lower),
      'uses_decoding_optimum':False}

def amplify(base,weights,new_eta):
    old_eta=F(base['scale']);new_eta=F(new_eta);assert new_eta>old_eta
    p=deepcopy(base);h={int(i):F(v) for i,v in base['h']};roots={int(i):int(q) for i,q in base['roots'].items()};ideal=dict(h)
    for i,w in enumerate(weights):ideal[roots[i]]+=(new_eta-old_eta)*F(w)/2
    rounded={q:float(v) for q,v in ideal.items()};rho=sum((abs(F(rounded[q])-v) for q,v in ideal.items()),F(0))
    low,high=map(F,p['ranges']['h']);assert all(low<=F(v)<=high for v in rounded.values())
    p['h']=[[q,v] for q,v in sorted(rounded.items())];p['scale']=float(new_eta)
    p['offset']=float(F(base['offset'])+(new_eta-old_eta)*sum(map(F,weights),F(0))/2)
    p['programming_policy']='Fixed roots, couplers and chain strengths; amplify only original objective fields.'
    p['objective_scale_exact']=[new_eta.numerator,new_eta.denominator];p['objective_field_rounding_l1_exact']=[rho.numerator,rho.denominator]
    N=len(h);Jsum=sum((abs(F(v)) for q,r,v in base['J']),F(0))
    lambda0=(N+sum(map(abs,h.values()),F(0))+Jsum)/2
    lambda1=(N+sum(map(abs,ideal.values()),F(0))+Jsum)/2
    lambdar=(N+sum((abs(F(v)) for v in rounded.values()),F(0))+Jsum)/2
    return p,{'eta_difference':new_eta-old_eta,'rounding':rho,'lambda0':lambda0,'lambda1':lambda1,'lambda_max':max(lambda0,lambda1,lambdar)}

def certificate(moments,parameters):
    d=F(*moments['short_time_cost_advantage_lower_exact']);A=parameters['eta_difference']*d/12
    pair=lambda v:[v.numerator,v.denominator]
    result={'coefficient_lower_exact':pair(A),'coefficient_lower':float(A),'cost_advantage_positive':d>0}
    if A<=0:return {**result,'status':'inconclusive_nonpositive_curvature_bound'}
    for k in range(81):
        T=F(1,2**k);lm=parameters['lambda_max'];x=2*lm*T
        if x>=F(1,2):continue
        def tail(lam):
            y=2*lam*T;return y**4/(24*(1-y*y/30))
        remainder=tail(parameters['lambda0'])+tail(parameters['lambda1'])
        rounding=T*parameters['rounding']/(1-x)
        lower=A*T*T-remainder-rounding
        if lower>0:
            return {**result,'status':'strict_finite_forward_order','duration_exact':pair(T),'duration':float(T),
              'relative_probability_advantage_lower_exact':pair(lower),'relative_probability_advantage_lower':float(lower),
              'remainder_upper_exact':pair(remainder),'rounding_upper_exact':pair(rounding),
              'interpretation':'Actual rounded amplified program beats baseline at this certified standard-|+> finite-forward duration. This tiny interval is not a moderate-time guarantee.'}
    return {**result,'status':'inconclusive_rounding_or_remainder'}
