#!/usr/bin/env python3
"""Aggregate measured branches without hiding discovery or validation costs."""
import hashlib,json,time
from pathlib import Path
import numpy as np
import scipy.sparse as sp

own=Path(__file__).resolve().parents[1];labs=own.parent;root=labs.parent
def read(p):return json.loads(p.read_text())
def rel(p):return str(p.relative_to(root))

def map_signature(directory):
    """Semantic exact equality permits a completed physical audit to be reused."""
    h=hashlib.sha256()
    for name in ('variable_names.json','full_variable_names.json','blocks.json'):
        p=directory/name
        if p.exists():h.update(json.dumps(read(p),sort_keys=True).encode())
    def dense(x):h.update(np.asarray(x,dtype=np.float64).tobytes())
    def sparse(p):
        A=sp.load_npz(p).tocsr();A.sum_duplicates();A.eliminate_zeros();A.sort_indices()
        h.update(str(A.shape).encode());h.update(A.indptr.astype(np.int64).tobytes());h.update(A.indices.astype(np.int64).tobytes());dense(A.data)
    for name in ('equalities.npz','symmetry_expansion.npz'):
        if (directory/name).exists():sparse(directory/name)
    for name in ('rhs.npy','objective.npy'):
        if (directory/name).exists():dense(np.load(directory/name))
    for b in read(directory/'blocks.json'):
        sparse(directory/(b['prefix']+'_A.npz'));dense(np.load(directory/(b['prefix']+'.npz'))['b'])
    return h.hexdigest()

def operator_dimension(name):
    if name.startswith('round_'):return None # adaptive orbit-rank not counted
    if name in ('dual-16-pqg','dual-blocks-pqg'):return 2257
    if name in ('pqg-eps6','pqg-eps8'):return 2081
    if name=='selected-t2-eps6':return 3041
    if name.startswith('two-site-t2'):return 5921
    if name=='two-site-spin-complete':return 6881
    if name=='three-site-stars-clarabel':return 7457
    if name=='t1-two-site-t2-sym':return 15841
    if name in ('pqgt1','pqgt1_sym'):return 12001
    if name=='pqgt2prime_mixed_sym':return 18465
    if name in ('pqgt2prime_sym','warm_start_smoke'):return 33825
    if name=='pqgt1t2prime_sym_s0':return 43745
    return None

def run():
    tick=time.perf_counter();audits=[];construction_audits=[];audit_by_dir={};by_signature={}
    audit_paths=list(own.glob('audit*.json'))+list((labs/'lab-004-exact-dual-verification/results').rglob('physical-audit.json'))
    for p in sorted(audit_paths):
        z=read(p)
        if not z.get('passed'):
            if z.get('passed_construction_checks'):construction_audits.append({'path':rel(p),'seconds':z['elapsed_seconds'],'peak_rss_bytes':z['peak_rss_bytes'],'full_export_audit_complete':False})
            continue
        d=Path(z['input_directory']);entry={'path':rel(p),'seconds':z['elapsed_seconds'],'peak_rss_bytes':z['peak_rss_bytes'],'portable':bool(z.get('portable_operator_input_directory'))}
        audits.append(entry);audit_by_dir.setdefault(str(d.resolve()),[]).append(entry)
    verification_by_dir={};verifications=[]
    for p in sorted(labs.rglob('verification.json')):
        z=read(p)
        if not z.get('source_directory'):continue
        d=Path(z['source_directory']).resolve();entry={'path':rel(p),'source_directory':str(d),'lower_bound':z['reported_total_energy_lower_bound'],'seconds':z['validation_seconds'],'peak_rss_bytes':z['peak_rss_bytes']}
        verification_by_dir.setdefault(str(d),[]).append(entry);verifications.append(entry)
    candidates=sorted(list((labs/'lab-002-moment-sdp/results').rglob('result.json'))+list((labs/'lab-003-theory-audit/outputs').rglob('result.json'))+list((labs/'lab-006-true-cubic-grams/outputs').rglob('result.json')))
    signatures={}
    for p in candidates:
        if (p.parent/'blocks.json').exists():signatures[str(p.parent.resolve())]=map_signature(p.parent)
    for d,entries in audit_by_dir.items():
        signature=signatures.get(d)
        if signature:by_signature.setdefault(signature,[]).extend(entries)
    rows=[]
    for p in candidates:
        d=p.parent;z=read(p);key=str(d.resolve());certs=verification_by_dir.get(key,[]);physical=audit_by_dir.get(key,[]);reused=False
        if not physical and signatures.get(key) in by_signature:physical=by_signature[signatures[key]];reused=True
        # The portable audit is the final self-contained replay route.
        preferred=next((q for q in physical if q['portable']),None) or (min(physical,key=lambda q:q['seconds']) if physical else None)
        cert=max(certs,key=lambda q:float(q['lower_bound'])) if certs else None
        adaptive='adaptive-t2-cuts' in p.parts;warm=d.name=='warm_start_smoke'
        model=z.get('model_construction_sec');build=z.get('build_sec');solve=z.get('solve_sec',z.get('seconds'))
        if adaptive:model_charge=0 # shared load charged once below
        else:model_charge=model or 0
        row={'experiment':rel(d),'name':d.name,'operator_dimension':operator_dimension(d.name),'solver':z.get('solver'),'status':z['status'],
             'primal_energy':z.get('energy_primal'),'floating_residual_corrected_lower':z.get('certificate_float_lower'),
             'exact_certified_lower':cert['lower_bound'] if cert else None,'certificate':cert,'physical_map_audit':preferred,'physical_audit_reused_after_exact_map_signature_match':reused,
             'variables':z.get('nvar',z.get('total_variables')),'cones':z.get('nblocks',z.get('number_of_gram_cones')),'max_cone_dim':z.get('max_psd_dim',z.get('max_gram_dimension')),'cone_entries':z.get('psd_entries'),
             'model_construction_seconds':model,'cvxpy_build_seconds':build,'solve_seconds':solve,'recorded_process_phase_seconds':model_charge+(build or 0)+(solve or 0),
             'process_peak_rss_bytes':z.get('peak_rss_bytes'),'singlet_ground_sector_refinement':d.name.endswith('_s0'),
             'scope':'adaptive checkpoint; shared construction/load charged once' if adaptive else 'warm-start continuation, prior discovery cost additional' if warm else 'independent measured run',
             'full_physical_and_exact_certificate_audit_complete':bool(cert and preferred)}
        if d.name=='fixed_full_t2_extension':row['scope']='feasibility pilot with fixed prior moments; no energy lower claimed'
        if d.name=='full_t2_plus_true_density':row['scope']='true cubic Gram pilot; semantic X maps not independently audited here, no promoted lower claim'
        rows.append(row)
    clusters=[]
    for p in sorted(own.glob('results*.json')):
        z=read(p);clusters.append({'experiment':rel(p),'name':p.stem,'exact_or_validated_lower':z['target_lower'],'seconds':z['elapsed_seconds'],'peak_rss_bytes':z['peak_rss_bytes'],'largest_sector_dim':max(r['dimension'] for r in z['results'])})
    adaptive_path=labs/'lab-002-moment-sdp/results/adaptive-t2-cuts/trace.json';adaptive=read(adaptive_path) if adaptive_path.exists() else None
    adaptive_summary=None
    if adaptive:
        ts=adaptive['trace'];adaptive_summary={'trace_file':rel(adaptive_path),'rounds':len(ts),'oracle_load_seconds_once':adaptive['oracle_load_sec'],'cumulative_oracle_seconds':ts[-1]['cumulative_oracle_sec'],'elapsed_total_seconds':ts[-1]['elapsed_total_sec'],'sum_round_solve_seconds':sum(q['solve_sec'] for q in ts),'peak_rss_bytes':max(q['peak_rss_bytes'] for q in ts),'last_round_floating_lower':ts[-1]['certificate_float_lower'],'note':'Checkpoint model_construction_sec repeats the same oracle load. It is charged once here, not once per round. Peak RSS is cumulative for one continuing process.'}
    abandoned=read(labs/'lab-003-theory-audit/abandoned_runs.json')
    postprocess=[]
    lp=labs/'lab-004-exact-dual-verification/results/pqgt2prime_sym-lp/exact/verification.json'
    if lp.exists():
        v=read(lp);postprocess.append({'name':'full-T2 equality-multiplier LP correction','exact_lower':v['reported_total_energy_lower_bound'],'exact_validation_seconds':v['validation_seconds'],'exact_validation_peak_rss_bytes':v['peak_rss_bytes'],'note':'Uses saved full-T2 dual factors; copied result.json is not a new solve. LP solve cost is separately recorded by lab004 when available.'})
    counts=read(own/'operator-count-audit.json') if (own/'operator-count-audit.json').exists() else None
    distillations=[]
    rank_paths=list((own/'distilled').glob('*/operator_space.json'))+list((labs/'lab-004-exact-dual-verification/results').glob('*/operator-space/operator_space.json'))
    for p in sorted(rank_paths):
        z=read(p);distillations.append({'path':rel(p),'operator_dimension':z.get('declared_operator_space_dimension',z.get('operator_space_dimension')),'exact_lower':z.get('exact_total_energy_lower_bound'),'seconds':z.get('elapsed_seconds'),'peak_rss_bytes':z.get('peak_rss_bytes')})
    compressions=[]
    for p in sorted((own/'compressed').glob('*/compression.json')):
        z=read(p);compressions.append({'path':rel(p),'seconds':z['compression_seconds']})
    cluster_searches=[]
    for name in ('weights-2x3.json','weights-2x4-open.json'):
        z=read(own/name);cluster_searches.append({'path':rel(own/name),'seconds':z['seconds'],'discovery_only':True})
    fresh_reproductions=[]
    for p in sorted((labs/'lab-004-exact-dual-verification/results').glob('*/reproduction.json')):
        z=read(p)
        if not z.get('completed'):continue
        z['metadata_path']=rel(p)
        for file,label in [('model/result.json','model_stage'),('physical-audit.json','physical_audit_stage'),('exact/verification.json','exact_stage'),('operator-space/operator_space.json','operator_rank_stage')]:
            q=p.parent/file
            if q.exists():
                s=read(q);z[label]={k:v for k,v in s.items() if k not in ['block_details','sector_ranks','factor_sha256','notes','input_sha256']}
        fresh_reproductions.append(z)
    report={'measurement_convention':['Times are per-process observed elapsed phases on a workstation shared by concurrent agents. Summing them is work accounting, not end-to-end wall time.','Process peak RSS is not global concurrent peak RSS. It includes all prior phases of the same process and adaptive checkpoint peaks are cumulative.','Physical-map validation includes CAR tests, geometry, reconstruction, exact coefficient comparisons and symmetry checks. Exact SOS validation alone does not include those costs.','A reused physical audit is listed only after exact semantic map/constant/objective/equality hashes match.','Missing construction times remain null; phase sums then omit that unrecorded phase. Failed and abandoned runs are retained separately; uninstrumented invocation overhead may remain uncounted.','Discovery of q20 directions required full-T2 optimization and audit. The13.82s six-block replay is a deployment cost, not the total discovery cost.','Literal O dimensions count original full Fock polynomials before further fixed-sector identities; cone entry counts and dual square counts are distinct.'],
            'global_experiments':rows,'validated_cluster_experiments':clusters,'fresh_sequential_reproductions':fresh_reproductions,'adaptive_campaign':adaptive_summary,'abandoned_runs':abandoned,'saved_certificate_postprocess':postprocess,'physical_audit_invocations':audits,'construction_only_audit_invocations':construction_audits,'exact_certificate_invocations':verifications,'operator_count_audit':counts,'exact_operator_distillation_invocations':distillations,'dual_compression_invocations':compressions,'cluster_weight_searches':cluster_searches,'earlier_repeated_cylinder_run':{'seconds':107.20985045912676,'peak_rss_bytes':1126678528,'note':'An earlier completed validation rerun retained separately from the latest cylinder JSON.'},
            'sum_recorded_global_process_phases_seconds':sum(r['recorded_process_phase_seconds'] for r in rows),'sum_recorded_cluster_seconds':sum(r['seconds'] for r in clusters),'sum_completed_physical_audit_invocation_seconds':sum(r['seconds'] for r in audits),'sum_construction_only_audit_seconds':sum(r['seconds'] for r in construction_audits),'sum_exact_verification_invocation_seconds':sum(r['seconds'] for r in verifications),'sum_operator_distillation_seconds':sum(r['seconds'] or 0 for r in distillations),'sum_dual_compression_seconds':sum(r['seconds'] for r in compressions),'operator_count_audit_seconds':counts['elapsed_seconds'] if counts else None,'sum_abandoned_wall_seconds':sum(r['wall_seconds'] for r in abandoned),'aggregation_seconds':time.perf_counter()-tick}
    (own/'global-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    lines=['Per-process measured comparisons. Bounds are total energies; a larger lower bound is stronger. “Float” rows have no completed exact certificate and physical audit pair in this table. Missing phases stay unrecorded.','',
           '| Branch | literal dim O | lower bound | model/build/solve s | RSS MB | audit s / exact s | cones / max dim |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for c in clusters:lines.append(f"| {c['name']} | — | {c['exact_or_validated_lower']:.9f} validated | {c['seconds']:.3f} total | {c['peak_rss_bytes']/1e6:.1f} | included | sectors max{c['largest_sector_dim']} |")
    for z in fresh_reproductions:
        lines.append(f"| {Path(z['metadata_path']).parent.name} fresh sequential pipeline | {z['operator_space_dimension']} | {float(z['certified_total_energy_lower_bound']):.9f} exact | {z['total_wall_seconds']:.3f} end-to-end | {z['largest_stage_process_peak_rss_bytes']/1e6:.1f} max stage | included | {z['nblocks']} / {z['max_psd_dim']} |")
    for r in rows:
        val=r['exact_certified_lower'] or r['floating_residual_corrected_lower'];label=' exact' if r['full_physical_and_exact_certificate_audit_complete'] else ' exact SOS, map pending' if r['exact_certified_lower'] else ' float'
        bound=f'{float(val):.9f}{label}' if val is not None else 'no bound'
        phases='/'.join('—' if r[k] is None else f'{r[k]:.2f}' for k in ('model_construction_seconds','cvxpy_build_seconds','solve_seconds'))
        validation=('—' if not r['physical_map_audit'] else f"{r['physical_map_audit']['seconds']:.2f}")+' / '+('—' if not r['certificate'] else f"{r['certificate']['seconds']:.2f}")
        name='adaptive/'+r['name'] if r['name'].startswith('round_') else r['name']
        lines.append(f"| {name} | {r['operator_dimension'] or '—'} | {bound} | {phases} | {(r['process_peak_rss_bytes'] or 0)/1e6:.1f} | {validation} | {r['cones']} / {r['max_cone_dim']} |")
    lines.extend(['','These rows include repeated runs and adaptive checkpoints. They cannot be summed into a single wall-clock runtime. The JSON records shared adaptive costs, abandoned runs, all validation invocations, and map-audit reuse explicitly.','',
                  'The final2257-dimensional space is PQG2081 plus88 symmetry-closed cubic directions and88 adjoints. Six added matrix cones constrain16 selected directions with one-body augmentation. Validation reconstructs their raw CAR maps directly; it does not use the discovery oracle.',
                  '', 'The final adaptive checkpoint passed all120 dyadic physical-map checks but remains a floating bound. Its weaker result was not sent through an additional exact verification. No further numerical branch is planned.'])
    (own/'global-comparison.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k.startswith('sum_')},indent=2))

if __name__=='__main__':run()
