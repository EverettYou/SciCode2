#!/usr/bin/env python3
"""Retain shared degree-six moments in separate density-assisted cubic Grams.

X(d,a,b)=<c†_(d,up)c_(0,up)n_(a,down)n_(b,down)>; a,b unordered.
For a=b, X is an existing two-RDM moment. Every new map is multiplied by256.
Fourier seeds F^+_(k,r)=1/4 sum_i exp(+ik.i)c†_(i,up)n_(i+r,down),
F^-=(F^+)†. Relative r=0 is removed using sum_r F_(k,r)=8*c†_k.
The remaining15 relative seeds plus the linear seed have individual PSD Grams.
"""
import argparse,json,time,pickle,sys,os,shutil
from pathlib import Path
from collections import defaultdict
import numpy as np
import scipy.sparse as sp

HERE=Path(__file__).resolve().parent
LABS=HERE.parents[1]
sys.path.insert(0,str(LABS/'lab-002-moment-sdp'/'scripts'))
sys.path.insert(0,str(LABS/'lab-003-theory-audit'))
from momentum_pqg import solve
from symmetry_reduce import q_orbit_representatives

ROOTS=np.array([1,1j,-1,-1j])

def add(a,b):return ((a%4+b%4)%4)+4*((a//4+b//4)%4)
def sub(a,b):return ((a%4-b%4)%4)+4*((a//4-b//4)%4)
def rot(a):x,y=a%4,a//4;return (-y)%4+4*x
def reflect(a):return (-a%4)+4*(a//4)
def phase(k,r):return ROOTS[((k%4)*(r%4)+(k//4)*(r//4))%4]
def canon(d,a,b):return (d,*sorted((a,b)))

def orbit(key):
    out={key};front=[key]
    while front:
        d,a,b=front.pop()
        for nxt in (canon(rot(d),rot(a),rot(b)),canon(reflect(d),reflect(a),reflect(b)),canon(sub(0,d),sub(a,d),sub(b,d))):
            if nxt not in out:out.add(nxt);front.append(nxt)
    return out

class MomentSpace:
    def __init__(self,full_names,T,offset):
        self.full_names=full_names;self.T=T;self.offset=offset;self.nglobal=T.shape[1]
        self.gamma=[]
        for z,name in enumerate(full_names):
            if name.startswith('Gamma_'):self.gamma.append((z,*map(int,name.split('_')[1:])))
        self.raw=[(d,a,b) for d in range(16) for a in range(16) for b in range(a+1,16)]
        self.reps={key:min(orbit(key)) for key in self.raw}
        self.representatives=sorted(set(self.reps.values()))
        self.index={r:offset+i for i,r in enumerate(self.representatives)}
        self.names=[f'X_{d}_{a}_{b}' for d,a,b in self.representatives]
        self.Y={};self.D={}
        for d in range(16):
            for a in range(16):
                coeff=np.zeros(len(full_names),dtype=complex)
                for z,k,p,l,q in self.gamma:
                    if not (k<16<=p):continue
                    coeff[z]=np.conj(phase(k,d))*np.conj(phase(p%16,a))*phase(q%16,a)
                    if (k,p)!=(l,q):coeff[z]+=np.conj(phase(l,d))*np.conj(phase(q%16,a))*phase(p%16,a)
                self.Y[d,a]=self.compress(coeff)
        for r in range(16):
            coeff=np.zeros(len(full_names),dtype=complex)
            if r==0:
                for k in range(16,32):coeff[k]=16
            else:
                for z,a,b,c,d in self.gamma:
                    if a<16:continue
                    wp=phase(b%16,r)-phase(a%16,r)
                    wq=phase(d%16,r)-phase(c%16,r)
                    coeff[z]=np.conj(wp)*wq
                    if (a,b)!=(c,d):coeff[z]+=np.conj(wq)*wp
            self.D[r]=self.compress(coeff)
        ncoeff=np.zeros(len(full_names),dtype=complex);ncoeff[16:32]=16
        self.nsite=self.compress(ncoeff)
        self.nmode={k:self.compress(np.eye(1,len(full_names),k).ravel()*256) for k in range(16)}
    def compress(self,coeff):
        coeff=np.asarray(coeff@self.T).ravel()
        assert np.max(np.abs(coeff.imag),initial=0)==0
        assert np.max(np.abs(coeff.real-np.rint(coeff.real)),initial=0)==0
        return {z:int(v) for z,v in enumerate(coeff.real) if v}
    def x(self,d,a,b):
        if a==b:return self.Y[d,a]
        return {self.index[self.reps[canon(d,a,b)]]:256}
    def export(self,out):
        out=Path(out)
        (out/'extra_moment_names.json').write_text(json.dumps(self.names))
        (out/'extra_moment_reduction.json').write_text(json.dumps(dict(definition='X(d,a,b)=<c†d_up c0_up n_a_down n_b_down>',representatives=self.representatives,raw_to_representative=[dict(raw=k,index=self.index[self.reps[k]]-self.offset,sign=1) for k in self.raw]),indent=2))
        moments=dict(Y={f'{d},{a}':p for (d,a),p in self.Y.items()},D={str(r):p for r,p in self.D.items()},nsite=self.nsite,nmode={str(k):v for k,v in self.nmode.items()})
        (out/'real_space_lower_moment_maps.json').write_text(json.dumps(moments))

def add_poly(target,poly,scale=1):
    for z,v in poly.items():target[z]+=scale*v

def clean(poly):return {z:v for z,v in poly.items() if v}

def realify_block(model,name,entries,dim):
    """Realification [[Re M,-Im M],[Im M,Re M]], exact Gaussian coefficients."""
    output=[]
    for i,j,p in entries:
        real={z:int(np.real(v)) for z,v in p.items() if np.real(v)}
        imag={z:int(np.imag(v)) for z,v in p.items() if np.imag(v)}
        assert all(complex(v).real==int(complex(v).real) and complex(v).imag==int(complex(v).imag) for v in p.values())
        output.extend([(i,j,real),(i+dim,j+dim,real),
                       (i,j+dim,{z:-v for z,v in imag.items()}),(i+dim,j,imag)])
    model.block(name,output,2*dim)
    block=model.blocks[-1]
    # Check exact real symmetry at the affine-map level.
    n=2*dim;order=np.arange(n*n).reshape(n,n).T.ravel()
    diff=block['A']-block['A'][order];diff.eliminate_zeros();assert diff.nnz==0,(name,diff.nnz)
    assert np.array_equal(block['b'],block['b'][order])

def append_true_grams(model,full_names,T,out,include_boxes=True):
    start=time.perf_counter();old=model.nvar
    space=MomentSpace(full_names,T,old);nextra=len(space.names)
    model.names+=space.names;model.nvar+=nextra;model.c=np.r_[model.c,np.zeros(nextra)]
    for block in model.blocks:block['A']=sp.hstack([block['A'],sp.csr_matrix((block['A'].shape[0],nextra))],format='csr')
    locations=list(range(1,16));dim=16;linear=15;sources=[]
    qreps=q_orbit_representatives(model)
    for k in sorted(set(qreps.values())):
        for charge in ('create','annihilate'):
            entries=[]
            for i,r in enumerate(locations):
                for j,s in enumerate(locations):
                    p=defaultdict(complex)
                    if charge=='create':add_poly(p,space.D[sub(s,r)])
                    for d in range(16):
                        ph=phase(k,d) if charge=='create' else np.conj(phase(k,d))
                        add_poly(p,space.x(d,r,add(d,s)),(-ph if charge=='create' else ph))
                    entries.append((i,j,clean(p)))
                p=defaultdict(complex)
                if charge=='create':add_poly(p,space.nsite)
                for d in range(16):
                    ph=phase(k,d) if charge=='create' else np.conj(phase(k,d))
                    add_poly(p,space.Y[d,r],(-ph if charge=='create' else ph))
                p=clean(p);entries.append((i,linear,p));entries.append((linear,i,{z:np.conj(v) for z,v in p.items()}))
            p=defaultdict(complex)
            if charge=='create':p[-1]=256;add_poly(p,space.nmode[k],-1)
            else:add_poly(p,space.nmode[k])
            entries.append((linear,linear,clean(p)))
            realify_block(model,f'true_density_{charge}_k{k}',entries,dim)
            sources.append(dict(name=f'true_density_{charge}_k{k}',momentum=k,charge=charge,relative_density_locations=locations,linear_last=True,complex_dim=dim,realified_dim=2*dim,scale=256))
    seen=set();ncontract=0
    def equality(name,p):
        nonlocal ncontract
        p={z:int(v) for z,v in p.items() if v}
        if not p:return
        first=p[min(p)]
        if first<0:p={z:-v for z,v in p.items()}
        key=tuple(sorted(p.items()))
        if key in seen:return
        seen.add(key);model.equality(name,p,0);ncontract+=1
    for d in range(16):
        for a in range(16):
            p=defaultdict(int)
            for b in range(16):add_poly(p,space.x(d,a,b))
            add_poly(p,space.Y[d,a],-8)
            equality(f'X_Nopp_{d}_{a}',p)
    for b in range(1,16):
        p=defaultdict(int)
        for i in range(16):add_poly(p,space.x(0,sub(0,i),sub(b,i)))
        add_poly(p,space.D[b],-8);equality(f'X_Nup_density_{b}',p)
    if include_boxes:
        for i in range(nextra):
            model.block(f'X_upper_{i}',[(0,0,{-1:1,old+i:-1})],1)
            model.block(f'X_lower_{i}',[(0,0,{-1:1,old+i:1})],1)
    space.export(out);(Path(out)/'true_gram_descriptors.json').write_text(json.dumps(sources,indent=2))
    # A faithful diagonal density operator on each fixed-spin sector is feasible.
    original=np.zeros(len(full_names))
    for z,name in enumerate(full_names):
        nums=list(map(int,name.split('_')[1:]))
        if len(nums)==1:original[z]=.5
        elif nums[:2]==nums[2:]:original[z]=7/30 if nums[0]//16==nums[1]//16 else .25
    y=np.zeros(model.nvar)
    for j in range(old):
        col=T.getcol(j);row=col.nonzero()[0][0];y[j]=original[row]/float(col[row,0])
    for i,(d,a,b) in enumerate(space.representatives):y[old+i]=7/60 if d==0 else 0
    eqerr=float(np.max(np.abs(model.eqmatrix()@y-np.array(model.rhs))))
    newblocks=[b for b in model.blocks if b['name'].startswith('true_density_')]
    mineig=min(float(np.linalg.eigvalsh((b['A']@y+b['b']).reshape(b['dim'],b['dim']))[0]) for b in newblocks)
    assert eqerr<1e-8,(eqerr,mineig)
    assert mineig>0,(eqerr,mineig)
    stats=dict(new_degree6_raw_moments=len(space.raw),new_degree6_variables=nextra,new_true_gram_cones=len(newblocks),max_true_gram_dim=32,contraction_equalities=ncontract,physical_uniform_state_equality_error=eqerr,physical_uniform_true_gram_min_eig=mineig,construction_sec=time.perf_counter()-start,total_variables=model.nvar)
    return space,stats

def main():
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('out');ap.add_argument('--eps',type=float,default=1e-5);ap.add_argument('--max-iters',type=int,default=5000);ap.add_argument('--solver',default='SCS');ap.add_argument('--verbose',action='store_true');ap.add_argument('--construct-only',action='store_true');args=ap.parse_args()
    inp=Path(args.input);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/'pid.txt').write_text(str(os.getpid()))
    with (inp/'model_cache.pkl').open('rb') as f:model=pickle.load(f)
    T=sp.load_npz(inp/'symmetry_expansion.npz');full_names=json.loads((inp/'full_variable_names.json').read_text())
    sp.save_npz(out/'global_symmetry_expansion.npz',T);(out/'full_global_names.json').write_text(json.dumps(full_names))
    shutil.copyfile(inp/'full_objective.npy',out/'full_global_objective.npy')
    space,stats=append_true_grams(model,full_names,T,out)
    sp.save_npz(out/'symmetry_expansion.npz',sp.block_diag((T,sp.eye(len(space.names),format='csr',dtype=int)),format='csr'))
    (out/'full_variable_names.json').write_text(json.dumps(full_names+space.names))
    with (out/'model_cache.pkl').open('wb') as f:pickle.dump(model,f)
    (out/'construction.json').write_text(json.dumps(stats,indent=2));print(json.dumps(stats,indent=2),flush=True)
    for name in ['source_operator_blocks.json','projection_descriptors.json']:
        if (inp/name).exists():shutil.copyfile(inp/name,out/name)
    for path in inp.glob('projection_*.npz'):shutil.copyfile(path,out/path.name)
    if args.construct_only:return
    result=solve(model,out,args.solver,args.eps,args.max_iters,args.verbose)
    result['model_construction_sec']=stats['construction_sec'];result.update(stats)
    (out/'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
