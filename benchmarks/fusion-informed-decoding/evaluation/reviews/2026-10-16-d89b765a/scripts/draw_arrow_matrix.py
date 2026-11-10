"""Illustrate binary occupancy, latent orientation, and every local F entry."""
from pathlib import Path
from itertools import product
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures' / 'path-explainer'
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
font_manager.fontManager.addfont(FONT)
plt.rcParams.update({'font.family': font_manager.FontProperties(fname=FONT).get_name(),
                     'font.size': 16, 'mathtext.fontset': 'dejavusans',
                     'axes.unicode_minus': False})
RED, BLUE, INK, GRAY = '#bf3c36', '#2469a8', '#22252a', '#cbd0d5'

def arrow(ax, start, end, color=RED, width=3):
    ax.annotate('', xy=end, xytext=start,
                arrowprops={'arrowstyle':'-|>', 'mutation_scale':23,
                            'lw':width, 'color':color, 'shrinkA':8, 'shrinkB':8},
                zorder=3)

def node(ax, xy, central=False):
    ax.scatter(*xy, s=135 if central else 70, facecolor='white', edgecolor=INK,
               linewidth=1.4, zorder=5)

# Three microscopic states project to two occupancy states.
fig, axes = plt.subplots(1, 3, figsize=(11.8, 5.3))
for ax, state in zip(axes, [0, 1, -1]):
    left, right = (-1.0, .45), (1.0, .45)
    active = state != 0
    if active:
        arrow(ax, left if state == 1 else right, right if state == 1 else left)
    else:
        ax.plot([-1, 1], [.45, .45], color=GRAY, lw=1.2)
    node(ax, left); node(ax, right)
    ax.text(-1, .05, r'$v_{i-1}$', ha='center', fontsize=18)
    ax.text(1, .05, r'$v_i$', ha='center', fontsize=18)
    ax.text(0, .02, r'$e_i$', ha='center', fontsize=18)
    if active:
        labels = (r'$\bar V$', '$V$') if state == 1 else ('$V$', r'$\bar V$')
        for x, label in zip([-1, 1], labels):
            ax.text(x, .83, label, ha='center', color=RED, fontsize=22)
        title = r'$x_{e_i}=1,\ \sigma_i=+$' if state == 1 else r'$x_{e_i}=1,\ \sigma_i=-$'
        chance = r'微观概率 $p/2$'
    else:
        title = r'$x_{e_i}=0$'
        chance = r'微观概率 $1-p$'
        ax.text(0, .86, '没有 arrivals；不定义取向', ha='center', fontsize=14)
    ax.set_title(title, fontsize=20, pad=20)
    ax.text(0, -.38, chance, ha='center', fontsize=16)
    ax.annotate('', xy=(0, -1.02), xytext=(0, -.62),
                arrowprops={'arrowstyle':'->', 'color':'#777777', 'lw':1.4})
    if active:
        ax.plot([-1, 1], [-1.2, -1.2], color=BLUE, lw=3)
    else:
        ax.plot([-1, 1], [-1.2, -1.2], color=GRAY, lw=1.2)
    node(ax, (-1, -1.2)); node(ax, (1, -1.2))
    ax.text(0, -1.63, r'只保留 binary：$x_e=1$' if active else r'只保留 binary：$x_e=0$',
            ha='center', fontsize=17, color=BLUE)
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.85, 1.17)
    ax.axis('off')
fig.suptitle('同一条 active 边有两种隐藏取向；x 和 c 仍然只有占据 / 不占据',
             fontsize=20, y=.985)
fig.text(.5, .89, r'路径的参考顺序：$v_{i-1}\ \longrightarrow\ v_i$；箭头端收到 V，另一端收到 V̄',
         ha='center', fontsize=16)
fig.text(.5, .018, '箭头只标记 V 在哪一端；不表示粒子运动，也不赋予 correction 一个方向。',
         ha='center', fontsize=15)
fig.subplots_adjust(left=.03, right=.99, top=.75, bottom=.11, wspace=.14)
fig.savefig(OUT / 'binary-and-orientation.png', dpi=170, facecolor='white')
plt.close(fig)

def center_arrivals(a, b):
    return a, -b

def local_probability(a, b, side, N=5):
    arrivals = list(center_arrivals(a, b)) + ([side] if side else [])
    if not side:
        return (1/N**2) if sum(arrivals) == 0 else 0
    return (2/N**2) if abs(sum(arrivals)) == 1 else 0

for side in [0, 1]:
    fig, axes = plt.subplots(2, 2, figsize=(11.4, 8.6))
    for (row, a), (col, b) in product(enumerate([1, -1]), repeat=2):
        ax = axes[row, col]
        left, center, right = (-1.45, .1), (0, .1), (1.45, .1)
        arrow(ax, left if a == 1 else center, center if a == 1 else left)
        arrow(ax, center if b == 1 else right, right if b == 1 else center)
        if side:
            arrow(ax, (0, 1.13), center)
            node(ax, (0, 1.13))
            ax.text(.25, .78, '$V$', color=RED, fontsize=19)
        else:
            ax.plot([0, 0], [.1, 1.13], lw=1.1, color=GRAY)
            node(ax, (0, 1.13))
        node(ax, left); node(ax, center, True); node(ax, right)
        ax.text(0, -.22, '$v_i$', ha='center', fontsize=18)
        ax.text(-.83, -.22, '$e_i$', ha='center', fontsize=18)
        ax.text(.83, -.22, '$e_{i+1}$', ha='center', fontsize=18)
        vals = center_arrivals(a, b)
        for x, value in zip([-.58, .58], vals):
            ax.text(x, .39, '$V$' if value == 1 else r'$\bar V$',
                    color=RED, fontsize=20, ha='center')
        composition = list(vals) + ([side] if side else [])
        count_v, count_bar = composition.count(1), composition.count(-1)
        pair = ('+' if a == 1 else '-') + ('+' if b == 1 else '-')
        prob = local_probability(a, b, side)
        ax.set_title(r'$F_{'+pair+r'}$：' + ('+' if a == 1 else '−') + ' → ' +
                     ('+' if b == 1 else '−'), fontsize=21, pad=14)
        ax.text(0, -.70, rf'中心收到：$a={count_v},\ b={count_bar}$',
                ha='center', fontsize=17)
        if prob:
            target = 'singlet' if not side else ('V' if count_v == 2 else 'V̄')
            ax.text(0, -1.08, '隐藏所需 readout：' + target, ha='center', fontsize=16)
            value = r'$1/N^2$' if not side else r'$2/N^2$'
            ax.text(0, -1.47, r'$F_{'+pair+r'}=$' + value, ha='center',
                    fontsize=21, color=BLUE)
        else:
            ax.text(0, -1.08, '无法隐藏成' + ('零次 arrivals' if not side else '一次 arrival'),
                    ha='center', fontsize=16)
            ax.text(0, -1.47, r'$F_{'+pair+r'}=0$', ha='center', fontsize=21, color=INK)
        ax.set_xlim(-1.85, 1.85); ax.set_ylim(-1.68, 1.29)
        ax.axis('off')
    fig.suptitle('取向矩阵的四个元素：' + ('第三条边 inactive' if not side else '第三条边向中心提供 V'),
                 fontsize=21, y=.985)
    fig.text(.5, .932, r'行 = 左边取向 $\sigma_i$；列 = 右边取向 $\sigma_{i+1}$；参考路径从左到右',
             ha='center', fontsize=16)
    fig.text(.29, .867, r'列：$\sigma_{i+1}=+$', ha='center', fontsize=18, color=BLUE)
    fig.text(.75, .867, r'列：$\sigma_{i+1}=-$', ha='center', fontsize=18, color=BLUE)
    fig.text(.025, .70, r'行 $+$', ha='center', fontsize=17, color=BLUE, rotation=90)
    fig.text(.025, .32, r'行 $-$', ha='center', fontsize=17, color=BLUE, rotation=90)
    fig.text(.5, .035, r'这里固定两条路径边真实为 11、correction 为 00。O2，$N\geq5$。',
             ha='center', fontsize=15)
    fig.subplots_adjust(left=.08, right=.99, top=.80, bottom=.09, wspace=.15, hspace=.24)
    fig.savefig(OUT / ('orientation-matrix-side-V.png' if side else 'orientation-matrix-side-empty.png'),
                dpi=170, facecolor='white')
    plt.close(fig)

N = 5
assert [[local_probability(a,b,0,N) for b in [1,-1]] for a in [1,-1]] == [[1/N**2,0],[0,1/N**2]]
assert [[local_probability(a,b,1,N) for b in [1,-1]] for a in [1,-1]] == [[2/N**2,0],[2/N**2,2/N**2]]
joint = sum(local_probability(a,b,1,N)*local_probability(b,c,-1,N)
            for a,b,c in product([1,-1], repeat=3))/8
assert abs(joint - 5/(2*N**4)) < 1e-14
data = {'convention':'sigma=+ iff V at the forward endpoint along the selected path',
        'N_range':'N>=5', 'row_and_column_order':['+','-'],
        'F_side_empty_times_N_squared':[[1,0],[0,1]],
        'F_side_V_times_N_squared':[[2,0],[2,2]],
        'states':'microscopic absent / V-forward / V-backward; x,c binary',
        'correlation_check_N5':{'joint':joint,'independent_product':9/(4*N**4)}}
(OUT / 'arrow-matrix-checked.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
for name in ['binary-and-orientation.png','orientation-matrix-side-empty.png','orientation-matrix-side-V.png']:
    print(OUT/name)
