#!/usr/bin/env python3
"""Full T2prime with exact D4/spinswap orbit and little-group cone reduction."""
import argparse,json,time,sys,os
from pathlib import Path
import numpy as np
import scipy.sparse as sp
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import Model,solve
from t2_extension import add_t2_constraints
from symmetry_reduce import reduce_variables,q_orbit_representatives,project_t2_little_groups

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True)
    ap.add_argument('--eps',type=float,default=1e-5)
    ap.add_argument('--max-iters',type=int,default=3000)
    ap.add_argument('--mixed-only',action='store_true')
    ap.add_argument('--t1',action='store_true')
    ap.add_argument('--t1-only',action='store_true')
    ap.add_argument('--singlet',action='store_true')
    ap.add_argument('--solver',default='SCS')
    ap.add_argument('--verbose',action='store_true')
    args=ap.parse_args();out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'pid.txt').write_text(str(os.getpid()))
    start=time.perf_counter()
    m=Model().build_pqg();m.c[:2*m.V]=np.rint(m.c[:2*m.V])
    original_names=m.names.copy();original_c=m.c.copy()
    qreps=q_orbit_representatives(m)
    chosen_down=(0,) if args.mixed_only else (-1,0)
    def key_filter(key):return key[0] in chosen_down and qreps[key[1]]==key[1]
    def progress(key,n,nnz,secs):
        print(json.dumps(dict(phase='T2_sym_construct',key=key,dim=n,nnz=nnz,elapsed_sec=secs)),flush=True)
    if not args.t1_only:
        add_t2_constraints(m,mixed_only=args.mixed_only,augment=True,prime=True,
                           progress=progress,key_filter=key_filter)
    if args.t1 or args.t1_only:
        from t1_extension import add_t1_constraints
        def t1filter(key):
            up,qx,qy=key;q=qx+m.L*qy
            return up in (0,1) and qreps[q]==q
        add_t1_constraints(m,key_filter=t1filter)
    if args.singlet:
        # At Sz=0, ||S+ psi||²=<S-S+>=<S²>. Lieb's theorem gives S=0.
        g=next(b for b in m.blocks if b['name']=='G_(0, -1)')
        row=np.asarray(g['A'].sum(axis=0)).ravel()
        m.equality('Lieb_ground_singlet_S2',dict(enumerate(row)), -float(g['b'].sum()))
    reduction,T=reduce_variables(m)
    sp.save_npz(out/'symmetry_expansion.npz',T)
    (out/'full_variable_names.json').write_text(json.dumps(original_names))
    np.save(out/'full_objective.npy',original_c)
    projections=project_t2_little_groups(m)
    m.moment_expansion=T;m.full_variable_names=original_names
    import pickle
    with (out/'model_cache.pkl').open('wb') as f:pickle.dump(m,f)
    # Validate exact signed expansion on a physical fixed-number diagonal state.
    V=m.V;N=V/2;x0=np.zeros(len(original_names))
    for i,name in enumerate(original_names):
        modes=list(map(int,name.split('_')[1:]))
        if len(modes)==1:x0[i]=0.5
        elif modes[:2]==modes[2:]:
            x0[i]=N*(N-1)/(V*(V-1)) if modes[0]//V==modes[1]//V else 0.25
    y0=np.zeros(m.nvar)
    for j in range(m.nvar):
        col=T.getcol(j);i=col.nonzero()[0][0];sgn=float(col[i,0]);y0[j]=x0[i]/sgn
    assert np.max(np.abs(T@y0-x0))<1e-14
    min_eig=min(float(np.linalg.eigvalsh((b['A']@y0+b['b']).reshape(b['dim'],b['dim']))[0]) for b in m.blocks)
    assert min_eig>-1e-10,min_eig
    # Diagonal fixed-N test state need not satisfy the optional singlet equality.
    construction_sec=time.perf_counter()-start
    stats=dict(phase='construction_done',construction_sec=construction_sec,
               reduction=reduction,projections=projections,physical_test_min_eig=min_eig)
    (out/'construction.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats),flush=True)
    result=solve(m,out,args.solver,args.eps,args.max_iters,args.verbose)
    result['model_construction_sec']=construction_sec;result['reduction']=reduction
    (out/'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
