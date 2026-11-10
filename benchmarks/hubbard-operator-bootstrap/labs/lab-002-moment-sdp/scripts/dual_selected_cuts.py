#!/usr/bin/env python3
"""Select the active full-T2 dual directions and replay with scalar tests."""
import argparse,json,shutil,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp
from momentum_pqg import solve
from resolve_export import SavedModel
from adaptive_t2_cuts import copy_metadata

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--oracle',required=True);ap.add_argument('--out',required=True);ap.add_argument('--bits',type=int,default=20);ap.add_argument('--threshold',type=float,default=1e-7);ap.add_argument('--retain-two-site',action='store_true');ap.add_argument('--block-projections',action='store_true');ap.add_argument('--augment-linear',action='store_true');ap.add_argument('--eps',type=float,default=1e-9);ap.add_argument('--max-iters',type=int,default=100);ap.add_argument('--verbose',action='store_true');a=ap.parse_args()
    start=time.perf_counter();source=Path(a.source);oracle=Path(a.oracle);out=Path(a.out);out.mkdir(parents=True,exist_ok=True);copy_metadata(source,out)
    m=SavedModel(source)
    if not a.retain_two_site:
        m.blocks=[b for b in m.blocks if not b['name'].startswith('T2')]
        (out/'cone_projections.json').write_text('[]');(out/'operator_descriptors.json').write_text('[]')
    cuts=[];eig_sec=0.;fullrank=0;projected=[]
    oracle_projections={d['block_name']:d for d in json.loads((oracle/'projection_descriptors.json').read_text())}
    for desc in json.loads((oracle/'blocks.json').read_text()):
        if not desc['name'].startswith('T2'):continue
        prefix=desc['prefix'];data=np.load(oracle/f'{prefix}.npz');B=data['factor'];ot=time.perf_counter();w,v=np.linalg.eigh(B@B.T);eig_sec+=time.perf_counter()-ot
        A=sp.load_npz(oracle/f'{prefix}_A.npz');b=data['b'];assert np.all(A.data==np.rint(A.data)) and np.all(b==np.rint(b));Ai=A.astype(np.int64);bi=b.astype(np.int64)
        fullrank+=len(w)
        local=[]
        for j in np.where(w>a.threshold)[0]:
            bits=a.bits
            while True:
                K=np.rint(v[:,j]*2**bits).astype(np.int64);outer=np.outer(K,K).ravel()
                bound=int(np.max(np.abs(outer)))*float(np.max(np.asarray(abs(Ai).sum(axis=0))));assert bound<2**62
                an=np.asarray(Ai.T@outer).ravel();bn=int(bi@outer)
                if max(int(np.max(np.abs(an))),abs(bn))<2**53:break
                bits-=1
            den=2**(2*bits);idx=len(cuts);file=f'cut_{idx:03d}.npz'
            np.savez_compressed(out/file,K=K,a_numerator=an,b_numerator=np.array([bn],dtype=np.int64),denominator_bits=2*bits)
            if not a.block_projections:m.blocks.append({'name':f'DUAL_CUT_{idx:03d}','dim':1,'A':sp.csr_matrix(an[None,:]/den),'b':np.array([bn/den])})
            cuts.append({'index':idx,'file':file,'source_name':desc['name'],'source_prefix':prefix,'bits':bits,'dual_eigenvalue':float(w[j])})
            local.append((idx,K,bits))
        if a.block_projections and local:
            bits=min(row[2] for row in local);columns=[np.rint(K/2**(oldbits-bits)).astype(np.int64) for _,K,oldbits in local];linear_index=None
            if a.augment_linear:
                W=sp.load_npz(oracle/oracle_projections[desc['name']]['W_file']);last=W.getrow(W.shape[0]-1)
                assert last.nnz==1
                linear_index=int(last.indices[0]);assert W.getcol(linear_index).nnz==1 and last.data[0]==1
                col=np.zeros(desc['dim'],dtype=np.int64);col[linear_index]=2**bits;columns.append(col)
            P=np.stack(columns,axis=1);Kron=sp.kron(sp.csr_matrix(P.T),sp.csr_matrix(P.T),format='csr')
            An=(Kron@Ai).tocsr();bn=np.asarray(Kron@bi).ravel();assert np.max(np.abs(An.data))<2**53 and np.max(np.abs(bn))<2**53
            den=2**(2*bits);name=f'DUAL_BLOCK_{len(projected):03d}';file=f'dual_block_{len(projected):03d}.npz'
            np.savez_compressed(out/file,P_integer=P,b_numerator=bn,denominator_bits=2*bits);sp.save_npz(out/f'dual_block_{len(projected):03d}_A_integer.npz',An)
            m.blocks.append({'name':name,'dim':P.shape[1],'A':An.astype(float)/den,'b':bn/den})
            projected.append({'name':name,'source_name':desc['name'],'source_prefix':prefix,'file':file,'bits':bits,'cut_indices':[row[0] for row in local],'linear_index':linear_index})
    metadata={'oracle_directory':str(oracle.resolve()),'cut_directory':str(out.resolve()),'selection':'dual_eigenvectors','threshold':a.threshold,'cuts':cuts,'retain_two_site':a.retain_two_site,'oracle_eig_sec':eig_sec,'full_oracle_total_dimension':fullrank}
    (out/'adaptive_cuts.json').write_text(json.dumps(metadata,indent=2));m.construction_sec=time.perf_counter()-start
    if projected:(out/'dual_blocks.json').write_text(json.dumps({'oracle_directory':str(oracle.resolve()),'blocks':projected},indent=2))
    print(json.dumps({'phase':'dual_selection','ncuts':len(cuts),'ncones':len(m.blocks),'max_dim':max(b['dim'] for b in m.blocks),'entries':sum(b['dim']**2 for b in m.blocks),'construction_sec':m.construction_sec,'eig_sec':eig_sec}),flush=True)
    solve(m,out,'CLARABEL',a.eps,a.max_iters,a.verbose)
if __name__=='__main__':main()
