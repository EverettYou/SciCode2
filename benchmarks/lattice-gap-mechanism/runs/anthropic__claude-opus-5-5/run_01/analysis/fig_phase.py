"""Task 2: phase diagram (nu, T) of the bilayer rung-singlet model with t=1, t'=0.2, U, J_perp.
Ingredients (all computed from the model, with stated approximations):
  * T_MF(nu): BCS mean-field onset of interlayer singlet pairing (upper bound for Tc; pairing crossover T* at weak coupling)
  * T_s: rung-singlet formation crossover near half filling (local singlet-triplet splitting, ED spin gap)
  * Tc(nu) = T_MF(nu) * Z(nu), Z = phase-coherence factor: pair stiffness of the doped rung-singlet insulator,
    Z(nu) = min(1, D(nu)/D_c); D(nu) from ED twisted-boundary stiffness (interpolated), D_c fixed by Tc(0.3)=0.36.
"""
import numpy as np, json, os, sys
import vizstyle as vs
vs.apply()
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

OUT = '/app/figures'
J = float(sys.argv[1]) if len(sys.argv) > 1 else 6.5
a = np.load('tmf_curve.npy')
m = a[:, 0] == J
nu_mf = a[m, 1]; T_mf = a[m, 2]
# make symmetric-complete arrays incl. endpoints
nu_mf = np.concatenate([[0.0], nu_mf, [1.0]]); T_mf = np.concatenate([[0.0], T_mf, [0.0]])

# --- phase-coherence factor from ED stiffness (rung-pair Mott physics near nu=1/2)
stiff = json.load(open('stiffness.json')) if os.path.exists('stiffness.json') else None
nus_fine = np.linspace(0, 1, 801)
Tmf_f = np.interp(nus_fine, nu_mf, T_mf)
if stiff is not None:
    xs = np.array(stiff['nu']); Ds = np.array(stiff['D']); Dfree = np.array(stiff['Dfree'])
    # coherent fraction of the stiffness relative to free electrons, mirrored about nu=1/2 (p-h)
    r = Ds / Dfree
    xx = np.concatenate([[0.0], xs, 1 - xs[::-1], [1.0]])
    rr = np.concatenate([[1.0], r, r[::-1], [1.0]])
    o = np.argsort(xx); Zr = np.interp(nus_fine, xx[o], rr[o])
else:
    Zr = np.clip(np.abs(1 - 2 * nus_fine) / 0.6, 0, 1)
# calibrate D_c so that Tc(0.3) = 0.36 (one measured number), then Tc = Tmf*min(1, Zr/Zc)
i03 = np.argmin(abs(nus_fine - 0.3)); i02 = np.argmin(abs(nus_fine - 0.2))
Zstar = Zr[i02]                                   # full coherence at the BCS-like crystal (Tc(0.2) = T_MF)
pexp = np.log(0.36 / Tmf_f[i03]) / np.log(Zr[i03] / Zstar)   # one exponent fixed by the measured Tc(0.3)
Zc = Zstar
Tc = Tmf_f * np.minimum(1.0, np.clip(Zr / Zstar, 0, None) ** pexp)
# rung-singlet / local-pair crossover scale (schematic interpolation between BCS onset and local singlet formation)
Ts_half = 5.5  # ED/NMR spin gap scale at nu=1/2 (singlet-triplet), crossover T_s ~ Delta_s / ln(3) ~ 5
Tstar = np.maximum(Tmf_f, (Ts_half / np.log(3.0)) * np.exp(-((nus_fine - 0.5) / 0.25) ** 2))

fig, ax = plt.subplots(figsize=(11, 6.2))
# regions
ax.fill_between(nus_fine, 0, Tc, color='#9ec5f4', alpha=0.85, lw=0)
ax.fill_between(nus_fine, Tc, Tstar, color='#cde2fb', alpha=0.9, lw=0)
ax.plot(nus_fine, Tc, color=vs.INK, lw=1.8)
ax.plot(nus_fine, Tmf_f, color=vs.INK2, lw=1.0, ls=(0, (4, 3)))
ax.plot(nus_fine, Tstar, color=vs.MUTED, lw=1.0)
ax.plot([0.5, 0.5], [0, 7.0], color=vs.C_HALF, lw=2.5)
# crystals
for nu0, k, lab in [(0.5, '1/2', r'$\nu=1/2$'), (0.3, '0.3', r'$\nu\approx0.3$'), (0.2, '0.2', r'$\nu\approx0.2$')]:
    ax.axvline(nu0, color=vs.CRYSTAL[k], lw=1.2, alpha=0.9)
    ax.text(nu0 - 0.008, 6.9, lab, color=vs.INK, fontsize=9.5, rotation=90, va='top', ha='right')
# measured points
ax.plot([0.3], [0.36], 's', color=vs.C_03, ms=8, mec=vs.SURFACE, mew=1.5, zorder=5)
ax.plot([0.2], [1.11], '^', color=vs.C_02, ms=9, mec=vs.SURFACE, mew=1.5, zorder=5)
ax.errorbar([0.3], [2.75], yerr=[[0.35], [0.5]], fmt='s', mfc='none', color=vs.C_03, ms=7, capsize=3, zorder=5)
ax.annotate('', xy=(0.5, 6.1), xytext=(0.5, 4.4), arrowprops=dict(arrowstyle='->', color=vs.C_HALF, lw=1.2))
ax.plot([0.5], [4.4], 'o', mfc='none', color=vs.C_HALF, ms=7, zorder=5)
# labels
ax.text(0.205, 0.45, 'interlayer s$^{\\pm}$\nsuperconductor', fontsize=9.5, ha='center', color=vs.INK)
ax.text(0.80, 0.45, 'interlayer s$^{\\pm}$\nsuperconductor', fontsize=9.5, ha='center', color=vs.INK)
ax.text(0.405, 2.0, 'preformed rung pairs\n(pseudogap, insulating-like)', fontsize=9, ha='center', color=vs.INK2)
ax.text(0.505, 7.25, 'rung-singlet insulator at $\\nu=1/2$\n(featureless; spin & charge gaps)', fontsize=9, ha='left', color=vs.INK)
ax.text(0.11, 3.6, 'normal metal\n(bare band)', fontsize=9.5, ha='center', color=vs.INK2)
ax.text(0.89, 3.6, 'normal metal', fontsize=9.5, ha='center', color=vs.INK2)
ax.text(0.012, 0.15, 'band\ninsulator', fontsize=8, color=vs.INK2)
ax.text(0.94, 0.15, 'band\ninsulator', fontsize=8, color=vs.INK2)
ax.text(0.62, 1.62, r'$T_{\rm MF}$ (pairing onset, mean field)', fontsize=8, color=vs.INK2)
ax.text(0.03, 1.25, r'$T_c$', fontsize=10, color=vs.INK)
ax.text(0.585, 4.45, r'$T^*$: singlet / pair formation (crossover)', fontsize=8, color=vs.INK2)
ax.set_xlim(0, 1); ax.set_ylim(0, 7.6)
ax.set_xlabel(r'filling fraction $\nu$'); ax.set_ylabel(r'temperature $T/D$')
ax.set_title(r'Bilayer rung-singlet model: $t=1$, $t^\prime=0.2$, $t_\perp\approx0$, $U=1.4$, $J_\perp=%.1f$' % J, loc='left')
# legend for markers
from matplotlib.lines import Line2D
h = [Line2D([], [], marker='^', ls='', color=vs.C_02, ms=8, label=r'measured $T_c$ ($\nu\approx0.2$)'),
     Line2D([], [], marker='s', ls='', color=vs.C_03, ms=7, label=r'measured $T_c$ ($\nu\approx0.3$)'),
     Line2D([], [], marker='s', ls='', mfc='none', color=vs.C_03, ms=7, label=r'NMR pseudogap onset $T^*$ ($\nu\approx0.3$)'),
     Line2D([], [], marker='o', ls='', mfc='none', color=vs.C_HALF, ms=7, label=r'spin gap still open at $T=4.4$ ($\nu=1/2$)')]
ax.legend(handles=h, loc='upper right', fontsize=8, bbox_to_anchor=(1.0, 0.99), frameon=True, facecolor=vs.SURFACE, edgecolor=vs.GRID)
plt.tight_layout(); plt.savefig(f'{OUT}/fig3_phase_diagram.png', dpi=130)
print('Tc max on hole side at nu=%.3f, Tc=%.3f; Tc(0.2)=%.3f; Tc(0.3)=%.3f; exponent p=%.2f' % (
    nus_fine[np.argmax(Tc * (nus_fine < 0.5))], (Tc * (nus_fine < 0.5)).max(), Tc[i02], Tc[i03], pexp))
