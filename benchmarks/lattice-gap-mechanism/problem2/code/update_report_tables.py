"""Rebuild every <!-- TABLE:L:nu --> ... <!-- /TABLE --> block in report/report.md from data/summary.json."""
import os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "report", "report.md")
s = open(p).read()
def repl(m):
    L, nu = m.group(1), m.group(2)
    tab = subprocess.run([os.path.join(ROOT, ".venv", "bin", "python"), os.path.join(ROOT, "code", "make_tables.py"), L, nu],
                         capture_output=True, text=True).stdout.strip()
    return f"<!-- TABLE:{L}:{nu} -->\n{tab}\n<!-- /TABLE -->"
s2 = re.sub(r"<!-- TABLE:(\d+):([\d.]+) -->.*?<!-- /TABLE -->", repl, s, flags=re.S)
grid = subprocess.run([os.path.join(ROOT, ".venv", "bin", "python"), os.path.join(ROOT, "code", "make_grid_table.py")], capture_output=True, text=True).stdout.strip()
s2 = re.sub(r"<!-- GRIDTABLE -->.*?<!-- /GRIDTABLE -->", lambda m: "<!-- GRIDTABLE -->\n" + grid + "\n<!-- /GRIDTABLE -->", s2, flags=re.S)
l6 = subprocess.run([os.path.join(ROOT, ".venv", "bin", "python"), os.path.join(ROOT, "code", "make_tables.py"), "6", "0.5", "_xr2"], capture_output=True, text=True).stdout.strip()
s2 = re.sub(r"<!-- L6TABLE -->.*?<!-- /L6TABLE -->", lambda m: "<!-- L6TABLE -->\n" + l6 + "\n<!-- /L6TABLE -->", s2, flags=re.S)
open(p, "w").write(s2)
print("tables rebuilt")
