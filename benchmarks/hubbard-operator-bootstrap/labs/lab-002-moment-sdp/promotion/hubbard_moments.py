#!/usr/bin/env python3
"""Translation reduced, real Hubbard P/Q/G moment SDP and dual export.

Modes 0..V-1 are up; V..2V-1 are down. Gamma_ab,cd =
<c_a^dag c_b^dag c_d c_c>, a<b,c<d. Fourier transformation is unitary
with c_k = V**(-1/2) sum_r exp(-ik.r)c_r. Real moments may be assumed
by averaging inversion and complex conjugation (both preserve H and O).
"""
from __future__ import annotations
import argparse, functools, itertools, json, os, resource, time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

@functools.lru_cache(None)
def normal_order(word):
    """Exact integer CAR normal ordering; creators asc, annihilators desc."""
    word=tuple(word)
    for i in range(len(word)-1):
        a,b=word[i:i+2]
        if a==b: return {}
        wrong=(a[0]<b[0]) or (a[0]==b[0] and ((a[0] and a[1]>b[1]) or (not a[0] and a[1]<b[1])))
        if wrong:
            ans={}
            swap=word[:i]+(b,a)+word[i+2:]
            for w,v in normal_order(swap).items(): ans[w]=ans.get(w,0)-v
            if not a[0] and b[0] and a[1]==b[1]:
                for w,v in normal_order(word[:i]+word[i+2:]).items(): ans[w]=ans.get(w,0)+v
            return {w:v for w,v in ans.items() if v}
    return {word:1}

def adjoint(word): return tuple((1-c,a) for c,a in reversed(word))

class Model:
    def __init__(self,L=4,U=8.):
        self.L=L; self.V=L*L; self.U=U
        self.xy=[(k%L,k//L) for k in range(self.V)]
        self.pairs=list(itertools.combinations(range(2*self.V),2))
        self.groups={}
        for a,b in self.pairs:
            key=(self.add(a%self.V,b%self.V), (a//self.V)+(b//self.V))
            self.groups.setdefault(key,[]).append((a,b))
        self.gamma_index={}; self.names=[f'n_{a}' for a in range(2*self.V)]
        for key,pairs in self.groups.items():
            for i,p in enumerate(pairs):
                for q in pairs[i:]:
                    z=len(self.names); self.gamma_index[p,q]=self.gamma_index[q,p]=z
                    self.names.append(f'Gamma_{p[0]}_{p[1]}_{q[0]}_{q[1]}')
        self.nvar=len(self.names); self.blocks=[]; self.erows=[]; self.rhs=[]; self.eqnames=[]
        self.c=np.zeros(self.nvar)
        for a in range(2*self.V):
            k=a%self.V; x,y=self.xy[k]
            self.c[a]=-2*(np.cos(2*np.pi*x/L)+np.cos(2*np.pi*y/L))
            if L==4:self.c[a]=np.rint(self.c[a]) # exact integer dispersion
        for k,p,q in itertools.product(range(self.V),repeat=3):
            g=self.gamma(self.add(k,q),self.V+self.sub(p,q),k,self.V+p)
            for z,v in g.items(): self.c[z]+=U/self.V*v

    def add(self,k,p):
        x,y=self.xy[k]; a,b=self.xy[p]
        return ((x+a)%self.L)+self.L*((y+b)%self.L)
    def sub(self,k,p):
        x,y=self.xy[k]; a,b=self.xy[p]
        return ((x-a)%self.L)+self.L*((y-b)%self.L)
    def gamma(self,a,b,c,d):
        if a==b or c==d:return {}
        s=1
        if a>b:a,b=b,a;s=-s
        if c>d:c,d=d,c;s=-s
        z=self.gamma_index.get(((a,b),(c,d)))
        return {} if z is None else {z:s}
    def moment_normal(self,w):
        if not w:return {-1:1}
        if len(w)==2:
            if w[0][0]!=1 or w[1][0]!=0: return {}
            return {w[0][1]:1} if w[0][1]==w[1][1] else {}
        if len(w)==4 and [v[0] for v in w]==[1,1,0,0]:
            return self.gamma(w[0][1],w[1][1],w[3][1],w[2][1])
        raise ValueError(f'Unrepresented moment {w}')
    def poly(self,word): return self.normal_poly_to_affine(normal_order(tuple(word)))
    def normal_poly_to_affine(self,poly):
        out={}
        for w,v in poly.items():
            for z,a in self.moment_normal(w).items():out[z]=out.get(z,0)+v*a
        return {z:v for z,v in out.items() if v}
    def block(self,name,entries,dim):
        rr=[];cc=[];dd=[];b=np.zeros(dim*dim)
        for i,j,p in entries:
            for z,v in p.items():
                if z<0:b[i*dim+j]+=v
                else:rr.append(i*dim+j);cc.append(z);dd.append(v)
        A=sp.csr_matrix((dd,(rr,cc)),shape=(dim*dim,self.nvar))
        self.blocks.append({'name':name,'dim':dim,'A':A,'b':b})
    def equality(self,name,p,rhs):
        self.eqnames.append(name); self.erows.append(p);self.rhs.append(rhs)
    def build_pqg(self):
        for key,pairs in self.groups.items():
            entries=[];qentries=[];d=len(pairs)
            for i,(a,b) in enumerate(pairs):
                for j,(c,e) in enumerate(pairs):
                    p=self.gamma(a,b,c,e); entries.append((i,j,p))
                    p=p.copy()
                    if i==j:
                        p[-1]=1;p[a]=p.get(a,0)-1;p[b]=p.get(b,0)-1
                    qentries.append((i,j,p))
            self.block(f'P_{key}',entries,d);self.block(f'Q_{key}',qentries,d)
        ggroups={}
        for a,b in itertools.product(range(2*self.V),repeat=2):
            key=(self.sub(a%self.V,b%self.V),a//self.V-b//self.V)
            ggroups.setdefault(key,[]).append((a,b))
        for key,ops in ggroups.items():
            entries=[];d=len(ops)
            for i,(a,b) in enumerate(ops):
                for j,(c,e) in enumerate(ops):
                    p={z:-v for z,v in self.gamma(b,c,e,a).items()}
                    if a==c and b==e:p[b]=p.get(b,0)+1
                    entries.append((i,j,p))
            self.block(f'G_{key}',entries,d)
        # Linear positivity explicitly included for residual-coordinate bounds.
        for a in range(2*self.V):
            self.block(f'n_{a}',[(0,0,{a:1})],1)
            self.block(f'hole_{a}',[(0,0,{-1:1,a:-1})],1)
        for spin in range(2):self.equality(f'N_{spin}',{a:1 for a in range(spin*self.V,(spin+1)*self.V)},self.V/2)
        for a in range(2*self.V):
            for spin in range(2):
                p={a:-(self.V/2-(a//self.V==spin))}
                for b in range(spin*self.V,(spin+1)*self.V):
                    for z,v in self.gamma(a,b,a,b).items():p[z]=p.get(z,0)+v
                self.equality(f'contraction_{a}_{spin}',p,0)
        return self
    def eqmatrix(self):
        rr=[];cc=[];dd=[]
        for r,p in enumerate(self.erows):
            for z,v in p.items():rr.append(r);cc.append(z);dd.append(v)
        return sp.csr_matrix((dd,(rr,cc)),shape=(len(self.erows),self.nvar))

def solve(model,out,solver='SCS',eps=1e-6,max_iters=100000,verbose=False,prebuilt=None,**solver_options):
    out=Path(out);out.mkdir(parents=True,exist_ok=True); t0=time.perf_counter()
    (out/'pid.txt').write_text(str(os.getpid()))
    E=model.eqmatrix();e=np.array(model.rhs)
    if prebuilt is None:
        x=cp.Variable(model.nvar);cons=[]
        for b in model.blocks:
            M=cp.reshape(b['A']@x+b['b'],(b['dim'],b['dim']),order='C')
            cons.append(M>>0)
        eq=E@x==e;cons.append(eq)
        prob=cp.Problem(cp.Minimize(model.c@x),cons)
    else:prob,x,cons,eq=prebuilt
    build_sec=time.perf_counter()-t0
    print(json.dumps({'phase':'built','nvar':model.nvar,'blocks':len(model.blocks),'max_dim':max(b['dim'] for b in model.blocks),'psd_entries':sum(b['dim']**2 for b in model.blocks),'build_sec':build_sec}),flush=True)
    opts={'eps_abs':eps,'eps_rel':eps,'max_iters':max_iters} if solver=='SCS' else {'tol_gap_abs':eps,'tol_feas':eps,'tol_gap_rel':eps,'max_iter':max_iters}
    opts.update(solver_options)
    try:value=prob.solve(solver=solver,verbose=verbose,**opts)
    except BaseException as error:
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if os.uname().sysname!='Darwin':rss*=1024
        (out/'attempt.json').write_text(json.dumps({'status':'no_completed_solution','exception':type(error).__name__,'elapsed_sec':time.perf_counter()-t0,'peak_rss_bytes':rss,'solver':solver,'eps':eps,'no_bound_claimed':True},indent=2))
        raise
    solve_sec=time.perf_counter()-t0-build_sec
    if x.value is None:raise RuntimeError(f'{prob.status}: no solution')
    np.save(out/'primal.npy',x.value);np.save(out/'objective.npy',model.c)
    sp.save_npz(out/'equalities.npz',E);np.save(out/'rhs.npy',e)
    lam=np.asarray(eq.dual_value);np.save(out/'lambda.npy',lam)
    residual=model.c+E.T@lam;lb=-e@lam;min_eigs=[];meta=[]
    for k,(b,con) in enumerate(zip(model.blocks,cons)):
        Y=np.asarray(con.dual_value);Y=(Y+Y.T)/2
        w,v=np.linalg.eigh(Y);B=v*np.sqrt(np.maximum(w,0))[None,:]
        Yp=B@B.T
        residual-=b['A'].T@Yp.ravel();lb-=b['b']@Yp.ravel()
        min_eigs.append(float(w.min()))
        prefix=f'block_{k:03d}';sp.save_npz(out/f'{prefix}_A.npz',b['A'])
        np.savez_compressed(out/f'{prefix}.npz',b=b['b'],factor=B,dual=Y)
        meta.append({'prefix':prefix,'name':b['name'],'dim':b['dim']})
    np.save(out/'residual.npy',residual)
    cert_lb=float(lb-np.abs(residual).sum())
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result={'solver':solver,'status':prob.status,'energy_primal':float(value),'dual_unadjusted':float(lb),'residual_l1':float(np.abs(residual).sum()),'certificate_float_lower':cert_lb,'dual_min_eigenvalue':min(min_eigs),'equality_max_residual':float(np.max(np.abs(E@x.value-e))),'nvar':model.nvar,'nblocks':len(model.blocks),'max_psd_dim':max(b['dim'] for b in model.blocks),'psd_entries':sum(b['dim']**2 for b in model.blocks),'model_construction_sec':getattr(model,'construction_sec',None),'build_sec':build_sec,'solve_sec':solve_sec,'solver_solve_time':prob.solver_stats.solve_time,'iterations':prob.solver_stats.num_iters,'peak_rss_bytes':rss,'eps':eps}
    (out/'blocks.json').write_text(json.dumps(meta,indent=2));(out/'variable_names.json').write_text(json.dumps(model.names))
    (out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
    return result
