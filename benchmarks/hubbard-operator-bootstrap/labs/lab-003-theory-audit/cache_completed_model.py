#!/usr/bin/env python3
"""Rebuild a lightweight shared Model cache from completed affine exports."""
import argparse,json,pickle,sys
from pathlib import Path
import numpy as np
import scipy.sparse as sp
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import Model

def cache(inp):
    inp=Path(inp);m=Model()
    m.names=json.loads((inp/'variable_names.json').read_text());m.nvar=len(m.names)
    m.c=np.load(inp/'objective.npy');m.blocks=[]
    for desc in json.loads((inp/'blocks.json').read_text()):
        data=np.load(inp/f'{desc["prefix"]}.npz')
        m.blocks.append(dict(name=desc['name'],dim=desc['dim'],
                             A=sp.load_npz(inp/f'{desc["prefix"]}_A.npz'),b=data['b']))
    E=sp.load_npz(inp/'equalities.npz');m.rhs=list(np.load(inp/'rhs.npy'))
    m.erows=[]
    for i in range(E.shape[0]):
        row=E.getrow(i);m.erows.append(dict(zip(row.indices,row.data)))
    m.eqnames=[f'exported_equality_{i}' for i in range(E.shape[0])]
    m.moment_expansion=sp.load_npz(inp/'symmetry_expansion.npz')
    m.full_variable_names=json.loads((inp/'full_variable_names.json').read_text())
    m.cache_warning='gamma() returns ORIGINAL indices; transform coefficients through moment_expansion before appending compressed-variable constraints.'
    with (inp/'model_cache.pkl').open('wb') as f:pickle.dump(m,f)
    print(dict(cache=str(inp/'model_cache.pkl'),nvar=m.nvar,blocks=len(m.blocks)))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');a=ap.parse_args();cache(a.input)
