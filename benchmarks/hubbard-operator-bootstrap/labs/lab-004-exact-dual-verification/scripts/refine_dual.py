#!/usr/bin/env python3
"""Improve an exact Gram witness by LP-fitting equality multipliers only.

The LP is discovery: its candidate is reverified using exactinteger arithmetic.
PSDGramfactors and the chosen operator subspace remain fixed.
"""
import argparse,json,time,shutil,sys
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog
from verify_exact import verify

def refine(inp,cert,out):
    inp=Path(inp);cert=Path(cert);out=Path(out);out.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    proof=json.loads((cert/'verification.json').read_text());den=int(proof['denominator'])
    r=np.array([int(v)/den for v in json.loads((cert/'residual_numerators.json').read_text())]);E=sp.load_npz(inp/'equalities.npz').tocsr();e=np.load(inp/'rhs.npy');n=len(r);m=len(e)
    A=sp.vstack([sp.hstack([E.T,-sp.eye(n)]),sp.hstack([-E.T,-sp.eye(n)])],format='csr')
    sol=linprog(np.r_[e,np.ones(n)],A_ub=A,b_ub=np.r_[-r,r],bounds=[(None,None)]*m+[(0,None)]*n,method='highs',options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    if not sol.success:raise RuntimeError(sol.message)
    data=out/'data';shutil.copytree(inp,data,dirs_exist_ok=True)
    lam=np.load(inp/'lambda.npy');np.save(data/'lambda.npy',lam+sol.x[:m])
    result=verify(data,out/'exact')
    meta={'lp_status':sol.message,'lp_iterations':sol.nit,'original_bound':proof['reported_total_energy_lower_bound'],'refined_bound':result['reported_total_energy_lower_bound'],'total_refinement_seconds':time.perf_counter()-start,'operator_space_changed':False,'gram_factors_changed':False,'notes':'LP candidate only changes equality multipliers; exact re-verification establishes the reported lower bound.'}
    (out/'refinement.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input');p.add_argument('certificate');p.add_argument('output');a=p.parse_args();refine(a.input,a.certificate,a.output)
