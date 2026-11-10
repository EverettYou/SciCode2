"""Integrate read-only source audits into a versioned reference and scorecards."""
from pathlib import Path
from fractions import Fraction as F
from math import sqrt, isqrt, floor, ceil
import csv
import hashlib
import json

ROOT=Path(__file__).resolve().parent
REVIEW=ROOT.parent
SOURCE=Path('/Users/home/Downloads/20261014-102308_d89b765a')
phase=json.loads((ROOT/'audits/phase-audit.json').read_text())
proof=json.loads((ROOT/'audits/proof-audit.json').read_text())
methods=json.loads((ROOT/'audits/methods-audit.json').read_text())
old=json.loads((REVIEW/'scores.json').read_text())
old_by={x['run_id']:x for x in old['runs']}
ids=['Fable03','Opus01','Opus02','Opus03','GPT01','GPT02','GPT03']
ph={x['id']:x for x in phase['runs']}
pr={x['run']:x for x in proof['runs']}
criteria={}
for line in (ROOT/'rubric.md').read_text().splitlines():
    if not line.startswith('| '):continue
    cells=[x.strip() for x in line.strip('|').split('|')]
    if cells[0][:1] in 'ABCDE' and len(cells[0])==2 and cells[0][1].isdigit():
        criteria[cells[0]]={'max':float(cells[1]),'title':cells[2],'anchor':cells[3]}
assert len(criteria)==23 and sum(x['max'] for x in criteria.values())==100

def ev_link(ev):
    path=Path(ev['file']); n=ev.get('line',ev.get('start',1))
    rel=path.relative_to(SOURCE) if path.is_relative_to(SOURCE) else path.relative_to(REVIEW)
    return f'[{rel}:{n}](<{path}:{n}>)'

def primary_evidence(x,k):
    ds=x['diagnostics']
    choices={'A1':['phase_strength'],'A2':['phase_strength'],'A3':['approximation','phase_strength'],
             'A4':['largeN_vs_phase'],'A5':['z4_feature','information_nesting'],
             'B1':['information_nesting'],'B2':['information_nesting'],
             'B3':['charge_equivalence'],'B4':['SU2']}
    for name in choices[k]:
        if name in ds and ds[name].get('evidence'):return ds[name]['evidence']
    return [{'file':x['report'],'line':1}]

reason_common={
'A1':'All 21 record/rank entries and the combined phase diagram are present; justified unresolved entries count toward coverage.',
'A4':'Distinguishes numerical phase assignments, large-N sufficient theorems, and the scope of bounds.',
'A5':'Addresses equivalent rows, information inclusion, and the low/high-noise Z4 features; nominal crossings smaller than the uncertainty are not treated as physical violations.',
'B1':'Noise, boundaries, syndrome, and binary logical-success conditions are consistent.',
'B2':'Data processing/garbling maps support the information hierarchy at fixed N; the cross-N relations used are derived.',
'B3':'Correctly identifies the N2, N3/6, N4, and N5/7/8 classes, including complete integer q at N5.',
'B4':'The SU2 and low-rank irrep probabilities used are correct.'}
specific={
'Fable03':{'A2':'Provides exact-posterior data at increasing two-dimensional sizes, but the positive-risk central charge phase is assigned from slow drift/positive-limit fits at L<=12; a very long crossover is not excluded.',
           'A3':'Exact contraction uses no bond truncation, and statistical and finite-size errors are disclosed; the gap in central-region limiting-risk inference is deducted only in A2, not again here.'},
'Opus01':{'A2':'Two-dimensional sizes reach about L48 and the diagnostics are useful; the zero central charge limit and charge-pinning explanation for the clean-loop phase still do not exclude alternative positive limits.',
          'A3':'Substantial chi comparisons and error classification are provided, but agreement between two approximations is not an upper bound on bias relative to the true posterior.'},
'Opus02':{'A2':'Two-dimensional sizes reach about L96; the Gaussian/BKT heuristic is not proved sufficient to exclude every nondecodable phase of the specified posterior model.',
          'A3':'Promotes the difference between chi and larger chi to an induced-bias upper bound without controlling the error of the latter.'},
'Opus03':{'A2':'Two-dimensional sizes reach about L64; slow decline and Gaussian/BKT exclusion do not establish a zero central charge limit.',
          'A3':'Larger chi can share the same bias; empirical convergence differences do not provide the claimed guarantee on true bias.'},
'GPT01':{'A2':'Keeps the slow charge region and small-N O2 unresolved, with size evidence and justified bounds, as permitted by the task.',
         'A3':'Exact posterior, no MPS truncation; statistical, finite-size, rounding, and perturbation checks are separated.'},
'GPT02':{'A2':'The 12/21 unresolved entries have valid bounds and size analysis; slow drift is not forced into a definite phase boundary.',
         'A3':'Exact posterior, independent checks, numerical range, and size limitations are treated separately.'},
'GPT03':{'A2':'Exact posteriors at increasing two-dimensional sizes support a numerical all-p assignment for small-N O2; finite grids and late crossovers remain caveats, and this is not an all-p theorem.',
         'A3':'No MPS truncation; statistical, finite-size, and rounding limitations are separated.'}}

Q={}
for line in (ROOT/'rubric.md').read_text().splitlines():
    if line.startswith('| Q'):
        c=[x.strip() for x in line.strip('|').split('|')]
        Q[c[0]]={'title':c[1],'scope':c[2]}
assert len(Q)==21

proofmap={'Q09':'binary_vs_latent','Q10':'difference_component_simple',
          'Q12':'necessary_not_sufficient_auxiliary_scope','Q13':'decoder_selection_condition',
          'Q14':'orientation_matrix_states','Q16':'side_edges_chords','Q17':'average_risk',
          'Q21':'four_element_arrow_diagrams'}

def diagnostic(run,q):
    pd={x['id']:x for x in pr[run]['diagnostics']}
    p=ph[run]['diagnostics']
    if q in proofmap:
        a=pd[proofmap[q]]
        return {'status':a['status'],'evidence':a.get('evidence',[]),'note':a.get('note','')}
    if q=='Q11':
        a=pd['M_local_minimum'];b=pd['only_11_needs_hiding']
        return {'status':'E' if a['status']==b['status']=='E' else 'I',
                'evidence':a.get('evidence',[])+b.get('evidence',[]),
                'note':'For routes without direct M constraints, I means equivalent content is dispersed/implicit; this route is not mandatory.'}
    if q=='Q15':
        a=pd['occupancy_matrix_states']
        return {'status':a['status'] if run in ['GPT01','GPT02'] else 'NA',
                'evidence':a.get('evidence',[]),'note':'Other valid proofs do not use both orientation and occupancy matrices.'}
    if q in ['Q01','Q02','Q03','Q04','Q05','Q06','Q07','Q08']:
        name='charge_equivalence' if q in ['Q02','Q03'] else 'z4_feature' if q in ['Q04','Q05','Q06','Q07'] else 'information_nesting'
        a=p[name]
        status='E'
        if q=='Q04': status='E' if run in ['GPT01','GPT02'] else 'I'
        if q=='Q05': status='E' if run in ['GPT01','GPT02'] else 'I'
        if q=='Q06': status='E' if run in ['GPT01','Opus03'] else 'I'
        if q=='Q07': status='E' if run in ['GPT01','Opus03'] else 'M'
        return {'status':status,'evidence':a.get('evidence',[]),'note':'E/I/M denotes explanatory coverage in the original submission; task points are not deducted for using a different exposition.'}
    if q=='Q18':
        a=next(x for x in methods['runs'][run]['scores'] if x['aspect']=='D2')
        return {'status':'I' if run=='Opus02' else 'E','evidence':a['evidence'],
                'note':'Opus02 remains exact at small sizes; the public API switches to MPS for L>9, so the broad no-truncation wording in its README needs qualification.' if run=='Opus02' else 'The small-size exact construction is supported by the submission and independent checks.'}
    if q=='Q19':
        return {'status':'X' if run.startswith('Opus') else 'I' if run=='Fable03' else 'E',
                'evidence':primary_evidence(ph[run],'A3'),
                'note':'X for Opus concerns its approximation-error upper-bound inference; I for Fable concerns model uncertainty in central phase assignment.'}
    if q=='Q20':
        a=next(x for x in methods['runs'][run]['scores'] if x['aspect']=='E4')
        return {'status':'X' if run in ['Fable03','Opus01','Opus02','Opus03'] else 'E',
                'evidence':a['evidence'],'note':a['reason']}
    raise ValueError(q)

runs=[]
for run in ids:
    ps=ph[run]; cs={}
    for k,points in ps['scores'].items():
        # A2 carries central-asymptotic inference; do not deduct the same issue again in A3.
        if run=='Fable03' and k=='A3':points=8
        cs[k]={'score':points,'max':criteria[k]['max'],
               'reason':specific[run].get(k,reason_common.get(k,'')),
               'evidence':primary_evidence(ps,k),'status':'supported' if points==criteria[k]['max'] else 'partial'}
    for x in pr[run]['criteria']:
        cs[x['id']]={'score':x['points_as_submitted'],'max':x['max_points'],
                     'score_review_supported':x['points_with_existing_independent_review'],
                     'reason':('The original all-p rigorous arithmetic certification has caveats; existing independent rational verification supports the theorem.' if x['id']=='C4' and x['points_as_submitted']<4 else 'The original proof steps and existing independent arithmetic verification support this item; valid alternative routes are accepted.'),
                     'evidence':x['evidence'],'status':'supported' if x['points_as_submitted']==x['max_points'] else 'partial'}
    for x in methods['runs'][run]['scores']:
        cs[x['aspect']]={'score':x['score'],'max':x['max'],'reason':x['reason'],
                        'evidence':x['evidence'],'review_evidence':x['review_evidence'],
                        'status':'supported' if x['score']==x['max'] else 'partial'}
    assert set(cs)==set(criteria)
    folder=methods['runs'][run]['folder']
    previous=old_by[folder]
    totals={g:sum(v['score'] for k,v in cs.items() if k.startswith(g)) for g in 'ABCDE'}
    totals['total']=sum(totals.values())
    rv={'id':run,'folder':folder,'N0':pr[run]['N0'],'assessable':True,'criteria':cs,'totals':totals,
        'R1_status':previous['criteria']['R1']['status'],
        'R3_theorem_status':'supported after review',
        'whole_task':previous['whole_task'],'diagnostics':{q:diagnostic(run,q) for q in Q},
        'ordinary_cases_passed':methods['runs'][run]['ordinary_posterior_pass'],
        'stress_cases_passed':methods['runs'][run]['stress_posterior_pass'],
        'unresolved_cells':ps['unresolved_cells'],'proof_method':pr[run]['method']}
    runs.append(rv)
for i in [1,2]:
    run=f'Fable0{i}'
    runs.append({'id':run,'folder':f'anthropic__claude-fable-5-1/run_0{i}',
                 'assessable':False,'N0':None,'criteria':{k:{'score':None,'max':v['max'],'status':'unknown','reason':'API output limit; no scientific deliverable.'} for k,v in criteria.items()},
                 'totals':{g:None for g in ['A','B','C','D','E','total']},
                 'whole_task':'not-assessable','R1_status':'unknown',
                 'diagnostics':{q:{'status':'U','evidence':[],'note':'Infrastructure failure; not assigned a scientific zero.'} for q in Q}})

record={'version':'posthoc-local-rubric-v1','date':'2026-10-16','official_scicode_weights':False,
        'formal_difficulty_calibration':'incomplete; no guided B protocol',
        'prompt_sha256':hashlib.sha256((SOURCE/'prompt.md').read_bytes()).hexdigest(),
        'criteria':criteria,'diagnostic_criteria':Q,'runs':runs,
        'integration_notes':['Fable03 A3 adjusted from the proposed 7 to 8: insufficient central extrapolation is deducted only in A2, avoiding double counting.',
                             'Group C totals reflect certification completeness as submitted; existing independent supplementary certificates support R3 correctness in all seven runs.',
                             'Opus01 explains charge pinning of the clean-loop phase; the Gaussian/BKT exclusion formulas explicitly occur in Opus02/03.',
                             'The a/b notation mix-up in this chat is an error in the reviewer explanation, not in the original runs.']}
(ROOT/'scores-v1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'scores-v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
    fields=['run','assessable','N0']+list(criteria)+['R1_30','R2_15','R3_20','R4_20','delivery_15','total_100','R1_status','whole_task']
    w=csv.DictWriter(f,fields);w.writeheader()
    for x in runs:
        row={'run':x['id'],'assessable':x['assessable'],'N0':x['N0'],**{k:v['score'] for k,v in x['criteria'].items()}}
        row.update(dict(zip(['R1_30','R2_15','R3_20','R4_20','delivery_15','total_100'],[x['totals'][k] for k in ['A','B','C','D','E','total']])))
        row.update(R1_status=x['R1_status'],whole_task=x['whole_task']);w.writerow(row)
with (ROOT/'score-details-v1.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['run','aspect','score','max','reason','source','line'])
    for x in runs:
        for k,v in x['criteria'].items():
            e=v.get('evidence',[{}])[0] if v.get('evidence') else {}
            w.writerow([x['id'],k,v['score'],v['max'],v['reason'],e.get('file',''),e.get('line',e.get('start',''))])

lines=['# Aspect scores and discussion-detail audit for nine attempts, v1','',
'This is a post hoc local completion rubric, not official SciCode weights or a prefrozen evaluator. Totals do not replace the R1-R4 scientific pass conditions. Seven scientific submissions and two API failures are retained.','',
'## 1. Overview','',
'| Run | R1 /30 | R2 /15 | R3 /20 | R4 /20 | Delivery /15 | Total /100 | N0 | Scientific assessment |',
'| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
verdict={'Fable03':'Partial completion: gaps in central-phase evidence and numerical range',
         'Opus01':'Partial completion: gaps in central extrapolation, approximation guarantees, and numerical range',
         'Opus02':'Partial completion: gaps in central extrapolation, approximation guarantees, and numerical range',
         'Opus03':'Partial completion: as above, with additional caveats on the original all-p arithmetic certification',
         'GPT01':'Provisional pass with the conservative answer permitted by the original task',
         'GPT02':'Provisional pass with the conservative answer permitted by the original task',
         'GPT03':'Provisional pass with caveats: numerical all-p extrapolation at small N'}
for x in runs:
    vals=[x['totals'][g] if x['assessable'] else 'NA' for g in ['A','B','C','D','E','total']]
    lines.append('| '+ ' | '.join(map(str,[x['id'],*vals,x['N0'] or 'NA',verdict.get(x['id'],'API output limit; not scientifically assessable')]))+' |')
lines+=['','The 100 for GPT01/02 means that the limited conclusions permitted by the original task satisfy this rubric, not that the complete physical phase diagram is solved. All seven produce high-quality core theory and ordinary posteriors, so partial submissions can still receive high completion scores; totals do not obscure key scientific gaps. Smaller valid N0 values are reported separately as stronger results.','',
'R3 is scored as submitted: 0.5 and 1 point are withheld for Fable03 and Opus03, respectively, for incomplete all-p arithmetic certification. Existing independent rational verification supports their theorems; their N0 conclusions have not been refuted.','',
'## 2. Matrix of 23 scoring criteria','',
'| Criterion | Maximum | '+' | '.join(ids)+' |',
'| --- | --- | '+' | '.join(['---']*len(ids))+' |']
by={x['id']:x for x in runs}
for k,v in criteria.items():
    lines.append('| '+ ' | '.join(map(str,[k+' '+v['title'],v['max'],*[by[r]['criteria'][k]['score'] for r in ids]]))+' |')
lines+=['','## 3. The 21 details discussed','',
'E=explicit and correct; I=implicit/partially developed; M=not found; X=specific error or insufficiently supported inference; NA=unneeded for a valid alternative route; U=no scientific submission. Teaching diagrams were requested later and do not incur retrospective deductions.','',
'| Detail | '+' | '.join(ids)+' |',
'| --- | '+' | '.join(['---']*len(ids))+' |']
for q,v in Q.items():
    lines.append('| '+v['title']+' | '+' | '.join(by[r]['diagnostics'][q]['status'] for r in ids)+' |')
lines+=['','NA does not mean correlations were ignored: Fable/Opus/GPT03 use valid alternative proofs. I/M also does not automatically mean task failure; the high-p Z4 identity and cell-by-cell teaching diagrams are enhanced explanations. For Q20, read the run-specific evidence to distinguish latent implementation defects from exceptions that actually occurred.','',
'## 4. Corrections to earlier assessments','',
'All seven correctly analyze complete integer q at N5 and saturation for N>=7; this is not a widespread omission. GPT01 and Opus03 give the Z4 active-component identity. Nonnested individual sufficient bounds do not imply that the true optimal phase regions violate information inclusion.','',
'The earlier REPORT characterized the three Opus central-region explanations too broadly: the Gaussian/BKT risk-lower-bound exclusion argument explicitly belongs to Opus02/03. Opus01 should be described as a physical explanation of typical charges pinning the clean-loop critical phase, together with slow-drift extrapolation. This corrects the attribution without revising the historical assessment.','',
'All seven pass all 210 ordinary posterior/correction cases each: 140 original R4 cases and 70 O0 controls. GPT passes all 18 extremely-low-p stress inputs; the other four fail locally. The Linux/macOS longdouble range difference for Opus02 remains a caveat.','',
'The Fable03 exception fallback to posterior=.5 would undercount failures, but its archived exception count is zero, making this a latent defect. Opus records hard failure as 1 but still uses .5 for posterior risk. GPT03 has 340600 archived slots, including 200 reserved conservative failure slots; these cannot all be called completed physical trials.','']
for run in ids:
    x=by[run]
    lines+=['## '+run+': criterion-by-criterion reasons and source locators','',
            f"N0={x['N0']}; R3 as submitted={x['totals']['C']}/20; theorem supported after review. unresolved={x['unresolved_cells']}/21.",'',
            '| Criterion | Score | Reason | Evidence |','| --- | --- | --- | --- |']
    for k,v in x['criteria'].items():
        links='; '.join(ev_link(e) for e in v.get('evidence',[])[:2])
        lines.append(f"| {k} | {v['score']}/{v['max']} | {v['reason']} | {links} |")
    lines+=['','Evidence for discussion details:','']
    for q,v in x['diagnostics'].items():
        links='; '.join(ev_link(e) for e in v.get('evidence',[])[:1])
        lines.append(f"- {q} {v['status']}: {Q[q]['title']}. {v.get('note','')} {links}")
    lines.append('')
(ROOT/'scorecards.md').write_text('\n'.join(lines)+'\n')

# Conservative endpoints with exact rational upward square-root certificates.
def sqrt_up(x):
    x=F(x);scale=10**40
    return F(isqrt(x.numerator*scale*scale//x.denominator)+1,scale)
mu_u=sqrt_up(2+sqrt_up(2));phi_u=(1+sqrt_up(5))/2;phi4_u=(3+sqrt_up(17))/4
mu=sqrt(2+sqrt(2));phi=(1+sqrt(5))/2
def growth_float(r,N,p):
    q=1-p
    if r=='O0' or r=='O1' and N==2:return 2*mu*sqrt(p*q)
    if r=='O1':
        a1=1 if N==4 else phi/2
        return mu*sqrt(p*q)*(1+((q/4+p*a1*a1)**.25))
    eta=sqrt(1+p)/2 if N==2 else sqrt(q/2+p*((3+sqrt(17))/4 if N==4 else phi))/N
    return mu*sqrt(p*q)*(1+eta)
def growth_up(r,N,p):
    p=F(p);q=1-p
    if r=='O0' or r=='O1' and N==2:return 2*mu_u*sqrt_up(p*q)
    if r=='O1':
        a1=F(1) if N==4 else phi_u/2
        return mu_u*sqrt_up(p*q)*(1+sqrt_up(sqrt_up(q/4+p*a1*a1)))
    eta=sqrt_up(1+p)/2 if N==2 else sqrt_up(q/2+p*(phi4_u if N==4 else phi_u))/N
    return mu_u*sqrt_up(p*q)*(1+eta)
def bisect(r,N,a,b):
    fa=growth_float(r,N,a)-1
    for _ in range(70):
        m=(a+b)/2;fm=growth_float(r,N,m)-1
        if fm*fa>0:a=m;fa=fm
        else:b=m
    return (a+b)/2
bounds=[];answers={'R1':{r:{} for r in ['O0','O1','O2']},'R3_N0':13}
for r in answers['R1']:
    for N in range(2,9):
        a=bisect(r,N,0,.5);b=bisect(r,N,.5,1)
        pa,pb=F(floor(a*10000),10000),F(ceil(b*10000),10000)
        ga,gb=growth_up(r,N,pa),growth_up(r,N,pb)
        assert ga<1 and gb<1
        text=f'Rigorous closed sufficient tails [0,{float(pa):.4f}] union [{float(pb):.4f},1]; roots of the sufficient inequality are NOT true phase boundaries; remaining phase set unresolved.'
        if r=='O0' or r=='O1' and N==2:
            text+=' Rigorous nondecodable central open interval (b_c/2,1-b_c/2), b_c=1-2*sin(pi/18), approximately (0.326351822333,0.673648177667); no N dependence; actual numerical critical estimate is separate.'
        if r=='O1':text+=' Charge equivalences and inherited information-order subsets apply.'
        if r=='O2':text+=' Also inherits proved O1 and O0 subsets at the same N.'
        answers['R1'][r][str(N)]={'unresolved':True,'bounds':text}
        bounds.append({'record':r,'N':N,'safe_low_closed':float(pa),'safe_high_closed':float(pb),
                       'low_growth_upper':str(ga),'high_growth_upper':str(gb),
                       'low_growth_upper_float':float(ga),'high_growth_upper_float':float(gb),
                       'roots_are_sufficient_only':True})
assert len(bounds)==21
(ROOT/'reference-answers.json').write_text(json.dumps(answers,ensure_ascii=False,indent=2)+'\n')
(ROOT/'reference-bound-certificates.json').write_text(json.dumps({'method':'Exact Fraction / integer-isqrt upward bounds at inward-rounded endpoints; analytic log-concavity gives single central superlevel interval.',
     'strict_endpoint_checks':bounds,'not_a_new_phase_simulation':True},indent=2)+'\n')
with (ROOT/'reference-bounds.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['record','N','proved_low_closed','proved_high_closed','status'])
    for x in bounds:w.writerow([x['record'],x['N'],x['safe_low_closed'],x['safe_high_closed'],'sufficient tails; other regions unresolved unless separately bounded'])
table=['# Appendix: verifiable safe intervals for all 21 entries','',
'All are inward-rounded closed sufficient intervals, not true phase boundaries. The original task permits the remaining ranges to be unresolved. All 21 entries are retained in reference-answers.json; rational endpoint certificates are in reference-bound-certificates.json.','',
'| Record | N | Proved low-p closed interval | Proved high-p closed interval | Center |','| --- | --- | --- | --- | --- |']
for x in bounds:table.append(f"| {x['record']} | {x['N']} | [0,{x['safe_low_closed']:.4f}] | [{x['safe_high_closed']:.4f},1] | unresolved; O0 and O1/N2 also have rigorous central nondecodability bounds |")
table+=['','Complete integer q inherits proved subsets from Z4 and q mod 6; O2 inherits O1/O0 at the same N. The O2 sufficient tails chosen here already cover the tabulated O1/O0 tails at the same N. These are not claimed to be the strongest provable bounds for each channel.']
(ROOT/'reference-bounds.md').write_text('\n'.join(table)+'\n')

# Validate every cited local source locator, then hash the generated reference.
checks=[]
for x in runs:
    for v in list(x['criteria'].values())+list(x['diagnostics'].values()):
        for e in v.get('evidence',[]):
            p=Path(e['file']);n=e.get('line',e.get('start',1))
            assert p.is_file(),str(p)
            num=len(p.read_text(errors='replace').splitlines())
            assert 1<=n<=num,(str(p),n,num)
            checks.append((str(p),n))
manifest={'date':'2026-10-16','prompt_sha256':record['prompt_sha256'],
          'source_locators_checked':len(checks),'unique_source_locators':len(set(checks)),
          'scientific_runs':7,'infrastructure_only_runs':2,'criteria_count':23,
          'diagnostic_count':21,'phase_cells':21,'weights_sum':100,
          'source_trajectories_modified':False,'new_model_trials':0,'new_phase_trials':0,
          'outputs':{}}
for p in sorted(ROOT.glob('*')):
    if p.is_file() and p.name!='manifest.json':manifest['outputs'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'scores':[(x['id'],x['totals']['total']) for x in runs],
                  'source_locators_checked':len(checks),'bounds':[(x['record'],x['N'],x['safe_low_closed'],x['safe_high_closed']) for x in bounds]},ensure_ascii=False))
