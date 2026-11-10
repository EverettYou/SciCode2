#!/usr/bin/env python3
"""Refine a completed affine SDP with bounded solver time and memory."""
import argparse,json,time,sys,os,pickle,threading,shutil
from pathlib import Path
here=Path(__file__).resolve().parent
sys.path.insert(0,str(here.parent/'lab-002-moment-sdp'/'scripts'))
from momentum_pqg import solve
import psutil

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input');ap.add_argument('out')
    ap.add_argument('--solver',default='CLARABEL')
    ap.add_argument('--eps',type=float,default=1e-8)
    ap.add_argument('--max-iters',type=int,default=150)
    ap.add_argument('--max-rss-gb',type=float,default=2)
    ap.add_argument('--max-seconds',type=float,default=600)
    args=ap.parse_args();inp=Path(args.input);out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();done=threading.Event();proc=psutil.Process()
    def monitor():
        peak=0
        while not done.wait(0.1):
            rss=proc.memory_info().rss;peak=max(peak,rss);sec=time.perf_counter()-start
            if rss>args.max_rss_gb*1e9 or sec>args.max_seconds:
                record=dict(outcome='Stopped bounded solver experiment',rss_bytes=rss,peak_sampled_rss_bytes=peak,elapsed_seconds=sec,reason='Memory/time watchdog')
                (out/'watchdog.json').write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True);os._exit(88)
    threading.Thread(target=monitor,daemon=True).start()
    for name in ['symmetry_expansion.npz','full_variable_names.json','full_objective.npy','source_operator_blocks.json','projection_descriptors.json','construction.json']:
        if (inp/name).exists():shutil.copyfile(inp/name,out/name)
    for path in inp.glob('projection_*.npz'):shutil.copyfile(path,out/path.name)
    with (inp/'model_cache.pkl').open('rb') as f:m=pickle.load(f)
    opts={'max_threads':1} if args.solver=='CLARABEL' else {}
    result=solve(m,out,args.solver,args.eps,args.max_iters,True,**opts)
    done.set();result['source_model_cache']=str(inp.resolve());result['refinement_elapsed_seconds']=time.perf_counter()-start
    (out/'result.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
