"""Phase diagram (nu, T) of the bilayer t1-t2-J model at J=8, t1=1, t2=0.2.
Lines: mean-field pairing temperature T*(nu); phase-ordering temperature T_theta(nu) from the
T=0 superfluid stiffness with the hard-core (pair-Mott) factor; Tc = min(T*, T_theta).
SMG insulator at nu=1/2.  Measured points overlaid.  Writes figures/phase_diagram.png, data/phase_diagram.json"""
import json, sys, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0, '.')
from band import eps, kgrid
mf = json.load(open('../data/meanfield.json')); fit = json.load(open('../data/fit_results.json'))
t1, t2, J = 1.0, 0.2, 8.0
kx, ky = kgrid(400); ek = eps(kx, ky, t1, t2); d2e = 2*t1*np.cos(kx) + 4*t2*np.cos(kx)*np.cos(ky)
nus = np.array(sorted(float(k) for k in mf['T0'])); Tstar = np.array([mf['Tstar'][str(n)] for n in nus])
Ds, Tth = [], []
for n in nus:
    r = mf['T0'][str(n)]; D, mu = r['Delta'], r['mu']
    xi = ek-mu; E = np.sqrt(xi**2+D**2); v2 = 0.5*(1-xi/E)
    Dss = 2*np.mean(d2e*v2)                 # spin-summed diamagnetic stiffness per layer (T=0, full gap)
    hc = (1-2*n) if n <= 0.5 else (2*n-1)   # hard-core pair factor 1-n_b, vanishes at the pair Mott point nu=1/2
    Ds.append(Dss); Tth.append(np.pi/4*Dss*hc)   # K = 2 layers x D_s/4 ; T_KT = (pi/2) K
Ds = np.array(Ds); Tth_f = np.array(Tth)
# hard-core pair-boson estimate: T_KT = 0.685 t_b * 4 n_b (1-n_b)  [QMC value at n_b=1/2, n_b(1-n_b) interpolation]
tb0 = mf['two_body']['t_b_fit']; tb_sc = 8*t1**2/(3*J)
def tb_of(n):
    x = n if n <= 0.5 else 1-n
    return tb0 + (tb_sc-tb0)*(2*x)
nb = np.where(nus <= 0.5, 2*nus, 2*(1-nus)); Tth_b = np.array([0.685*tb_of(n)*4*b*(1-b) for n, b in zip(nus, nb)])
Tth = np.maximum(Tth_f, Tth_b); Tc = np.minimum(Tstar, Tth)
# pseudogap (pair-breaking) scale: the single-particle gap Delta_1(nu) where pairs are tightly bound
# (nu >= 0.3 on the hole side), merging into the mean-field T* in the BCS regime (nu <= 0.2)
D02m = fit['panel_c']['Delta'][0]; D03m = 0.5*(abs(fit['panel_b']['gap_edges'][0])+abs(fit['panel_b']['gap_edges'][1])); D12m = 0.5*fit['panel_a']['gap_total']
nu_pg = np.array([0.0, 0.20, 0.301, 0.5, 0.699, 0.80, 1.0]); D1 = np.array([0.33/2, D02m, D03m, D12m, D03m, D02m, 0.33/2])
def wpg(n):
    x = n if n <= 0.5 else 1-n
    u = float(np.clip((x-0.18)/0.14, 0, 1)); return 3*u**2-2*u**3
Tpg = np.array([max(np.interp(n, nus, Tstar), np.interp(n, nu_pg, D1)*wpg(n)) for n in nu_pg])
out = dict(nu=nus.tolist(), Tstar=Tstar.tolist(), D_s=Ds.tolist(), T_theta_fermion=Tth_f.tolist(), T_theta_boson=Tth_b.tolist(), T_theta=Tth.tolist(), Tc=Tc.tolist())
for n in (0.2, 0.25, 0.3, 0.301, 0.4, 0.45, 0.5, 0.7, 0.75, 0.8):
    i = np.argmin(abs(nus-n)); print(f'nu={nus[i]:.2f}: T*={Tstar[i]:.3f} D_s={Ds[i]:.3f} T_theta_f={Tth_f[i]:.3f} T_theta_b={Tth_b[i]:.3f} Tc={Tc[i]:.3f} Delta_MF={mf["T0"][str(nus[i])]["Delta"]:.3f}')
json.dump(out, open('../data/phase_diagram.json', 'w'), indent=1)

fig, ax = plt.subplots(figsize=(8.2, 6.4))
ax.fill_between(nus, 0, Tc, color='#9fc5e8', alpha=0.9, label='interlayer-singlet superconductor (s-wave on the rung)')
pg_hi = np.array([max(Ts_, np.interp(n, nu_pg, D1)*wpg(n)) for n, Ts_ in zip(nus, Tstar)])
ax.fill_between(nus, Tc, np.maximum(Tstar, pg_hi), where=(np.maximum(Tstar, pg_hi) > Tc), color='#f6d5a7', alpha=0.7, label='paired, phase-incoherent (pseudogap / pair liquid)')
ax.plot(nus, Tstar, 'k--', lw=1, label='$T^*$ mean-field pairing')
ax.plot(nus, Tth, 'k:', lw=1, label='$T_\\theta$ 2D phase-ordering estimate (pair stiffness)')
ax.plot(nus, Tc, 'k-', lw=1.6, label='$T_c=\\min(T^*,T_\\theta)$')
ax.plot(nus, pg_hi, color='C1', lw=1, ls='-.', label='pair-breaking scale: $T^*$ (BCS side) or $\\Delta_1(\\nu)$ (bound pairs)')
ax.plot([0.5, 0.5], [0, 2.75], color='C3', lw=4, alpha=0.8, label='SMG insulator at $\\nu=1/2$ (gapped, symmetric); crossover above $\\Delta_s/2$')
ax.plot([0.5, 0.5], [2.75, 4.0], color='C3', lw=4, alpha=0.3)
for n, lab, c in ((0.5, '$\\nu=1/2$', 'C3'), (0.301, '$\\nu\\approx0.3$', 'C2'), (0.20, '$\\nu\\approx0.2$', 'C0')):
    ax.axvline(n, color=c, ls='-', lw=0.8, alpha=0.6); ax.text(n+0.005, 4.12 if n>0.4 else 4.3, lab, color=c, fontsize=9)
# ED pair-breaking gaps (half of E(N+1)+E(N-1)-2E(N)), averaged over periodic/antiperiodic 4x2 tori, plus the 3x3 SMG gap
try:
    g = json.load(open('../data/ed_calibration.json'))['gaps']
    ed_nu, ed_d = [], []
    for N in (6, 8, 10, 12, 14):
        vals = [g[f'gap1_4x2_N{N}_{b}'] for b in ('pp', 'aa') if f'gap1_4x2_N{N}_{b}' in g]
        if vals: ed_nu.append(N/32); ed_d.append(0.5*np.mean(vals))
    for N in (8, 12):
        if f'gap1_3x3_N{N}' in g: ed_nu.append(N/36); ed_d.append(0.5*g[f'gap1_3x3_N{N}'])
    if 'charge_gap_3x3_mixedBC' in g: ed_nu.append(0.5); ed_d.append(0.5*g['charge_gap_3x3_mixedBC'])
    print('ED crosses (nu, Delta1):', [(round(a, 3), round(b_, 2)) for a, b_ in zip(ed_nu, ed_d)])
    ax.plot(ed_nu, ed_d, 'kx', ms=7, mew=1.5, label='ED: half the pair-breaking gap $\\Delta_1$ (4x2, 3x3 tori)')
    ax.plot([0.20, 0.301, 0.5], [D02m, D03m, D12m], 'k+', ms=9, mew=1.5, label='measured single-particle gap $\\Delta_1$ (STS)')
except Exception as e: print('no ED gaps', e)
ax.errorbar([0.20], [fit['res']['≈0.2']['Tc'][0]], yerr=[fit['res']['≈0.2']['Tc'][1]], fmt='o', color='C0', ms=6, zorder=5, label='measured $T_c$ (resistivity)')
ax.errorbar([0.301], [fit['res']['≈0.3']['Tc'][0]], yerr=[fit['res']['≈0.3']['Tc'][1]], fmt='o', color='C2', ms=6, zorder=5)
ax.text(0.52, 1.0, 'pair Mott\ninsulator\n(SMG)', color='C3', fontsize=8)
ax.text(0.06, 2.4, 'normal metal\n(Fermi liquid)', fontsize=9); ax.text(0.80, 2.4, 'normal metal', fontsize=9)
ax.text(0.5, 4.42, 'incoherent paramagnet / bad metal', fontsize=8, ha='center')
ax.set_xlim(0, 1); ax.set_ylim(0, 4.6); ax.set_xlabel('filling fraction $\\nu$'); ax.set_ylabel('temperature $T/D$')
ax.legend(fontsize=7, loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=2); ax.set_title('bilayer $t_1$-$t_2$-$J$ model, $t_1=D$, $t_2=0.2D$, $J=8D$', fontsize=10)
fig.tight_layout(); fig.savefig('../figures/phase_diagram.png', dpi=150)
