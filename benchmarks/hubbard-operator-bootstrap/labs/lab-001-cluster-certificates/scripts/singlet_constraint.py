#!/usr/bin/env python3
"""Independent S^-S^+=S^2 row at Sz=0, with direct Fock-space tests."""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path
import numpy as np
from audit_moment_maps import Audit,add_scaled,dagger

def apply(word,mask):
    sign=1
    for create,p in reversed(word):
        if ((mask>>p)&1)==create:return None,0
        sign*=(-1)**((mask&((1<<p)-1)).bit_count());mask^=1<<p
    return mask,sign

def spin_norm_squared(psi):
    out=collections.defaultdict(int)
    for mask,amp in psi.items():
        for k in range(16):
            target,sign=apply(((1,k),(0,16+k)),mask)
            if sign:out[target]+=amp*sign
    return sum(v*v for v in out.values())/sum(v*v for v in psi.values())

def moments(a,psi):
    x=np.zeros(len(a.names));norm=sum(v*v for v in psi.values())
    for z,name in enumerate(a.names):
        if name.startswith('n_'):
            k=int(name[2:]);x[z]=sum(amp*amp*((mask>>k)&1) for mask,amp in psi.items())/norm
        else:
            i,j,k,l=map(int,name.split('_')[1:]);word=((1,i),(1,j),(0,l),(0,k));s=0
            for mask,amp in psi.items():
                target,sign=apply(word,mask)
                if sign:s+=psi.get(target,0)*amp*sign
            x[z]=s/norm
    return x

def derive(names):
    a=Audit(names);row=collections.defaultdict(int);compact=collections.defaultdict(int)
    for k,p in __import__('itertools').product(range(16),repeat=2):
        # Direct four-operator expansion of (sum c†down cup)(sum c†up cdown).
        add_scaled(row,a.words_affine([(1,((1,16+k),(0,k),(1,p),(0,16+p)))]))
        add_scaled(compact,a.gamma(16+k,p,16+p,k),-1)
    for k in range(16):compact[a.index[f'n_{16+k}']]+=1
    row={z:v for z,v in row.items() if v};compact={z:v for z,v in compact.items() if v}
    assert row==compact and -1 not in row
    common=sum((1<<k)|(1<<(16+k)) for k in range(7))
    ma=common|(1<<7)|(1<<(16+8));mb=common|(1<<8)|(1<<(16+7))
    tests=[]
    for sign in [-1,1]:
        psi={ma:1,mb:sign};x=moments(a,psi);value=sum(v*x[z] for z,v in row.items());direct=spin_norm_squared(psi)
        assert value==direct and value in [0.,2.]
        tests.append({'relative_determinant_sign':sign,'moment_row_value':value,'direct_spin_raise_norm_squared':direct})
    assert {t['moment_row_value'] for t in tests}=={0.,2.}
    # An eight-doubly-occupied-orbital Slater determinant is also a singlet.
    mask=sum((1<<k)|(1<<(16+k)) for k in range(8));x=moments(a,{mask:1})
    assert sum(v*x[z] for z,v in row.items())==spin_norm_squared({mask:1})==0
    return {'equation':'sum_k n_(k,down) - sum_(k,p) Gamma_(downk,upp;downp,upk) = 0','coefficient_by_name':{names[z]:v for z,v in sorted(row.items())},'rhs':0,'nnz':len(row),'direct_fock_tests':tests,'sector_assumption':'The state is a spin singlet. At Nup=Ndown=8, Sz=0, so S^-S^+=S².','ground_state_justification_required':'Lieb theorem for repulsive half-filled connected bipartite Hubbard lattice with equal sublattices.','scope':'A theorem-backed restriction preserving the physical ground energy, not an extra identity for all states of the original Nup=Ndown=8 sector.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('variable_names',type=Path);p.add_argument('output',type=Path);args=p.parse_args();r=derive(json.loads(args.variable_names.read_text()));args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='coefficient_by_name'},indent=2))
