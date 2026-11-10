"""Exact, checked L=3 example and local illustrations for the path proof."""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures' / 'path-explainer'
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font_manager.fontManager.addfont(FONT)
plt.rcParams.update({'font.family': font_manager.FontProperties(fname=FONT).get_name(),
                     'font.size': 13, 'axes.unicode_minus': False,
                     'mathtext.fontset': 'dejavusans'})
RED, BLUE, PURPLE, GRAY = '#bf3c36', '#2469a8', '#8256aa', '#d3d6d9'
INK, ORANGE = '#22252a', '#b66a15'

L = 3
edges = []
for j in range(1, L):
    for i in range(2*L-1):
        edges.append(((i,j),(i+1,j)))
for j in range(L):
    for i in range(2*L):
        if (i+j)%2 == 0:
            edges.append(((i,j),(i,j+1)))
edges = tuple(sorted(edges))
vertices = sorted({v for e in edges for v in e})
detectors = [v for v in vertices if 0<v[1]<L]
pos = {v:(math.sqrt(3)*v[0]/2, 1.5*v[1]+.25*(-1)**sum(v)) for v in vertices}
nodes = [(0,0),(0,1),(1,1),(1,2),(0,2),(0,3)]
path_edges = [tuple(sorted((a,b))) for a,b in zip(nodes,nodes[1:])]
x_bits, c_bits = [1,1,0,1,0], [0,0,1,0,1]
x = {e:b for e,b in zip(path_edges,x_bits) if b}
c = {e:b for e,b in zip(path_edges,c_bits) if b}
D = {e:1 for e in path_edges}
def count(state,v): return sum(state.get(e,0) for e in edges if v in e)
nx = {v:count(x,v) for v in detectors}
nc = {v:count(c,v) for v in detectors}
M = {v:0 for v in detectors}
M.update({v:m for v,m in zip(nodes[1:-1],[0,1,1,1])})
assert len(edges)==19 and len(path_edges)==5
assert all(nx[v]%2==nc[v]%2 for v in detectors)
assert all(nc[v] in (M[v],M[v]+2) for v in detectors)
assert [nx[v] for v in nodes[1:-1]]==[2,1,1,1]
assert [nc[v] for v in nodes[1:-1]]==[0,1,1,1]
top = {e for e in edges if any(v[1]==L for v in e)}
ell_x = sum(x.get(e,0) for e in top)%2
ell_c = sum(c.get(e,0) for e in top)%2
assert (ell_x,ell_c)==(0,1)
assert not any(all(int(v in e)%2==nx[v]%2 for v in detectors) for e in edges)

def line(ax, a,b,color,lw=1.1,arrow=False):
    pa,pb=pos[a],pos[b]
    if arrow:
        ax.annotate('',xy=pb,xytext=pa,
                    arrowprops={'arrowstyle':'-|>','mutation_scale':18,
                                'lw':lw,'color':color,'shrinkA':6,'shrinkB':6},zorder=3)
    else:
        ax.plot([pa[0],pb[0]],[pa[1],pb[1]],color=color,lw=lw,zorder=2,
                solid_capstyle='round')

fig,axes=plt.subplots(1,3,figsize=(14.2,7.0))
panels=[(x,RED,'(a) 真实 error x','沿 P 的真实状态：1 1 0 1 0',
         r'$(n_x(v_1),\ldots,n_x(v_4))=(2,1,1,1)$'+'\n'+r'$\ell(x)=0$'),
        (c,BLUE,'(b) 辅助 decoder 的 correction c','沿 P 的纠正状态：0 0 1 0 1',
         r'$(n_c(v_1),\ldots,n_c(v_4))=(0,1,1,1)$'+'\n'+r'$\ell(c)=1$'),
        (D,PURPLE,r'(c) 差分 $D=x\oplus c$','沿 P 的差分状态：1 1 1 1 1',
         r'$P\subseteq D,\quad d=5=2L-1$'+'\n'+'贯穿两个未测边界：逻辑失败')]
for ax,(state,color,title,pattern,details) in zip(axes,panels):
    for a,b in edges: line(ax,a,b,GRAY)
    for e in state:
        if state is x:
            idx=path_edges.index(e)
            line(ax,nodes[idx],nodes[idx+1],color,3.5,True)
        else:line(ax,*e,color,3.5)
    for v in vertices:
        boundary=v[1] in (0,L)
        s=count(state,v)%2 if not boundary else 0
        ax.scatter(*pos[v],s=65 if boundary else 47,
                   facecolor='white' if boundary or not s else INK,
                   edgecolor=INK if not boundary else '#80868d',linewidth=1.1,zorder=5)
    for k,v in enumerate(nodes[1:-1],1):
        px,py=pos[v]
        ax.text(px-.23,py+.02,rf'$v_{k}$',ha='right',va='center',fontsize=13,
                color=ORANGE if k==1 else INK)
    if state is D:
        for k,(a,b) in enumerate(zip(nodes,nodes[1:]),1):
            pa,pb=pos[a],pos[b]
            ax.text((pa[0]+pb[0])/2-.28,(pa[1]+pb[1])/2,
                    rf'$e_{k}$',ha='right',va='center',fontsize=11,color=PURPLE)
    ax.text(2.2,4.55,'上方 rough boundary：没有 detector',ha='center',fontsize=11)
    ax.text(2.2,-.1,'下方 rough boundary：没有 detector',ha='center',fontsize=11)
    ax.text(2.2,-.65,pattern,ha='center',fontsize=12,color=color)
    ax.text(2.2,-1.15,details,ha='center',va='top',fontsize=12,linespacing=1.7)
    ax.set_title(title,fontsize=15,pad=13)
    ax.set_xlim(-1.0,5.15);ax.set_ylim(-1.9,4.9);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('同一个例子中的三个对象：真实边、纠正边、差分路径',fontsize=18,y=.98)
legend=[Line2D([],[],marker='o',linestyle='',color=INK,markerfacecolor=INK,label='实心 detector：syndrome = 1'),
        Line2D([],[],marker='o',linestyle='',color=INK,markerfacecolor='white',label='空心 detector：syndrome = 0')]
fig.legend(handles=legend,loc='lower center',bbox_to_anchor=(.5,.055),ncol=2,frameon=False,fontsize=12)
fig.text(.5,.015,'(a)、(b) 的 syndrome 完全相同；箭头端点收到 V，另一端收到 V̄。correction 只画二元边集合。',
         ha='center',fontsize=11)
fig.subplots_adjust(left=.025,right=.99,top=.87,bottom=.19,wspace=.13)
fig.savefig(OUT/'truth-correction-difference.png',dpi=165,facecolor='white')
plt.close(fig)

def star(ax,cx,cy,bits,color,orient=False,signs=None):
    center=(cx,cy)
    tips=[(cx-1.0,cy-.55),(cx+1.0,cy-.55),(cx,cy+1.0)]
    for k,(tip,b) in enumerate(zip(tips,bits)):
        if b:
            if orient:
                incoming=signs[k]==1
                ax.annotate('',xy=center if incoming else tip,xytext=tip if incoming else center,
                            arrowprops={'arrowstyle':'-|>','mutation_scale':16,'lw':3,'color':color,
                                        'shrinkA':5,'shrinkB':7},zorder=3)
                if k==0:loc=(cx-.57,cy-.05)
                elif k==1:loc=(cx+.57,cy-.05)
                else:loc=(cx+.23,cy+.57)
                ax.text(*loc,'V' if incoming else 'V̄',fontsize=13,ha='center',color=color)
            else:
                ax.plot([cx,tip[0]],[cy,tip[1]],color=color,lw=3,zorder=2)
        else:ax.plot([cx,tip[0]],[cy,tip[1]],color=GRAY,lw=1.3,zorder=1)
        ax.scatter(*tip,s=25,facecolor='white',edgecolor='#999999',zorder=4)
    ax.scatter(cx,cy,s=160,facecolor='white',edgecolor=INK,zorder=5)
    ax.text(cx,cy,'v',ha='center',va='center',fontsize=12,zorder=6)
    ax.text(cx,cy+1.15,f'第三条边 h={bits[2]}',ha='center',fontsize=11)

rows=[([1,1,0],[0,0,0],[1,-1,0],2,0,0,'11 → 00：必须隐藏一对 arrivals',
       'O1：相反 arrivals 给 q=0\nO2：还必须观测 singlet\n给定 V、V̄，概率为 1/N²'),
      ([0,1,0],[1,0,0],[0,1,0],1,1,1,'01 → 10：数量不变',
       '真实只有一次 arrival\ncorrection 也选一条边\n不要求出现隐藏事件'),
      ([0,0,0],[1,1,0],[0,0,0],0,2,0,'00 → 11：候选多选两条边',
       '真实背景为空，M=0\n数量约束允许 correction 选两条\n这里没有真实 pair 被隐藏'),
      ([1,1,1],[0,0,1],[1,-1,1],3,1,1,'11 → 00，且 h=1：三次看起来像一次',
       '图示真实输入：V、V、V̄\nO1：q=1，与单次 arrival 相同\nO2：需观测 V，概率为 2/N²')]
fig,axes=plt.subplots(4,1,figsize=(13.8,11.4))
for ax,(xb,cb,signs,xx,cc,mm,title,detail) in zip(axes,rows):
    star(ax,1.75,.15,xb,RED,True,signs)
    star(ax,5.35,.15,cb,BLUE)
    ax.text(1.75,-.82,rf'$n_x(v)={xx}$',ha='center',fontsize=16,color=RED)
    ax.text(5.35,-.82,rf'$n_c(v)={cc}$',ha='center',fontsize=16,color=BLUE)
    ax.annotate('',xy=(3.8,.13),xytext=(3.15,.13),arrowprops={'arrowstyle':'->','color':'#888888','lw':1.2})
    ax.text(7.4,1.0,title,fontsize=14,color=INK,va='top')
    ax.text(7.4,.55,rf'$M_v={mm},\quad n_c\in\{{M_v,M_v+2\}}$',fontsize=13,color=ORANGE)
    ax.text(7.4,.17,detail,fontsize=12,va='top',linespacing=1.55)
    ax.set_xlim(.2,13.0);ax.set_ylim(-1.08,1.72);ax.set_aspect('equal');ax.axis('off')
fig.suptitle('放大一个路径顶点：两条路径边翻转，第三条边保持不变',fontsize=18,y=.985)
fig.text(.245,.942,'真实 error x（红箭头）',ha='center',fontsize=14,color=RED)
fig.text(.502,.942,'correction c（蓝边）',ha='center',fontsize=14,color=BLUE)
fig.text(.5,.015,'M 值由真实观测确定。以上 O2 概率针对所示 mixed 输入、N≥3；图示不是每个样本都必然得到的 readout。',ha='center',fontsize=11)
fig.subplots_adjust(left=.025,right=.99,top=.915,bottom=.045,hspace=.11)
fig.savefig(OUT/'local-hidden-pair.png',dpi=160,facecolor='white')
plt.close(fig)

evidence={'L':L,'path_nodes':nodes,'true_bits':x_bits,'correction_bits':c_bits,
          'path_difference_bits':[1]*5,'true_counts':[nx[v] for v in nodes[1:-1]],
          'correction_counts':[nc[v] for v in nodes[1:-1]],'M':[M[v] for v in nodes[1:-1]],
          'syndrome':[nx[v]%2 for v in nodes[1:-1]],'ell_true':ell_x,'ell_correction':ell_c,
          'O2_record':['singlet','V','Vbar','V'], 'minimum_correction_cardinality':2,
          'purpose':'exact illustrative configuration, not a new phase-diagram experiment'}
(OUT/'checked-example.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
print(OUT/'truth-correction-difference.png')
print(OUT/'local-hidden-pair.png')
