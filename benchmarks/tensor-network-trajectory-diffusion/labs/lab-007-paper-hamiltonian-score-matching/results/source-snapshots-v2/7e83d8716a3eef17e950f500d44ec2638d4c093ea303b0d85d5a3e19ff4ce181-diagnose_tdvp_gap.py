"""Frozen-weight paired dense/legacy/projector-splitting audit; never trains."""
import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import torch
import mps_backend as mb

LAB = Path(__file__).resolve().parent

def provenance():
    return dict(created_at=datetime.now(timezone.utc).isoformat(), python=sys.version,
                executable=sys.executable, torch=torch.__version__, platform=platform.platform(),
                cuda=torch.version.cuda, source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [Path(__file__), LAB/'mps_backend.py', LAB/'train_mps_ancilla_cluster.py']},
                environment_deviation='Historical ambient Torch 2.6.0 runtime; declared uv environment absent.')

def parity():
    torch.manual_seed(72026)
    rows=[]
    for n in [1,2,3,5]:
        psi=torch.randn(2,2**n,dtype=torch.complex128); psi=psi/psi.norm(dim=-1,keepdim=True)
        target=torch.randn_like(psi); target=target/target.norm(dim=-1,keepdim=True)
        m=mb.mps_from_dense(psi,n)
        on=torch.randn(2,n,3,dtype=torch.float64,requires_grad=True)
        bo=torch.randn(2,n-1,9,dtype=torch.float64,requires_grad=True) if n>1 else None
        axes=torch.randint(3,(2,n)); ex=torch.stack([m.expect_site(i,mb.PAULI_XYZ[axes[:,i]]) for i in range(n)],1)
        dense=mb.reverse_dense_local(psi,on,bo,axes,ex,1.,.01)
        tn=mb.reverse_tdvp_local(m,on,bo,axes,1.,.01).to_dense()
        pars=[on]+([bo] if bo is not None else [])
        loss=lambda x: (1-(target.conj()*x).sum(-1).abs().square()).mean()
        gd=torch.autograd.grad(loss(dense),pars)
        gt=torch.autograd.grad(loss(tn),pars)
        def value(eps):
            h=on.detach().clone(); h[0,0,0]+=eps
            return float(loss(mb.reverse_tdvp_local(m,h,bo.detach() if bo is not None else None,axes,1.,.01).to_dense()))
        fd=(value(1e-5)-value(-1e-5))/2e-5
        row=dict(n=n,state_error=float((dense-tn).norm(dim=-1).max()),
                 gradient_error=max(float((a-b).abs().max()) for a,b in zip(gd,gt)),
                 fd_error=abs(fd-float(gt[0][0,0,0])),norm_error=float((tn.norm(dim=-1)-1).abs().max()))
        assert row['state_error']<1e-10 and row['gradient_error']<1e-8 and row['fd_error']<1e-5, row
        rows.append(row)
    # A unitary two-site term must be able to change both tensors at full chi.
    return rows

@torch.no_grad()
def rollout(device, batch):
    import train_mps_ancilla_cluster as anc
    checkpoint=LAB/'results/mps-n5-ancilla-cluster-zradius2-htwo_local-tdvp-hybrid-v1/model.pt'
    model=anc.TwoLocalControl(len(anc.Z_INDEX)).to(device)
    model.load_state_dict(torch.load(checkpoint,map_location=device,weights_only=True)); model.eval()
    torch.manual_seed(72026)
    states,axes,psi0=anc.collect_forward(batch,device)
    final=states[-1]; del states
    results={}; vectors={}
    for backend in ['dense','legacy','tdvp']:
        start=time.perf_counter(); state=final.to_dense() if backend=='dense' else final
        for step in range(anc.N_STEPS-1,-1,-1):
            t=torch.full((batch,1),(step+1)/anc.N_STEPS,device=device,dtype=torch.float32)
            if backend=='dense':
                state=anc.apply_dense(model,state,t,axes[step])
            else:
                h=model.field(anc.mps_z(state),t).double(); on,bo=model.unpack(h)
                apply=mb.reverse_projected_gate_legacy if backend=='legacy' else mb.reverse_tdvp_local
                state=apply(state,on,bo,axes[step],anc.GAMMA,anc.DT)
            if step%100==0:
                print(json.dumps(dict(backend=backend,remaining=step,elapsed=time.perf_counter()-start)),flush=True)
        v=state if backend=='dense' else state.to_dense(); v=v/v.norm(dim=-1,keepdim=True)
        vectors[backend]=v
        checks=anc.pauli_vector(v,anc.CHECK_INDEX)
        f=(psi0.conj()*v).sum(-1).abs().square()
        results[backend]=dict(seconds=time.perf_counter()-start,fidelity=f.tolist(),mean_fidelity=float(f.mean()),
                              check_names=[x[0] for x in anc.CHECKS],checks=checks.tolist(),mean_checks=checks.mean(0).tolist())
    for backend in ['legacy','tdvp']:
        paired=(vectors['dense'].conj()*vectors[backend]).sum(-1).abs().square()
        results[backend]['paired_dense_fidelity']=paired.tolist()
        results[backend]['max_dense_vector_error']=float((vectors['dense']-vectors[backend]).norm(dim=-1).max())
    assert min(results['tdvp']['paired_dense_fidelity'])>1-1e-8
    return dict(seed=72026,n_eval=batch,checkpoint=str(checkpoint.relative_to(LAB)),
                checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),backends=results)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--device',default='cpu'); ap.add_argument('--batch',type=int,default=8)
    ap.add_argument('--parity-only',action='store_true'); ap.add_argument('--output',type=Path,required=True); a=ap.parse_args()
    torch.set_num_threads(1); a.output.mkdir(parents=True,exist_ok=True)
    out=provenance(); out['parity']=parity(); print(json.dumps(out['parity']),flush=True)
    (a.output/'parity.json').write_text(json.dumps(out,indent=2)+'\n')
    if not a.parity_only: out['rollout']=rollout(torch.device(a.device),a.batch)
    (a.output/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'done':str(a.output)}),flush=True)

if __name__=='__main__': main()
