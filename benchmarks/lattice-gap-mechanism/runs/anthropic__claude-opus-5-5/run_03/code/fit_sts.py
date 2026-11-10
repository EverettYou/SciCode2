"""Fits of the STS differential conductance (Figure 1) with model spectral densities.
dI/dV(V) = amp * N(V) (Gaussian instrumental broadening sig) + b|V| (smooth tunnelling background, absent in the gap)
(d) high T, nu~0.3 : bare t-t' band                      -> t, t', mu
(a) low T,  nu=1/2 : rung-singlet (SMG) insulator        -> Phi, slope (=1/2), weight asymmetry alpha
                     compared with the Hubbard-I / hybridization (nonlinear) form and with BCS
(c) low T,  nu~0.2 : isotropic s-wave BCS on the bare band -> Delta, mu
(b) low T,  nu~0.3 : strong-coupling two-gap s-wave state (phenomenological)
"""
import numpy as np
from scipy.optimize import least_squares
from common import load, kgrid, eps_c, cic, gauss_conv, save_json, FIG
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sts, _, _ = load()
Vf = sts['a'][0]; dV = Vf[1] - Vf[0]
CX, CY = kgrid(300); NK = len(CX)


def report(s, names):
    J = s.jac; dof = len(s.fun) - len(s.x); s2 = (s.fun ** 2).sum() / dof
    cov = np.linalg.pinv(J.T @ J) * s2
    err = np.sqrt(np.abs(np.diag(cov)))
    return {n: (float(v), float(e)) for n, v, e in zip(names, s.x, err)}, float(2 * s.cost)


def fit(model, p0, lo, hi, G):
    return least_squares(lambda p: model(p) - G, p0, bounds=(lo, hi), diff_step=1e-3, max_nfev=2000)


out = {}
# ---------------- (d) bare band ----------------
def model_d(p):
    t, tp, mu, sig, amp, b0, b1 = p
    e = eps_c(CX, CY, t, tp) - mu
    A = gauss_conv(cic(e, np.ones_like(e), Vf, NK), dV, sig)
    return amp * A + np.where(Vf < e.min(), b0 * np.abs(Vf), 0) + np.where(Vf > e.max(), b1 * np.abs(Vf), 0)
Gd = sts['d'][1]
sd = fit(model_d, [1.0, 0.19, -0.9, 0.1, 3, 0.01, 0.01], [0.8, 0, -3, 0.005, 0.1, 0, 0], [1.2, 0.4, 1, 0.6, 30, 0.05, 0.05], Gd)
pd, sse = report(sd, ['t', 'tp', 'mu', 'sig', 'amp', 'b0', 'b1'])
e = eps_c(CX, CY, sd.x[0], sd.x[1])
out['d'] = dict(params=pd, SSE=sse, filling=float(np.mean(e < sd.x[2])),
                band_bottom_minus_mu=float(e.min() - sd.x[2]), band_top_minus_mu=float(e.max() - sd.x[2]),
                vHs_minus_mu=float(4 * sd.x[1] - sd.x[2]))
t0, tp0 = sd.x[0], sd.x[1]
E0 = eps_c(CX, CY, t0, tp0); ec = 0.5 * (E0.min() + E0.max())

# ---------------- (a) SMG insulator: translated half-width copies ----------------
def model_a(p):
    Phi, s, tp, alpha, d0, sig, amp, b = p
    e = eps_c(CX, CY, t0, tp); c = 0.5 * (e.min() + e.max()); x = e - c
    Ep, Em = Phi + s * x + d0, -Phi + s * x + d0
    Zp, Zm = 0.5 * (1 + alpha * x), 0.5 * (1 - alpha * x)
    A = gauss_conv(cic(np.concatenate([Ep, Em]), np.concatenate([Zp, Zm]), Vf, NK), dV, sig)
    edge = Phi - s * (e.max() - e.min()) / 2
    return amp * A + b * np.abs(Vf) * (np.abs(Vf - d0) > edge)
def model_a_hyb(p):   # Hubbard-I / hybridization: E = (e+lam)/2 +- sqrt(((e-lam)/2)^2+V^2), mid-gap at 0
    Vh, lam, sig, amp, b = p
    e = E0; R = np.sqrt(((e - lam) / 2) ** 2 + Vh ** 2)
    Ep, Em = (e + lam) / 2 + R, (e + lam) / 2 - R
    mid = 0.5 * (Ep.min() + Em.max()); Ep, Em = Ep - mid, Em - mid
    Zp, Zm = 0.5 * (1 + (e - lam) / (2 * R)), 0.5 * (1 - (e - lam) / (2 * R))
    A = gauss_conv(cic(np.concatenate([Ep, Em]), np.concatenate([Zp, Zm]), Vf, NK), dV, sig)
    return amp * A + b * np.abs(Vf) * (np.abs(Vf) > Ep.min())
def model_a_bcs(p):
    mu, D, sig, amp, b = p
    xi = E0 - mu; E = np.sqrt(xi ** 2 + D ** 2)
    A = gauss_conv(cic(np.concatenate([E, -E]), np.concatenate([0.5 * (1 + xi / E), 0.5 * (1 - xi / E)]), Vf, NK), dV, sig)
    return amp * A + b * np.abs(Vf) * (np.abs(Vf) > D)
Ga = sts['a'][1]
sa = fit(model_a, [6.0, 0.5, 0.19, 0.05, 0.0, 0.12, 3, 0.012], [4, 0.3, 0.0, -0.2, -0.5, 0.01, 0.1, 0], [8, 0.7, 0.4, 0.2, 0.5, 0.6, 30, 0.05], Ga)
pa, ssea = report(sa, ['Phi', 'slope', 'tp', 'alpha', 'd0', 'sig', 'amp', 'b'])
sah = fit(model_a_hyb, [6.0, -0.8, 0.12, 3, 0.012], [3, -6, 0.01, 0.1, 0], [9, 6, 0.6, 30, 0.05], Ga)
pah, sseah = report(sah, ['V', 'lambda', 'sig', 'amp', 'b'])
sab = None
for mu in [-1.5, -0.5, 0.0, 0.5]:
    s_ = fit(model_a_bcs, [mu, 4.0, 0.12, 3, 0.012], [-4, 1, 0.01, 0.1, 0], [4, 8, 0.6, 30, 0.05], Ga)
    if sab is None or s_.cost < sab.cost: sab = s_
pab, sseab = report(sab, ['mu', 'Delta', 'sig', 'amp', 'b'])
out['a'] = dict(translated_copies=dict(params=pa, SSE=ssea), hubbardI_hybridization=dict(params=pah, SSE=sseah),
                bcs_mirror=dict(params=pab, SSE=sseab),
                gap_edge=float(sa.x[0] - sa.x[1] * (E0.max() - E0.min()) / 2))

# ---------------- (c) BCS ----------------
def model_c(p):
    g, mu, D, sig, amp, b0, b1 = p
    xi = g * E0 - mu; E = np.sqrt(xi ** 2 + D ** 2)
    A = gauss_conv(cic(np.concatenate([E, -E]), np.concatenate([0.5 * (1 + xi / E), 0.5 * (1 - xi / E)]), Vf, NK), dV, sig)
    lo, hi = -np.sqrt(xi.min() ** 2 + D ** 2), np.sqrt(xi.max() ** 2 + D ** 2)
    return amp * A + np.where(Vf < lo, b0 * np.abs(Vf), 0) + np.where(Vf > hi, b1 * np.abs(Vf), 0)
Gc = sts['c'][1]
sc = fit(model_c, [1.0, -1.9, 1.9, 0.12, 3, 0.01, 0.01], [0.5, -4, 0.5, 0.005, 0.1, 0, 0], [1.5, 1, 4, 0.6, 30, 0.05, 0.05], Gc)
pc, ssec = report(sc, ['g', 'mu', 'Delta', 'sig', 'amp', 'b0', 'b1'])
xi = sc.x[0] * E0 - sc.x[1]; E = np.sqrt(xi ** 2 + sc.x[2] ** 2)
out['c'] = dict(params=pc, SSE=ssec, normal_state_filling=float(np.mean(sc.x[0] * E0 < sc.x[1])),
                bcs_number_filling=float(np.mean(1 - xi / E) / 2))

# ---------------- (b) strong-coupling two-gap state ----------------
CXb, CYb = kgrid(200); NKb = len(CXb); E0b = eps_c(CXb, CYb, t0, tp0)
DW = (CXb - CYb) ** 2 / 4
def model_b(p):
    DF0, DF1, Dp, Dm, w, mu, sig, amp, b = p
    xi = E0b - mu; DF = DF0 + DF1 * DW; Dinf = np.where(xi >= 0, Dp, Dm)
    D = np.sqrt(DF ** 2 + np.clip(Dinf ** 2 - DF ** 2, 0, None) * xi ** 2 / (xi ** 2 + w ** 2))
    E = np.sqrt(xi ** 2 + D ** 2)
    A = gauss_conv(cic(np.concatenate([E, -E]), np.concatenate([0.5 * (1 + xi / E), 0.5 * (1 - xi / E)]), Vf, NKb), dV, sig)
    return amp * A + b * np.abs(Vf) * (np.abs(Vf) > E.min())
Gb = sts['b'][1]
best = None
for DF0 in [3.0, 3.8]:
    for DF1 in [-2.4, 0.5]:
        s_ = fit(model_b, [DF0, DF1, 4.9, 5.6, 0.95, -1.34, 0.15, 3.0, 0.012], [1.0, -3, 2, 2, 0.05, -2.5, 0.02, 0.1, 0], [5, 4, 8, 8, 4, 0.5, 0.6, 30, 0.05], Gb)
        if best is None or s_.cost < best.cost: best = s_
sb = best
pb, sseb = report(sb, ['DF0', 'DF1', 'Dinf_plus', 'Dinf_minus', 'w', 'mu', 'sig', 'amp', 'b'])
xi = E0b - sb.x[5]; DF = sb.x[0] + sb.x[1] * DW; Dinf = np.where(xi >= 0, sb.x[2], sb.x[3])
D = np.sqrt(DF ** 2 + np.clip(Dinf ** 2 - DF ** 2, 0, None) * xi ** 2 / (xi ** 2 + sb.x[4] ** 2)); E = np.sqrt(xi ** 2 + D ** 2)
onFS = np.abs(xi) < 0.05
out['b'] = dict(params=pb, SSE=sseb, bcs_number_filling=float(np.mean(1 - xi / E) / 2),
                gap_on_FS_min=float(D[onFS].min()), gap_on_FS_max=float(D[onFS].max()), Emin=float(E.min()))
# noise level estimate (variance in the gap of panel a, times N)
out['noise_SSE_estimate'] = float(np.var(Ga[np.abs(Vf) < 3.5]) * len(Vf))

# ---------------- spectral weight check (occupied / empty) ----------------
wt = {}
for pan, b, edge in [('a', pa['b'][0], 3.9), ('b', pb['b'][0], 2.5), ('c', pc['b0'][0], 1.6)]:
    V, G = sts[pan]; Gs = G - b * np.abs(V) * (np.abs(V) > edge)
    occ = np.trapezoid(Gs[(V < 0) & (V > -9)], V[(V < 0) & (V > -9)]); emp = np.trapezoid(Gs[(V > 0) & (V < 9)], V[(V > 0) & (V < 9)])
    wt[pan] = dict(occupied=float(occ), empty=float(emp), implied_nu=float(occ / (occ + emp)))
V, G = sts['d']; Gs = G - pd['b0'][0] * np.abs(V) * ((V < -3.9) | (V > 4.2))
occ = np.trapezoid(Gs[(V < 0) & (V > -4.3)], V[(V < 0) & (V > -4.3)]); emp = np.trapezoid(Gs[(V > 0) & (V < 4.6)], V[(V > 0) & (V < 4.6)])
wt['d'] = dict(occupied=float(occ), empty=float(emp), implied_nu=float(occ / (occ + emp)))
out['weights'] = wt
save_json(out, 'sts_fits.json')

# ---------------- figure ----------------
fig, axs = plt.subplots(2, 2, figsize=(13, 8.5), sharex=True)
titles = {'a': r'(a) $\nu=1/2$, low $T$', 'b': r'(b) $\nu\approx0.3$, low $T$', 'c': r'(c) $\nu\approx0.2$, low $T$', 'd': r'(d) $\nu\approx0.3$, high $T$'}
curves = {'a': [(model_a(sa.x), 'rung-singlet (SMG) insulator: $E_\\pm=\\pm\\Phi+(\\epsilon_k-\\epsilon_c)/2$', 'C3', '-'),
                (model_a_hyb(sah.x), 'Hubbard-I / hybridization form', 'C0', '--'),
                (model_a_bcs(sab.x), 'BCS (mirror) form', 'C2', ':')],
          'b': [(model_b(sb.x), 'strong-coupling two-gap s-wave state', 'C3', '-')],
          'c': [(model_c(sc.x), 'BCS, isotropic $\\Delta$ on bare band', 'C3', '-')],
          'd': [(model_d(sd.x), 'bare $t$-$t\'$ band', 'C3', '-')]}
for ax, pan in zip(axs.ravel(), ['a', 'b', 'c', 'd']):
    V, G = sts[pan]
    ax.plot(V, G, color='0.35', lw=0.6, label='data')
    for y, lab, col, ls in curves[pan]:
        ax.plot(Vf, y, color=col, ls=ls, lw=1.6, label=lab)
    ax.set_title(titles[pan]); ax.set_ylim(-0.05, 1.15); ax.legend(fontsize=7.5, loc='upper left')
    ax.grid(alpha=0.25)
for ax in axs[1]: ax.set_xlabel('bias $V/D$')
for ax in axs[:, 0]: ax.set_ylabel('$dI/dV$ (normalized)')
fig.tight_layout(); fig.savefig(f'{FIG}/fig1_sts_fits.png', dpi=140)
for k in ['d', 'a', 'c', 'b']:
    print(k, out[k] if k != 'a' else {kk: out['a'][kk] for kk in out['a']})
print('weights', wt)
