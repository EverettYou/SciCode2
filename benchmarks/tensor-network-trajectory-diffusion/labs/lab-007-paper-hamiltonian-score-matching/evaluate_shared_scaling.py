"""Frozen short-chain checkpoint on unseen cluster sizes, local contractions only."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
import torch
import mps_backend as mb
from shared_cluster import SharedControl,Windows,collect,pad_bonds,check_values,middle_entropy,reduced_density,environments,boundary_hadamards,ancilla_fields
from diagnose_tdvp_gap import provenance

@torch.no_grad()
def metrics(state,initial,ancilla=False):
    f=state.inner(initial).abs().square()/(state.inner().real*initial.inner().real)
    checks=check_values(boundary_hadamards(state) if ancilla else state); s=middle_entropy(state); env=environments(state); env0=environments(initial)
    ds=[]
    for i in range(state.n_sites-2):
        delta=reduced_density(state,i,i+3,env)-reduced_density(initial,i,i+3,env0)
        ds.append(torch.linalg.eigvalsh(delta).abs().sum(-1)*.5)
    distances=torch.stack(ds,1)
    labels=[]
    for i in range(state.n_sites):
        word=['I']*state.n_sites; word[i]='X'
        if i>0: word[i-1]='Z'
        if i+1<state.n_sites: word[i+1]='Z'
        if ancilla:
            for j in [0,state.n_sites-1]: word[j]={'I':'I','X':'Z','Z':'X'}[word[j]]
        labels.append(''.join(word))
    return dict(check_operators=labels,fidelity=f.tolist(),mean_fidelity=float(f.mean()),fidelity_sem=float(f.std(unbiased=True)/f.numel()**.5),
                mean_fidelity_per_site=float(f.clamp_min(1e-30).pow(1/state.n_sites).mean()),
                checks=checks.tolist(),mean_checks=checks.mean(0).tolist(),minimum_mean_check=float(checks.mean(0).min()),
                middle_entropy_bits=s.tolist(),mean_middle_entropy_bits=float(s.mean()),
                window3_trace_distance=distances.tolist(),mean_window3_trace_distance=float(distances.mean()),
                # Point-mass initial ensemble: W1 with pure-state trace cost is exactly this mean.
                ensemble_w1_trace_to_fixed_target=float((1-f).clamp_min(0).sqrt().mean()),
                max_norm_error=float((state.inner().real-1).abs().max()),
                tensor_storage_bytes=sum(a.numel()*a.element_size() for a in state.tensors),
                max_bond_dim=state.max_bond_dim())

@torch.no_grad()
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--checkpoint',type=Path,required=True); ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--target',choices=['cluster','ancilla'],default='cluster')
    ap.add_argument('--sizes',type=int,nargs='+',default=[3,4,5,6,8,12]); ap.add_argument('--chis',type=int,nargs='+',default=[2,4])
    ap.add_argument('--substeps',type=int,nargs='+',default=[1]); ap.add_argument('--batch',type=int,default=16); a=ap.parse_args()
    if a.output.exists(): raise RuntimeError('Refuse to overwrite experiment')
    a.output.mkdir(parents=True); torch.set_num_threads(1)
    training=json.loads((a.checkpoint.parent/'environment.json').read_text())
    model=SharedControl(training['config']['hidden'])
    model.load_state_dict(torch.load(a.checkpoint,map_location='cpu',weights_only=True)); model.eval()
    env=provenance(); env.update(checkpoint=str(a.checkpoint),checkpoint_sha256=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest(),
        train_n=training['config']['n'],target=a.target,seed_rule='82026 + N; identical forward records across chi/substep cells',batch=a.batch,
        sizes=a.sizes,chis=a.chis,substeps=a.substeps,steps=300,dt=.01,gamma=1.,backend='projector-splitting TDVP',
        state_access='exact local MPS expectations, no measurement-record decoder',
        source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('shared_cluster.py')]})
    (a.output/'environment.json').write_text(json.dumps(env,indent=2)+'\n'); rows=[]
    for n in a.sizes:
        begin=time.perf_counter(); states,axes=collect(n,a.batch,torch.device('cpu'),82026+n,ancilla=a.target=='ancilla')
        initial,final=states[0],states[-1]; del states
        forward_seconds=time.perf_counter()-begin
        rows.append(dict(n=n,backend='no-control',forward_seconds=forward_seconds,**metrics(final,initial,a.target=='ancilla')))
        win=Windows(n,'cpu'); previous={}
        for chi in a.chis:
            for subs in a.substeps:
                start=time.perf_counter(); state=pad_bonds(final,chi)
                for step in range(299,-1,-1):
                    z=win.mps(boundary_hadamards(state) if a.target=='ancilla' else state); t=torch.full((a.batch,1),(step+1)/300)
                    on,bo=model(z,t)
                    if a.target=='ancilla': on,bo=ancilla_fields(on,bo)
                    state=mb.reverse_tdvp_local(state,on,bo,axes[step],1.,.01,substeps=subs)
                elapsed=time.perf_counter()-start
                row=dict(n=n,chi=chi,substeps=subs,backend='tdvp',reverse_seconds=elapsed,
                         process_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,**metrics(state,initial,a.target=='ancilla'))
                if subs in previous:
                    agreement=state.inner(previous[subs]).abs().square()
                    row['paired_previous_chi_fidelity']=agreement.tolist()
                previous[subs]=state
                rows.append(row); print(json.dumps({k:row[k] for k in ['n','chi','substeps','mean_fidelity','minimum_mean_check','mean_middle_entropy_bits','reverse_seconds']}),flush=True)
                (a.output/'progress.json').write_text(json.dumps(dict(environment=env,rows=rows),indent=2)+'\n')
    (a.output/'summary.json').write_text(json.dumps(dict(environment=env,rows=rows),indent=2)+'\n')
if __name__=='__main__': main()
