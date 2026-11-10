#!/usr/bin/env python3
"""Export reproducible physical operator words and integer cone congruences."""
import argparse,json,sys
from pathlib import Path
from types import SimpleNamespace
import scipy.sparse as sp
from t1_extension import triple_blocks
from t2_extension import t2_blocks
from symmetry_reduce import q_orbit_representatives,signed_op_permutation,character_bases

def minimal_model(L=4):
    V=L*L;m=SimpleNamespace(L=L,V=V,xy=[(k%L,k//L) for k in range(V)])
    m.add=lambda a,b:((a%L+b%L)%L)+L*((a//L+b//L)%L)
    m.sub=lambda a,b:((a%L-b%L)%L)+L*((a//L-b//L)%L)
    return m

def export(out,t1=False,t1_only=False,mixed_only=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);m=minimal_model()
    reps=q_orbit_representatives(m);sources=[];projections=[]
    if not t1_only:
        for (down,q),ops in t2_blocks(m,mixed_only,True).items():
            if down not in ((0,) if mixed_only else (-1,0)) or reps[q]!=q:continue
            family='mixed' if mixed_only else 'full'
            sources.append(dict(source_name=f'T2prime{family}_{(down,q)}',kind='T2prime',key=[down,q],ops=ops,mixed_only=mixed_only))
    if t1 or t1_only:
        for (up,qx,qy),triples in triple_blocks().items():
            q=qx+m.L*qy
            if up not in (0,1) or reps[q]!=q:continue
            sources.append(dict(source_name=f'T1_{(up,qx,qy)}',kind='T1',key=[up,q],
                                ops=[tuple((False,p) for p in reversed(t)) for t in triples]))
    for si,source in enumerate(sources):
        q=source['key'][1];x,y=m.xy[q]
        special=lambda z:z in (0,2)
        if special(x) and special(y):kinds=['rx','ry']
        elif special(x):kinds=['rx']
        elif special(y):kinds=['ry']
        elif x==y:kinds=['swap']
        elif (x+y)%4==0:kinds=['antiswap']
        else:raise ValueError(q)
        perms=[signed_op_permutation(m,source['ops'],kind) for kind in kinds]
        for pi,(chars,W) in enumerate(character_bases(perms)):
            filename=f'projection_{si:03d}_{pi}.npz';sp.save_npz(out/filename,W)
            projections.append(dict(block_name=f'{source["source_name"]}_char{chars}',
                                    source_name=source['source_name'],source_kind=source['kind'],
                                    W_file=filename,source_dim=W.shape[0],projected_dim=W.shape[1],
                                    reflection_generators=kinds,characters=chars))
    (out/'source_operator_blocks.json').write_text(json.dumps(sources))
    (out/'projection_descriptors.json').write_text(json.dumps(projections,indent=2))
    print(json.dumps(dict(output=str(out),sources=len(sources),projections=len(projections))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('out');p.add_argument('--t1',action='store_true');p.add_argument('--t1-only',action='store_true');p.add_argument('--mixed-only',action='store_true');a=p.parse_args();export(a.out,a.t1,a.t1_only,a.mixed_only)
