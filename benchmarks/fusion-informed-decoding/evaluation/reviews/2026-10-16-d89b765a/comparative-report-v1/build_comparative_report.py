"""Build an aspect-by-aspect comparative report without changing frozen scores."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,re,csv

ROOT=Path(__file__).resolve().parent
REVIEW=ROOT.parent
REF=REVIEW/'reference-v1'
SOURCE=Path('/Users/home/Downloads/20261014-102308_d89b765a')
OUT=ROOT/'output/pdf';OUT.mkdir(parents=True,exist_ok=True)
SCORE_PATH=REF/'scores-v1.json'
FROZEN_HASH=hashlib.sha256(SCORE_PATH.read_bytes()).hexdigest()
baseline=json.loads((REVIEW/'english-translation-qa.json').read_text())
def score_projection(record):
    return {x['id']:{'totals':x['totals'],'N0':x['N0'],'assessable':x['assessable'],'criteria':{k:{t:v[t] for t in ('score','max','status') if t in v} for k,v in x['criteria'].items()},'diagnostics':{k:v['status'] for k,v in x['diagnostics'].items()}} for x in record['runs']}
assert score_projection(json.loads(SCORE_PATH.read_text()))==baseline['score_projection']
scores=json.loads(SCORE_PATH.read_text())
RUNS=['Fable03','Opus01','Opus02','Opus03','GPT01','GPT02','GPT03']
BY={x['id']:x for x in scores['runs']}
docs={n:json.loads((ROOT/'inputs'/f'{n}-rows.json').read_text()) for n in ['phase','proof','methods']}
aspects={}
for d in docs.values():
    for key in ['aspects','diagnostics']:
        for a in d.get(key,[]):
            assert a['id'] not in aspects,a['id']
            aspects[a['id']]=a
assert set(aspects)==set(scores['criteria'])|set(scores['diagnostic_criteria'])

def text_of(a,*keys,default=''):
    for k in keys:
        if k in a:return a[k]
    return default

def esc(s):
    d={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#',
       '_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}',
       '≤':r'\ensuremath{\leq}','≥':r'\ensuremath{\geq}','≈':r'\ensuremath{\approx}',
       '→':r'\ensuremath{\rightarrow}','←':r'\ensuremath{\leftarrow}',
       '∞':r'\ensuremath{\infty}','χ':r'\ensuremath{\chi}','μ':r'\ensuremath{\mu}',
       'φ':r'\ensuremath{\varphi}','ϕ':r'\ensuremath{\varphi}','σ':r'\ensuremath{\sigma}',
       'τ':r'\ensuremath{\tau}','ρ':r'\ensuremath{\rho}','δ':r'\ensuremath{\delta}',
       'λ':r'\ensuremath{\lambda}','⊕':r'\ensuremath{\oplus}','⊆':r'\ensuremath{\subseteq}',
       '≠':r'\ensuremath{\ne}','±':r'\ensuremath{\pm}','×':r'\ensuremath{\times}',
       'θ':r'\ensuremath{\theta}','η':r'\ensuremath{\eta}','ε':r'\ensuremath{\epsilon}',
       'α':r'\ensuremath{\alpha}','β':r'\ensuremath{\beta}','Γ':r'\ensuremath{\Gamma}',
       '∈':r'\ensuremath{\in}','√':r'\ensuremath{\surd}','∑':r'\ensuremath{\sum}',
       'ℓ':r'\ensuremath{\ell}','≅':r'\ensuremath{\cong}',
       'ψ':r'\ensuremath{\psi}','∓':r'\ensuremath{\mp}',
       '–':'-','—':'-','−':r'\ensuremath{-}','/':r'/\allowbreak{}',',':r',\allowbreak{}'}
    return ''.join(d.get(c,c) for c in str(s))

def inline(s):
    result=[]
    for t in re.split(r'(\\\(.*?\\\)|`[^`]+`|\*\*[^*]+\*\*)',str(s)):
        if t.startswith(r'\('):result.append(t)
        elif t.startswith('`'):result.append(r'\nolinkurl{'+t[1:-1]+'}')
        elif t.startswith('**'):result.append(r'\textbf{'+esc(t[2:-2])+'}')
        else:result.append(esc(t))
    return ''.join(result)

registry={};counters=defaultdict(int);locators=set()
def evs(row):
    raw=row.get('evidence',[])
    if isinstance(raw,dict):raw=[raw]
    if isinstance(raw,str):raw=[{'file':raw,'line':1}]
    ev=list(raw)
    review=row.get('review_evidence')
    if isinstance(review,str):ev.append({'file':review,'line':1,'kind':'review'})
    elif isinstance(review,dict):ev.append(review)
    elif isinstance(review,list):ev.extend(review)
    return ev

def source_entry(e):
    if isinstance(e,str):e={'file':e,'line':1}
    path=Path(e.get('file',e.get('path','')))
    line=e.get('line',e.get('start',1))
    if isinstance(line,str):line=int(re.search(r'\d+',line).group())
    assert path.is_file(),str(path)
    n=len(path.read_text(errors='replace').splitlines())
    assert 1<=line<=n,(str(path),line,n)
    if str(path) not in registry:
        prefix='REV';rel=str(path.relative_to(REVIEW)) if path.is_relative_to(REVIEW) else str(path)
        if path.is_relative_to(SOURCE):
            p=str(path.relative_to(SOURCE));rel=p
            for run in RUNS:
                if p.startswith(BY[run]['folder']+'/'):
                    prefix=run.replace('Fable','F').replace('Opus','O').replace('GPT','G');rel=p[len(BY[run]['folder'])+1:];break
        counters[prefix]+=1
        registry[str(path)]={'id':f'{prefix}-{counters[prefix]:02d}','path':str(path),'relative':rel,
                             'prefix':prefix,'lines':set(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    entry=registry[str(path)];entry['lines'].add(line);locators.add((str(path),line))
    return entry['id'],line

# Freeze score/status values and collect all locators before writing appendix.
for k,a in aspects.items():
    rows={x['run']:x for x in a['rows']}
    assert set(rows)==set(RUNS),(k,set(rows))
    a['rows']=[rows[r] for r in RUNS]
    for r in a['rows']:
        if k in scores['criteria']:
            frozen=BY[r['run']]['criteria'][k]
            if 'score' in r:assert r['score']==frozen['score'],(k,r['run'])
            r['score']=frozen['score'];r['max']=frozen['max']
        else:
            frozen=BY[r['run']]['diagnostics'][k]
            if 'status' in r:assert r['status']==frozen['status'],(k,r['run'],r['status'],frozen['status'])
            r['status']=frozen['status']
        assert r.get('done') and r.get('issue'),(k,r['run'])
        for e in evs(r):source_entry(e)

def cite_tex(row):
    a=[]
    for e in evs(row)[:2]:
        sid,line=source_entry(e)
        a.append(r'\hyperref[src:'+sid+']{'+esc(sid+':'+str(line))+'}')
    return r'\newline '.join(a) if a else 'See review scope in text'

def cite_md(row):
    a=[]
    for e in evs(row)[:2]:
        sid,line=source_entry(e);p=e.get('file',e.get('path','')) if isinstance(e,dict) else e
        a.append(f'[{sid}:{line}](<{p}:{line}>)')
    return '; '.join(a)

PRE=r'''\RequirePackage{fix-cm}
\documentclass[11pt,a4paper]{article}
\usepackage[margin=19mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf]
\setmonofont{lmmono10-regular.otf}[Scale=0.82]
\usepackage{amsmath,amssymb,array,booktabs,longtable,xurl,enumitem,xcolor}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue,bookmarksnumbered=true]{hyperref}
\usepackage{bookmark,fancyhdr,lastpage}
\pdfstringdefDisableCommands{\def\allowbreak{}}
\hypersetup{pdftitle={Aspect-by-aspect comparative study of seven valid AI submissions},pdfauthor={SciCode2 independent review}}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}
\setlist[itemize]{nosep,leftmargin=1.4em}
\renewcommand{\arraystretch}{1.13}
\setcounter{tocdepth}{2}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small Decoder v0.7 / Seven valid submissions}
\fancyhead[R]{\small rubric v1 · 2026-10-16}
\fancyfoot[C]{\small \thepage\ / \pageref{LastPage}}
\begin{document}
\fontsize{10.5}{15.2}\selectfont
'''
tex=[PRE];md=[]

def para(s):tex.append(inline(s)+'\n');md.extend([s,''])
def section(s):tex.append(r'\section{'+inline(s)+'}');md.extend(['# '+s,''])
def subsection(s):tex.append(r'\subsection{'+inline(s)+'}');md.extend(['## '+s,''])
def page():tex.append(r'\clearpage')

def table(headers,rows,widths=None,font=9.0,caption=None,rawcols=()):
    if widths is None:widths=[1/len(headers)]*len(headers)
    assert abs(sum(widths)-1)<1e-4
    cols=''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+str(round(w,6))+r'\linewidth-2\tabcolsep\relax}' for w in widths)
    labels={'Maximum':'Max.','Delivery/15':'Deliv. /15','Rank':'No.','Attempts':'Runs'}
    head=' & '.join(r'\textbf{'+inline(labels.get(x,x))+'}' for x in headers)+r'\tabularnewline'
    tex.extend([r'{\fontsize{'+str(font)+'}{'+str(font*1.4)+r'}\selectfont',r'\setlength{\tabcolsep}{2.5pt}',r'\begin{longtable}{'+cols+'}'])
    if caption:tex.append(r'\caption{'+inline(caption)+r'}\\')
    tex.extend([r'\toprule',head,r'\midrule',r'\endfirsthead',r'\toprule',head,r'\midrule',r'\endhead'])
    md.append('| '+' | '.join(headers)+' |');md.append('| '+' | '.join(['---']*len(headers))+' |')
    for row in rows:
        assert len(row)==len(headers),(headers,row)
        tex.append('{}'+' & '.join(str(c) if i in rawcols else inline(c) for i,c in enumerate(row))+r'\tabularnewline')
    tex.extend([r'\bottomrule',r'\end{longtable}','}'])

def md_table_rows(rows):
    for row in rows:md.append('| '+' | '.join(str(x).replace('|','/') for x in row)+' |')
    md.append('')

tex.append(r'\begin{center}\vspace*{12mm}{\LARGE\bfseries Seven valid AI submissions\\[4mm]Aspect-by-aspect comparative study}\\[6mm]{\large Herald / symmetry-informed decoding benchmark}\\[3mm]{\large Scored using the established rubric v1}\\[5mm]October 16, 2026\end{center}')
md.extend(['# Aspect-by-aspect comparative study of seven valid AI submissions',''])
para('Review population: nine attempts, comprising seven scientific submissions for comparison and two Fable API failures listed separately as void attempts. The comparison unit is the individual run; a single run is not generalized to overall model ability.')
para('The report covers 23 scored aspects of the original task and 21 discussion details. Each question has a seven-row comparison table recording accomplishments, actual issues or evidential limitations, score/coverage status, and source locators. Cross-aspect summaries and issue classifications follow.')
para('The previous rubric weights, scores, and scientific assessments are retained. Original runs are unchanged, and teaching requirements added in this review do not incur retrospective deductions. This is a post hoc local comparison, not a prefrozen official SciCode difficulty test.')
para('Main findings: all seven receive full credit on 18 of the 23 main criteria. Differences concentrate on phase-assignment evidence, approximation-error guarantees, all-p proof certification, extreme numerical range, and failure accounting. High completion scores do not erase key scientific gaps.')
para('GPT01/02 meet all main criteria by giving justified unresolved answers, as permitted by the original task; the true central phase diagram is not thereby fully solved. Fable/Opus are strong on core structure and algorithms, but the evidence for several phase-region conclusions is insufficient.')
page();tex.append(r'\tableofcontents');page()

section('Review population, scoring conventions, and evidence')
para('All nine attempts use the same v0.7 task. The original prompt SHA-256 is `'+scores['prompt_sha256']+'`. This report uses scores-v1.json, whose SHA-256 is `'+FROZEN_HASH+'`. ')
object_rows=[]
for r in RUNS:
    x=BY[r]
    model='Fable 5.1' if r.startswith('Fable') else 'Opus 5.5' if r.startswith('Opus') else 'GPT 6 Astra'
    object_rows.append([r,model,'Valid; included in scoring',str(x['totals']['total'])+'/100',str(x['unresolved_cells'])+'/21'])
for r in ['Fable01','Fable02']:object_rows.append([r,'Fable 5.1','API output limit; void','NA','NA'])
table(['Run','Archived model label','Treatment in this report','Total','unresolved'],object_rows,[.13,.20,.33,.17,.17],caption='Inclusion and exclusion of nine attempts');md_table_rows(object_rows)
para('Void attempts are not assigned scientific zeros and are excluded from the seven-run ranking and model-group means. The 23 main criteria total 100 points: R1 phase diagram 30, R2 exact structure 15, R3 large-N proof 20, R4 posterior 20, and delivery/reproducibility 15. Key scientific pass conditions are assessed individually, without a post hoc automatic total-score pass threshold.')
para('Discussion details do not add points: E=explicit and correct; I=implicit or partially developed; M=no explanation found; X=specific error or insufficiently supported inference; NA=unneeded for a valid alternative method. Teaching diagrams were requested later. Mixing the matrix indices a,b with arrival counts a,b occurred in this chat explanation and is not attributed to the original runs.')
para('The evidence column uses file-ID:line-number locators linked to the appendix file index. Original submissions are distinguished from subsequent independent verification: of 210 ordinary checks, 140 belong to original R4 and 70 are O0 controls; 18 extremely-low-p stress inputs diagnose posterior numerical range. Independent certificates support the theorems but are not retrospectively credited as certification in the original AI submissions.')
para('Possible errors form a checklist; the actual issues/limitations column records observations in this review. No error found means none was identified within the reviewed and tested scope, not a formal proof over the entire parameter domain.')

group_names={'A':'R1: phase diagrams, assignment evidence, and anomalies','B':'R2: model and exact information structure','C':'R3: large-N theorems and proof chains','D':'R4: exact posteriors, numerical range, and decoding','E':'Deliverables, reproducibility, and unconditional accounting'}
for group in 'ABCDE':
    keys=[k for k in scores['criteria'] if k.startswith(group)]
    for j,k in enumerate(keys):
        page()
        if j==0:section(group_names[group])
        a=aspects[k];c=scores['criteria'][k]
        subsection(k+' '+a.get('title',c['title'])+f"({c['max']:g} points)")
        tex.append(r'\label{aspect:'+k+'}')
        para('Review question: '+a['question'])
        para('Scoring requirement: '+c['anchor'])
        para('Scientific significance: '+text_of(a,'why_matters','why_it_matters'))
        mistakes=text_of(a,'possible_mistakes','possible_mistake',default=[])
        if isinstance(mistakes,str):mistakes=[mistakes]
        para('Possible errors (checklist, not errors attributed to all seven): '+'; '.join(mistakes))
        tr=[];mr=[]
        for row in a['rows']:
            tr.append([row['run'],f"{row['score']:g}/{row['max']:g}",row['done'],row['issue'],cite_tex(row)])
            mr.append([row['run'],f"{row['score']:g}/{row['max']:g}",row['done'],row['issue'],cite_md(row)])
        table(['Run','Score','Accomplishments','Actual issues / evidential limitations','Evidence'],tr,[.11,.08,.30,.40,.11],font=9.0,caption=k+': comparison of seven valid submissions',rawcols=(4,));md_table_rows(mr)
        para('Comparison: '+a['conclusion'])
        full=sum(BY[r]['criteria'][k]['score']==c['max'] for r in RUNS)
        para(f'Score distribution: {full}/7 receive full credit; the other {7-full}/7 have explicit deductions or caveats. The same issue already recorded under another aspect is not deducted again.')

for i,k in enumerate(scores['diagnostic_criteria']):
    page()
    if i==0:section('Discussion details: seven-run comparison for each question')
    a=aspects[k];dc=scores['diagnostic_criteria'][k]
    subsection(k+' '+a.get('title',dc['title']))
    tex.append(r'\label{aspect:'+k+'}')
    para('Question: '+a['question'])
    para('Relation to the original task: '+dc['scope']+'. Coverage statuses in this section do not change the main 100-point score.')
    why=text_of(a,'why_matters','why_it_matters')
    if why:para('Reason for checking: '+why)
    mistakes=text_of(a,'possible_mistakes','possible_mistake',default=[])
    if isinstance(mistakes,str):mistakes=[mistakes]
    if mistakes:para('Possible confusions: '+'; '.join(mistakes))
    tr=[];mr=[]
    for row in a['rows']:
        tr.append([row['run'],row['status'],row['done'],row['issue'],cite_tex(row)])
        mr.append([row['run'],row['status'],row['done'],row['issue'],cite_md(row)])
    table(['Run','Status','Content in the submission','Explanatory gaps / caveats / alternative routes','Evidence'],tr,[.11,.07,.31,.40,.11],font=9.0,caption=k+': comparison of discussion-detail coverage',rawcols=(4,));md_table_rows(mr)
    para('Comparative conclusion: '+a['conclusion'])

page();section('Cross-aspect summaries: scores, methods, errors, and shared capabilities')
subsection('Totals, component scores, and key scientific assessments')
ranked=sorted(RUNS,key=lambda r:BY[r]['totals']['total'],reverse=True)
verdict={'Fable03':'Partial: central-phase evidence / numerical range',
         'Opus01':'Partial: central extrapolation / approximation guarantees / numerical range',
         'Opus02':'Partial: central extrapolation / approximation guarantees / numerical range',
         'Opus03':'Partial; additional caveat on original all-p certification',
         'GPT01':'Provisional pass with the conservative answer permitted by the task',
         'GPT02':'Provisional pass with the conservative answer permitted by the task',
         'GPT03':'Pass with caveats: numerical all-p extrapolation at small N'}
rr=[]
for i,r in enumerate(ranked):
    x=BY[r];rank=1+sum(BY[t]['totals']['total']>x['totals']['total'] for t in RUNS)
    rr.append([str(rank),r,*[str(x['totals'][g]) for g in 'ABCDE'],str(x['totals']['total']),verdict[r]])
table(['Rank','Run','R1/30','R2/15','R3/20','R4/20','Delivery/15','Total','Scientific assessment'],rr,[.05,.10,.065,.065,.065,.065,.075,.065,.45],font=8.3,caption='Component totals for seven valid submissions');md_table_rows(rr)
para('Equal totals receive tied ranks. Fable01/02 are void and unranked. Scores follow the established rubric; totals do not replace scientific assessments. For example, insufficient evidence for a definite central-phase conclusion remains a key gap even when structure, algorithms, code, and data earn substantial completion credit.')

page();subsection('Complete matrix and discrimination of the 23 main criteria')
rr=[[k+' '+c['title'],f"{c['max']:g}",*[f"{BY[r]['criteria'][k]['score']:g}" for r in RUNS]] for k,c in scores['criteria'].items()]
table(['Criterion','Maximum',*RUNS],rr,[.30,.06]+[.64/7]*7,font=8.2,caption='Matrix of all main scoring criteria');md_table_rows(rr)
variable=[k for k in scores['criteria'] if len({BY[r]['criteria'][k]['score'] for r in RUNS})>1]
assert variable==['A2','A3','C4','D4','E4']
para('All seven receive full credit on 18/23 criteria. Five criteria discriminate between scores: A2 phase-assignment evidence, A3 error control, C4 exponential bounds and all-p certification, D4 numerical range, and E4 unconditional accounting. Shared high scores reflect supported abilities in exact structure and finite-size algorithms and should remain visible; key differences concern the use of scientific evidence and the scope of numerical commitments.')

page();subsection('Potential errors, actual issues, and affected runs')
error_rows=[
['Overextrapolating finite-size trends','Fable03, Opus01/02/03; a milder extrapolation caveat for GPT03','Key evidence insufficient in the first four; GPT03 has a caveat on an acceptable numerical assignment','A2, Q19'],
['Treating agreement between approximations as a true-error upper bound','Opus01, Opus02, Opus03','Insufficient approximation-error guarantees; robustness of all phase assignments is not guaranteed','A3, Q18/19'],
['Treating a numerical maximum as rigorous all-p certification','Opus03; milder caveat on the original arithmetic presentation of Fable03','Certification completeness as submitted; theorem supported after independent supplementary certification','C4'],
['Underflow or false zero-support diagnosis for positive-probability records','Local stress checks for Fable03 and Opus01/02/03','Implementation-range gap; Linux/macOS differences remain a caveat','D4'],
['Recording posterior risk as 0.5 rather than failure 1 on exceptions','Latent Fable03 code path; code paths in all three Opus runs','Fable archives zero exceptions; Opus01 explicitly reports two, with no inferred counts for the others','E4, Q20'],
['Calling reserved slots completed physical trials','GPT03 specifically checked in this report','Accounting caveat, not classified as scientific failure; 200 reserved slots listed separately','E4, Q20'],
['Missing complete q at N5 or incorrectly claiming monotonicity for all N','All seven correctly handle charge classes','No such core error found in this batch; differences are not invented','B3, Q02/03'],
['Ignoring shared orientations / requiring arrow matrices in every proof','The seven use different valid routes to handle correlations','No scientific reason found to require a single matrix formulation','C3, Q14/16']]
table(['Error type checked','Affected runs in this review','Nature of evidence and caveats','Related criteria'],error_rows,[.24,.25,.39,.12],font=9.0,caption='Actual issues and common errors not observed');md_table_rows(error_rows)
para('This table distinguishes wrong conclusions, insufficient evidence, numerical implementation, delivery accounting, and review considerations. The true physical conclusion for the central phase region has not been proved; insufficient evidence is not described as proved physical falsity.')

page();subsection('Large-N proof routes and strength of results')
proof_cn={
'Fable03':'Random degree coarse-graining; MAP configurations, Bhattacharyya and occupancy matrices; finite-memory path bounds.',
'Opus01':'Random degree coarse-graining, MAP/Bhattacharyya; chords handled through shared side edges; rational certificates.',
'Opus02':'Random degree coarse-graining; direct posterior/polymer injection and fractional moments; interval certificates.',
'Opus03':'Random degree coarse-graining, MAP/Bhattacharyya; occupancy summed before side-edge treatment; original maximum obtained by floating-point optimization.',
'GPT01':'Direct coarse M constraints and parity penalties; orientation norms, chord grouping, occupancy sums; three-part rational certificate.',
'GPT02':'Minimum/maximum edge counts, orientation matrices, and Chernoff; positive-cycle/Ihara-Bass strengthening to N13.',
'GPT03':'Minimum-edge auxiliary decoder; bipartite Cauchy-Schwarz correlation control; Chernoff and rational bounds.'}
rr=[]
for r in RUNS:
    x=BY[r];rr.append([r,str(x['N0']),proof_cn[r],str(x['totals']['C'])+'/20','Supported; sufficient, not minimal'])
table(['Run','N0','Proof route used','As-submitted score','Theorem after review'],rr,[.12,.07,.47,.12,.22],font=9.0,caption='R3 sufficient bounds and method comparison');md_table_rows(rr)
para('The values 13, 14, 15, and 19 do not conflict: each is a sufficient N0. A smaller valid N0 is stronger and is therefore reported separately; under the original rubric, a larger valid N0 does not constitute R3 failure. A proof can avoid direct orientation matrices through valid garbling or Cauchy-Schwarz; it must not lose points for differing from the teaching route.')

page();subsection('Posterior algorithms, approximation scope, and independent verification')
algorithm=docs['methods']['algorithm_comparison']
algorithm=algorithm['rows'] if isinstance(algorithm,dict) else algorithm
rr=[]
for row in algorithm:
    rr.append([row['run'],row['exact_small_L'],row['large_L_method'],row['limit']])
table(['Run','Small-size exact method','Larger-size research method','Comparison caveats'],rr,[.12,.26,.30,.32],font=9.0,caption='Comparison of partition-function computation routes');md_table_rows(rr)
rr=[[r,'210/210','140 original R4 + 70 O0',str(BY[r]['stress_cases_passed'])+'/18','210/210'] for r in RUNS]
table(['Run','Ordinary posterior','Ordinary case composition','Very-low-p stress','Ordinary correction'],rr,[.14,.20,.28,.18,.20],font=9.0,caption='Existing independent verification results');md_table_rows(rr)
para('The maximum ordinary posterior discrepancy is about 1.033e-14, below the original 1e-9 requirement. Stress inputs have strictly positive probability, but local macOS longdouble range differs from the original Linux environment, particularly requiring qualification for Opus02. Computing p/2 in Python float first introduces a separate cross-platform risk of losing the smallest subnormal.')

page();subsection('Run profiles and scope of conclusions')
profiles=[
['Fable03','Complete exact-posterior and structural analysis; valid N19 sufficient proof.','Positive-risk central charge conclusion does not exclude a long crossover; gaps in extreme range and latent exception fallback.','Partial completion; 92.5 points do not establish the central-phase assignment.'],
['Opus01','Larger two-dimensional sizes and extensive diagnostics; N15 proof.','Charge pinning of the clean-loop phase is a physical explanation; chi differences do not certify true bias.','Partial completion; avoid attributing the same BKT formula as Opus02/03.'],
['Opus02','Large-size MPS study and cross-rank information analysis; direct posterior proof.','BKT exclusion and approximation guarantees are unestablished; API exact range and platform need qualification.','Partial completion; ordinary small-size R4 checks still pass.'],
['Opus03','Independent Z4 active-component identity; larger-size study.','Insufficient central extrapolation and chi-bias guarantees; original all-p arithmetic certification needs supplementation.','Partial completion; supplementary certification supports the N15 theorem.'],
['GPT01','N13 direct matrix proof, Z4 identity, and comprehensive numerical safeguards.','11/21 phase entries remain unresolved; the full physical phase diagram is not solved.','Provisional pass with the conservative answer permitted by the original task.'],
['GPT02','Strengthened N13 proof, exact support pruning, and detailed certificates.','12/21 entries unresolved, appropriately retaining undecided ranges.','Provisional pass with the conservative answer permitted by the original task.'],
['GPT03','N14 bipartite proof; exact posterior and endpoint safeguards.','All-p small-N O2 is a numerical assignment; finite-grid/late-crossover caveats remain.','Provisional pass with caveats; slots distinguished from actual trials.']]
table(['Run','Established strengths','Main issues or unknowns','Scientific assessment'],profiles,[.12,.28,.36,.24],font=9.0,caption='Comparative profiles of seven valid submissions');md_table_rows(profiles)
group_rows=[]
for model,prefix,attempts in [('Fable','Fable',3),('Opus','Opus',3),('GPT','GPT',3)]:
    vals=[BY[r]['totals']['total'] for r in RUNS if r.startswith(prefix)]
    group_rows.append([model,str(attempts),str(len(vals)),f'{sum(vals)/len(vals):.2f}',f'{min(vals):g}-{max(vals):g}','Describes a few runs of the same task; cannot establish population success rates'])
table(['Archived model group','Attempts','Valid','Mean among valid runs','Valid-run range','Interpretation'],group_rows,[.15,.08,.08,.13,.15,.41],font=9.0,caption='Descriptive summary by model label');md_table_rows(group_rows)

page();section('Conclusions and fairness limits')
para('This batch shows strong shared capabilities: exact structure, charge equivalence classes, small-size joint posteriors, and valid corrections are independently completed by all seven. Integer-q recovery at N5 and saturation for N>=7 are not widespread omissions; self-avoiding components and correlations also admit different valid treatments.')
para('Expert judgment is needed to assess whether evidence supports final phase-region and error commitments: slow decline and apparent plateaus do not determine the infinite-size limit; agreement between two truncated results does not bound bias relative to the exact value; floating-point global optimization is not rigorous all-p certification. Numerical range and failure accounting are separately repairable implementation/delivery issues and are not automatically failures of deep scientific ability.')
para('The 100 points for GPT01/02 mean their outputs satisfy the current task commitments on justified unresolved results, valid sufficient bounds, and interfaces. This scoring system does not require a fully solved physical phase diagram as the only acceptable answer. Full credit can therefore coexist with open phase regions.')
para('Scores assess final submissions and saved evidence. Rational proofs supplemented in subsequent review are not credited as present in the original AI submissions, nor represented as actual reruns after expert intervention. Four-cell teaching diagrams were not required by the original task and incur no retrospective deductions; the a/b notation mix-up belongs to this chat explanation.')
para('Without guided-B controls and a complete formal freezing protocol, this does not establish completed SciCode difficulty calibration. Small-sample differences among seven runs do not establish overall model superiority, and the two void API attempts are not scientific failures. The true central O1 phase still requires independent research; a gold answer is not chosen by majority vote.')

page();tex.append(r'\appendix');section('Evidence index and traceability records')
para('Main submission root: `'+str(SOURCE)+'`. File-ID prefixes F03, O01, O02, O03, G01, G02, and G03 correspond to the run names and archived directories in this report; REV denotes saved independent-review evidence. The number after the colon is the original file line number. Full absolute paths, SHA-256 hashes, and all cited line numbers are stored in `comparative-report.json`. ')
rr=[]
for path,entry in registry.items():
    display=entry['relative']
    if entry['prefix']=='REV':display='review/'+display
    lines=', '.join(map(str,sorted(entry['lines'])))
    rr.append([r'\phantomsection\label{src:'+entry['id']+'}'+esc(entry['id']),r'\nolinkurl{'+display+'}',lines])
table(['File ID','Archived relative file','Lines cited in this report'],rr,[.13,.64,.23],font=8.5,caption='Evidence file index',rawcols=(0,1))
md_table_rows([[e['id'],e['relative'],','.join(map(str,sorted(e['lines'])))] for e in registry.values()])
para('The original runs and the scientific content of reference-v1 remain unchanged. This edition translates and expands the comparative presentation, checks references, and verifies PDF rendering; there are no new model trials or production phase simulations.')
tex.append(r'\end{document}')

(OUT/'comparative-scoring-report-en.tex').write_text('\n'.join(tex)+'\n')
(ROOT/'comparative-scoring-report.md').write_text('\n'.join(md)+'\n')
records={'version':'comparative-report-v1','date':'2026-10-16','frozen_scores_sha256':FROZEN_HASH,
         'rubric_changed':False,'scores_changed':False,'scientific_runs':RUNS,
         'void_runs':['Fable01','Fable02'],'main_aspect_count':23,'diagnostic_aspect_count':21,
         'aspect_tables':aspects,'summary_error_rows':error_rows,'profiles':profiles,
         'source_registry':[{**e,'lines':sorted(e['lines'])} for e in registry.values()],
         'source_locators_checked':len(locators),'score_snapshot':scores,
         'no_new_model_or_production_phase_trials':True}
(ROOT/'comparative-report.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
with (ROOT/'comparison-long.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['aspect','run','score','max','coverage_status','done','issue','evidence'])
    for k,a in aspects.items():
        for row in a['rows']:w.writerow([k,row['run'],row.get('score',''),row.get('max',''),row.get('status',''),row['done'],row['issue'],cite_md(row)])
print(json.dumps({'main_tables':23,'diagnostic_tables':21,'rows':sum(len(a['rows']) for a in aspects.values()),'source_files':len(registry),'source_locators_checked':len(locators),'tex':str(OUT/'comparative-scoring-report-en.tex')},ensure_ascii=False))
