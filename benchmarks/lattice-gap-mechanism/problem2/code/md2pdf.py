"""Minimal Markdown -> LaTeX -> PDF (tectonic) for the report (headers, paragraphs, bullet lists,
pipe tables, inline code, bold/italic, figure references by `figures/...png` mention)."""
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

UNICODE = {
    "Δ": r"$\Delta$", "ν": r"$\nu$", "σ": r"$\sigma$", "ℓ": r"$\ell$", "π": r"$\pi$", "ω": r"$\omega$",
    "χ": r"$\chi$", "ρ": r"$\rho$", "τ": r"$\tau$", "μ": r"$\mu$", "ε": r"$\varepsilon$", "ξ": r"$\xi$",
    "α": r"$\alpha$", "β": r"$\beta$", "δ": r"$\delta$", "λ": r"$\lambda$", "κ": r"$\kappa$", "η": r"$\eta$",
    "Σ": r"$\sum$", "†": r"$^\dagger$", "⟨": r"$\langle$", "⟩": r"$\rangle$", "·": r"$\cdot$", "×": r"$\times$",
    "≈": r"$\approx$", "≤": r"$\le$", "≥": r"$\ge$", "≠": r"$\ne$", "→": r"$\to$", "↔": r"$\leftrightarrow$",
    "±": r"$\pm$", "−": "--", "–": "--", "—": "---", "∝": r"$\propto$", "∞": r"$\infty$", "√": r"$\sqrt{}$",
    "²": r"$^2$", "³": r"$^3$", "¼": "1/4", "½": "1/2", "⁻": r"$^-$", "⁺": r"$^+$", "₁": r"$_1$", "₂": r"$_2$",
    "₀": r"$_0$", "₊": r"$_+$", "₋": r"$_-$", "ᵀ": r"$^T$", "″": "''", "′": "'", "∈": r"$\in$", "∫": r"$\int$",
    "ħ": r"$\hbar$", "°": r"$^\circ$", "ʰ": "h", "ₛ": r"$_s$", "ᵢ": r"$_i$", "₁₁": r"$_{11}$", "ψ": r"$\psi$",
    "Φ": r"$\Phi$", "φ": r"$\phi$", "θ": r"$\theta$", "Ω": r"$\Omega$", "γ": r"$\gamma$", "·": r"$\cdot$",
    "↑": r"$\uparrow$", "↓": r"$\downarrow$", "∧": r"$\wedge$", "ℏ": r"$\hbar$", "∂": r"$\partial$",
    "⁴": r"$^4$", "₃": r"$_3$", "⅓": "1/3", "ẑ": "z", "̂": "", "R̂": r"$\hat R$", "∑": r"$\sum$", "∥": r"$\parallel$",
    "≲": r"$\lesssim$", "≳": r"$\gtrsim$", "…": r"\ldots{}", "″": "''", "ℓ": r"$\ell$",
}


def esc(t: str) -> str:
    # protect inline code first
    parts = re.split(r"(`[^`]*`)", t)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) >= 2:
            body = p[1:-1].replace("\\", r"\textbackslash{}").replace("_", r"\_").replace("%", r"\%").replace("#", r"\#").replace("&", r"\&").replace("{", r"\{").replace("}", r"\}")
            out.append(r"\texttt{" + body + "}")
            continue
        p = p.replace("\\", r"\textbackslash{}")
        for a, b in (("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("$", r"\$"), ("{", r"\{"), ("}", r"\}"), ("^", r"\^{}"), ("~", r"\~{}")):
            p = p.replace(a, b)
        for u, l in UNICODE.items():
            p = p.replace(u, l)
        p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
        p = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"\\emph{\1}", p)
        out.append(p)
    return "".join(out)


def join_paragraphs(md: str) -> str:
    out, buf = [], []
    for ln in md.splitlines():
        special = ln.startswith(("#", "|", "* ", "  ")) or ln.strip() == ""
        if special:
            if buf:
                out.append(" ".join(buf)); buf = []
            out.append(ln)
        else:
            buf.append(ln.strip())
    if buf:
        out.append(" ".join(buf))
    return "\n".join(out)


def convert(md: str) -> str:
    md = re.sub(r"<!--.*?-->\n?", "", md, flags=re.S)
    md = join_paragraphs(md)
    lines = md.splitlines()
    tex = []
    i = 0
    in_list = False
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| :]+\|?$", lines[i + 1].strip()):
            # table
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            ncol = len(header)
            tex.append(r"\begin{center}\footnotesize\setlength{\tabcolsep}{3pt}")
            if ncol > 7:
                tex.append(r"\resizebox{\textwidth}{!}{%")
            tex.append(r"\begin{tabular}{" + "l" * ncol + "}\\toprule")
            tex.append(" & ".join(esc(h) for h in header) + r" \\ \midrule")
            for r in rows:
                r = r + [""] * (ncol - len(r))
                tex.append(" & ".join(esc(c) for c in r[:ncol]) + r" \\")
            tex.append(r"\bottomrule\end{tabular}" + ("}" if ncol > 7 else "") + r"\end{center}")
            continue
        if in_list and not ln.startswith("* ") and not ln.startswith("  "):
            tex.append(r"\end{itemize}")
            in_list = False
        if ln.startswith("# "):
            tex.append(r"\title{" + esc(ln[2:]) + r"}\maketitle")
        elif ln.startswith("## "):
            tex.append(r"\section*{" + esc(ln[3:]) + "}")
        elif ln.startswith("### "):
            tex.append(r"\subsection*{" + esc(ln[4:]) + "}")
        elif ln.startswith("* "):
            if not in_list:
                tex.append(r"\begin{itemize}")
                in_list = True
            tex.append(r"\item " + esc(ln[2:]))
        elif ln.startswith("  ") and in_list:
            tex.append(esc(ln.strip()))
        elif ln.strip() == "":
            tex.append("")
        else:
            m = re.search(r"figures/([\w.\-]+\.png)", ln)
            tex.append(esc(ln))
            if m:
                tex.append(r"\begin{center}\includegraphics[width=0.95\textwidth]{figures/" + m.group(1) + r"}\end{center}")
        i += 1
    if in_list:
        tex.append(r"\end{itemize}")
    head = r"""\documentclass[10pt]{article}
\usepackage[margin=0.8in]{geometry}
\usepackage{amsmath,amssymb,booktabs,graphicx,hyperref,xcolor}
\hypersetup{colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black}
\setlength{\parskip}{0.4em}\setlength{\parindent}{0pt}
\graphicspath{{../}}
\author{}\date{}
\begin{document}
"""
    return head + "\n".join(tex) + "\n\\end{document}\n"


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "report", "report.md")
    md = open(src).read()
    tex = convert(md)
    out = os.path.join(ROOT, "report", "report.tex")
    open(out, "w").write(tex)
    env = dict(os.environ)
    cache = os.path.join(ROOT, ".tectonic_cache")
    env["TECTONIC_CACHE_DIR"] = cache
    env["XDG_CACHE_HOME"] = cache
    libdir = os.path.expanduser("~/.local/texdeps/usr/lib/x86_64-linux-gnu")
    if os.path.isdir(libdir):
        env["LD_LIBRARY_PATH"] = libdir + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")
    tectonic = os.path.expanduser("~/.local/bin/tectonic") if os.path.exists(os.path.expanduser("~/.local/bin/tectonic")) else "tectonic"
    r = subprocess.run([tectonic, "-X", "compile", "--keep-logs", out], capture_output=True, text=True,
                       cwd=os.path.join(ROOT, "report"), env=env)
    print(r.stdout[-2000:], r.stderr[-3000:])
    print("exit", r.returncode)


if __name__ == "__main__":
    main()
