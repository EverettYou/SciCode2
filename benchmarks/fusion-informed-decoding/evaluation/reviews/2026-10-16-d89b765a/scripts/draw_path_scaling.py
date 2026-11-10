"""Plot the proof logic and its asymptotic size factor; no simulation data."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch
import numpy as np

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "figures" / "path-explainer"
OUT.mkdir(parents=True, exist_ok=True)
font_manager.fontManager.addfont("/Library/Fonts/Arial Unicode.ttf")
plt.rcParams.update({
    "font.family": "Arial Unicode MS",
    "mathtext.fontset": "dejavusans",
    "axes.unicode_minus": False,
    "font.size": 18,
    "savefig.facecolor": "#ffffff",
})

fig = plt.figure(figsize=(14.4, 15.8), facecolor="white")
gs = fig.add_gridspec(2, 1, height_ratios=[1.70, 1.0],
                      left=.075, right=.965, top=.955, bottom=.105, hspace=.22)
ax = fig.add_subplot(gs[0]); ax.set_axis_off()
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.text(0, 1.015, "A　失败路径如何给出一个证明", fontsize=26, weight="bold", va="bottom")

def box(y, height, color, lines):
    rect = FancyBboxPatch((.025, y), .95, height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        facecolor=color, edgecolor="#b4c3cf", linewidth=1.4)
    ax.add_patch(rect)
    n = len(lines)
    for j, (txt, size) in enumerate(lines):
        yy = y + height * (1 - (j + .55) / n)
        ax.text(.5, yy, txt, fontsize=size, ha="center", va="center", color="#173047")

def arrow(y1, y2):
    ax.annotate("", xy=(.5, y2), xytext=(.5, y1),
        arrowprops=dict(arrowstyle="-|>", color="#647c90", lw=2.1,
                        mutation_scale=20))

box(.815, .145, "#edf3fa", [
    ("辅助 decoder 的逻辑纠正失败", 22),
    (r"$\Longrightarrow\ D=x\oplus c$ 中存在贯穿路径 $P$，$d\geq 2L-1$", 21),
])
arrow(.798, .765)
box(.565, .185, "#eaf6f5", [
    ("固定一个候选路径 P，平均真实 error 与观测", 21),
    ("11 顶点须隐藏一对 arrivals；还须满足 decoder 选择条件", 19),
    (r"$\Pr(E_P)\leq A_N\,\rho_N(p)^d$", 24),
])
arrow(.549, .517)
box(.370, .132, "#fff6e7", [
    (r"长度 $d$ 的候选路径数 $\leq C_\epsilon L(\mu+\epsilon)^d$", 22),
    (r"$\mu=\sqrt{2+\sqrt{2}}\approx 1.847759$", 21),
])
arrow(.354, .321)
box(.105, .200, "#f0edf9", [
    ("对所有候选路径求和（union bound）", 21),
    (r"$R_{\rm aux}\leq C_{N,\epsilon}L\!\sum_{d\geq2L-1}r^d"
     r"=C_{N,\epsilon}L\,\frac{r^{2L-1}}{1-r}$", 24),
    (r"$r=(\mu+\epsilon)\rho_N(p)<1$，则上界随 $L\to\infty$ 趋于零", 20),
])
ax.text(.5, .035, r"$0\leq R^*_{\rm optimal}\leq R_{\rm aux}\longrightarrow0$",
        fontsize=25, ha="center", va="center", color="#173047")

bx = fig.add_subplot(gs[1])
bx.set_title("B　几何级数中的尺寸因子为什么最终下降", loc="left", fontsize=25, pad=19, weight="bold")
Ls = np.arange(2, 121)
for r, color in [(.85, "#007c91"), (.95, "#e49b25"), (.98, "#9b547c")]:
    bx.plot(Ls, Ls * r ** (2 * Ls - 1), lw=3.2, color=color,
            label=fr"$r={r:.2f}$")
bx.set_yscale("log")
bx.set_ylim(8e-16, 30)
bx.set_xlim(2, 120)
bx.set_xlabel(r"系统尺寸 $L$", fontsize=21)
bx.set_ylabel(r"$F(L)=Lr^{2L-1}$", fontsize=22)
bx.grid(axis="y", which="major", color="#dbe2e8", lw=.8)
bx.spines[["top", "right"]].set_visible(False)
bx.tick_params(labelsize=17)
bx.legend(loc="lower left", fontsize=20, frameon=True, facecolor="white", edgecolor="#cbd5dd")
bx.text(.98, .52, "r 越接近 1，\n下降所需的尺寸越大。\n有限尺寸甚至可先上升。",
        transform=bx.transAxes, ha="right", va="center", fontsize=18,
        bbox=dict(boxstyle="round,pad=.55", facecolor="#f6f8fb", edgecolor="#d7dfe7"))
fig.text(.52, .022, "尺寸因子，不是模拟错误率；未乘常数和 1/(1−r)。", ha="center",
         fontsize=20, color="#924133", weight="bold")

fig.savefig(OUT / "proof-scaling.png", dpi=180)
plt.close(fig)
print(OUT / "proof-scaling.png")
