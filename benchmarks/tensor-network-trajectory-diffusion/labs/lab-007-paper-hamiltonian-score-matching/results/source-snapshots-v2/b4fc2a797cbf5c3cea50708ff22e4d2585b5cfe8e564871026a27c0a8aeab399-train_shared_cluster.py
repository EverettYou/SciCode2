"""Bounded short-chain shared-Hamiltonian training, frozen-size transfer later."""
import argparse,hashlib,json,time
from pathlib import Path
import torch
import mps_backend as mb
from shared_cluster import SharedControl,Windows,collect,cluster_mps,pad_bonds
from diagnose_tdvp_gap import provenance
LAB=Path(__file__).resolve().parent

class DenseApply:
    def __init__(self,n,device):
        self.n=n; self.windows=Windows(n,device)
        xyz=mb.PAULI_XYZ.to(device); self.site=[]; self.bond=[]
        for i in range(n): self.site.append(mb.embed_operator(xyz,i,n))
        for i in range(n-1):
            ops=torch.stack([torch.kron(a,b) for a in xyz for b in xyz])
            self.bond.append(mb.embed_operator(ops,i,n))
        self.site=torch.stack(self.site); self.bond=torch.stack(self.bond)
    def __call__(self,model,psi,t,axes):
        z=self.windows.dense(psi); on,bo=model(z,t)
        ham=torch.einsum('bna,naij->bij',on.to(psi.dtype),self.site)+torch.einsum('bna,naij->bij',bo.to(psi.dtype),self.bond)
        ops=self.site[torch.arange(self.n,device=psi.device)[None,:],axes]
        ex=torch.einsum('bi,bnij,bj->bn',psi.conj(),ops,psi).real
        # The omitted scalar multiple of identity cancels exactly on normalization.
        gen=2j*ham+torch.einsum('bn,bnij->bij',ex.to(psi.dtype),ops)
        out=(torch.linalg.matrix_exp(.01*gen)@psi[:,:,None])[:,:,0]
        return out/out.norm(dim=-1,keepdim=True)

def rollout(model,engine,psi,axes):
    for j in range(len(axes)-1,-1,-1):
        t=torch.full((psi.shape[0],1),(j+1)/len(axes),device=psi.device)
        psi=engine(model,psi,t,axes[j])
    return psi

def f(a,b): return (a.conj()*b).sum(-1).abs().square()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--n',type=int,default=3); ap.add_argument('--epochs',type=int,default=80)
    ap.add_argument('--batch',type=int,default=8); ap.add_argument('--seed',type=int,default=72026)
    ap.add_argument('--output',type=Path,required=True); ap.add_argument('--hidden',type=int,default=32)
    ap.add_argument('--lr',type=float,default=.003); a=ap.parse_args(); torch.set_num_threads(1)
    if a.output.exists(): raise RuntimeError('Refuse to overwrite an existing experiment')
    a.output.mkdir(parents=True); torch.manual_seed(a.seed); device=torch.device('cpu')
    model=SharedControl(a.hidden); engine=DenseApply(a.n,device)
    # Independent, frozen validation trajectories; validation never selects a checkpoint.
    vs,va=collect(a.n,16,device,a.seed+100000); v0=vs[0].to_dense(); vf=vs[-1].to_dense(); del vs
    # Physical gradient and local-feature gate, before any optimizer step.
    psi=torch.randn(2,2**a.n,dtype=torch.complex128); psi/=psi.norm(dim=-1,keepdim=True)
    tn=mb.mps_from_dense(psi,a.n); ax=torch.randint(3,(2,a.n)); t=torch.full((2,1),.5)
    z=engine.windows.mps(tn); zd=engine.windows.dense(psi)
    assert (z-zd).abs().max()<1e-10
    on,bo=model(z,t); out=mb.reverse_tdvp_local(tn,on,bo,ax,1.,.01).to_dense()
    dense=engine(model,psi,t,ax)
    assert (out-dense).norm(dim=-1).max()<1e-10
    target=cluster_mps(a.n,2,device).to_dense()
    g1=torch.autograd.grad((1-f(target,out)).mean(),list(model.parameters()))
    g2=torch.autograd.grad((1-f(target,dense)).mean(),list(model.parameters()))
    ge=max(float((x-y).abs().max()) for x,y in zip(g1,g2)); assert ge<1e-7
    env=provenance(); env.update(config={k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},
        model_parameters=sum(p.numel() for p in model.parameters()),gradient_parity_max=ge,
        training_backend='dense short-chain ceiling; corrected TDVP and feature gradient parity passed',
        objective='0.5 one-step infidelity (16 uniformly sampled times) + 0.5 full 300-step endpoint infidelity',
        validation_seed=a.seed+100000,checkpoint_selection='final epoch only',
        source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),LAB/'shared_cluster.py']})
    (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n')
    optimizer=torch.optim.Adam(model.parameters(),lr=a.lr); curve=[]; start=time.perf_counter()
    for epoch in range(1,a.epochs+1):
        states,axes=collect(a.n,a.batch,device,a.seed+epoch)
        initial=states[0].to_dense(); final=states[-1].to_dense()
        picks=torch.randint(300,(16,)).tolist(); current=torch.cat([states[i+1].to_dense() for i in picks])
        targets=torch.cat([states[i].to_dense() for i in picks]); sampled_axes=torch.cat([axes[i] for i in picks])
        ts=torch.cat([torch.full((a.batch,1),(i+1)/300) for i in picks]); del states
        optimizer.zero_grad(); one=(1-f(targets,engine(model,current,ts,sampled_axes))).mean()
        endpoint=(1-f(initial,rollout(model,engine,final,axes))).mean(); loss=.5*(one+endpoint)
        loss.backward(); gn=torch.nn.utils.clip_grad_norm_(model.parameters(),1.)
        if not torch.isfinite(gn): raise RuntimeError('Nonfinite gradient')
        optimizer.step(); row=dict(epoch=epoch,loss=float(loss.detach()),one_step=float(one.detach()),endpoint=float(endpoint.detach()),seconds=time.perf_counter()-start)
        if epoch==1 or epoch%10==0 or epoch==a.epochs:
            with torch.no_grad(): vals=f(v0,rollout(model,engine,vf,va))
            row.update(validation_fidelity=vals.tolist(),mean_validation_fidelity=float(vals.mean()))
            torch.save(model.state_dict(),a.output/f'model-epoch{epoch:04d}.pt')
            (a.output/'progress.json').write_text(json.dumps(row,indent=2)+'\n'); print(json.dumps(row),flush=True)
        curve.append(row)
    torch.save(model.state_dict(),a.output/'model.pt')
    (a.output/'summary.json').write_text(json.dumps(dict(environment=env,curve=curve,final=curve[-1]),indent=2)+'\n')
if __name__=='__main__': main()
