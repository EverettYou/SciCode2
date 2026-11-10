from pathlib import Path
import csv,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle,Patch
ROOT=Path(__file__).resolve().parent
font='/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font_manager.fontManager.addfont(font)
plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                     'font.size':13,'axes.unicode_minus':False})
data=list(csv.DictReader((ROOT/'reference-bounds.csv').open()))
fig,axes=plt.subplots(1,3,figsize=(13.6,5.2),sharey=True)
blue,orange,gray='#2469a8','#b66a15','#eef0f2'
bc=(1-2*math.sin(math.pi/18))/2
for ax,r in zip(axes,['O0','O1','O2']):
    rows=[x for x in data if x['record']==r]
    for row in rows:
        n=int(row['N']);a=float(row['proved_low_closed']);b=float(row['proved_high_closed'])
        ax.add_patch(Rectangle((0,n-.43),1,.86,facecolor=gray,hatch='///',edgecolor='#c5c9ce',lw=0))
        ax.add_patch(Rectangle((0,n-.43),a,.86,facecolor=blue,lw=0))
        ax.add_patch(Rectangle((b,n-.43),1-b,.86,facecolor=blue,lw=0))
        if r=='O0' or r=='O1' and n==2:
            ax.add_patch(Rectangle((bc,n-.43),1-2*bc,.86,facecolor=orange,lw=0))
    ax.set_xlim(0,1);ax.set_ylim(1.4,8.6)
    ax.set_xticks([0,.25,.5,.75,1]);ax.set_yticks(range(2,9))
    ax.set_xlabel('Noise probability p');ax.set_title(r,fontsize=17,pad=10)
    ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('N')
fig.suptitle('Conservative rigorous bounds in the reference answer, not full physical phase boundaries',fontsize=16,y=.97)
fig.legend(handles=[Patch(facecolor=blue,label='Proved decodable (sufficient region)'),
                    Patch(facecolor=orange,label='Proved nondecodable'),
                    Patch(facecolor=gray,hatch='///',edgecolor='#c5c9ce',label='Unresolved')],
           loc='lower center',bbox_to_anchor=(.5,.035),ncol=3,frameon=False,fontsize=13)
fig.text(.5,.012,'The all-p O2 theorem for N≥13 lies outside the plotted N=2,...,8 range; hatching does not mean nondecodable.',ha='center',fontsize=12)
fig.subplots_adjust(left=.065,right=.99,top=.83,bottom=.23,wspace=.12)
fig.savefig(ROOT/'reference-phase-diagram.png',dpi=180,facecolor='white')
print(ROOT/'reference-phase-diagram.png')
