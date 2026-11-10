import re, json, glob, numpy as np
Dfree_rung = {0.1875: 1.4089, 0.3125: 1.7484, 0.5: 1.6770}
rows = {}
for f in glob.glob('stiff_U1.8_J6.5_*.log'):
    for line in open(f):
        m = re.search(r'nu=([\d.]+): E0=([-\d.]+) D\(2nd diff\)=([-\d.]+) D\(curv\)=([-\d.]+)', line)
        if m:
            nu = float(m.group(1)); rows[nu] = float(m.group(4))
nus = sorted(rows)
out = {'nu': nus, 'D': [rows[n] for n in nus], 'Dfree': [Dfree_rung[n] for n in nus]}
json.dump(out, open('stiffness.json', 'w'), indent=1)
print(out)
