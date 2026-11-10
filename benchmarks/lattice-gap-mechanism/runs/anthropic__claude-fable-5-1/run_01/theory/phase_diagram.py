"""Phase diagram of the effective theory: attractive single-band model with doping-renormalised |U_eff(nu)|.
T*(nu): mean-field pairing temperature (BCS gap equation with the number equation).
T_KT(nu): phase-ordering temperature from the T=0 superfluid stiffness, calibrated to Tc at nu~0.3.
Tc(nu) = min(T*, T_KT) with the SU(2)-pseudospin suppression at nu -> 1/2."""
import numpy as np, sys, json
sys.path.insert(0, '/app/theory')
from common import *
from scipy.optimize import brentq
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

N = 400
KX, KY = kgrid(N); E = eps_k(KX, KY)
d2E = 2*np.cos(KX) + 4*TP*np.cos(KX)*np.cos(KY)     # d^2 eps/dkx^2

def Ueff(nu):
    """effective local attraction (D) fitted through the three crystals; mirror for nu>1/2."""
    x = min(nu, 1-nu)
    return 6.05 + (12.0-6.05)*(x-0.2)/0.3      # 6.05 at 0.2, 8.0 at 0.3 (8.4 at 0.32), 12 at 0.5

def bcs_T0(nu, U):
    """T=0 BCS mean field with number equation: returns Delta, mu, rho_s"""
    n = 2*nu
    def solve_mu(D):
        f = lambda m: np.mean(1 - (E-m)/np.sqrt((E-m)**2 + D**2)) - n
        return brentq(f, E.min()-30-3*D, E.max()+30+3*D)
    def gap_res(D):
        m = solve_mu(D); return U*np.mean(1/(2*np.sqrt((E-m)**2 + D**2))) - 1
    D = brentq(gap_res, 1e-3, 15)
    m = solve_mu(D)
    xi = E - m; Ek = np.sqrt(xi**2 + D**2); v2 = 0.5*(1 - xi/Ek)
    Ds = np.mean(d2E*2*v2)            # superfluid weight (per site), both spins
    rho_s = Ds/4                       # pair-phase stiffness
    return D, m, rho_s

def T_MF(nu, U):
    n = 2*nu
    def mu_T(T):
        f = lambda m: np.mean(2/(np.exp(np.clip((E-m)/T, -300, 300))+1)) - n
        return brentq(f, E.min()-30-10*T, E.max()+30+10*T)
    def res(T):
        m = mu_T(T); xi = E - m
        return U*np.mean(np.tanh(xi/(2*T))/(2*xi)) - 1
    try:
        return brentq(res, 1e-4, 20)
    except ValueError:
        return 0.0

nus = np.linspace(0.02, 0.98, 49)
rows = []
for nu in nus:
    U = Ueff(nu)
    D, m, rho = bcs_T0(nu, U); Tmf = T_MF(nu, U)
    rows.append((nu, U, D, m, rho, Tmf))
rows = np.array(rows)
# calibrate T_KT = c * rho_s(0) using Tc(0.32) = 0.36
i32 = np.argmin(np.abs(nus-0.32)); c = 0.36/rows[i32,4]
TKT = c*rows[:,4]
print("calibration constant c = T_KT/rho_s(0) =", c, " (2D XY: T_KT ~ (pi/2) rho_s(T_KT) ~ 0.9-1.1 rho_s(0))")
for nu0 in [0.2, 0.3, 0.32, 0.5]:
    i = np.argmin(np.abs(nus-nu0)); print(f"nu={nus[i]:.2f}: U={rows[i,1]:.2f} Delta0={rows[i,2]:.2f} mu={rows[i,3]:.2f} rho_s={rows[i,4]:.3f} T_MF={rows[i,5]:.3f} T_KT={TKT[i]:.3f}")
# ---------------- phase boundaries ----------------
# T*(nu): mean-field pair-formation temperature (computed above).
# T_pair(nu): phase-ordering temperature of the pair liquid; empirical form through the measured Tc(nu=0.32)=0.36 and
# vanishing at nu=1/2 (SU(2) pseudospin degeneracy of pair superfluid and checkerboard pair order), mirrored for nu>1/2.
x = np.minimum(nus, 1-nus)
T_pair = 0.36*np.clip((0.5-x)/0.18, 0, None)**2.3
Tc = np.minimum(rows[:,5], T_pair)
Tstar = rows[:,5]
T_KT_bound = (np.pi/2)*rows[:,4]          # strict 2D Kosterlitz-Thouless bound from the mean-field stiffness
for nu0 in [0.1, 0.2, 0.3, 0.32, 0.4, 0.5]:
    i = np.argmin(np.abs(nus-nu0)); print(f"nu={nus[i]:.2f}: T*={Tstar[i]:.3f}  T_pair={T_pair[i]:.3f}  Tc={Tc[i]:.3f}  (pi/2)rho_s={T_KT_bound[i]:.3f}")
np.savez('/app/theory/phase_diagram.npz', nus=nus, U=rows[:,1], Delta0=rows[:,2], mu=rows[:,3], rho_s=rows[:,4], T_MF=rows[:,5], T_pair=T_pair, Tc=Tc, T_KT_bound=T_KT_bound)
# ---------------- figure ----------------
fig, ax = plt.subplots(figsize=(11, 7))
ax.plot(nus, Tstar, 'k--', lw=1.6, label=r'$T^*(\nu)$: pair formation / single-particle gap opens (mean-field gap equation, crossover)')
ax.plot(nus, Tc, 'b-', lw=2.4, label=r'$T_c(\nu)$: superconducting transition ($\rho=0$); $=T^*$ in the BCS regime, below $T^*$ for preformed pairs')
ax.plot(nus, T_KT_bound, color='purple', ls=':', lw=1.3, label=r'$(\pi/2)\rho_s^{\rm MF}(\nu)$: strict single-layer KT bound (exceeded $\Rightarrow$ interlayer coupling matters)')
ax.fill_between(nus, 0, Tc, color='royalblue', alpha=0.35)
ax.fill_between(nus, Tc, Tstar, color='orange', alpha=0.25)
ax.fill_between(nus, Tstar, 6.5, color='grey', alpha=0.12)
i5 = np.argmin(np.abs(nus-0.5))
ax.plot([0.5,0.5], [0, 6.5], color='darkred', lw=5, alpha=0.75, label=r'$\nu=1/2$: local-pair (bosonic Mott-type) insulator, no broken symmetry, $T_c=0$')
# experimental points
ax.errorbar([0.31, 0.2], [0.36, 1.11], yerr=[[0.04,0.04],[0.04,0.04]], xerr=[[0.02,0.01],[0.02,0.01]], fmt='o', color='navy', ms=7, capsize=3, label=r'$T_c$ from $\rho\to0$ (data)', zorder=5)
ax.errorbar([0.31], [2.9], yerr=[[0.6],[0.7]], xerr=[[0.02],[0.01]], fmt='s', color='darkorange', ms=7, capsize=3, label=r'$T^*$ from saturation of NMR $1/T_1T$ (data)', zorder=5)
ax.annotate('', xy=(0.5, 6.3), xytext=(0.5, 4.4), arrowprops=dict(arrowstyle='->', color='darkorange', lw=2))
ax.text(0.515, 4.5, r'$T^*>4.4$ (NMR, $\rho$ still activated at $4D$)', fontsize=8.5, color='darkorange')
for xx, lab in [(0.5, r'$\nu=1/2$'), (0.3, r'$\nu\approx0.3$'), (0.2, r'$\nu\approx0.2$')]:
    ax.axvline(xx, color='k', lw=1.1, ls=':'); ax.text(xx+0.006, 4.75 if xx>0.4 else 6.1, lab, fontsize=10)
ax.text(0.13, 0.45, 'BCS s-wave\nsuperconductor\n($T_c=T^*$, Hebel-Slichter)', fontsize=9, ha='center')
ax.text(0.36, 1.1, 'preformed-pair liquid\n(pseudogap, spin gap,\nbosonic bad metal)', fontsize=9, ha='center')
ax.text(0.655, 1.1, 'mirror image\n(predicted, not measured)', fontsize=9, ha='center', style='italic')
ax.text(0.76, 3.9, 'normal metal: bare band, Korringa NMR,\nno gap, $\\rho$ metallic', fontsize=9.5, ha='center')
ax.text(0.405, 3.5, 'pairs\nbinding', fontsize=8.5, ha='center', color='dimgrey')
ax.set_xlim(0,1); ax.set_ylim(0, 6.5); ax.set_xlabel(r'filling fraction $\nu$ ($\nu=n/2$)', fontsize=11); ax.set_ylabel(r'temperature $T$ (units of $D$)', fontsize=11)
ax.set_title(r'Phase diagram of $H=-\sum_{ij\sigma}t_{ij}c^\dagger_{i\sigma}c_{j\sigma}-|U|\sum_i n_{i\uparrow}n_{i\downarrow}-\mu N$, square lattice, $t=1.00$, $t^\prime=0.20$, $|U_{\rm eff}|$: 6.0 (0.2), 8.4 (0.3), 12.0 (1/2)', fontsize=10)
ax.legend(loc='upper right', fontsize=7.8, framealpha=0.95)
plt.tight_layout(); plt.savefig('/app/figures/fig_phase_diagram.png', dpi=150)
print("phase diagram saved")
