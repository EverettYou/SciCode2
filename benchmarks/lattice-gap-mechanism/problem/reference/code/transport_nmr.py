"""Model curves for the resistivity and NMR 1/(T1 T) of the three crystals, compared with the data.
Half filling: constant-tau Boltzmann transport in the holon/trion bands; 1/(T1T) from intraband
triplon scattering.  nu~0.2: BCS Hebel-Slichter integral.  nu~0.3: quasiparticle integral with the
measured (coherence-peak-free) tunneling DOS.  Writes figures/nmr_model.png, figures/resistivity_model.png,
data/transport_nmr.json."""
import json, sys, os, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '.')
from band import eps, kgrid
ROOT = '/home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem'
d = json.load(open(f'{ROOT}/measurements.json'))['measurements']
sts, nmr, res = d
fit = json.load(open('../data/fit_results.json'))
out = {}
kx, ky = kgrid(600); ek = eps(kx, ky)
dedkx = 2*np.sin(kx) + 0.8*np.sin(kx)*np.cos(ky)
def fermi_deriv(E, T):
    x = np.clip(E/T, -60, 60); return 0.25/T/np.cosh(x/2)**2
def bose(E, T):
    x = np.clip(E/T, 1e-9, 60); return 1/np.expm1(x)

# ---------------- half filling: Boltzmann resistivity ----------------
def half_bands():
    """ED-calibrated holon/trion bands if available, else first-order (midpoint of gap at 0)"""
    p = '../data/half_filling_bands.json'
    if os.path.exists(p):
        import calib; b = json.load(open(p)); return calib.ev(b['fits']['Ep'], kx, ky)-b['mu'], calib.ev(b['fits']['Eh'], kx, ky)-b['mu']
    return 6.4 + ek/2, -5.6 + ek/2
Ep, Eh = half_bands()
def sigma_half(T):
    s = 0.0
    for E, v in ((Ep, 0.5*dedkx), (Eh, 0.5*dedkx)):
        s += np.mean(v**2*fermi_deriv(E, T))
    return s
Ts = np.linspace(0.4, 4.2, 60); rho = np.array([1/sigma_half(T) for T in Ts]); rho /= 1/sigma_half(4.0)
sl = np.polyfit(1/Ts[Ts <= 2], np.log(rho[Ts <= 2]), 1)[0]
out['half_resistivity'] = dict(T=Ts.tolist(), rho=rho.tolist(), activation_fit_Tle2=float(sl))
print('half filling Boltzmann: ln rho slope (T<=2) = %.3f  (data %.3f)' % (sl, fit['res']['1/2']['activation_Tmax2.0'][0]))

# ---------------- half filling: triplon NMR ----------------
def triplon_band():
    p = '../data/triplon_fit.json'
    if os.path.exists(p):
        b = json.load(open(p)); return b['a'] + b['b']*(np.cos(kx)+np.cos(ky)) + b['c']*np.cos(kx)*np.cos(ky) + b.get('d', 0)*(np.cos(2*kx)+np.cos(2*ky)), b
    sc = json.load(open('../data/strong_coupling.json'))['triplon_band']
    return sc['J'] + 4*sc['de1'] + 4*sc['de2'] + 2*sc['tau1']*(np.cos(kx)+np.cos(ky)) + 4*sc['tau2']*np.cos(kx)*np.cos(ky), sc
om, tb = triplon_band()
Egrid = np.linspace(om.min()-0.05, om.max()+0.05, 600); dE = Egrid[1]-Egrid[0]
rho_t = np.histogram(om.ravel(), bins=np.concatenate([Egrid-dE/2, [Egrid[-1]+dE/2]]))[0]/om.size/dE
rho_t = gaussian_filter1d(rho_t, 2)
def T1T_half(T):
    n = bose(Egrid, T); return np.sum(rho_t**2*n*(1+n))*dE/T
Tn = np.array(nmr['samples'][0]['temperature']); rn = np.array(nmr['samples'][0]['one_over_T1'])/Tn
Tm = np.linspace(0.4, 4.5, 80); m = np.array([T1T_half(T) for T in Tm]); m /= T1T_half(4.0)
sl = np.polyfit(1/Tm[Tm <= 2], np.log(m[Tm <= 2]), 1)[0]
out['half_nmr'] = dict(T=Tm.tolist(), T1T=m.tolist(), slope_Tle2=float(-sl), triplon_edge=float(om.min()), triplon_top=float(om.max()))
print('half filling triplon NMR: Arrhenius slope of 1/(T1T) (T<=2) = %.3f ; triplon edge %.3f (data slope %.2f +- %.2f)' % (-sl, om.min(), *fit['nmr']['1/2']['slope_T1T_Tmax2.0']))

# ---------------- nu~0.2: Hebel-Slichter ----------------
D0 = fit['panel_c']['Delta'][0]; Tc = fit['res']['≈0.2']['Tc'][0]
def Delta_T(T): return D0*np.tanh(1.74*np.sqrt(np.clip(Tc/T-1, 0, None))) if T < Tc else 0.0
def hs(T, Gamma=0.05):
    D = Delta_T(T); E = np.linspace(-12, 12, 6001)
    z = E + 1j*Gamma; r = np.sqrt(z**2 - D**2 + 0j); r = np.where(r.imag < 0, -r, r)
    Ns = (z/r).real; Ms = (D/r).real
    return np.trapezoid((Ns**2 + Ms**2)*fermi_deriv(E, T), E)
Tm2 = np.linspace(0.2, 4.5, 120); h = np.array([hs(T) for T in Tm2]); h /= hs(4.0)
out['nu02_nmr'] = dict(T=Tm2.tolist(), T1T=h.tolist(), Delta0=D0, Tc=Tc, Gamma=0.05, peak=float(h.max()), T_peak=float(Tm2[np.argmax(h)]))
print('nu~0.2 Hebel-Slichter: peak %.2f at T=%.2f (data %.2f at %.2f)' % (h.max(), Tm2[np.argmax(h)], *fit['nmr']['≈0.2']['HS_peak']))

# ---------------- nu~0.3: measured DOS, no coherence factor ----------------
V = np.array(sts['spectra'][1]['bias']); y = np.array(sts['spectra'][1]['dI_dV'])
Nb = np.clip(y - 0.11*(V/9)**2*(np.abs(V) > 6.6), 0, None); Nb = gaussian_filter1d(Nb, 2)
Nb_sym = 0.5*(Nb + Nb[::-1]); EDGE = 0.5*(abs(fit['panel_b']['gap_edges'][0])+abs(fit['panel_b']['gap_edges'][1])); Nb_sym[np.abs(V) < EDGE] = 0.0
Nn = np.mean(Nb_sym[(np.abs(V) > 2.6) & (np.abs(V) < 6.5)])
def t1t_03_dos(T, Tstar=4.0):
    # (i) quasiparticle integral with the measured (coherence-peak-free) DOS, gap closing smoothly at T*
    f = np.tanh(1.74*np.sqrt(max(Tstar/T-1, 0))) if T < Tstar else 0.0
    if f < 1e-3: return 1.0
    Vs = V*f; Ns = np.interp(V, Vs, Nb_sym)/Nn
    Ns = np.where(np.abs(V) > 6.5*f, 1.0, Ns); Ns = np.where(np.abs(V) < EDGE*f, 0.0, Ns)
    return np.trapezoid(Ns**2*fermi_deriv(V, T), V)
Tc3 = fit['res']['≈0.3']['Tc'][0]
def t1t_03(T, p0=0.3, w=0.1, Tstar=4.0):
    # (ii) pair liquid: a step-edged gap EDGE without coherence peak (no Hebel-Slichter term) below Tc; above Tc the
    # phase-incoherent pairs fill the gap with a uniform in-gap weight p(T) that jumps to p0 at Tc and grows to 1 at T*
    D = EDGE*np.tanh(1.74*np.sqrt(max(Tstar/T-1, 0))) if T < Tstar else 0.0
    p = 0.0 if T <= Tc3 else min(1.0, p0 + (1-p0)*(T-Tc3)/(Tstar-Tc3))
    E = np.linspace(-12, 12, 6001); Ns = p + (1-p)*0.5*(1+np.tanh((np.abs(E)-D)/w))
    return np.trapezoid(Ns**2*fermi_deriv(E, T), E)
Tm3 = np.linspace(0.2, 4.5, 120); h3 = np.array([t1t_03(T) for T in Tm3]); h3 /= t1t_03(4.0)
h3d = np.array([t1t_03_dos(T) for T in Tm3]); h3d /= t1t_03_dos(4.0)
def arr_slope(Tv, h, lo, hi):
    m = (Tv >= lo) & (Tv <= hi); return float(-np.polyfit(1/Tv[m], np.log(h[m]), 1)[0])
out['nu03_nmr'] = dict(T=Tm3.tolist(), T1T=h3.tolist(), T1T_measuredDOS=h3d.tolist(), slope_below_Tc=arr_slope(Tm3, h3, 0.2, Tc3), slope_above_Tc=arr_slope(Tm3, h3, 0.4, 2.0),
                       slope_measuredDOS_Tle2=arr_slope(Tm3, h3d, 0.3, 2.0), Tc=Tc3, p0=0.3, w=0.1, Tstar=4.0)
print('nu~0.3 pair-liquid NMR model: slope below Tc %.2f (data %.2f), slope 0.4<T<2 %.2f (data %.2f); measured-DOS integral slope %.2f; max %.2f (no coherence peak)' % (
    out['nu03_nmr']['slope_below_Tc'], fit['nmr']['≈0.3']['slope_T1T_T0.0-0.36'][0], out['nu03_nmr']['slope_above_Tc'], fit['nmr']['≈0.3']['slope_T1T_T0.4-2.0'][0], out['nu03_nmr']['slope_measuredDOS_Tle2'], h3.max()))

# ---------------- nu~0.2 normal-state resistivity (Fermi liquid, T^2 + residual) ----------------
json.dump(out, open('../data/transport_nmr.json', 'w'), indent=1)

# ---------------- figures ----------------
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
cols = {'1/2': 'C3', '≈0.3': 'C2', '≈0.2': 'C0'}
for s in nmr['samples']:
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    ax[0].errorbar(1/T, r/T, yerr=u/T, fmt='o', ms=3, color=cols[s['filling']], label=f"data $\\nu$={s['filling']}")
ax[0].plot(1/Tm, m, '-', color='C3', label='triplon intraband, edge %.2f' % om.min())
ax[0].plot(1/Tm3, h3, '-', color='C2', label='step gap %.2f, no coherence peak; 30%% in-gap weight above $T_c$' % EDGE)
ax[0].plot(1/Tm3, h3d, '--', color='C2', lw=0.8, label='quasiparticle integral with the measured DOS')
ax[0].plot(1/Tm2, h, '-', color='C0', label='BCS Hebel-Slichter, $\\Delta_0$=%.2f, $T_c$=%.2f' % (D0, Tc))
ax[0].set_yscale('log'); ax[0].set_ylim(1e-5, 8); ax[0].set_xlim(0, 5.3); ax[0].set_xlabel('D/T'); ax[0].set_ylabel('1/(T$_1$T) (norm. at T=4D)'); ax[0].legend(fontsize=7)
for s in res['samples']:
    T = np.array(s['temperature']); r = np.array(s['resistivity']); u = np.array(s['uncertainty']); mm = r > 0
    ax[1].errorbar(T[mm], r[mm], yerr=u[mm], fmt='o', ms=3, color=cols[s['filling']], label=f"data $\\nu$={s['filling']}")
ax[1].plot(Ts, rho, '-', color='C3', label='Boltzmann, two bands, const. $\\tau$')
ax[1].set_yscale('log'); ax[1].set_xlabel('T/D'); ax[1].set_ylabel('resistivity (norm. at T=4D)'); ax[1].legend(fontsize=7)
ax[1].axvline(fit['res']['≈0.2']['Tc'][0], color='C0', ls=':', lw=1); ax[1].axvline(fit['res']['≈0.3']['Tc'][0], color='C2', ls=':', lw=1)
fig.tight_layout(); fig.savefig('../figures/nmr_resistivity_model.png', dpi=140)
