#!/usr/bin/env python3
"""Re-solve a saved affine model without repeating operator construction."""
import argparse,json,shutil,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from momentum_pqg import solve

class SavedModel:
    def __init__(self,source):
        start=time.perf_counter();source=Path(source)
        self.c=np.load(source/'objective.npy');self.nvar=len(self.c)
        self.names=json.loads((source/'variable_names.json').read_text())
        self.E=sp.load_npz(source/'equalities.npz');self.rhs=np.load(source/'rhs.npy').tolist()
        self.blocks=[]
        for desc in json.loads((source/'blocks.json').read_text()):
            p=desc['prefix'];data=np.load(source/f'{p}.npz')
            self.blocks.append({'name':desc['name'],'dim':desc['dim'],'A':sp.load_npz(source/f'{p}_A.npz'),'b':data['b']})
        self.construction_sec=time.perf_counter()-start
    def eqmatrix(self):return self.E

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--solver',default='CLARABEL');p.add_argument('--eps',type=float,default=1e-8);p.add_argument('--max-iters',type=int,default=100);p.add_argument('--verbose',action='store_true');a=p.parse_args()
    source=Path(a.source);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for file in source.iterdir():
        if file.name in ('symmetry_expansion.npz','full_variable_names.json','full_objective.npy','cone_projections.json','operator_descriptors.json','construction.json') or file.name.startswith('projection_'):shutil.copy2(file,out/file.name)
    m=SavedModel(source);print(json.dumps({'loaded_model_sec':m.construction_sec,'nvar':m.nvar,'ncones':len(m.blocks)}),flush=True)
    solve(m,out,a.solver,a.eps,a.max_iters,a.verbose)
if __name__=='__main__':main()
