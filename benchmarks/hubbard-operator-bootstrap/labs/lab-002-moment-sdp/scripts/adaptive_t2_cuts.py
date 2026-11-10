#!/usr/bin/env python3
"""Discover affordable cubic SOS tests from violated full-T2 eigenvectors.

The optimization retains the small two-site T2' cones and adds scalar tests
v^T M_full(x) v >= 0. Eigenvectors are quantized to K/2**bits; integer
quadratic forms are evaluated before the exact dyadic scaling. Full-oracle
construction, loading, eigenvalue evaluation, solves, and exports are timed.
"""
import argparse,json,os,shutil,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
import cvxpy as cp
from momentum_pqg import solve
from resolve_export import SavedModel

class ScalarDual:
    def __init__(self,constraint,index):self.constraint=constraint;self.index=index
    @property
    def dual_value(self):return np.array([[self.constraint.dual_value[self.index]]])

def copy_metadata(source,out):
    for file in source.iterdir():
        if file.name in ('symmetry_expansion.npz','full_variable_names.json','full_objective.npy','cone_projections.json','operator_descriptors.json') or file.name.startswith('projection_'):shutil.copy2(file,out/file.name)

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--oracle',required=True);p.add_argument('--out',required=True);p.add_argument('--target',type=float,default=-8.78);p.add_argument('--batch',type=int,default=12);p.add_argument('--rounds',type=int,default=10);p.add_argument('--bits',type=int,default=12);p.add_argument('--eps',type=float,default=1e-8);p.add_argument('--max-iters',type=int,default=100);p.add_argument('--verbose',action='store_true');a=p.parse_args()
    start=time.perf_counter();source=Path(a.source);oracle_dir=Path(a.oracle);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);(out/'pid.txt').write_text(str(os.getpid()))
    m=SavedModel(source);full=SavedModel(oracle_dir)
    assert m.names==full.names and np.array_equal(m.c,full.c)
    T1=sp.load_npz(source/'symmetry_expansion.npz');T2=sp.load_npz(oracle_dir/'symmetry_expansion.npz');assert not (T1-T2).nnz
    oracle=[]
    full_meta=json.loads((oracle_dir/'blocks.json').read_text())
    for block,meta in zip(full.blocks,full_meta):
        if not block['name'].startswith('T2'):continue
        assert np.all(block['A'].data==np.rint(block['A'].data)) and np.all(block['b']==np.rint(block['b']))
        oracle.append({**block,'prefix':meta['prefix'],'integer_A':block['A'].astype(np.int64),'integer_b':block['b'].astype(np.int64)})
    oracle_load_sec=time.perf_counter()-start
    nbase=len(m.blocks);capacity=a.batch*a.rounds
    C=np.zeros((capacity,m.nvar));d=np.ones(capacity);Cpar=cp.Parameter(C.shape,value=C);dpar=cp.Parameter(d.shape,value=d)
    x=cp.Variable(m.nvar);basecons=[]
    for b in m.blocks:basecons.append(cp.reshape(b['A']@x+b['b'],(b['dim'],b['dim']),order='C')>>0)
    cutcon=Cpar@x+dpar>=0;eq=m.eqmatrix()@x==np.asarray(m.rhs)
    prob=cp.Problem(cp.Minimize(m.c@x),basecons+[cutcon,eq])
    for j in range(capacity):m.blocks.append({'name':f'ADAPTIVE_UNUSED_{j:03d}','dim':1,'A':sp.csr_matrix((1,m.nvar)),'b':np.ones(1)})
    exportcons=basecons+[ScalarDual(cutcon,j) for j in range(capacity)]
    current=np.load(source/'primal.npy');cuts=[];trace=[];oracle_time=0.;oldvectors={}
    for iteration in range(1,a.rounds+1):
        ot=time.perf_counter();candidates=[];worst=0.;negative=0
        for ob in oracle:
            M=(ob['A']@current+ob['b']).reshape(ob['dim'],ob['dim']);M=(M+M.T)/2
            w,v=np.linalg.eigh(M);worst=min(worst,float(w[0]));negative+=int((w<-1e-6).sum())
            for j in range(min(3,len(w))):
                if w[j]>=-1e-6:break
                vector=v[:,j];previous=oldvectors.get(ob['name'],[])
                if any(abs(vector@old)>0.9995 for old in previous):continue
                K=np.rint(vector*2**a.bits).astype(np.int64);outer=np.outer(K,K).ravel()
                # This bound controls every sum/product in signed int64.
                max_outer=int(np.max(np.abs(outer)));bound=max_outer*float(np.max(np.asarray(abs(ob['integer_A']).sum(axis=0))))
                assert bound<2**62
                an=np.asarray(ob['integer_A'].T@outer).ravel();bn=int(ob['integer_b']@outer)
                den=2**(2*a.bits);value=float((an@current+bn)/den)
                if value<-1e-6:candidates.append((value,ob,vector,K,an,bn))
        elapsed=time.perf_counter()-ot;oracle_time+=elapsed;candidates.sort(key=lambda row:row[0])
        chosen=candidates[:min(a.batch,capacity-len(cuts))]
        print(json.dumps({'phase':'oracle','round':iteration,'worst_eigenvalue':worst,'negative_eigenvalues':negative,'new_cuts':len(chosen),'oracle_sec':elapsed}),flush=True)
        if not chosen:break
        for value,ob,vector,K,an,bn in chosen:
            j=len(cuts);den=2**(2*a.bits);C[j]=an/den;d[j]=bn/den
            m.blocks[nbase+j]={'name':f'ADAPTIVE_CUT_{j:03d}','dim':1,'A':sp.csr_matrix(C[j:j+1]),'b':np.array([d[j]])}
            file=f'cut_{j:03d}.npz';np.savez_compressed(out/file,K=K,a_numerator=an,b_numerator=np.array([bn],dtype=np.int64),denominator_bits=2*a.bits)
            cuts.append({'index':j,'file':file,'source_name':ob['name'],'source_prefix':ob['prefix'],'bits':a.bits,'value_when_selected':value})
            oldvectors.setdefault(ob['name'],[]).append(vector)
        Cpar.value=C;dpar.value=d;x.value=current
        checkpoint=out/f'round_{iteration:02d}';checkpoint.mkdir(exist_ok=True);copy_metadata(source,checkpoint)
        (checkpoint/'adaptive_cuts.json').write_text(json.dumps({'oracle_directory':str(oracle_dir.resolve()),'cut_directory':str(out.resolve()),'cuts':cuts,'inactive_constant_constraints':capacity-len(cuts)},indent=2))
        m.construction_sec=oracle_load_sec
        result=solve(m,checkpoint,'CLARABEL',a.eps,a.max_iters,a.verbose,prebuilt=(prob,x,exportcons,eq),warm_start=True)
        current=np.asarray(x.value).copy();row={'round':iteration,'ncuts':len(cuts),'worst_oracle_eigenvalue_before':worst,'oracle_sec':elapsed,'cumulative_oracle_sec':oracle_time,'elapsed_total_sec':time.perf_counter()-start,**result};trace.append(row)
        (out/'trace.json').write_text(json.dumps({'oracle_directory':str(oracle_dir.resolve()),'base_directory':str(source.resolve()),'oracle_load_sec':oracle_load_sec,'oracle_cones':len(oracle),'oracle_matrix_entries':sum(b['dim']**2 for b in oracle),'capacity':capacity,'trace':trace},indent=2))
        if result['certificate_float_lower']>=a.target:break
    print(json.dumps({'completed_rounds':len(trace),'cuts':len(cuts),'oracle_sec':oracle_time,'total_sec':time.perf_counter()-start,'best_float_lower':max((row['certificate_float_lower'] for row in trace),default=None)}),flush=True)
if __name__=='__main__':main()
