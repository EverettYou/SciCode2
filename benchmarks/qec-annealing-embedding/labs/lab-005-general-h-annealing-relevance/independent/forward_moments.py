"""Sparse T²/T⁴ physical-forward readout moments; no Hilbert space or decoding solve."""
from fractions import Fraction as F
from itertools import combinations
from forward_certificate import cost_moments

def expansion(h,J,exact=False):
    h={int(q):(F(v) if exact else float(v)) for q,v in h.items()};J={tuple(sorted((int(q),int(r)))):(F(v) if exact else float(v)) for (q,r),v in J.items() if v}
    zero=F(0) if exact else 0.;ratio=lambda a,b:F(a,b) if exact else a/b
    q2={};q4={};neighbors={q:[] for q in h}
    def add(p,mask,value):
        if not value:return
        p[mask]=p.get(mask,zero)+value
        if not p[mask]:del p[mask]
    for q,v in h.items():add(q2,1<<q,-v*ratio(1,6));add(q4,1<<q,v*ratio(1,168))
    for (q,r),v in J.items():
        mask=(1<<q)|(1<<r);add(q2,mask,-v*ratio(1,3));add(q4,mask,v*ratio(1,21));neighbors[q].append((r,v));neighbors[r].append((q,v))
    for q,hq in h.items():
        ns=neighbors[q];S=sum((v*v for r,v in ns),zero);qmask=1<<q
        add(q4,0,-(hq*hq+2*S)*ratio(1,72));add(q4,qmask,(hq**3+3*hq*S)*ratio(1,168))
        for r,v in ns:
            add(q4,1<<r,-hq*v*ratio(41,840));add(q4,qmask|(1<<r),v*(3*hq*hq+3*S-2*v*v)*ratio(1,168))
        for (r,v),(s,w) in combinations(ns,2):
            add(q4,(1<<r)|(1<<s),-v*w*ratio(22,315));add(q4,qmask|(1<<r)|(1<<s),hq*v*w*ratio(1,28))
        for (r,v),(s,w),(t,x) in combinations(ns,3):add(q4,qmask|(1<<r)|(1<<s)|(1<<t),v*w*x*ratio(1,28))
    return q2,q4

def grouped(poly,root_positions,patterns,reference):
    root_by_position={q:i for i,q in enumerate(root_positions)};groups={}
    for mask,value in poly.items():
        unobserved=0;character=0;sign=1;m=mask
        while m:
            bit=m&-m;q=bit.bit_length()-1;m^=bit
            if q in root_by_position:
                i=root_by_position[q];character^=patterns[i];sign*=2*reference[i]-1
            else:unobserved|=bit
        key=(unobserved,character);groups[key]=groups.get(key,0.)+float(value)*sign
    return groups

def evaluate_moments(data,program,moments=None):
    moments=moments or cost_moments(data['rows'],data['n'],data['syndrome'],data['weights'])
    nodes=sorted(q for q,v in program['h']);idx={q:i for i,q in enumerate(nodes)}
    h={idx[q]:v for q,v in program['h']};J={(idx[q],idx[r]):v for q,r,v in program['J'] if v}
    roots={int(i):q for i,q in program['roots'].items()};root_positions=[idx[roots[i]] for i in range(data['n'])]
    q2,q4=expansion(h,J);patterns=[int(v,16) for v in moments['kernel_character_hex']];reference=moments['particular_solution']
    g2=grouped(q2,root_positions,patterns,reference);g4=grouped(q4,root_positions,patterns,reference);costchars={}
    for i,p in enumerate(patterns):
        if p:costchars[p]=costchars.get(p,0.)+float(data['weights'][i])*(2*reference[i]-1)/2
    a2=g2.get((0,0),0.);a4=g4.get((0,0),0.)+.5*sum(v*v for v in g2.values())
    c2=sum(v*g2.get((0,k),0.) for k,v in costchars.items())
    cov4=sum(v*g4.get((0,k),0.) for k,v in costchars.items())
    for character,c in costchars.items():cov4+=.5*c*sum(v*g2.get((unobserved,k^character),0.) for (unobserved,k),v in g2.items())
    c4=cov4-a2*c2
    return {'rank':moments['rank'],'physical_spins':len(nodes),'physical_nonzero_couplers':len(J),'q2_terms':len(q2),'q4_terms':len(q4),
      'feasible_probability_at_zero':2.**(-moments['rank']),'uniform_feasible_cost':float(F(*moments['mean_exact'])),
      'feasibility_relative_T2':a2,'feasibility_relative_T4':a4,'conditional_cost_T2':c2,'conditional_cost_T4':c4,
      'interpretation':'Exact-order algebra, evaluated numerically. T²/T⁴ coefficients are not a moderate-time probability certificate without a remainder bound.'}
