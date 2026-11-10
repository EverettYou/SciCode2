#!/usr/bin/env python3
"""Symmetry-reduced selected T2' with optional T1 and cone compression."""
import argparse, ast, itertools, json, os, sys, time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'lab-003-theory-audit'))
from momentum_pqg import Model,solve
from selected_t2 import add_selected_t2
from symmetry_reduce import reduce_variables,q_orbit_representatives,mode_transform,character_bases

def drop_orbit_cones(model):
    reps=q_orbit_representatives(model);keep=[];removed=[]
    for b in model.blocks:
        name=b['name'];yes=True
        if name.startswith(('P_','Q_','G_')):
            q,spin=ast.literal_eval(name[2:])
            yes=reps[q]==q and spin in ((0,1) if name[0] in 'PQ' else (0,1))
        elif name.startswith(('n_','hole_')):
            a=int(name.split('_')[-1]);yes=a<model.V and reps[a]==a
        elif name.startswith('T1_'):
            nup,qx,qy=ast.literal_eval(name[3:]);q=qx+model.L*qy
            yes=nup in (0,1) and reps[q]==q
        elif name.startswith(('T2prime_','T2pure_')):
            spin=int(name.split('_spin')[1].split('_')[0]);k=int(name.rsplit('_k',1)[1])
            yes=spin==0 and reps[k]==k
        (keep if yes else removed).append(b)
    model.blocks=keep
    return {'kept_cones':len(keep),'removed_cones':len(removed),'removed_names':[b['name'] for b in removed]}

def split_selected_cones(model,out,prefix='projection',metadata_file='cone_projections.json'):
    new=[];metadata=[]
    for b in model.blocks:
        is_t1=b['name'].startswith('T1_')
        if not is_t1 and not b['name'].startswith(('T2prime_','T2pure_')):
            new.append(b);continue
        if is_t1:
            nup,qx,qy=ast.literal_eval(b['name'][3:]);k=qx+model.L*qy
            triples=[t for t in itertools.combinations(range(2*model.V),3) if sum(a<model.V for a in t)==nup and model.add(model.add(t[0]%model.V,t[1]%model.V),t[2]%model.V)==k]
            index={t:i for i,t in enumerate(triples)}
            assert len(triples)==b['dim']
        else:k=int(b['name'].rsplit('_k',1)[1])
        x,y=model.xy[k];special=lambda z:z in (0,model.L//2)
        kinds=['rx','ry'] if special(x) and special(y) else ['rx'] if special(x) else ['ry'] if special(y) else ['swap'] if x==y else ['antiswap']
        pure=b['name'].startswith('T2pure_')
        family_count=(b['dim']-(not pure))//(model.V-1);perms=[]
        for kind in kinds:
            p=[];signs=[]
            if is_t1:
                for t in triples:
                    mapped=[mode_transform(model,kind,a) for a in t]
                    sign=(-1)**sum(mapped[i]>mapped[j] for i in range(3) for j in range(i+1,3))
                    p.append(index[tuple(sorted(mapped))]);signs.append(sign)
            else:
                for family in range(family_count):
                    for q in range(1,model.V):
                        mapped=mode_transform(model,kind,q)
                        p.append(family*(model.V-1)+mapped-1)
                if not pure:p.append(b['dim']-1)
                signs=[1]*b['dim']
            perms.append((p,signs))
        for chars,W in character_bases(perms):
            K=sp.kron(W.T,W.T,format='csr');name=f'{b["name"]}_char{chars}'
            nb={'name':name,'dim':W.shape[1],'A':(K@b['A']).tocsr(),'b':np.asarray(K@b['b']).ravel()}
            new.append(nb)
            path=f'{prefix}_{len(metadata):03d}.npz';sp.save_npz(out/path,W)
            metadata.append({'name':name,'source_name':b['name'],'source_dim':b['dim'],'dim':nb['dim'],'characters':chars,'reflections':kinds,'projection':path})
    model.blocks=new;(out/metadata_file).write_text(json.dumps(metadata,indent=2))
    return metadata

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--eps',type=float,default=1e-6);ap.add_argument('--max-iters',type=int,default=30000);ap.add_argument('--solver',default='SCS');ap.add_argument('--t1',action='store_true');ap.add_argument('--density-only',action='store_true');ap.add_argument('--no-cone-reduction',action='store_true');ap.add_argument('--verbose',action='store_true');args=ap.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True);(out/'pid.txt').write_text(str(os.getpid()))
    start=time.perf_counter();m=Model().build_pqg()
    if args.t1:
        from t1_extension import add_t1_constraints
        add_t1_constraints(m)
    add_selected_t2(m,out/'operator_descriptors.json',not args.density_only)
    (out/'full_variable_names.json').write_text(json.dumps(m.names));np.save(out/'full_objective.npy',m.c)
    stats,T=reduce_variables(m);sp.save_npz(out/'symmetry_expansion.npz',T)
    if not args.no_cone_reduction:
        stats['cone_orbits']=drop_orbit_cones(m);stats['character_blocks']=split_selected_cones(m,out)
    m.construction_sec=time.perf_counter()-start
    (out/'construction.json').write_text(json.dumps({'construction_sec':m.construction_sec,**stats},indent=2))
    print(json.dumps({'phase':'symmetry_done','construction_sec':m.construction_sec,'nvar':m.nvar,'ncones':len(m.blocks),'max_dim':max(b['dim'] for b in m.blocks),'entries':sum(b['dim']**2 for b in m.blocks)}),flush=True)
    solve(m,out,args.solver,args.eps,args.max_iters,args.verbose)

if __name__=='__main__':main()
