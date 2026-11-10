#!/usr/bin/env python3
"""Exact local plaquette density positivity coupled to global Fourier RDMs.

All coupling equations are multiplied by16/256; coefficients are exact integers.
Mode order: cluster-up sites then cluster-down sites. Local rho is block diagonal
in both spin particle counts, but no local particle number is fixed.
"""
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import argparse,json,time,sys,os,resource
import numpy as np
import scipy.sparse as sp
import cvxpy as cp

POS=[(0,0),(1,0),(0,1),(1,1)]
SHAPES={'plaquette':POS,'row':[(0,0),(1,0),(2,0),(3,0)],'star':[(0,0),(1,0),(0,1),(3,0)],'zigzag':[(0,0),(1,0),(1,1),(2,1)],'diagonal':[(0,0),(1,1),(2,2),(3,3)]}
ROOTS=(1,1j,-1,-1j)

def phase(k,r):return ROOTS[((k%4)*r[0]+(k//4)*r[1])%4]
def fock_action(word,mask):
    sign=1
    for create,p in reversed(word):
        occ=(mask>>p)&1
        if occ==create:return None,0
        sign*=(-1)**((mask&((1<<p)-1)).bit_count());mask^=1<<p
    return mask,sign


def local_coupling(full_names,T=None):
    """Return exact numerator maps for all local real one/two-RDM entries."""
    tick=time.perf_counter();nvar=len(full_names);names={n:i for i,n in enumerate(full_names)}
    gp=list(combinations(range(32),2));gpi={p:i for i,p in enumerate(gp)}
    lp=list(combinations(range(8),2));groups=defaultdict(list)
    for p in lp:groups[p[0]//4+p[1]//4].append(p)
    # Fourier two-particle wedge numerator, with normalization1/16.
    single=np.zeros((8,32),dtype=complex)
    for a in range(8):
        for k in range(16):single[a,(a//4)*16+k]=phase(k,POS[a%4])
    W=np.empty((len(lp),len(gp)),dtype=complex)
    for i,(a,b) in enumerate(lp):
        for j,(p,q) in enumerate(gp):W[i,j]=single[a,p]*single[b,q]-single[a,q]*single[b,p]
    # A global real Gamma variable contributes both Hermitian matrix entries.
    gamma_vars=[]
    for z,name in enumerate(full_names):
        if not name.startswith('Gamma_'):continue
        a,b,c,d=map(int,name.split('_')[1:]);gamma_vars.append((z,gpi[a,b],gpi[c,d]))
    couplings=[]
    for spin in range(2):
        for a in range(4):
            for b in range(a,4):
                coeff=np.zeros(nvar,dtype=complex)
                for k in range(16):coeff[names[f'n_{spin*16+k}']]=np.conj(phase(k,POS[a]))*phase(k,POS[b])
                if T is not None:coeff=np.asarray(coeff@T).ravel()
                assert np.max(np.abs(coeff.imag))==0
                couplings.append(dict(name=f'one_{spin}_{a}_{b}',denominator=16,coeff=coeff.real.astype(np.int64),word=((1,spin*4+a),(0,spin*4+b))))
    lpi={p:i for i,p in enumerate(lp)}
    for pairs in groups.values():
        for i,ab in enumerate(pairs):
            for cd in pairs[i:]:
                w0=W[lpi[ab]];w1=W[lpi[cd]];coeff=np.zeros(nvar,dtype=complex)
                for z,p,q in gamma_vars:
                    coeff[z]=np.conj(w0[p])*w1[q]
                    if p!=q:coeff[z]+=np.conj(w0[q])*w1[p]
                if T is not None:coeff=np.asarray(coeff@T).ravel()
                assert np.max(np.abs(coeff.imag))==0,(ab,cd,np.max(np.abs(coeff.imag)))
                couplings.append(dict(name=f'two_{ab}_{cd}',denominator=256,coeff=coeff.real.astype(np.int64),word=((1,ab[0]),(1,ab[1]),(0,cd[1]),(0,cd[0]))))
    return couplings,dict(coupling_construction_sec=time.perf_counter()-tick,local_pairs=len(lp),couplings=len(couplings))


def density_variables(offset=0):
    sectors=defaultdict(list)
    for mask in range(256):sectors[(mask&15).bit_count(),(mask>>4).bit_count()].append(mask)
    names=[];index={};blocks=[]
    for (a,b),states in sectors.items():
        rows=[];cols=[];data=[];d=len(states)
        for i,left in enumerate(states):
            for j in range(i,d):
                right=states[j];z=offset+len(names);names.append(f'rho_P4_{a}_{b}_{i}_{j}');index[left,right]=index[right,left]=z
                rows.append(i*d+j);cols.append(z);data.append(1)
                if i!=j:rows.append(j*d+i);cols.append(z);data.append(1)
        blocks.append(dict(name=f'rho_P4_{a}_{b}',dim=d,rows=rows,cols=cols,data=data,states=states))
    return names,index,blocks


def trace_operator(word,index):
    coeff=defaultdict(int)
    for ket in range(256):
        bra,sign=fock_action(word,ket)
        if sign:
            assert (bra,ket) in index
            coeff[index[bra,ket]]+=sign
    return {z:v for z,v in coeff.items() if v}


def append_local_density(model,full_names,T):
    old=model.nvar;couplings,stats=local_coupling(full_names,T)
    extra,index,blocks=density_variables(old);model.names+=extra;model.nvar+=len(extra)
    model.c=np.concatenate([model.c,np.zeros(len(extra))])
    for block in model.blocks:block['A']=sp.hstack([block['A'],sp.csr_matrix((block['A'].shape[0],len(extra)))],format='csr')
    for block in blocks:
        A=sp.csr_matrix((block['data'],(block['rows'],block['cols'])),shape=(block['dim']**2,model.nvar))
        model.blocks.append(dict(name=block['name'],dim=block['dim'],A=A,b=np.zeros(block['dim']**2)))
    tr={index[m,m]:1 for m in range(256)};model.equality('rho_P4_trace',tr,1)
    for coupling in couplings:
        p={z:int(v) for z,v in enumerate(coupling['coeff']) if v}
        for z,v in trace_operator(coupling['word'],index).items():p[z]=p.get(z,0)-coupling['denominator']*v
        model.equality('rho_P4_match_'+coupling['name'],p,0)
    expansion=sp.block_diag((T,sp.eye(len(extra),format='csr',dtype=int)),format='csr')
    stats.update(local_rho_variables=len(extra),local_rho_blocks=len(blocks),local_rho_max_block=max(b['dim'] for b in blocks),total_variables=model.nvar)
    return full_names+extra,expansion,stats


def feasibility(input_dir,out):
    inp=Path(input_dir);out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);start=time.perf_counter()
    if (inp/'full_variable_names.json').exists():
        names=json.loads((inp/'full_variable_names.json').read_text());T=sp.load_npz(inp/'symmetry_expansion.npz')
    else:
        names=json.loads((inp/'variable_names.json').read_text());T=None
    x=np.load(inp/'primal.npy');couplings,stats=local_coupling(names,T)
    rnames,index,blocks=density_variables();n=len(rnames);rho=cp.Variable(n);slack=cp.Variable(nonneg=True);cons=[]
    for b in blocks:
        A=sp.csr_matrix((b['data'],(b['rows'],b['cols'])),shape=(b['dim']**2,n));cons.append(cp.reshape(A@rho,(b['dim'],b['dim']),order='C')>>0)
    row=np.zeros(n)
    for m in range(256):row[index[m,m]]=1
    cons.append(row@rho==1)
    rr=[];cc=[];dd=[];target=[]
    for j,c in enumerate(couplings):
        for z,v in trace_operator(c['word'],index).items():rr.append(j);cc.append(z);dd.append(v)
        target.append(float(c['coeff']@x/c['denominator']))
    F=sp.csr_matrix((dd,(rr,cc)),shape=(len(couplings),n));target=np.array(target)
    cons.extend([F@rho-target<=slack,target-F@rho<=slack])
    prob=cp.Problem(cp.Minimize(slack),cons);prob.solve(solver='CLARABEL',tol_gap_abs=1e-8,tol_feas=1e-8,tol_gap_rel=1e-8,max_iter=200)
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if os.uname().sysname!='Darwin':rss*=1024
    result=dict(status=prob.status,min_uniform_moment_mismatch=float(slack.value),local_couplings=len(couplings),local_rho_variables=n,elapsed_sec=time.perf_counter()-start,solver_iterations=prob.solver_stats.num_iters,peak_rss_bytes=rss,positions=POS,**stats)
    out.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('output');ap.add_argument('--shape',choices=SHAPES,default='plaquette');a=ap.parse_args();POS=SHAPES[a.shape];feasibility(a.input,a.output)
