"""Phase diagram of the bilayer t-t'-J_perp model versus filling nu and temperature T.
Ingredients (approximations stated in REPORT.md):
 * T_MF(nu): Hartree-Fock-Bogoliubov (BCS) onset of interlayer s-wave pairing, V = 3J_perp/4, bare band,
             mu held at the normal-state value (as the STS of the nu~0.2 crystal implies). 600x600 k-grid.
 * T_theta(nu): Kosterlitz-Thouless temperature of hard-core rung pairs near the SMG insulator,
             T_KT = 0.686 t_b * 4x(1-x), x = |1-2nu| (empty or doubly filled rungs), t_b from ED / two-body.
 * nu = 1/2: incompressible rung-singlet (SMG) insulator; charge gap 8, spin gap 5.4.
 * T*(nu): crossover where rung-singlet (preformed-pair) correlations open the pseudogap.
"""
import numpy as np, json
from scipy.optimize import brentq
from common import kgrid, eps_c, save_json, FIG, RES, V_PAIR, T_NN, T_NNN
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

cx, cy = kgrid(600); e0 = eps_c(cx, cy); es = np.sort(e0)
nus = np.concatenate([np.linspace(0.01, 0.99, 99), [0.2, 0.3, 0.5]]); nus = np.unique(np.round(nus, 4))
TMF, D0, MU = [], [], []
for nu in nus:
    mu = es[int(nu * len(es))]
    xi = e0 - mu; x0 = np.where(np.abs(xi) < 1e-12, 1e-12, xi)
    f = lambda T: 1 - V_PAIR * np.mean(np.tanh(x0 / (2 * T)) / (2 * x0))
    TMF.append(brentq(f, 1e-3, 30))
    D0.append(brentq(lambda D: 1 - V_PAIR * np.mean(1 / (2 * np.sqrt(xi ** 2 + D ** 2))), 1e-4, 30))
    MU.append(mu)
TMF, D0, MU = map(np.array, (TMF, D0, MU))
# van Hove filling
nu_vhs = float(np.mean(e0 < 4 * T_NNN))

sc = json.load(open(f'{RES}/strong_coupling.json'))
tb_lo, tb_hi = sc['coherence_estimates']['tb_dense_2nd_order'], sc['coherence_estimates']['tb_dilute_curvature']
tb_c = sc['coherence_estimates']['tb_needed_for_measured_Tc0p3']
x = np.abs(1 - 2 * nus)
TKT = lambda tb: 0.686 * tb * 4 * x * (1 - x)

# boundary of the strongly correlated (doped-SMG / preformed-pair) regime: nu* from the vanishing of the
# normal-state transport gap E_rho(nu) (3.72 at nu=1/2, 0.90 at nu=0.3) -> nu* = 0.236; mirrored for nu>1/2
nustar = 0.5 - (0.5 - 0.3) * 3.72 / (3.72 - 0.90)
nustar_r = 1 - nustar
# T*: pseudogap crossover. Anchors: T*(0.3)=2.5+-0.35 (NMR), T*(1/2) ~ spin gap 5.4 (>4.4 from data),
# T* -> T_MF at nu*; piecewise-linear interpolation, symmetric about 1/2 in the strong-coupling region
def Tstar(nu):
    nu = np.asarray(nu); y = np.abs(nu - 0.5); ys = 0.5 - nustar
    Tm = np.interp(nustar, nus, TMF)
    return np.where(y <= ys, np.interp(y, [0, 0.2, ys], [5.4, 2.5, Tm]), np.nan)
def blend(nu, width=0.012):
    # weight of the strongly correlated (preformed-pair) regime: smooth steps at nu* and 1-nu*
    return 0.5 * (np.tanh((nu - nustar) / width) - np.tanh((nu - nustar_r) / width))
def Tc_of(nu, TMFv, TKTv):
    w = blend(nu)
    Tc = np.exp((1 - w) * np.log(TMFv) + w * np.log(np.maximum(np.minimum(TKTv, TMFv), 1e-6)))
    # dilute limit (E_F < pair binding 0.33, nu < ~0.02 or > ~0.98): T_c -> 0 linearly
    return Tc * np.clip(np.minimum(nu, 1 - nu) / 0.03, 0, 1)
Tc = Tc_of(nus, TMF, TKT(tb_c))

out = dict(nu=nus, T_MF=TMF, Delta0_MF=D0, mu=MU, nu_vHs=nu_vhs, nu_star=nustar, nu_star_right=nustar_r,
           T_KT_band=[TKT(tb_lo), TKT(tb_hi)], T_KT_central=TKT(tb_c), Tc=Tc,
           checks={'T_MF(0.2)': float(np.interp(0.2, nus, TMF)), 'T_MF(0.3)': float(np.interp(0.3, nus, TMF)),
                   'Delta0(0.2)': float(np.interp(0.2, nus, D0)), 'T_KT(0.3) range': [float(np.interp(0.3, nus, TKT(tb_lo))), float(np.interp(0.3, nus, TKT(tb_hi)))]})
save_json(out, 'phase_diagram.json')

# ------------------- figure -------------------
fig, ax = plt.subplots(figsize=(11, 7))
nn = np.linspace(0.005, 0.995, 600)
TMFi = np.interp(nn, nus, TMF); TKTc = np.interp(nn, nus, TKT(tb_c))
TKTlo = np.interp(nn, nus, TKT(tb_lo)); TKThi = np.interp(nn, nus, TKT(tb_hi))
strong = (nn > nustar) & (nn < nustar_r)
Tci = Tc_of(nn, TMFi, TKTc)
Ts = Tstar(nn)
# metal background
ax.fill_between(nn, 0, 6.5, color='#f3f3f3', zorder=0)
# pseudogap region
ax.fill_between(nn, np.where(strong, Tci, np.nan), np.where(strong, Ts, np.nan), color='#f6d7b0', zorder=1)
# SC
ax.fill_between(nn, 0, Tci, color='#9ecae1', zorder=2)
ax.plot(nn, Tci, color='#08519c', lw=2.2, zorder=4, label=r'$T_c$ (superconducting transition)')
ax.fill_between(nn[strong], TKTlo[strong], np.minimum(TKThi[strong], TMFi[strong]), color='#08519c', alpha=0.18, zorder=3,
                label=r'$T_\theta$ band: rung-pair coherence, $t_b=0.30$–$0.58$')
ax.plot(nn, TMFi, color='#3182bd', lw=1.2, ls='--', zorder=4, label=r'$T_{\rm MF}$: HFB pairing onset ($V=3J_\perp/4=6$)')
ax.plot(nn, Ts, color='#d94801', lw=1.8, ls='-.', zorder=4, label=r'$T^*$: rung-singlet pseudogap crossover')
# SMG insulator at nu = 1/2
ax.plot([0.5, 0.5], [0, 5.4], color='#a50f15', lw=6, solid_capstyle='butt', zorder=5)
ax.text(0.505, 3.3, 'SMG\n(rung-singlet)\ninsulator', color='#a50f15', fontsize=10, va='center', zorder=6)
# crystals
for nu0, lab in [(0.2, r'$\nu\approx0.2$'), (0.3, r'$\nu\approx0.3$'), (0.5, r'$\nu=1/2$')]:
    ax.axvline(nu0, color='k', lw=1.0, ls=':', zorder=6)
    ax.text(nu0, 6.25, lab, ha='center', fontsize=10, zorder=7, bbox=dict(fc='w', ec='none', alpha=0.8))
# data points
ax.errorbar([0.2], [1.1125], yerr=[[0.0375], [0.0375]], fmt='s', color='k', ms=6, zorder=8, label='data: $T_c$ (resistivity)')
ax.errorbar([0.3], [0.3625], yerr=[[0.0375], [0.0375]], fmt='s', color='k', ms=6, zorder=8)
ax.errorbar([0.3], [2.5], yerr=[[0.35], [0.35]], fmt='D', color='#d94801', mec='k', ms=6, zorder=8, label=r'data: $T^*$ (onset of $1/T_1T$ drop)')
ax.annotate('', xy=(0.5, 4.9), xytext=(0.5, 4.4), arrowprops=dict(arrowstyle='->', color='k'), zorder=8)
ax.plot([0.5], [4.4], 'k^', ms=7, zorder=8, label='data: activated up to $T\\geq4.4$')
ax.text(0.09, 0.45, 'SC\n(interlayer s-wave)', fontsize=10, color='#08306b', zorder=7)
ax.text(0.78, 0.55, 'SC', fontsize=10, color='#08306b', zorder=7)
ax.text(0.04, 2.3, 'metal\n(Fermi liquid;\nbare $t$-$t\'$ band)', fontsize=10, color='0.25', zorder=7)
ax.text(0.86, 2.3, 'metal', fontsize=10, color='0.25', zorder=7)
ax.plot([0.3], [1.236], marker='o', mfc='w', mec='#3182bd', ms=7, zorder=8)
ax.annotate('pairing amplitude at $k_F$\n(HS bump in $1/T_1T$ near $T\\approx0.9$)', xy=(0.3, 1.236), xytext=(0.115, 1.75),
            fontsize=8, color='#08519c', arrowprops=dict(arrowstyle='->', color='#08519c'), zorder=8)
ax.text(0.505, 5.55, 'incoherent metal (above crossover)', fontsize=8, color='0.3', zorder=7)
ax.text(0.33, 1.25, 'pseudogap:\npreformed rung\npairs (spin gap,\nincoherent charge)', fontsize=9, color='#8c2d04', zorder=7)
ax.text(0.585, 1.25, 'pseudogap', fontsize=9, color='#8c2d04', zorder=7)
ax.set_xlim(0, 1); ax.set_ylim(0, 6.5)
ax.set_xlabel(r'filling fraction $\nu$  ($\nu=1$: two electrons per transition-metal site)', fontsize=11)
ax.set_ylabel(r'temperature $T/D$', fontsize=11)
ax.set_title(r"Bilayer $t$-$t'$-$J_\perp$ model ($t=1$, $t'=0.195$, $J_\perp=8$, $U=0$): phase diagram", fontsize=12)
h, l = ax.get_legend_handles_labels()
h += [Patch(color='#9ecae1'), Patch(color='#f6d7b0'), Patch(color='#f3f3f3')]
l += ['superconductor', 'pseudogap crossover regime', 'metal']
ax.legend(h, l, fontsize=8, loc='upper right', bbox_to_anchor=(1.0, 0.93), framealpha=0.92)
fig.tight_layout(); fig.savefig(f'{FIG}/fig3_phase_diagram.png', dpi=150)
print(json.dumps(out['checks'], indent=1), 'nu*=%.3f nu_vHs=%.3f' % (nustar, nu_vhs))
for nu0 in [0.05, 0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 0.95]:
    print('nu=%.2f T_MF=%.3f Delta0=%.3f Tc=%.3f' % (nu0, np.interp(nu0, nus, TMF), np.interp(nu0, nus, D0), np.interp(nu0, nus, Tc)))
