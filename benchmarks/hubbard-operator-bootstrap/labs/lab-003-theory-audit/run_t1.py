#!/usr/bin/env python3
"""Construct and solve independent global PQG+T1 benchmark refinement."""
import argparse,json,time,sys,os
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import Model,solve
from t1_extension import add_t1_constraints

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True)
    ap.add_argument('--eps',type=float,default=1e-5)
    ap.add_argument('--max-iters',type=int,default=5000)
    ap.add_argument('--spin-counts',default='0,1,2,3')
    ap.add_argument('--solver',default='SCS')
    ap.add_argument('--verbose',action='store_true')
    args=ap.parse_args()
    start=time.perf_counter()
    m=Model().build_pqg()
    def progress(key,n,nnz,secs):
        print(json.dumps(dict(phase='T1_construct',key=key,dim=n,nnz=nnz,elapsed_sec=secs)),flush=True)
    add_t1_constraints(m,[int(x) for x in args.spin_counts.split(',')],progress)
    construction_sec=time.perf_counter()-start
    print(json.dumps(dict(phase='construction_done',construction_sec=construction_sec)),flush=True)
    result=solve(m,args.out,args.solver,args.eps,args.max_iters,args.verbose)
    result['model_construction_sec']=construction_sec
    Path(args.out,'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
