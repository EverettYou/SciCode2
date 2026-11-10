#!/usr/bin/env python3
"""Postprocess dual Gram factors into a compact operator witness.

Discovery cost of the parent SDP is retained. Exact verification must be rerun
on the resulting factors; threshold ranks are never themselves certificates.
"""
from __future__ import annotations
import argparse,json,time,os,resource
from pathlib import Path
import numpy as np
import scipy.sparse as sp

def prepare(inp,out,threshold):
    inp=Path(inp).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    for p in inp.iterdir():
        if p.is_file():
            target=out/p.name
            if target.is_symlink():target.unlink()
            if not target.exists():target.symlink_to(os.path.relpath(p,out))
    blocks=json.loads((inp/'blocks.json').read_text());r=np.load(inp/'objective.npy')+sp.load_npz(inp/'equalities.npz').T@np.load(inp/'lambda.npy');const=-np.load(inp/'rhs.npy')@np.load(inp/'lambda.npy')
    counts={};time0=time.perf_counter()
    for block in blocks:
        src=inp/(block['prefix']+'.npz');data=np.load(src);B=data['factor'];norm=np.sum(B*B,axis=0);keep=norm>threshold;C=B[:,keep];retained=int(keep.sum())
        if retained==0:C=np.zeros((B.shape[0],1))
        target=out/src.name
        if target.is_symlink():target.unlink()
        np.savez_compressed(target,b=data['b'],factor=C,dual=data['dual'])
        Y=C@C.T;A=sp.load_npz(inp/(block['prefix']+'_A.npz'));r-=A.T@Y.ravel();const-=data['b']@Y.ravel()
        kind=block['name'].split('_')[0];z=counts.setdefault(kind,{'full_factor_columns':0,'retained_columns':0,'retained_square_operators':0,'discarded_trace':0.})
        z['full_factor_columns']+=B.shape[1];z['retained_columns']+=retained;z['retained_square_operators']+=retained*(2 if kind.startswith('T') else 1);z['discarded_trace']+=float(norm[~keep].sum())
    result={'source':str(inp),'threshold_column_norm_squared':threshold,'counts':counts,'floating_constant':float(const),'floating_residual_l1':float(np.abs(r).sum()),'floating_corrected_lower':float(const-np.abs(r).sum()),'compression_seconds':time.perf_counter()-time0,'initial_search_cost_included_by_reference':str(inp/'result.json'),'note':'The physical moment maps and constraints are unchanged; exact certificate verification is required for the compressed factors.'}
    (out/'compression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);p.add_argument('--threshold',type=float,default=1e-10);a=p.parse_args();prepare(a.input,a.output,a.threshold)
