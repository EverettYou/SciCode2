#!/usr/bin/env python3
"""Project raw T2' onto two-site operators plus nearest-neighbor stars.

New spatial monomials are c†_(i,up)c†_(i+r,tau)c_(i+s,tau), with r,s
distinct nearest-neighbor vectors and tau either spin. Their cosine and sine
momentum coefficients are integers on the 4x4 torus. Only the six D4 momentum
representatives and net-up spin sector are constructed; the full test space
includes their symmetry orbits and adjoints.
"""
import argparse,itertools,json,shutil,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from momentum_pqg import Model,solve
from selected_t2 import triple_t2,addto
from resolve_export import SavedModel
from run_selected_sym import mode_transform,character_bases,q_orbit_representatives

def rankmod(A,prime=1000003):
    A=np.asarray(A,dtype=np.int64)%prime;r=0
    for j in range(A.shape[1]):
        pivot=next((i for i in range(r,A.shape[0]) if A[i,j]),None)
        if pivot is None:continue
        A[[r,pivot]]=A[[pivot,r]];A[r]=A[r]*pow(int(A[r,j]),-1,prime)%prime
        for i in range(r+1,A.shape[0]):
            if A[i,j]:A[i]=(A[i]-A[i,j]*A[r])%prime
        r+=1
        if r==A.shape[0]:break
    return r

def raw_main_block(m,k):
    triples=[]
    for a,b in itertools.combinations(range(2*m.V),2):
        down=a//m.V+b//m.V
        if down<=1:triples.append((a,b,down*m.V+m.sub(m.add(a%m.V,b%m.V),k)))
    entries=[];n=len(triples)+1
    for i,t in enumerate(triples):
        for j in range(i,len(triples)):
            p=triple_t2(m,t,triples[j])
            if p:
                entries.append((i,j,p))
                if i!=j:entries.append((j,i,p))
        a,b,c=t;p=m.poly(((1,c),(0,b),(0,a),(1,k)))
        if p:entries.append((i,n-1,p));entries.append((n-1,i,p))
    entries.append((n-1,n-1,{-1:1,k:-1}))
    m.block(f'T2primefull_(0, {k})',entries,n)
    return triples,m.blocks.pop()

def selected_vectors(m,k,triples):
    index={t:i for i,t in enumerate(triples)};columns=[];labels=[]
    def put(terms,label):
        col={}
        for (a,b,c),coefficient in terms:
            if a==b:continue
            if a>b:a,b,coefficient=b,a,-coefficient
            row=index[a,b,c];col[row]=col.get(row,0)+coefficient
        columns.append({i:v for i,v in col.items() if v});labels.append(label)
    V=m.V
    for q in range(1,V):put([((m.add(k,q),V+m.sub(p,q),V+p),1) for p in range(V)],('opposite_density',q))
    for q in range(1,V):put([((m.add(k,q),m.sub(p,q),p),1) for p in range(V)],('same_density',q))
    for p in range(1,V):put([((q,V+m.sub(m.add(k,p),q),V+p),1) for q in range(V)],('doublon_pair',p))
    for p in range(1,V):put([((q,V+p,V+m.sub(m.add(q,p),k)),1) for q in range(V)],('spin_exchange',p))
    nn=(1,3,4,12);neg=lambda a:m.sub(0,a)
    reps=[(r,s) for r in nn for s in nn if r!=s and (r,s)<(neg(r),neg(s))]
    cos=(1,0,-1,0);sin=(0,1,0,-1)
    for tau,(r,s),part in itertools.product(range(2),reps,('cos','sin')):
        rx,ry=m.xy[r];sx,sy=m.xy[s];terms=[]
        for b,c in itertools.product(range(V),repeat=2):
            bx,by=m.xy[b];cx,cy=m.xy[c]
            phase=(-bx*rx-by*ry+cx*sx+cy*sy)%4
            coefficient=(cos if part=='cos' else sin)[phase]
            if coefficient:terms.append(((m.add(k,m.sub(c,b)),tau*V+b,tau*V+c),coefficient))
        put(terms,('star',tau,r,s,part))
    columns.append({len(triples):4});labels.append(('linear',k))
    rr=[];cc=[];dd=[]
    for j,col in enumerate(columns):
        for i,v in col.items():rr.append(i);cc.append(j);dd.append(v)
    P=sp.csr_matrix((dd,(rr,cc)),shape=(len(triples)+1,len(columns)),dtype=np.int64)
    return P,labels

def character_projections(m,k,labels):
    x,y=m.xy[k];special=lambda a:a in(0,m.L//2)
    kinds=['rx','ry'] if special(x) and special(y) else ['rx'] if special(x) else ['ry'] if special(y) else ['swap']
    index={label:i for i,label in enumerate(labels)};perms=[]
    for kind in kinds:
        perm=[];signs=[]
        for label in labels:
            sign=1
            if label[0]=='linear':target=label
            elif label[0]=='star':
                _,tau,r,s,part=label;r=mode_transform(m,kind,r);s=mode_transform(m,kind,s)
                nr,ns=m.sub(0,r),m.sub(0,s)
                if (nr,ns)<(r,s):r,s=nr,ns;sign=-1 if part=='sin' else 1
                target=('star',tau,r,s,part)
            else:target=(label[0],mode_transform(m,kind,label[1]))
            perm.append(index[target]);signs.append(sign)
        perms.append((perm,signs))
    return kinds,character_bases(perms)

def verify_character(m,k,triples,projection,kinds,characters):
    index={t:i for i,t in enumerate(triples)}
    for kind,character in zip(kinds,characters):
        rows=[];signs=[]
        for t in triples:
            a,b,c=[mode_transform(m,kind,p) for p in t];sign=1
            if a>b:a,b,sign=b,a,-1
            rows.append(index[a,b,c]);signs.append(sign)
        rows.append(len(triples));signs.append(1)
        R=sp.csr_matrix((signs,(rows,range(len(rows)))),shape=(len(rows),len(rows)))
        error=(R@projection-character*projection).tocsr();error.eliminate_zeros()
        assert not error.nnz,(kind,k,error.nnz)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--out',required=True);ap.add_argument('--eps',type=float,default=1e-6);ap.add_argument('--max-iters',type=int,default=30000);ap.add_argument('--solver',default='SCS');ap.add_argument('--verbose',action='store_true');args=ap.parse_args()
    start=time.perf_counter();source=Path(args.source);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    for file in source.iterdir():
        if file.name in('symmetry_expansion.npz','full_variable_names.json','full_objective.npy','operator_descriptors.json') or file.name.startswith(('projection_','extreme_projection_')):shutil.copy2(file,out/file.name)
    saved=SavedModel(source);saved.blocks=[b for b in saved.blocks if not b['name'].startswith('T2prime_two_site_')]
    metadata=[p for p in json.loads((source/'cone_projections.json').read_text()) if not p['source_name'].startswith('T2prime_two_site_')]
    T=sp.load_npz(source/'symmetry_expansion.npz');m=Model();reps=q_orbit_representatives(m);stats=[]
    for k in range(m.V):
        if reps[k]!=k:continue
        triples,block=raw_main_block(m,k);P,labels=selected_vectors(m,k,triples)
        rank=rankmod(P.toarray());kinds,bases=character_projections(m,k,labels)
        block['A']=(block['A']@T).tocsr()
        for chars,W in bases:
            projection=(P@W).tocsr();K=sp.kron(projection.T,projection.T,format='csr')
            verify_character(m,k,triples,projection,kinds,chars)
            name=f'T2prime_three_site_stars_spin0_k{k}_char{chars}'
            saved.blocks.append({'name':name,'dim':projection.shape[1],'A':(K@block['A']).tocsr(),'b':np.asarray(K@block['b']).ravel()})
            path=f'star_projection_{len(metadata):03d}.npz';sp.save_npz(out/path,projection)
            metadata.append({'name':name,'source_name':block['name'],'source_dim':block['dim'],'dim':projection.shape[1],'characters':chars,'reflections':kinds,'projection':path})
        stats.append({'k':k,'selected_columns':P.shape[1],'rank_mod_1000003':rank,'labels':labels})
        print(json.dumps({'phase':'star_construct','k':k,'rank':rank,'elapsed_sec':time.perf_counter()-start}),flush=True)
    (out/'cone_projections.json').write_text(json.dumps(metadata,indent=2));(out/'star_construction.json').write_text(json.dumps(stats,indent=2))
    saved.construction_sec=time.perf_counter()-start
    (out/'construction.json').write_text(json.dumps({'construction_sec':saved.construction_sec,'source':str(source.resolve()),'ncones':len(saved.blocks),'nvar':saved.nvar,'max_dim':max(b['dim'] for b in saved.blocks),'entries':sum(b['dim']**2 for b in saved.blocks)},indent=2))
    solve(saved,out,args.solver,args.eps,args.max_iters,args.verbose)
if __name__=='__main__':main()
