"""Audit AD through all 300 corrected MPS steps against a dense loss."""
import argparse,hashlib,json,time
from pathlib import Path
import torch
import mps_backend as mb
from shared_cluster import SharedControl,Windows,collect,pad_bonds
from train_shared_cluster import DenseApply,rollout,f
from diagnose_tdvp_gap import provenance

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    a.output.mkdir(parents=True,exist_ok=True);torch.set_num_threads(1);rows=[]
    for n in (3,5):
        torch.manual_seed(912);model=SharedControl(32)
        states,axes=collect(n,2,torch.device('cpu'),912+n)
        initial,final=states[0],states[-1];del states
        engine=DenseApply(n,'cpu'); start=time.perf_counter()
        d=rollout(model,engine,final.to_dense(),axes)
        ld=(1-f(initial.to_dense(),d)).mean();gd=torch.autograd.grad(ld,list(model.parameters()))
        dense_seconds=time.perf_counter()-start;start=time.perf_counter()
        win=Windows(n,'cpu');state=pad_bonds(final,2**(n//2))
        for i in range(299,-1,-1):
            t=torch.full((2,1),(i+1)/300);on,bo=model(win.mps(state),t)
            state=mb.reverse_tdvp_local(state,on,bo,axes[i],1.,.01)
        lm=(1-state.inner(initial).abs().square()).mean()
        gm=torch.autograd.grad(lm,list(model.parameters()))
        gerr=max(float((x-y).abs().max()) for x,y in zip(gd,gm)); finite=all(bool(torch.isfinite(g).all()) for g in gm)
        norm=max(float(g.abs().max()) for g in gd)
        assert norm>1e-8, 'Degenerate zero-gradient check'
        row=dict(max_dense_gradient=norm,n=n,seed=912+n,batch=2,steps=300,dense_loss=float(ld.detach()),mps_loss=float(lm.detach()),
                 max_gradient_error=gerr,all_gradients_finite=finite,dense_seconds=dense_seconds,mps_seconds=time.perf_counter()-start)
        row['passed']=finite and abs(row['dense_loss']-row['mps_loss'])<1e-7 and gerr<1e-5
        rows.append(row);print(json.dumps(row),flush=True)
        (a.output/'summary.json').write_text(json.dumps(dict(environment=provenance(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows),indent=2)+'\n')
if __name__=='__main__':main()
