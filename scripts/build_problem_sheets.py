#!/usr/bin/env python3
"""Build the three lightweight candidate sheets directly from canonical TASK.md.

Uses a local pdfLaTeX installation and pypdf. The generated main.tex is editable,
but TASK.md remains the source of truth. A matching compatibility PDF is written
under output/pdf, and the D4 model JSON is embedded byte-for-byte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = {
    "fusion-informed-decoding": 1,
    "u1-directional-logical-gap": 2,
    "d4-adaptive-readout-value": 3,
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def escape(text: str) -> str:
    mapping = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(mapping.get(c, c) for c in text)


def inline(text: str) -> str:
    pattern = r"(\$[^$\n]+\$|`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))"
    result = []
    for part in re.split(pattern, text):
        if part.startswith("$") and part.endswith("$"):
            result.append(part)
        elif part.startswith("`") and part.endswith("`"):
            code = escape(part[1:-1]).replace(r"\_", r"\_\allowbreak{}")
            code = code.replace(",", r",\allowbreak{}").replace("(", r"(\allowbreak{}")
            result.append(r"{\ttfamily\small " + code + "}")
        elif part.startswith("**") and part.endswith("**"):
            result.append(r"\textbf{" + inline(part[2:-2]) + "}")
        elif re.fullmatch(r"\[[^\]]+\]\([^)]+\)", part):
            label, target = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part).groups()
            result.append(r"\href{" + escape(target) + "}{" + inline(label) + "}")
        else:
            result.append(escape(part))
    return "".join(result)


def markdown_body(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    title = lines.pop(0).removeprefix("# ").strip()
    while lines and not lines[0].strip():
        lines.pop(0)
    subtitle = lines.pop(0).strip()
    body = [r"{\raggedright\hyphenpenalty=10000\exhyphenpenalty=10000\fontsize{24}{28}\selectfont\sffamily\bfseries " + inline(title) + r"\par}",
            r"\vspace{7pt}{\large\sffamily\color{accent} " + inline(subtitle) + r"\par}",
            r"\vspace{8pt}"]
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("## "):
            heading = line[3:]
            if heading.startswith("Appendix"):
                body.append(r"\clearpage")
            body.append(r"\section*{" + inline(heading) + "}")
            i += 1
        elif line.startswith("$$"):
            if not line.endswith("$$") or len(line) < 4:
                raise ValueError("Display equations must occupy one Markdown line")
            body.append(r"\begin{center}\displayfit{" + line[2:-2] + r"}\end{center}")
            i += 1
        elif line.startswith("!["):
            match = re.fullmatch(r"!\[(.*)\]\(([^)]+)\)", line)
            if not match:
                raise ValueError("Unsupported image syntax: " + line)
            caption, path = match.groups()
            body.append(r"\begin{center}\begin{minipage}{\linewidth}\centering" + "\n" +
                        r"\includegraphics[width=\linewidth,height=2.85in,keepaspectratio]{" + path + "}\n" +
                        r"\par\vspace{4pt}{\small " + inline(caption) + r"\par}" + "\n" +
                        r"\end{minipage}\end{center}")
            i += 1
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", x) for x in row):
                    if len(row) != 2:
                        raise ValueError("Only two-column tables are supported")
                    rows.append(row)
                i += 1
            head = " & ".join(r"\textbf{" + inline(x) + "}" for x in rows[0]) + r" \\"
            contents = "\n".join(" & ".join(inline(x) for x in row) + r" \\[5pt]" for row in rows[1:])
            if len(rows) <= 5:
                body.append(r"\begin{center}\begin{minipage}{\linewidth}\begin{tabular}{@{}p{0.29\linewidth}p{0.67\linewidth}@{}}" + "\n" +
                            r"\toprule " + head + "\n" + r"\midrule" + "\n" + contents + "\n" +
                            r"\bottomrule\end{tabular}\end{minipage}\end{center}")
            else:
                body.append(r"\begin{longtable}{@{}p{0.29\linewidth}p{0.67\linewidth}@{}}" + "\n" +
                            r"\toprule " + head + "\n" + r"\midrule\endhead" + "\n" + contents +
                            "\n" + r"\bottomrule\end{longtable}")
        elif line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(r"\item " + inline(lines[i].strip()[2:]))
                i += 1
            body.append(r"\begin{itemize}" + "\n" + "\n".join(items) + "\n" + r"\end{itemize}")
        else:
            parts = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("## ", "$$", "![", "|", "- ", "<!--")):
                parts.append(lines[i].strip())
                i += 1
            following = i
            while following < len(lines) and not lines[following].strip():
                following += 1
            if following < len(lines) and lines[following].strip().startswith("|"):
                body.append(r"\Needspace{9\baselineskip}")
            elif following < len(lines) and lines[following].strip().startswith("$$") and len(" ".join(parts)) < 150:
                body.append(r"\Needspace{4\baselineskip}")
            body.append(inline(" ".join(parts)) + r"\par")
    return title, "\n\n".join(body)


PREAMBLE = r"""\documentclass[11pt,letterpaper]{article}
\usepackage[margin=0.78in,headheight=15pt,headsep=17pt,footskip=27pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,amsmath,amssymb,microtype,graphicx,longtable,booktabs,array}
\usepackage{enumitem,xcolor,titlesec,fancyhdr,hyperref,needspace}
\definecolor{accent}{HTML}{145E72}
\definecolor{ink}{HTML}{172D3E}
\hypersetup{colorlinks=true,urlcolor=accent,linkcolor=accent}
\color{ink}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\footnotesize\sffamily\color{accent} SCI CODE 2 | RESEARCH BENCHMARK}
\fancyhead[R]{\footnotesize\sffamily CANDIDATE __NUMBER__}
\fancyfoot[L]{\footnotesize\sffamily Review draft __VERSION__ | __DATE__}
\fancyfoot[R]{\footnotesize\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0.3pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{4pt}
\setlength{\emergencystretch}{2em}
\setlist{leftmargin=*,itemsep=3pt,topsep=4pt,parsep=0pt}
\titleformat{\section}{\large\sffamily\bfseries\color{accent}}{}{0em}{}
\titlespacing*{\section}{0pt}{12pt}{5pt}
\widowpenalty=10000\clubpenalty=10000
\newsavebox{\mathbox}
\newcommand{\displayfit}[1]{\sbox{\mathbox}{$\displaystyle #1$}\ifdim\wd\mathbox>\linewidth\resizebox{\linewidth}{!}{\usebox{\mathbox}}\else\usebox{\mathbox}\fi}
\begin{document}
\fontsize{10.5}{12.7}\selectfont
"""


def build(bid: str) -> dict:
    benchmark = ROOT / "benchmarks" / bid
    problem = benchmark / "problem"
    task = problem / "TASK.md"
    metadata = (benchmark / "metadata.yml").read_text()
    version = re.search(r"^formulation_revision: (.+)$", metadata, re.M).group(1).removeprefix("review-draft-")
    title, body = markdown_body(task.read_text())
    updated_match = re.search(r"^formulation_updated: ['\"]?([0-9-]+)", metadata, re.M)
    updated = date.fromisoformat(updated_match.group(1)) if updated_match else date.today()
    label_date = updated.strftime("%d %B %Y").lstrip("0")
    preamble = PREAMBLE.replace("__NUMBER__", f"{CANDIDATES[bid]:02d}").replace("__VERSION__", version).replace("__DATE__", label_date)
    tex = problem / "main.tex"
    tex.write_text(f"% Generated from TASK.md; sha256={sha(task)}\n" + preamble + body + "\n\\end{document}\n")
    compiler = shutil.which("pdflatex") or "/Library/TeX/texbin/pdflatex"
    if not Path(compiler).is_file():
        raise FileNotFoundError("No local pdfLaTeX installation found")
    with tempfile.TemporaryDirectory(prefix="scicode2-sheets-") as temp:
        args = [compiler, "-interaction=nonstopmode", "-halt-on-error", "-output-directory=" + temp, str(tex)]
        for _ in range(2):
            result = subprocess.run(args, cwd=problem, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(result.stdout[-6000:] + result.stderr[-1000:])
        log = (Path(temp) / "main.log").read_text(errors="replace")
        overfull = re.findall(r"Overfull[^\n]+", log)
        reader = PdfReader(Path(temp) / "main.pdf")
        writer = PdfWriter()
        writer.clone_document_from_reader(reader)
        writer.add_metadata({"/Title": title, "/Author": "SciCode2", "/Subject": "Review draft " + version})
        if bid == "d4-adaptive-readout-value":
            writer.add_attachment("d4-instrument-v1.json", (problem / "inputs/d4-instrument-v1.json").read_bytes())
        pdf = problem / "problem.pdf"
        with pdf.open("wb") as output:
            writer.write(output)
    compat = benchmark / "output/pdf/problem.pdf"
    compat.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(pdf, compat)
    paths = ["problem/TASK.md", "problem/main.tex", "problem/problem.pdf", "output/pdf/problem.pdf", "metadata.yml"]
    if bid == "fusion-informed-decoding":
        paths.append("problem/figures/geometry-L3.png")
    if bid == "d4-adaptive-readout-value":
        paths.append("problem/inputs/d4-instrument-v1.json")
    record = {
        "revision": "review-draft-" + version,
        "purpose": "human question review; editable and not frozen for model trials",
        "canonical_question": "problem/TASK.md",
        "canonical_pdf": "problem/problem.pdf",
        "builder": "scripts/build_problem_sheets.py",
        "built_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": sha(task),
        "files": {path: sha(benchmark / path) for path in paths},
        "pdf_pages": len(PdfReader(pdf).pages),
        "overfull_boxes": overfull,
        "qa": "compiled; visual inspection pending",
        "scientific_execution": "not-started",
        "model_trials": "not-started",
    }
    (compat.parent / "build-record.json").write_text(json.dumps(record, indent=2) + "\n")
    return {"benchmark": bid, "revision": version, "pages": record["pdf_pages"], "overfull_boxes": overfull}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("benchmarks", nargs="*", metavar="BENCHMARK")
    selected = parser.parse_args().benchmarks or list(CANDIDATES)
    unknown = set(selected) - set(CANDIDATES)
    if unknown:
        parser.error("Unknown benchmark(s): " + ", ".join(sorted(unknown)))
    for name in selected:
        print(json.dumps(build(name)))
