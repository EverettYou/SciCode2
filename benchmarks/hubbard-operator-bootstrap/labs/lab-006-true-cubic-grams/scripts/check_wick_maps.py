#!/usr/bin/env python3
"""Check global Fourier maps on a nontrivial D4-averaged fixed-N Slater state."""
import argparse,json,pickle,sys
from pathlib import Path
import numpy as np
import scipy.sparse as sp

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'lab-002-moment-sdp'/'scripts'))
sys.path.insert(0,str(HERE.parents[1]/'lab-003-theory-audit'))
from true_density_grams import phase,rot,reflect,sub

def check(inp):
    inp=Path(inp)
    names=json.loads((inp/'full_global_names.json').read_text())
    T=sp.load_npz(inp/'global_symmetry_expansion.npz')
    data=json.loads((inp/'extra_moment_reduction.json').read_text())
    # Every component occupies exactly eight orbitals of each spin.
    seed={0,1,2,4,5,7,10,13}
    sets=[]
    for flip in (False,True):
        K={reflect(k) for k in seed} if flip else seed.copy()
        for turn in range(4):
            sets.append(K.copy());K={rot(k) for k in K}
    occ=np.array([[float(k%16 in K) for k in range(32)] for K in sets])
    original=np.zeros(len(names))
    for z,name in enumerate(names):
        p=list(map(int,name.split('_')[1:]))
        if name.startswith('n_'):original[z]=occ[:,p[0]].mean()
        elif p[:2]==p[2:]:original[z]=(occ[:,p[0]]*occ[:,p[1]]).mean()
    gamma=np.array([[sum(np.conj(phase(k,d)) for k in K)/16 for d in range(16)] for K in sets])
    y=np.zeros(T.shape[1]+len(data['representatives']))
    for j in range(T.shape[1]):
        col=T.getcol(j);row=col.nonzero()[0][0]
        y[j]=original[row]/float(col[row,0])
    assert np.max(np.abs(T@y[:T.shape[1]]-original))==0
    for j,(d,a,b) in enumerate(data['representatives']):
        val=np.mean(gamma[:,d]*(.25-np.abs(gamma[:,sub(b,a)])**2))
        assert abs(val.imag)<1e-15
        y[T.shape[1]+j]=val.real
    maps=json.loads((inp/'real_space_lower_moment_maps.json').read_text())
    def evaluate(p):return sum(v*y[int(z)] for z,v in p.items())/256
    maperr=0.
    for key,p in maps['Y'].items():
        d,a=map(int,key.split(','))
        maperr=max(maperr,abs(evaluate(p)-.5*gamma[:,d].mean()))
    for key,p in maps['D'].items():
        r=int(key);value=.5 if r==0 else np.mean(.25-np.abs(gamma[:,r])**2)
        maperr=max(maperr,abs(evaluate(p)-value))
    assert maperr<1e-14,maperr
    with (inp/'model_cache.pkl').open('rb') as f:model=pickle.load(f)
    eqerr=float(np.max(np.abs(model.eqmatrix()@y-np.array(model.rhs))))
    mins={b['name']:float(np.linalg.eigvalsh((b['A']@y+b['b']).reshape(b['dim'],b['dim']))[0]) for b in model.blocks if b['name'].startswith('true_density_')}
    assert eqerr<1e-10,eqerr
    assert min(mins.values())>-1e-10,mins
    result=dict(state='Equal D4 mixture of Slater determinant with momenta '+str(sorted(seed))+' occupied in each spin',fourier_lower_moment_max_error=float(maperr),number_contraction_max_error=eqerr,true_gram_min_eigenvalue=min(mins.values()),new_moment_max_absolute=float(np.max(np.abs(y[T.shape[1]:]))))
    print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--out');args=ap.parse_args()
    result=check(args.input)
    if args.out:Path(args.out).write_text(json.dumps(result,indent=2))
