"""Plot only phase information that is directly supported by the input data."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/layered-oxide-mpl')
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.facecolor':'white'})
COL = {'sc':'#285c91','metal':'#16817a','activated':'#c78328','unknown':'#e9edf1'}
fig, ax = plt.subplots(figsize=(11.1,5.8))
ax.set_facecolor('#f3f5f7')
ax.set_xlim(0,1); ax.set_ylim(0,4.15)
ax.text(.74,2.35,'Unmeasured fillings\nNo inferred phase boundaries',ha='center',va='center',
        fontsize=14,color='#677582',linespacing=1.6)
width=.046
def block(nu,lo,hi,col,hatch=None):
    ax.add_patch(Rectangle((nu-width/2,lo),width,hi-lo,facecolor=col,
                          hatch=hatch,edgecolor='white',linewidth=.6,zorder=2))
for nu in [.2,.3,.5]:
    ax.axvline(nu,color='#26374a',ls='--',lw=.9,zorder=4)
block(.2,.1,1.075,COL['sc']);block(.2,1.075,1.15,'#cad9e8','///')
block(.2,1.15,4,COL['metal'])
block(.3,.1,.325,COL['sc']);block(.3,.325,.4,'#cad9e8','///')
block(.3,.4,4,COL['activated'])
block(.5,.45,4,COL['activated'])
for nu,low in [(.2,.1),(.3,.1),(.5,.45)]:block(nu,0,low,'#dfe3e8','xxx')
ax.annotate(r'$1.075<T_c/D\leq1.150$',xy=(.2,1.1125),xytext=(.012,1.63),
            arrowprops={'arrowstyle':'-','color':'#344458'},fontsize=10,color='#243950')
ax.annotate(r'$0.325<T_c/D\leq0.400$',xy=(.3,.3625),xytext=(.34,.93),
            arrowprops={'arrowstyle':'-','color':'#344458'},fontsize=10,color='#243950')
ax.text(.5,2.7,'Activated transport',rotation=90,ha='center',va='center',color='white',fontsize=10,zorder=5)
ax.text(.3,2.4,'Activated normal state',rotation=90,ha='center',va='center',color='white',fontsize=10,zorder=5)
ax.text(.2,2.75,'Metallic transport',rotation=90,ha='center',va='center',color='white',fontsize=10,zorder=5)
ax.text(.5,.19,'?',ha='center',va='center',color='#465565',fontsize=14,zorder=5)
ax.set_xticks([0,.2,.3,.5,1],['0',r'$\simeq0.2$',r'$\simeq0.3$',r'$1/2$','1'])
ax.set_xlabel(r'Filling fraction $\nu$ (two electrons per site at $\nu=1$)')
ax.set_ylabel(r'Temperature $T/D$')
ax.set_title('Measurement-constrained state map',loc='left',fontsize=17,pad=25,weight='bold')
ax.text(0,1.025,'Colored strips show sampled compositions only; their width is not a filling uncertainty.',
        transform=ax.transAxes,fontsize=10,color='#556475')
legend=[Patch(facecolor=COL['sc'],label='Zero resistance: superconducting candidate'),
        Patch(facecolor=COL['metal'],label='Metallic slope'),
        Patch(facecolor=COL['activated'],label='Activated resistance'),
        Patch(facecolor='#dfe3e8',hatch='xxx',label='Below measured temperature')]
fig.legend(handles=legend,loc='lower center',ncol=2,frameon=False,bbox_to_anchor=(.52,.005),fontsize=10)
fig.subplots_adjust(left=.08,right=.97,bottom=.23,top=.85)
fig.savefig(ROOT/'figures/phase_constraints.png',dpi=220)
json.dump({'type':'measurement-constrained map, not a computed Hamiltonian phase diagram',
           'nu_0.2':{'rho_zero_T_range':[.1,1.075],'Tc_interval':[1.075,1.15],'positive_rho_metallic_T_range':[1.15,4]},
           'nu_0.3':{'rho_zero_T_range':[.1,.325],'Tc_interval':[.325,.4],'positive_rho_activated_T_range':[.4,4]},
           'nu_0.5':{'positive_rho_activated_T_range':[.45,4],'T_below_.45':'unmeasured'},
           'assumption':'Interpretation of zero resistance as superconductivity; no Meissner or phase-stiffness measurement supplied'},
          open(ROOT/'data/phase_constraints.json','w'),indent=2)
