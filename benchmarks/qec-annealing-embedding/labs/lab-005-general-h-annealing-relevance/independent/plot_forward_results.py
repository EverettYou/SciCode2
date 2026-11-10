from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
LAB=Path(__file__).resolve().parents[1]
def main():
 d=json.loads((LAB/'results/certified_mapping_summary.json').read_text());a=d['summary']['balanced'];times=sorted(map(float,a));balanced=[a[str(t)]['strict_qubit_reductions'] for t in times];standard=[d['summary']['standard'][str(t)]['strict_qubit_reductions'] for t in times]
 fig,axes=plt.subplots(1,2,figsize=(10,4.2),layout='constrained');ax=axes[0];ax.plot(times,balanced,'o-',color='#176179',label='Balanced compiler (23 inputs)');ax.plot(times,standard,'s--',color='#b85c38',label='Standard compiler (24 inputs)')
 ax.axvline(d['primary_T'],color='#999999',lw=.8,ls=':');ax.set_xscale('log',base=2);ax.set_xticks(times);ax.set_xticklabels([f'1/{round(1/t)}' for t in times],rotation=45);ax.set_ylim(-.5,17);ax.set_yticks([0,3,6,9,12,15]);ax.set_ylabel('Strictly smaller mappings with proved success gain');ax.set_xlabel('Common dimensionless quantum-forward duration T');ax.set_title('Actual original-optimum event certificates');ax.legend(fontsize=8,loc='upper right');ax.grid(axis='y',alpha=.2)
 global_=json.loads((LAB/'results/forward_ordinary_summary.json').read_text());word=json.loads((LAB/'theory_extensions/results/word_summary.json').read_text());event=json.loads((LAB/'results/event_fourth_summary.json').read_text());values=[global_['certified_duration_median'],word['median_duration'],event['median_duration']];ax=axes[1];bars=ax.bar(['Global norm','Word bound','Exact T4 + word'],values,color=['#b6c9cf','#7197a6','#176179']);ax.set_yscale('log');ax.set_ylim(1e-6,.03);ax.set_ylabel('Median largest certified menu duration');ax.set_title('Same 45/48 ordinary programming comparisons');ax.grid(axis='y',alpha=.2)
 for bar,v in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,v*1.18,f'{v:.3g}',ha='center',fontsize=9)
 fig.suptitle('General-H quantum theory: a certified early-time loop, with tiny guaranteed gains',fontsize=11);fig.savefig(LAB/'figures/quantum_event_certificates.png',dpi=180);plt.close(fig)
if __name__=='__main__':main()
