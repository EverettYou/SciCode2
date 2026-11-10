"""Produce standalone XeLaTeX sources from the reviewed reference Markdown."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)

def escape(s):
    table={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$',
           '#':r'\#','_':r'\_','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}',
           '≤':r'\ensuremath{\leq}','≥':r'\ensuremath{\geq}','≈':r'\ensuremath{\approx}',
           '→':r'\ensuremath{\rightarrow}','∞':r'\ensuremath{\infty}',
           'χ':r'\ensuremath{\chi}','μ':r'\ensuremath{\mu}','φ':r'\ensuremath{\varphi}',
           '/':r'/\allowbreak{}'}
    return ''.join(table.get(c,c) for c in s)

def inline(s):
    # Local source links are rendered as their human-readable locators; full clickable paths stay in MD/JSON.
    s=re.sub(r'\[([^\]]+)\]\(<[^>]+>\)',lambda m:m.group(1),s)
    s=re.sub(r'\[([^\]]+)\]\([^\)]+\)',lambda m:m.group(1),s)
    tokens=re.split(r'(\\\(.*?\\\)|`[^`]+`|\*\*[^*]+\*\*)',s)
    out=[]
    for t in tokens:
        if t.startswith(r'\('):out.append(t)
        elif t.startswith('`'):out.append(r'\nolinkurl{'+t[1:-1]+'}')
        elif t.startswith('**'):out.append(r'\textbf{'+escape(t[2:-2])+'}')
        else:out.append(escape(t))
    return ''.join(out)

def widths(header):
    n=len(header)
    if n==9:
        if 'Scientific assessment' in header:return [.12]+[.07]*7+[.39]
        return [.30,.06]+[.64/7]*7
    if n==8:return [.37]+[.09]*7
    if n==5:return [.10,.06,.19,.19,.46]
    if n==4:return [.07,.08,.17,.68]
    if n==3:return [.12,.53,.35]
    if n==2:return [.28,.72]
    return [1/n]*n

def table(lines):
    rows=[[x.strip() for x in s.strip().strip('|').split('|')] for s in lines]
    header=rows[0];rows=[x for x in rows[1:] if not all(re.fullmatch(r'[-: ]+',c) for c in x)]
    ws=widths(header)
    spec=''.join(r'>{\raggedright\arraybackslash}p{\dimexpr '+str(round(w,5))+r'\linewidth-2\tabcolsep\relax}' for w in ws)
    font=r'\fontsize{8.1}{11}\selectfont' if len(header)>=8 else r'\fontsize{9}{12.5}\selectfont'
    labels={'Maximum':'Max.','Delivery /15':'Deliv. /15'}
    h=' & '.join(r'\textbf{'+inline(labels.get(x,x))+'}' for x in header)+r'\tabularnewline'
    body=[r'{'+font,r'\setlength{\tabcolsep}{2.2pt}',r'\renewcommand{\arraystretch}{1.05}' if len(header)>=8 else '',r'\begin{longtable}{'+spec+'}',r'\toprule',h,r'\midrule',r'\endfirsthead',r'\toprule',h,r'\midrule',r'\endhead']
    for row in rows:
        assert len(row)==len(header),(header,row)
        body.append('{}'+' & '.join(inline(x) for x in row)+r'\tabularnewline')
    body += [r'\bottomrule',r'\end{longtable}','}']
    return '\n'.join(body)

def convert(md):
    lines=md.splitlines();out=[];i=0;in_list=False
    while i<len(lines):
        line=lines[i]
        if in_list and not line.startswith('- '):out.append(r'\end{itemize}');in_list=False
        if line.startswith('!['):
            m=re.fullmatch(r'!\[([^\]]+)\]\(([^\)]+)\)',line)
            assert m,line
            path=ROOT/m.group(2)
            out.append(r'\begin{center}\includegraphics[width=\linewidth]{\detokenize{'+str(path)+r'}}\end{center}')
            i+=1;continue
        if line.strip()==r'\[':
            block=[line];i+=1
            while i<len(lines):
                block.append(lines[i]);i+=1
                if block[-1].strip()==r'\]':break
            out.extend(block);continue
        if line.startswith('|'):
            block=[]
            while i<len(lines) and lines[i].startswith('|'):block.append(lines[i]);i+=1
            out.append(table(block));continue
        if line.startswith('# '):out.append(r'\section*{'+inline(line[2:])+'}')
        elif line.startswith('## '):out.append(r'\section*{'+inline(line[3:])+'}')
        elif line.startswith('### '):out.append(r'\subsection*{'+inline(line[4:])+'}')
        elif line.startswith('- '):
            if not in_list:out.append(r'\begin{itemize}');in_list=True
            out.append(r'\item '+inline(line[2:]))
        elif not line.strip():out.append('')
        else:out.append(inline(line))
        i+=1
    if in_list:out.append(r'\end{itemize}')
    return '\n'.join(out)

PRE=r'''\documentclass[11pt,a4paper]{article}
\usepackage[margin=20mm,headheight=14pt]{geometry}
\usepackage{fontspec}
\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf]
\setsansfont{lmsans10-regular.otf}
\setmonofont{lmmono10-regular.otf}[Scale=0.82]
\usepackage{amsmath,amssymb,booktabs,longtable,array,xurl,enumitem,graphicx}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\usepackage{fancyhdr,lastpage}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{3em}
\setlist[itemize]{nosep,leftmargin=1.5em}
\renewcommand{\arraystretch}{1.18}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small SciCode2 / Decoder v0.7}
\fancyhead[R]{\small Post hoc independent review / 2026-10-16}
\fancyfoot[C]{\small \thepage\ / \pageref{LastPage}}
\begin{document}
'''

standard=(ROOT/'standard-answer.md').read_text()+'\n\n'+(ROOT/'reference-bounds.md').read_text()
(OUT/'standard-answer-en.tex').write_text(PRE+convert(standard)+'\n\\end{document}\n')

rubric=(ROOT/'rubric.md').read_text()
score=(ROOT/'scorecards.md').read_text().split('## Fable03:')[0]
record=json.loads((ROOT/'scores-v1.json').read_text())
appendix=['# Appendix: evidence for deductions and caveats','',
'All 161 scientific-submission scores, 21 discussion diagnostics, and full absolute paths are retained in scorecards.md, scores-v1.json, and score-details-v1.csv. Items affecting scores or conclusions are collected below.','']
source=Path('/Users/home/Downloads/20261014-102308_d89b765a')
for x in record['runs']:
    if not x['assessable']:continue
    appendix+=['## '+x['id'],'']
    deductions=[(k,v) for k,v in x['criteria'].items() if v['score']<v['max']]
    if not deductions:
        appendix+=['All main criteria of this rubric are satisfied. The central phase region remains unknown, as in the reference answer; the full phase diagram is not thereby solved.','']
    for k,v in deductions:
        e=v['evidence'][0];p=Path(e['file']);rel=p.relative_to(source);line=e.get('line',e.get('start',1))
        appendix += [f"- {k}: {v['score']}/{v['max']}. {v['reason']} Source: `{rel}:{line}`."]
    if x['id']=='Fable03':appendix+=['- The exception-accounting defect is latent: the archived summaries total zero exceptions, and no change to the archived phase-diagram values was found.']
    if x['id']=='Opus02':appendix+=['- The extremely-low-p numerical gap includes the longdouble range difference between the original Linux environment and the macOS review; loss of the smallest subnormal when computing p/2 first in Python float is independent of that difference.']
    if x['id']=='GPT03':appendix+=['- The 340600 archived slots include 200 reserved failure slots whose execution is unverified; the report interprets them with this qualification.']
    appendix.append('')
appendix+=['# Appendix: version and review scope','',
'Original prompt SHA-256: `'+record['prompt_sha256']+'`. The task is unchanged, with no new model runs or production phase-diagram experiments. Existing independent oracles, 210 ordinary checks, 18 stress checks, and large-N rational certificates are reused; this review adds the rubric, detailed deliverable audit, and certification of reference safe endpoints.','',
'The scores are not a formal SciCode A/B difficulty conclusion. The full official template remains unverified; local weights are not represented as official rules. Totals measure completion, while key scientific pass conditions remain individually stated.']
(OUT/'rubric-and-scorecards-en.tex').write_text(PRE+convert(rubric)+'\n\\clearpage\n'+convert(score)+'\n'+convert('\n'.join(appendix))+'\n\\end{document}\n')
print(OUT/'standard-answer-en.tex')
print(OUT/'rubric-and-scorecards-en.tex')
