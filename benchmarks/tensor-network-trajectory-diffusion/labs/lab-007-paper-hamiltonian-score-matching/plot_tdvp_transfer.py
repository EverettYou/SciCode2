"""Regenerate the repair / frozen-transfer figure from saved numeric artifacts."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
LAB=Path(__file__).resolve().parent

def main():
    fig,axs=plt.subplots(1,3,figsize=(13,3.8),layout='constrained')
    audit=json.loads((LAB/'results/tdvp-gap-audit-64-v2/summary.json').read_text())['rollout']['backends']
    names=['legacy','dense','tdvp']; labels=['Legacy','Dense','Corrected TDVP']
    vals=[np.array(audit[n]['fidelity']) for n in names]
    axs[0].bar(labels,[v.mean() for v in vals],yerr=[v.std(ddof=1)/len(v)**.5 for v in vals],color=['#c95e53','#888888','#227c9d'],capsize=4)
    axs[0].set(ylim=(0,1),ylabel='Full-state fidelity',title='Frozen five-qubit checkpoint')
    axs[0].tick_params(axis='x',rotation=15)
    for tag,title,color in [('shared-cluster-transfer-v2','Train N=3','#c95e53'),('shared-cluster-n5-transfer-v2','Train N=5','#227c9d')]:
        path=LAB/'results'/tag/'summary.json'
        if not path.exists(): continue
        rows=json.loads(path.read_text())['rows']
        extra=LAB/'results/shared-cluster-large-transfer-v2/summary.json'
        if title=='Train N=5' and extra.exists(): rows+=json.loads(extra.read_text())['rows']
        for chi,style in [(2,'--'),(4,'-')]:
            data=[r for r in rows if r.get('chi')==chi and r.get('substeps')==1]
            axs[1].errorbar([r['n'] for r in data],[r['mean_fidelity'] for r in data],yerr=[r['fidelity_sem'] for r in data],fmt='o'+style,color=color,label=f'{title}, χ={chi}',capsize=2)
        data=[r for r in rows if r.get('chi')==4 and r.get('substeps')==1]
        axs[2].plot([r['n'] for r in data],[r['reverse_seconds'] for r in data],'o-',color=color,label=title)
    axs[1].set(xlabel='Number of qubits',ylabel='Full-state fidelity',ylim=(0,1.03),title='Frozen shared-controller transfer')
    axs[1].legend(fontsize=8)
    axs[2].set(xlabel='Number of qubits',ylabel='Seconds / 16 trajectories',title='300-step MPS reverse, χ=4')
    axs[2].legend(fontsize=8)
    for ax in axs: ax.grid(axis='y',alpha=.2)
    out=LAB/'figures/tdvp-transfer-v2';out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/'repair-and-transfer.png',dpi=180);fig.savefig(out/'repair-and-transfer.pdf')
if __name__=='__main__':main()
