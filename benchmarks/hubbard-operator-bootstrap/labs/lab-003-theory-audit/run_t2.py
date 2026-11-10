#!/usr/bin/env python3
"""Construct/solve PQG with full or mixed-spin momentum T2 refinement."""
import argparse,json,time,sys
from pathlib import Path
import numpy as np
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import Model,solve
from t2_extension import add_t2_constraints

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True)
    ap.add_argument('--eps',type=float,default=1e-4)
    ap.add_argument('--max-iters',type=int,default=2000)
    ap.add_argument('--full',action='store_true')
    ap.add_argument('--no-augment',action='store_true')
    ap.add_argument('--weak-augment',action='store_true')
    ap.add_argument('--t1',action='store_true')
    ap.add_argument('--solver',default='SCS')
    ap.add_argument('--verbose',action='store_true')
    args=ap.parse_args()
    start=time.perf_counter()
    Path(args.out).mkdir(parents=True,exist_ok=True)
    Path(args.out,'pid.txt').write_text(str(__import__('os').getpid()))
    m=Model().build_pqg();m.c[:2*m.V]=np.rint(m.c[:2*m.V])
    def progress(key,n,nnz,secs):
        print(json.dumps(dict(phase='T2_construct',key=key,dim=n,nnz=nnz,elapsed_sec=secs)),flush=True)
    add_t2_constraints(m,mixed_only=not args.full,augment=not args.no_augment,prime=not args.weak_augment,progress=progress)
    if args.t1:
        from t1_extension import add_t1_constraints
        add_t1_constraints(m)
    construction_sec=time.perf_counter()-start
    print(json.dumps(dict(phase='construction_done',construction_sec=construction_sec)),flush=True)
    result=solve(m,args.out,args.solver,args.eps,args.max_iters,args.verbose)
    result['model_construction_sec']=construction_sec
    Path(args.out,'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
