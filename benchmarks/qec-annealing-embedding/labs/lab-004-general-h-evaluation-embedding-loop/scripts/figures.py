from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
a=json.loads((OUT/'analysis_summary.json').read_text())['rows']
fig,axes=plt.subplots(1,3,figsize=(13,4),layout='constrained')
colors={'random_regular':'#4477AA','irregular_hubs':'#EE6677','rewired_band':'#228833','mixed_hypergraph':'#AA3377'}
for family,color in colors.items():
 rows=[x for x in a if x['family']==family]
 axes[0].scatter([x['first_qubits'] for x in rows],[x['guided_qubits'] for x in rows],c=color,label=family.replace('_',' '),s=25)
 axes[1].scatter([100*x['size_only_reduction_fraction'] for x in rows],[x['size_only_scale']/x['first_scale'] for x in rows],c=color,s=25)
maxq=max(x['first_qubits'] for x in a);axes[0].plot([0,maxq],[0,maxq],ls='--',c='gray',lw=1)
axes[0].set(xlabel='First automatic mapping: physical qubits',ylabel='Guided mapping: physical qubits',title='General-H compactness, 36 inputs')
axes[0].legend(fontsize=7,loc='upper left')
axes[1].axhline(1,color='gray',ls='--',lw=1);axes[1].set(xlabel='Unconstrained size-only qubit reduction (%)',ylabel='Size-only scale / reference scale',title='Smallest mapping can lose usable scale')
g=json.loads((OUT/'logical_gibbs_validation.json').read_text())['records']
x=[r['scores']['first']['ground_probability'] for r in g];y=[r['scores']['guided_pruned']['ground_probability'] for r in g]
axes[2].scatter(x,y,c=[colors[r['name'].rsplit('_n',1)[0]] for r in g],s=35)
lim=max(x+y)*1.07;axes[2].plot([0,lim],[0,lim],ls='--',c='gray',lw=1)
axes[2].set(xlabel='Reference conditional ground probability',ylabel='Guided conditional ground probability',title='Exact logical Gibbs, ordinary n=16')
for ax in axes:ax.grid(alpha=.15)
fig.savefig(FIG/'general_h_loop.png',dpi=180);fig.savefig(FIG/'general_h_loop.pdf')
print(str(FIG/'general_h_loop.png'))
