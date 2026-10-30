"""Extract model parameters from measurements.json.
Outputs data/fit_results.json and figures/fit_*.png"""
import json, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '.')
from band import eps, dos, filling, mu_of_filling, kgrid

ROOT = '/home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem'
d = json.load(open(f'{ROOT}/measurements.json'))['measurements']
sts, nmr, res = d
spec = {s['panel']: (np.array(s['bias']), np.array(s['dI_dV'])) for s in sts['spectra']}
out = {}

def dos_on(V, t1, t2, mu, sigma):
    """normal-state DOS at bias V (energy relative to mu), broadened"""
    E = V + mu
    return dos(E, t1, t2, n=1600, sigma=0)*1.0 if sigma == 0 else gaussian_filter1d(dos(E, t1, t2, n=1600, sigma=0), sigma/(V[1]-V[0]))

# ---------------- panel (d): normal-state band ----------------
V, y = spec['d']
def model_d(p, V):
    t1, t2, mu, a, b, sig = p
    rho = dos_on(V, t1, t2, mu, abs(sig))
    m = a*rho
    inband = rho > 1e-3
    bg = b*(V/9.0)**2*(~inband)
    return m + bg
def resid_d(p): return model_d(p, V) - y
p0 = [1.0, 0.2, -0.9, 5.0, 0.1, 0.05]
fit = least_squares(resid_d, p0, diff_step=2e-2, bounds=([0.5, -0.5, -4, 0, 0, 0.01], [2, 0.5, 4, 50, 1, 0.5]))
J = fit.jac; cov = np.linalg.pinv(J.T@J)*np.sum(fit.fun**2)/(len(V)-len(p0))
err = np.sqrt(np.diag(cov))
names = ['t1', 't2', 'mu', 'amp', 'bg', 'sigma']
out['panel_d'] = {n: [float(v), float(e)] for n, v, e in zip(names, fit.x, err)}
out['panel_d']['chi2_per_dof'] = float(np.sum(fit.fun**2)/(len(V)-6))
out['panel_d']['nu_from_mu'] = float(filling(fit.x[2], fit.x[0], fit.x[1]))
print('panel d fit:', out['panel_d'])
# band edges in the data: last/first bias where y>0.25 within the band
t1d, t2d, mud = fit.x[:3]
out['panel_d']['edges_model'] = [float(-4*t1d-4*t2d-mud), float(4*t1d-4*t2d-mud)]
out['panel_d']['vanhove_model'] = float(4*t2d-mud)

# ---------------- panel (a): half filling, strong-coupling two-band DOS ----------------
V, y = spec['a']
def dos_half(V, t1, t2, Ep, Eh, wp, wh, sig):
    """particle band at Ep+eps/2, hole band at Eh+eps/2 (weights wp, wh)"""
    kx, ky = kgrid(1200); e2 = (eps(kx, ky, t1, t2)/2).ravel()
    dV = V[1]-V[0]
    bins = np.concatenate([V-dV/2, [V[-1]+dV/2]])
    hp, _ = np.histogram(e2+Ep, bins=bins); hh, _ = np.histogram(e2+Eh, bins=bins)
    rho = (wp*hp + wh*hh)/(len(e2)*dV)
    return gaussian_filter1d(rho, sig/dV)
def model_a(p, V):
    t1, t2, Ep, Eh, wp, wh, b, sig = p
    rho = dos_half(V, t1, t2, Ep, Eh, wp, wh, abs(sig))
    gap = (V > Eh+2*t1-2*t2+0.05) & (V < Ep-2*t1-2*t2-0.05)
    return rho + b*(V/9)**2*(~gap)*(rho < 1e-3)
def resid_a(p): return model_a(p, V) - y
p0 = [1.0, 0.2, 6.4, -5.6, 2.0, 2.0, 0.1, 0.05]
fit = least_squares(resid_a, p0, diff_step=2e-2, bounds=([0.5, -0.5, 3, -9, 0, 0, 0, 0.01], [2, 0.5, 9, -3, 20, 20, 1, 0.5]))
J = fit.jac; cov = np.linalg.pinv(J.T@J)*np.sum(fit.fun**2)/(len(V)-len(p0)); err = np.sqrt(np.diag(cov))
names = ['t1', 't2', 'Ep', 'Eh', 'wp', 'wh', 'bg', 'sigma']
out['panel_a'] = {n: [float(v), float(e)] for n, v, e in zip(names, fit.x, err)}
t1a, t2a, Ep, Eh, wp, wh = fit.x[:6]
out['panel_a']['edge_particle'] = float(Ep-2*t1a-2*t2a)
out['panel_a']['edge_hole'] = float(Eh+2*t1a-2*t2a)
out['panel_a']['gap_total'] = float(Ep-Eh-4*t1a)
out['panel_a']['weight_ratio_p_over_h'] = float(wp/wh)
out['panel_a']['chi2_per_dof'] = float(np.sum(fit.fun**2)/(len(V)-8))
print('panel a fit:', out['panel_a'])
# model-free gap edges: threshold crossing of smoothed data
ys = gaussian_filter1d(y, 3)
i0 = 400
lo = i0
while ys[lo] < 0.02: lo -= 1
hi = i0
while ys[hi] < 0.02: hi += 1
out['panel_a']['edges_threshold'] = [float(V[lo]), float(V[hi])]
print('panel a threshold edges', V[lo], V[hi])

# ---------------- panel (c): BCS DOS ----------------
V, y = spec['c']
def bcs_dos(V, t1, t2, mu, Delta, sig):
    kx, ky = kgrid(1000); xi = (eps(kx, ky, t1, t2)-mu).ravel()
    E = np.sqrt(xi**2+Delta**2); u2 = 0.5*(1+xi/E); v2 = 1-u2
    dV = V[1]-V[0]; bins = np.concatenate([V-dV/2, [V[-1]+dV/2]])
    hp, _ = np.histogram(E, bins=bins, weights=u2); hh, _ = np.histogram(-E, bins=bins, weights=v2)
    rho = (hp+hh)/(len(xi)*dV)
    return gaussian_filter1d(rho, sig/dV)
def model_c(p, V):
    t1, t2, mu, Delta, a, b, sig = p
    rho = a*bcs_dos(V, t1, t2, mu, Delta, abs(sig))
    return rho + b*(V/9)**2*(np.abs(V) > Delta+0.05)*(rho < 1e-3)
def resid_c(p): return model_c(p, V) - y
fit = None
for mu0, D0 in ((-1.9, 2.0), (-2.4, 1.7), (-2.8, 1.5), (-1.5, 2.3)):
    p0 = [1.0, 0.2, mu0, D0, 5.0, 0.1, 0.05]
    f_ = least_squares(resid_c, p0, diff_step=2e-2, bounds=([0.5, -0.5, -5, 0.5, 0, 0, 0.01], [2, 0.5, 3, 4, 50, 1, 0.5]))
    print(f'  panel c start mu={mu0} Delta={D0}: cost {f_.cost:.5f} -> mu={f_.x[2]:.3f} Delta={f_.x[3]:.3f}')
    if fit is None or f_.cost < fit.cost: fit = f_
J = fit.jac; cov = np.linalg.pinv(J.T@J)*np.sum(fit.fun**2)/(len(V)-len(p0)); err = np.sqrt(np.diag(cov))
names = ['t1', 't2', 'mu', 'Delta', 'amp', 'bg', 'sigma']
out['panel_c'] = {n: [float(v), float(e)] for n, v, e in zip(names, fit.x, err)}
out['panel_c']['nu_from_mu'] = float(filling(fit.x[2], fit.x[0], fit.x[1]))
out['panel_c']['chi2_per_dof'] = float(np.sum(fit.fun**2)/(len(V)-7))
print('panel c fit:', out['panel_c'])

# ---------------- panel (b): model-free features ----------------
V, y = spec['b']
ys = gaussian_filter1d(y, 3)
lo = 400
while ys[lo] < 0.02: lo -= 1
hi = 400
while ys[hi] < 0.02: hi += 1
# outer edges: where smoothed data drops below 0.25 going outward from the peaks
ip = np.argmax(ys); ih = np.argmax(ys[:400])
ho = ih
while ys[ho] > 0.25: ho -= 1
po = ip
while ys[po] > 0.25: po += 1
out['panel_b'] = {'gap_edges': [float(V[lo]), float(V[hi])], 'peak_hole': [float(V[ih]), float(ys[ih])],
                  'peak_particle': [float(V[ip]), float(ys[ip])], 'outer_edges': [float(V[ho]), float(V[po])],
                  'weight_hole_side': float(np.trapezoid(np.clip(y[:400]-0.11*(V[:400]/9)**2*(V[:400] < V[ho]), 0, None), V[:400])),
                  'weight_particle_side': float(np.trapezoid(np.clip(y[400:]-0.11*(V[400:]/9)**2*(V[400:] > V[po]), 0, None), V[400:]))}
print('panel b:', out['panel_b'])

# ---------------- NMR ----------------
out['nmr'] = {}
for s in nmr['samples']:
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    rec = {}
    windows = {'≈0.3': [(0.0, 0.36), (0.4, 2.0)], '≈0.2': [(0.0, 0.47)]}.get(s['filling'], [])
    for Tmin, Tmax in windows + [(0.0, 2.0), (0.0, 4.0)]:
        m = (T <= Tmax) & (T > Tmin) & (r > 3*u)
        x = 1/T[m]; yv = np.log(r[m]/T[m]); w = r[m]/u[m]
        A = np.vstack([x, np.ones_like(x)]).T*w[:, None]
        coef, *_ = np.linalg.lstsq(A, yv*w, rcond=None)
        resid = (A@coef - yv*w); dof = max(m.sum()-2, 1)
        cov = np.linalg.inv(A.T@A)*max(1.0, np.sum(resid**2)/dof)
        rec[f'slope_T1T_Tmax{Tmax}' if Tmin == 0.0 and (Tmin, Tmax) not in windows else f'slope_T1T_T{Tmin}-{Tmax}'] = [float(-coef[0]), float(np.sqrt(cov[0, 0]))]
    # Korringa check: 1/(T1 T) at T>=4 relative to T=4
    m = T >= 4
    rec['T1T_high'] = [[float(t), float(rr/t)] for t, rr in zip(T[m], r[m])]
    out['nmr'][s['filling']] = rec
    print('NMR', s['filling'], rec)
# Hebel-Slichter peak height at nu~0.2
s = nmr['samples'][2]; T = np.array(s['temperature']); r = np.array(s['one_over_T1'])
k = r/T; i = np.argmax(k[(T > 0.2) & (T < 2.0)]); sub = np.where((T > 0.2) & (T < 2.0))[0]
out['nmr']['≈0.2']['HS_peak'] = [float(T[sub[i]]), float(k[sub[i]])]
print('HS peak', out['nmr']['≈0.2']['HS_peak'])

# ---------------- resistivity ----------------
out['res'] = {}
for s in res['samples']:
    T = np.array(s['temperature']); r = np.array(s['resistivity']); u = np.array(s['uncertainty'])
    rec = {}
    m = r > 0
    if (~m).any():
        rec['Tc_bracket'] = [float(T[~m].max()), float(T[m].min())]
        rec['Tc'] = [float(0.5*(T[~m].max()+T[m].min())), float(0.5*(T[m].min()-T[~m].max()))]
    for Tmax in (1.0, 2.0, 4.0):
        mm = m & (T <= Tmax)
        if mm.sum() > 3:
            x = 1/T[mm]; yv = np.log(r[mm]); w = r[mm]/u[mm]
            A = np.vstack([x, np.ones_like(x)]).T*w[:, None]
            coef, *_ = np.linalg.lstsq(A, yv*w, rcond=None)
            resid = (A@coef - yv*w); dof = max(mm.sum()-2, 1)
            cov = np.linalg.inv(A.T@A)*max(1.0, np.sum(resid**2)/dof)
            rec[f'activation_Tmax{Tmax}'] = [float(coef[0]), float(np.sqrt(cov[0, 0]))]
    out['res'][s['filling']] = rec
    print('RES', s['filling'], rec)

json.dump(out, open('../data/fit_results.json', 'w'), indent=1)

# ---------------- figure of the fits ----------------
fig, ax = plt.subplots(2, 2, figsize=(11, 7))
for a, pan in zip(ax.flat, 'abcd'):
    V, y = spec[pan]
    a.plot(V, y, color='0.6', lw=0.7, label='data')
    if pan == 'd':
        p = [out['panel_d'][n][0] for n in ['t1', 't2', 'mu', 'amp', 'bg', 'sigma']]; a.plot(V, model_d(p, V), 'r', lw=1, label='band DOS fit')
    if pan == 'a':
        p = [out['panel_a'][n][0] for n in ['t1', 't2', 'Ep', 'Eh', 'wp', 'wh', 'bg', 'sigma']]; a.plot(V, model_a(p, V), 'r', lw=1, label='two-band fit')
    if pan == 'c':
        p = [out['panel_c'][n][0] for n in ['t1', 't2', 'mu', 'Delta', 'amp', 'bg', 'sigma']]; a.plot(V, model_c(p, V), 'r', lw=1, label='BCS DOS fit')
    a.set_title(f'panel ({pan})'); a.legend(fontsize=8); a.set_xlabel('V/D'); a.set_ylabel('dI/dV (norm.)')
fig.tight_layout(); fig.savefig('../figures/fit_sts.png', dpi=130)
