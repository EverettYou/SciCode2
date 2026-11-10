from pathlib import Path
import json,os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/scicode2-lab005-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
summary=json.loads((OUT/'analysis_summary.json').read_text());pairs=summary['pairs']
fig,axes=plt.subplots(1,3,figsize=(13.5,4.1),layout='constrained')
colors={16:'#4477AA',32:'#228833',64:'#AA3377'}
for n,color in colors.items():
 rows=[r for r in pairs if r['n']==n];q=[next(x for x in r['curves'] if x['beta']==20) for r in rows]
 axes[0].scatter([x['standard_tv_bound'] for x in q],[x['balanced_tv_bound'] for x in q],c=color,label=f'n={n}',s=28)
axes[0].plot([0,1],[0,1],'--',c='gray',lw=1);axes[0].axhline(.25,c='gray',ls=':',lw=1);axes[0].axvline(.25,c='gray',ls=':',lw=1)
axes[0].set(xlabel='Ordinary compiler: readout TV upper bound',ylabel='Balanced compiler: readout TV upper bound',title='Original-error certificate, beta=20',xlim=(-.03,1.03),ylim=(-.03,1.03));axes[0].legend(fontsize=8)
a=json.loads((OUT/'anneal_standard_summary.json').read_text());b=json.loads((OUT/'anneal_summary.json').read_text());n16=[r for r in pairs if r['n']==16]
ref=[next(x for x in r['curves'] if x['beta']==20) for r in n16]
eq=[np.mean([r['standard_exact']['original_optimum_probability'] for r in ref]),np.mean([r['balanced_exact']['original_optimum_probability'] for r in ref])]
sim=[np.mean([r['variants']['before']['results'][-1]['optimal']['rate'] for r in a['records'] if r['n']==16]),np.mean([r['variants']['before']['results'][-1]['optimal']['rate'] for r in b['records'] if r['n']==16])]
axes[1].bar([0,1,2.3,3.3],100*np.array(eq+sim),color=['#4477AA','#EE6677','#4477AA','#EE6677'])
axes[1].set(xticks=[.5,2.8],xticklabels=['Terminal Gibbs\nlogical reference','Finite classical anneal\nn x 10000 updates'],ylabel='Original-error optimum probability (%)',title='n=16: endpoint benefit fails in finite work')
for x,y in zip([0,1,2.3,3.3],100*np.array(eq+sim)):axes[1].text(x,y+.12,f'{y:.2f}',ha='center',fontsize=8)
axes[1].plot([],[],color='#4477AA',lw=6,label='ordinary');axes[1].plot([],[],color='#EE6677',lw=6,label='balanced');axes[1].legend(fontsize=8)
for scheme,src,color in [('ordinary',a,'#4477AA'),('balanced',b,'#EE6677')]:
 for variant,ls in [('before','-'),('after','--')]:
  rows=[r for r in src['records'] if r['n']==16];rates=[np.mean([r['variants'][variant]['results'][j]['feasible']['rate'] for r in rows]) for j in range(3)]
  axes[2].plot([100,1000,10000],rates,ls=ls,marker='o',c=color,label=f'{scheme}, '+('original chains' if variant=='before' else 'relaxed chains'))
axes[2].set(xscale='log',xlabel='Classical attempted updates / original variable',ylabel='Original-error syndrome feasibility',title='Conditional equilibrium is not a runtime theorem',ylim=(0,.7));axes[2].legend(fontsize=6.9)
for ax in axes:ax.grid(alpha=.13)
fig.savefig(FIG/'original_error_and_dynamics.png',dpi=180);fig.savefig(FIG/'original_error_and_dynamics.pdf')
print(FIG/'original_error_and_dynamics.png')
