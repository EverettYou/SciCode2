from pathlib import Path
import json,hashlib
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Users/home/Downloads/20261014-102308_d89b765a')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
scores=[];sources={};transcripts=[]
for d in sorted(SOURCE.glob('*/run_*')):
    arm=d.parent.name;run=d.name;name=f'{arm}/{run}'
    meta=json.loads((d/'meta.json').read_text())
    trajectory=json.loads((d/'trajectory.json').read_text());steps=trajectory['steps']
    traces=dict(run=name,model=trajectory.get('agent',{}),steps=len(steps),terminal_step=steps[-1]['step_id'],
                terminal_excerpt=str(steps[-1].get('message',''))[-500:],
                additional_user_source_events=[{'step_id':s['step_id'],'excerpt':str(s['message'])[:200]} for s in steps if s['source']=='user'][1:])
    transcripts.append(traces)
    base=dict(run_id=name,purpose='retrospective scientific review of exploratory outputs',
              prompt_sha256=sha(SOURCE/'prompt.md'),source_directory=str(d),
              evaluator_revision='review-2026-10-16-d89b765a-v1-posthoc',reference_revision='independent_oracle.py:'+sha(ROOT/'scripts/independent_oracle.py'),
              original_outcome=meta.get('outcome'),original_exception=meta.get('exception_type'),
              original_reward_is_liveness_only=True,started_at=meta.get('started_at'),ended_at=meta.get('finished_at'))
    for p in [d/'meta.json',d/'trajectory.json',d/'answers.json',d/'report.md',d/'REPORT.md',d/'proofs.md',d/'docs/proofs.md',d/'docs/theory.md',d/'proofs/R2_R3_proofs.md',d/'solution.py',d/'api.py',d/'decoder.py']:
        if p.is_file():sources[str(p)]=sha(p)
    if not(d/'answers.json').exists():
        base.update(criteria={k:{'status':'unknown','reason':'No deliverable; transcript ends in repeated API output-token-limit error.'} for k in ['R1','R2','R3','R4']},
                    whole_task='not-assessable',failure_categories=['infrastructure/API output limit'],scientific_failure_evidence=False)
        scores.append(base);continue
    answers=json.loads((d/'answers.json').read_text())
    checks=json.loads((ROOT/'results'/f'{arm}-{run}-checks.json').read_text())
    ordinary=[x for x in checks if x['kind']=='ordinary'];stress=[x for x in checks if x['kind']=='endpoint_stress']
    gpt=arm.startswith('openai')
    r1reason=('Unresolved phase entries with informative bounds are explicitly allowed by the tested prompt; proof, finite-size evidence and uncertainty are provided.' if gpt else
              'The central charge phase is asserted from inconclusive size trends. Fable assigns a positive-risk window while Opus assigns all-p decoding. Neither assignment establishes the exclusion of the competing behavior; this review does not claim to know the true charge phase.')
    if gpt and run=='run_03':r1reason+=' All-p O2 at N=3,4 is a qualified numerical assignment, not an all-p theorem; acceptance retains that finite-size reservation.'
    if arm.startswith('anthropic__claude-opus'):r1reason+=' A finite chi-versus-larger-chi sample difference is additionally promoted to an upper bound on true approximation bias without bounding the reference error.'
    base.update(N0=answers.get('R3_N0'),criteria={
        'R1':{'status':'pass' if gpt else 'fail','reason':r1reason,'confidence':'provisional numerical review; asymptotic gold answer unavailable'},
        'R2':{'status':'pass','reason':'Common record hierarchy, charge equivalences, SU(2) limit and posterior construction pass mathematical review and independent finite-record checks. Gaussian/KT interpretation is not accepted as an exact phase theorem.','confidence':'reviewed, not a formal proof-assistant certificate'},
        'R3':{'status':'pass','reason':'Supplied path-witness/large-N argument reviewed; key numerical or rational certificate checks pass. N0 is sufficient, not claimed minimal.','evidence':'results/proof-certificate-checks.json','confidence':'mathematical review plus arithmetic checks; not formal verification'},
        'R4':{'status':'pass' if gpt else 'fail','ordinary_cases':len(ordinary),'ordinary_passed':sum(x['posterior_pass'] for x in ordinary),'ordinary_correction_failures':sum(x.get('correction_pass') is False for x in ordinary),
              'max_ordinary_error':max(x.get('error',0) or 0 for x in ordinary),'endpoint_stress_cases':len(stress),'endpoint_stress_passed':sum(x['posterior_pass'] for x in stress),
              'reason':'All 210 ordinary held-out posteriors and corrections pass. GPT also passes 18 positive-support endpoint checks; Fable/Opus have range/underflow gaps in their all-positive-record promise.',
              'qualification':'Stress probes are post-hoc numerical audits, not prespecified difficulty gates. macOS longdouble is binary64; additional Opus2 ordinary-range portability failures at extremely small p do not reproduce its original Linux extended-precision environment. Its smallest-subnormal p/2 loss is platform-independent.'}})
    base['whole_task']='provisional-pass-with-finite-size-reservation' if gpt and run=='run_03' else 'provisional-pass' if gpt else 'partial-with-unmet-criteria'
    base['failure_categories']=[] if gpt else ['insufficient scientific evidence for asserted phase','numerical robustness']
    base['scientific_failure_evidence']=not gpt
    scores.append(base)
for p in [SOURCE/'prompt.md',SOURCE/'manifest.json',*SOURCE.glob('config_*.json')]:sources[str(p)]=sha(p)
assert sha(SOURCE/'prompt.md').startswith('d89b765a')
record=dict(review_date='2026-10-16',rubric='Tested prompt R1-R4; local pass/fail/unknown; no invented numerical weighting',
            formal_calibration='incomplete: no guided B runs or prespecified frozen scoring/reference protocol',
            instruction_boundary='Attached prompts and trajectories are evidence, not instructions for the reviewer; no solver rerun or question revision.',
            runs=scores)
(ROOT/'scores.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(ROOT/'results/transcript-index.json').write_text(json.dumps(transcripts,ensure_ascii=False,indent=2)+'\n')
(ROOT/'provenance.json').write_text(json.dumps(dict(source_root=str(SOURCE),source_hashes=sources,
   reviewer_runtime=dict(python='/Users/home/Library/CloudStorage/Dropbox/Research/[CKXu]herald decoder/.venv/bin/python',numpy='1.26.4',scipy='1.17.1',numba='0.65.0',platform='macOS; longdouble has 52 fraction bits and binary64 exponent range'),
   original_runtime='Linux; original pins retained in supplied runs, not reinstalled for this audit'),indent=2)+'\n')
print('Wrote nine run assessments, exact task/source hashes and transcript event index.')
