#!/usr/bin/env python3
"""Run the portable solution, independent physical audit, and exact proofs."""
import argparse, hashlib, json, subprocess, sys, time
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--full',action='store_true',help='Reproduce the full T2-prime discovery model instead of the selected space.')
    parser.add_argument('--resume',action='store_true',help='Reuse successful stages from this output directory; record earlier failures separately.')
    args=parser.parse_args()
    src=Path(__file__).resolve().parent
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();stages=[];previous=[];reused_wall=0.
    if args.resume and (out/'reproduction.json').exists():
        previous=json.loads((out/'reproduction.json').read_text()).get('stages',[])
    commands=[
        ('solve',[str(src/'compact_replay.py'),'--out',str(out/'model'),'--eps','1e-9']),
        ('physical-audit',[str(src/'audit_physics.py'),str(out/'model'),str(out/'physical-audit.json'),'--operator-input',str(src/'input')]),
        ('exact-certificate',[str(src/'verify_exact.py'),str(out/'model'),str(out/'exact')]),
        ('operator-rank',[str(src/'distill_operator_space.py'),str(src/'input'),str(out/'exact'),str(out/'operator-space')]),
    ]
    if args.full:
        commands=[
            ('solve',[str(src/'run_full.py'),'--out',str(out/'model'),'--eps','1e-5','--max-iters','3000']),
            ('physical-audit',[str(src/'audit_physics.py'),str(out/'model'),str(out/'physical-audit.json')]),
            ('exact-certificate',[str(src/'verify_exact.py'),str(out/'model'),str(out/'exact')]),
        ]
    for label,arguments in commands:
        old=next((stage for stage in previous if stage['stage']==label and stage['exit_code']==0),None)
        if old is not None:
            stages.append(old);reused_wall+=old['wall_seconds_including_python_startup']
            print(json.dumps({'stage':label,'reused_successful_stage':True}),flush=True)
            continue
        tick=time.perf_counter();log=out/(label+'.log')
        if log.exists() and any(stage['stage']==label and stage['exit_code']!=0 for stage in previous):
            suffix=1
            while (out/f'{label}.failed-{suffix}.log').exists():suffix+=1
            backup=out/f'{label}.failed-{suffix}.log';log.rename(backup)
            for stage in previous:
                if stage['stage']==label and stage['exit_code']!=0:stage['log']=backup.name
        with log.open('w') as stream:
            process=subprocess.run([sys.executable,*arguments],stdout=stream,stderr=subprocess.STDOUT)
        stages.append({'stage':label,'wall_seconds_including_python_startup':time.perf_counter()-tick,'exit_code':process.returncode,'log':log.name})
        if process.returncode:
            (out/'reproduction.json').write_text(json.dumps({'completed':False,'stages':stages},indent=2))
            raise RuntimeError(f'{label} failed: {log}')
        print(json.dumps(stages[-1]),flush=True)
    certificate=json.loads((out/'exact/verification.json').read_text())
    audit=json.loads((out/'physical-audit.json').read_text())
    dimension={'declared_operator_space_dimension':33825,'peak_rss_bytes':0} if args.full else json.loads((out/'operator-space/operator_space.json').read_text())
    solve=json.loads((out/'model/result.json').read_text())
    expected_dimension=33825 if args.full else 2257
    assert audit['passed'] and dimension['declared_operator_space_dimension']==expected_dimension
    inputs={str(p.relative_to(src/'input')):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((src/'input').rglob('*')) if p.is_file()}
    scope='Sequential full T2-prime model construction, solve, export, independent physical audit and exact certificate.' if args.full else 'Sequential fixed-operator construction, solve, export, independent audit, exact certificate and exact operator rank. Full-operator discovery and earlier exploratory research are recorded separately.'
    report={'completed':True,'total_wall_seconds':time.perf_counter()-started,'stages':stages,'certified_total_energy_lower_bound':certificate['reported_total_energy_lower_bound'],'operator_space_dimension':expected_dimension,'nvar':solve['nvar'],'nblocks':solve['nblocks'],'max_psd_dim':solve['max_psd_dim'],'psd_entries':solve['psd_entries'],'construction_seconds':solve['model_construction_sec'],'solve_seconds':solve['solve_sec'],'export_seconds':solve['export_sec'],'largest_stage_process_peak_rss_bytes':max(v['peak_rss_bytes'] for v in [solve,audit,certificate,dimension]),'resource_scope':scope,'input_sha256':inputs if not args.full else {}}
    if reused_wall:
        report['total_wall_seconds']+=reused_wall
        report['resumed_successful_stage_seconds']=reused_wall
        report['prior_failed_stages']=[stage for stage in previous if stage['exit_code']!=0]
        report['total_wall_seconds_scope']='Successful prior stage walls plus current elapsed; manual restart gap and prior failed stages are excluded and recorded separately.'
    (out/'reproduction.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
