"""Plot measured, exactly certified reference outcomes from canonical JSON."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
b=Path(__file__).resolve().parents[2]
models=[
 ('PQG','labs/lab-002-moment-sdp/results/pqg-eps6/result.json','labs/lab-004-exact-dual-verification/results/pqg-eps6/verification.json'),
 ('Two-site T2prime','labs/lab-002-moment-sdp/results/two-site-t2-sym-clarabel/result.json','labs/lab-004-exact-dual-verification/results/two-site-t2-sym-clarabel/verification.json'),
 ('Full T2prime','labs/lab-004-exact-dual-verification/results/full-reproduction/model/result.json','labs/lab-004-exact-dual-verification/results/full-reproduction/exact/verification.json'),
 ('Selected T2prime','labs/lab-004-exact-dual-verification/results/portable-reproduction/model/result.json','labs/lab-004-exact-dual-verification/results/portable-reproduction/exact/verification.json'),
]
rows=[]
for label,solve,cert in models:
    d=json.loads((b/solve).read_text());c=json.loads((b/cert).read_text())
    rows.append(dict(model=label,lower=float(c['reported_total_energy_lower_bound']),entries=d['psd_entries'],solve_seconds=d['solve_sec'],peak_mb=d['peak_rss_bytes']/1e6,solve_source=solve,certificate_source=cert))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,(ax,foot)=plt.subplots(1,2,figsize=(10,3.8),gridspec_kw={'width_ratios':[1.1,1]},sharey=True)
y=np.arange(len(rows));colors=['#627d98']*3+['#b45309']
ax.scatter([r['lower'] for r in rows],y,c=colors,s=75,zorder=3)
for i,row in enumerate(rows):ax.text(row['lower']+0.06,i,f"{row['lower']:.6f}",va='center',color=colors[i])
ax.set(yticks=y,yticklabels=[r['model'] for r in rows],xlim=(-10.8,-8.18),xlabel='Certified total-energy lower bound',title='Attainable certificates')
ax.invert_yaxis();ax.grid(axis='x',alpha=.18)
foot.barh(y,[r['entries'] for r in rows],color=colors,height=.5)
foot.set_xscale('log');foot.set(xlim=(7000,1e6),xlabel='Full PSD matrix entries',title='Reduced cone footprint')
for i,row in enumerate(rows):foot.text(row['entries']*1.08,i,f"{row['entries']:,}",va='center')
foot.grid(axis='x',alpha=.18)
fig.suptitle('Hubbard 4 x 4, U=8, half filling',fontsize=13)
fig.text(.5,.025,'Selection uses full-model discovery; solve precision differs. Complete time and memory records accompany the figure.',ha='center',fontsize=8,color='#475569')
fig.tight_layout(rect=(0,.07,1,.96))
out=Path(__file__).resolve().parent
fig.savefig(out/'operator-cost-frontier.png',dpi=180)
fig.savefig(out/'operator-cost-frontier.pdf')
(out/'operator-cost-frontier.json').write_text(json.dumps(rows,indent=2)+'\n')
print(out/'operator-cost-frontier.png')
