#!/usr/bin/env python3
"""Extend a saved two-site model by the missing spin-3/2 cubic cones."""
import argparse,json,shutil,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from momentum_pqg import Model,solve
from resolve_export import SavedModel
from selected_t2 import add_extreme_t2
from run_selected_sym import split_selected_cones,q_orbit_representatives

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--eps',type=float,default=1e-6);p.add_argument('--max-iters',type=int,default=30000);p.add_argument('--solver',default='SCS');p.add_argument('--verbose',action='store_true');a=p.parse_args()
    start=time.perf_counter();source=Path(a.source);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    for file in source.iterdir():
        if file.name in ('symmetry_expansion.npz','full_variable_names.json','full_objective.npy') or file.name.startswith('projection_'):shutil.copy2(file,out/file.name)
    saved=SavedModel(source);T=sp.load_npz(source/'symmetry_expansion.npz')
    extra=Model();desc=add_extreme_t2(extra);reps=q_orbit_representatives(extra)
    extra.blocks=[b for b in extra.blocks if '_spin0_' in b['name'] and reps[int(b['name'].rsplit('_k',1)[1])]==int(b['name'].rsplit('_k',1)[1])]
    for b in extra.blocks:b['A']=(b['A']@T).tocsr()
    metadata=split_selected_cones(extra,out,prefix='extreme_projection',metadata_file='extreme_projections.json')
    oldproj=json.loads((source/'cone_projections.json').read_text());(out/'cone_projections.json').write_text(json.dumps(oldproj+metadata,indent=2))
    olddesc=json.loads((source/'operator_descriptors.json').read_text());(out/'operator_descriptors.json').write_text(json.dumps(olddesc+desc,indent=2))
    saved.blocks.extend(extra.blocks);saved.construction_sec=time.perf_counter()-start
    (out/'construction.json').write_text(json.dumps({'construction_sec':saved.construction_sec,'source':str(source.resolve()),'additional_full_cubic_seeds':32*15,'full_operator_dimension':6881,'ncones':len(saved.blocks)},indent=2))
    print(json.dumps({'construction_sec':saved.construction_sec,'nvar':saved.nvar,'ncones':len(saved.blocks),'max_dim':max(b['dim'] for b in saved.blocks),'entries':sum(b['dim']**2 for b in saved.blocks)}),flush=True)
    solve(saved,out,a.solver,a.eps,a.max_iters,a.verbose)
if __name__=='__main__':main()
