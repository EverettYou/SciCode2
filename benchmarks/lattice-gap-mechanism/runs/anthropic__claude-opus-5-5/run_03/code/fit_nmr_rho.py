"""NMR 1/T1 and resistivity: activation fits and model curves."""
import numpy as np
from scipy.optimize import least_squares, brentq
from common import load, kgrid, eps_c, mu_normal, save_json, FIG, V_PAIR
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

_, nmr, rho = load()
out = {'nmr': {}, 'rho': {}}


def arrhenius(T, y, e, p, sign, mask):
    """y = A T^p exp(sign*E/T); weighted least squares in linear space"""
    T, y, e = T[mask], y[mask], e[mask]
    def r(x): return (np.exp(x[0]) * T ** p * np.exp(sign * x[1] / T) - y) / e
    best = None
    for E0 in [0.5, 2, 4, 6]:
        s = least_squares(r, [0.0, E0])
        if best is None or s.cost < best.cost: best = s
    J = best.jac; cov = np.linalg.inv(J.T @ J)
    chi2 = 2 * best.cost; dof = mask.sum() - 2
    return best.x, np.sqrt(np.diag(cov)), chi2, dof


# ---------- NMR ----------
for nu, T, r, e in [(k, *v) for k, v in nmr.items()]:
    res = {}
    if nu == '1/2':
        m = np.ones_like(T, bool)
        for p in [0, 0.5, 1, 1.5, 2]:
            x, dx, c2, dof = arrhenius(T, r, e, p, -1, m)
            res['p=%g' % p] = dict(E=x[1], dE=dx[1], chi2=c2, dof=dof)
    elif nu == '≈0.3':
        for lo, hi, lab in [(0.2, 0.45, 'T<0.45 (around/below Tc)'), (0.3, 0.6, '0.3<T<0.6'), (0.5, 1.0, '0.5<T<1'), (1.0, 2.2, '1<T<2.2')]:
            m = (T >= lo) & (T <= hi) & (r > 2 * e)
            x, dx, c2, dof = arrhenius(T, r, e, 1, -1, m)
            res[lab] = dict(E=x[1], dE=dx[1], chi2=c2, dof=dof)
    else:
        for lo, hi, lab in [(0.2, 0.45, 'T<0.45'), (0.2, 0.35, 'T<0.35')]:
            m = (T >= lo) & (T <= hi)
            x, dx, c2, dof = arrhenius(T, r, e, 1, -1, m)
            res[lab] = dict(E=x[1], dE=dx[1], chi2=c2, dof=dof)
        hi_T = T >= 1.2
        res['normal_state_1/T1T_mean'] = float(np.mean(r[hi_T] / T[hi_T])); res['normal_state_scatter'] = float(np.std(r[hi_T] / T[hi_T]))
    out['nmr'][nu] = res

# ---------- resistivity ----------
for nu, T, y, e in [(k, *v) for k, v in rho.items()]:
    res = {}
    sc = T[y == 0]; nsc = T[y > 0]
    if len(sc): res['Tc_window'] = (float(sc.max()), float(nsc.min()))
    if nu in ('1/2', '≈0.3'):
        m = y > 0
        for p in [-1, -0.5, 0, 0.5, 1]:
            x, dx, c2, dof = arrhenius(T, y, e, p, +1, m)
            res['p=%g' % p] = dict(E=x[1], dE=dx[1], chi2=c2, dof=dof)
    out['rho'][nu] = res

# ---------- BCS model for 1/T1T at nu ~ 0.2 (HFB gap, V = 3 J_perp / 4) ----------
cx, cy = kgrid(400); e0 = eps_c(cx, cy)
mu02 = -1.937                           # from STS (c): normal-state value
xi = e0 - mu02
def gap_T(T):
    def f(D):
        E = np.sqrt(xi ** 2 + D ** 2); return 1 - V_PAIR * np.mean(np.tanh(E / (2 * T)) / (2 * E))
    if f(1e-6) > 0: return 0.0
    return brentq(f, 1e-6, 10)
x0 = np.where(np.abs(xi) < 1e-12, 1e-12, xi)
Tc_mf = brentq(lambda T: 1 - V_PAIR * np.mean(np.tanh(x0 / (2 * T)) / (2 * x0)), 0.05, 20)
D0 = gap_T(0.01)
Tgrid = np.linspace(0.18, 3.0, 120)
Dgrid = np.array([gap_T(T) if T < Tc_mf else 0.0 for T in Tgrid])
def t1t_ratio(T, D, Gam, coh=True):
    """(1/T1T)_s/(1/T1T)_n with constant normal DOS near E_F, Dynes broadening Gam"""
    E = np.linspace(-12 * T - 6, 12 * T + 6, 6001); z = E + 1j * Gam
    root = np.sqrt(z ** 2 - D ** 2 + 0j); root = np.where(root.imag * z.imag < 0, -root, root)
    Ns = np.real(z / root) if D > 0 else np.ones_like(E)
    Ms = np.real(D / root) if D > 0 else np.zeros_like(E)
    w = 1 / (4 * T * np.cosh(E / (2 * T)) ** 2)
    integrand = (Ns ** 2 + (Ms ** 2 if coh else 0)) * w
    return np.trapezoid(integrand, E)
curves = {}
for Gam, coh in [(0.10, True), (0.20, True), (0.05, False), (0.10, False)]:
    curves[(Gam, coh)] = np.array([t1t_ratio(T, D, Gam, coh) for T, D in zip(Tgrid, Dgrid)])
out['bcs_nu0.2'] = dict(Tc_MF=Tc_mf, Delta0=D0, two_Delta_over_Tc=2 * D0 / Tc_mf)
save_json(out, 'nmr_rho_fits.json')

# ---------- figure ----------
fig, axs = plt.subplots(1, 2, figsize=(14, 5.5))
ax = axs[0]
cols = {'1/2': 'C3', '≈0.3': 'C2', '≈0.2': 'C0'}
for nu, (T, r, e) in nmr.items():
    y = r / T; ey = e / T; m = r > 0
    ax.errorbar(1 / T[m], y[m], ey[m], fmt='o', ms=4, color=cols[nu], label=r'$\nu$=' + nu, capsize=2, alpha=0.8)
D = np.linspace(0.2, 5.2, 300)
Es = out['nmr']['1/2']['p=1']['E']
ax.plot(D, np.exp(-Es * (D - 0.25)), 'C3-', lw=1, label=r'$\nu=1/2$: $e^{-\Delta_s/T}$, $\Delta_s$=%.2f (fit)' % Es)
ax.plot(D, np.exp(-5.43 * (D - 0.25)), 'C3--', lw=1, label=r'theory: 2D rung-triplet gap 5.43 ($J_\perp$=8)')
E3 = out['nmr']['≈0.3']['T<0.45 (around/below Tc)']['E']
ax.plot(D[D > 1.6], 0.0035 * np.exp(-E3 * (D[D > 1.6] - 2.23)), 'C2-', lw=1, label=r'$\nu\approx0.3$: activation %.2f' % E3)
norm = 1.0  # normalized at T=4 in data, our ratio normalized to normal state ~1.08
for (Gam, coh), c in curves.items():
    ls = '-' if coh else ':'
    ax.plot(1 / Tgrid, 1.08 * c, color='C0', ls=ls, lw=1, alpha=0.9 if Gam == 0.1 else 0.5,
            label=r'$\nu\approx0.2$ BCS ($\Gamma$=%.2f, %s)' % (Gam, 'with coherence term' if coh else 'no coherence term'))
ax.set_yscale('log'); ax.set_ylim(1e-5, 8); ax.set_xlim(0, 5.3)
ax.set_xlabel('$D/T$'); ax.set_ylabel('$1/(T_1T)$ (normalized at $T=4D$)'); ax.legend(fontsize=7); ax.grid(alpha=0.3)
ax = axs[1]
for nu, (T, y, e) in rho.items():
    m = y > 0
    ax.errorbar(T[m], y[m], e[m], fmt='o', ms=3.5, color=cols[nu], capsize=2, label=r'$\nu$=' + nu)
    ax.plot(T[~m], 1e-2 * np.ones((~m).sum()), 'v', color=cols[nu], ms=4)
Tt = np.linspace(0.4, 4, 200)
E1 = out['rho']['1/2']['p=0']['E']; E2 = out['rho']['≈0.3']['p=0']['E']
ax.plot(Tt, np.exp(E1 * (1 / Tt - 0.25)), 'C3-', lw=1, label=r'$e^{E/T}$, $E$=%.2f' % E1)
ax.plot(Tt, np.exp(4.0 * (1 / Tt - 0.25)), 'C3--', lw=1, label=r'$e^{\Delta_c/2T}$, $\Delta_c/2$=4.0 (STS)')
ax.plot(Tt, np.exp(E2 * (1 / Tt - 0.25)), 'C2-', lw=1, label=r'$e^{E/T}$, $E$=%.2f' % E2)
ax.axvline(Tc_mf, color='C0', ls=':', lw=1); ax.text(Tc_mf + 0.03, 3e3, r'$T_c^{\rm MF}(\nu=0.2)$', color='C0', fontsize=8)
ax.set_yscale('log'); ax.set_ylim(5e-3, 1e4); ax.set_xlabel('$T/D$'); ax.set_ylabel(r'$\rho$ (normalized at $T=4D$); $\rho=0$ shown as $\triangledown$')
ax.legend(fontsize=7.5); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(f'{FIG}/fig2_nmr_rho.png', dpi=140)
import json
print(json.dumps({k: out[k] for k in out}, indent=1, default=float))
