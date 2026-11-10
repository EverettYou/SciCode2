#!/usr/bin/env python3
from pathlib import Path
import sys,json,math
from fractions import Fraction
import numpy as np
import scipy.sparse as sp
here=Path(__file__).resolve().parent;sys.path.insert(0,str(here))
from local_extension import local_coupling,density_variables,trace_operator,POS,phase
root=here.parents[2]

def run():
    inp=root/'labs/lab-003-theory-audit/outputs/pqgt2prime_sym'
    names=json.loads((inp/'full_variable_names.json').read_text());T=sp.load_npz(inp/'symmetry_expansion.npz')
    maps,stats=local_coupling(names,T);rnames,index,blocks=density_variables()
    def reduce(x):
        y=[]
        for j in range(T.shape[1]):
            col=T.getcol(j).tocoo();y.append(x[int(col.row[0])]*int(col.data[0]))
        return y
    x=[]
    for name in names:
        if name.startswith('n_'):x.append(Fraction(1,2))
        else:
            a,b,c,d=map(int,name.split('_')[1:]);x.append(Fraction(0) if (a,b)!=(c,d) else(Fraction(7,30) if a//16==b//16 else Fraction(1,4)))
    y=reduce(x);rho=[Fraction(0)]*len(rnames)
    for mask in range(256):
        a=(mask&15).bit_count();b=(mask>>4).bit_count()
        rho[index[mask,mask]]=Fraction(math.comb(12,8-a)*math.comb(12,8-b),math.comb(16,8)**2)
    max_error=Fraction(0)
    for m in maps:
        lhs=sum(int(v)*y[z] for z,v in enumerate(m['coeff']) if v)/m['denominator']
        rhs=sum(v*rho[z] for z,v in trace_operator(m['word'],index).items())
        max_error=max(max_error,abs(lhs-rhs));assert lhs==rhs,(m['name'],lhs,rhs)
    # An independent closed-shell Slater check uses Wick'sdeterminant locally.
    filled={0,10,2,8,1,3,4,12};occup=np.array([int(a%16 in filled) for a in range(32)])
    x=[]
    for name in names:
        if name.startswith('n_'):x.append(int(occup[int(name[2:])]))
        else:
            a,b,c,d=map(int,name.split('_')[1:]);x.append(int(occup[a]*occup[b]) if (a,b)==(c,d) else 0)
    y=reduce(x);gamma=np.zeros((8,8),dtype=complex)
    for a in range(8):
        for b in range(8):
            if a//4==b//4:gamma[a,b]=sum(np.conj(phase(k,POS[a%4]))*phase(k,POS[b%4]) for k in filled)/16
    worst=0.
    for m in maps:
        actual=float(sum(int(v)*y[z] for z,v in enumerate(m['coeff']) if v)/m['denominator'])
        w=m['word']
        if len(w)==2:expected=gamma[w[0][1],w[1][1]]
        else:
            a,b,d,c=[p for _,p in w];expected=gamma[a,c]*gamma[b,d]-gamma[a,d]*gamma[b,c]
        worst=max(worst,abs(actual-expected));assert actual==expected,(m['name'],actual,expected)
    out=dict(**stats,local_rho_variables=len(rnames),hypergeometric_all198_moments_exact=True,hypergeometric_max_fraction_error=str(max_error),closed_shell_all198_wick_moments_exact=True,closed_shell_max_error=worst)
    p=root/'labs/lab-005-local-rdm-extension/results/physical-map-checks.json';p.write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':run()
