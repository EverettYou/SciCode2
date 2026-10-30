"""Predicted low-temperature ARPES intensity / f(omega) = A(k,omega) along (0,0)->(1/2,0)->(1/2,1/2)->(0,0)
for nu=1/2 (ED-calibrated two-pole strong-coupling spectrum), nu~0.2 and nu~0.3 (interlayer-singlet
Bogoliubov spectra with the measured gaps), with ED poles overlaid.  Writes figures/arpes.png, data/arpes_*.npz"""
import json, os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import brentq
sys.path.insert(0, '.'); from band import eps, path_kpoints, kgrid, filling
import calib
fit = json.load(open('../data/fit_results.json')); cal = json.load(open('../data/ed_calibration.json'))
d3 = json.load(open('../data/ed_3x3_path.json')) if os.path.exists('../data/ed_3x3_path.json') else {}
kx, ky, s, ticks = path_kpoints(160); ek = eps(kx, ky)
def lor(w, w0, eta): return eta/np.pi/((w-w0)**2+eta**2)

# ---------------- nu = 1/2 ----------------
b = cal.get('bands_3x3') or cal['bands_4x2']
mu_half = b['mu']
def half_model(qx, qy):
    f = b['fits']
    Ep = calib.ev(f['Ep'], qx, qy) - mu_half; Eh = calib.ev(f['Eh'], qx, qy) - mu_half
    wp = np.clip(calib.ev(f['wp'], qx, qy), 0.02, 1); wh = np.clip(calib.ev(f['wh'], qx, qy), 0.02, 1)
    nk = np.clip(calib.ev(f['nk'], qx, qy), 0.05, 0.95)
    wp_rest = np.clip(1-nk-wp, 0, None); wh_rest = np.clip(nk-wh, 0, None)
    return Ep, Eh, wp, wh, wp_rest, wh_rest, nk
def A_half(qx, qy, w, eta=0.12, eta_sat=1.2):
    Ep, Eh, wp, wh, wpr, whr, nk = half_model(qx, qy)
    A = wp[:, None]*lor(w[None, :], Ep[:, None], eta) + wh[:, None]*lor(w[None, :], Eh[:, None], eta)
    A += wpr[:, None]*lor(w[None, :], (Ep+b['sat_p_offset'])[:, None], eta_sat) + whr[:, None]*lor(w[None, :], (Eh+b['sat_h_offset'])[:, None], eta_sat)
    return A
w = np.linspace(-12, 12, 961)
A1 = A_half(kx, ky, w)

# ---------------- BCS spectra ----------------
def bcs_A(e, w, mu, Delta, eta=0.12):
    xi = e-mu; E = np.sqrt(xi**2+Delta**2); u2 = 0.5*(1+xi/E); v2 = 1-u2
    return u2[:, None]*lor(w[None, :], E[:, None], eta) + v2[:, None]*lor(w[None, :], -E[:, None], eta)
mu02, D02 = fit['panel_c']['mu'][0], fit['panel_c']['Delta'][0]
# nu~0.3: gap edge from panel (b); mu from the number equation at nu=0.301 with that Delta
D03 = 0.5*(abs(fit['panel_b']['gap_edges'][0])+abs(fit['panel_b']['gap_edges'][1]))
KX, KY = kgrid(500); EK = eps(KX, KY).ravel()
def nu_of(mu, D): xi = EK-mu; return 0.5*np.mean(1-xi/np.sqrt(xi**2+D**2))
mu03 = brentq(lambda m: nu_of(m, D03)-0.301, -8, 4)
mu02_check = brentq(lambda m: nu_of(m, D02)-0.20, -8, 4)
print(f'nu~0.2: Delta={D02:.3f} mu(fit)={mu02:.3f}, mu(number eq.)={mu02_check:.3f};  nu~0.3: Delta_edge={D03:.3f}, mu(number eq.)={mu03:.3f}')
w2 = np.linspace(-7, 7, 701)
A2 = bcs_A(ek, w2, mu02, D02); A3 = bcs_A(ek, w2, mu03, D03)
np.savez('../data/arpes_spectra.npz', s=s, kx=kx, ky=ky, w_half=w, A_half=A1, w_sc=w2, A_02=A2, A_03=A3, mu_half=mu_half, mu02=mu02, mu03=mu03, D02=D02, D03=D03)

# ---------------- ED poles along the path (3x3 grid points that lie on the path) ----------------
def ed_points(key, mu_shift):
    pts = []
    for bcn in ('pp', 'ap', 'aa'):
        rec = d3.get(f'{key}_{bcn}', {})
        for kk, v in rec.get('A', {}).items():
            qx, qy = map(float, kk.split(','))
            # position along the path, if on it (use C4 image (qy,qx) too)
            for (ax_, ay_) in ((qx, qy), (qy, qx)):
                if abs(ay_) < 1e-6 and 0 <= ax_ <= np.pi+1e-6: sp = ax_
                elif abs(ax_-np.pi) < 1e-6 and 0 <= ay_ <= np.pi+1e-6: sp = np.pi+ay_
                elif abs(ax_-ay_) < 1e-6 and 0 <= ax_ <= np.pi+1e-6: sp = 2*np.pi+np.sqrt(2)*(np.pi-ax_)
                else: continue
                for br, sign in (('add', 1), ('rem', -1)):
                    if br in v:
                        for p_, w_ in zip(*v[br]):
                            if w_ > 0.02: pts.append((sp, p_-mu_shift, w_))
                break
    return pts
def mu_doped(key):
    """chemical potential of a doped sector: midpoint between lowest addition and highest removal pole"""
    lo, hi = [], []
    for bcn in ('pp', 'ap', 'aa'):
        for kk, v in d3.get(f'{key}_{bcn}', {}).get('A', {}).items():
            if 'add' in v and v['add'][0]: lo.append(min(v['add'][0]))
            if 'rem' in v and v['rem'][0]: hi.append(max(v['rem'][0]))
    return 0.5*(min(lo)+max(hi)) if lo and hi else 0.0

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
panels = [(A1, w, 'a) $\\nu=1/2$: SMG insulator (ED-calibrated two-pole spectrum)', 'N18', mu_half),
          (A3, w2, 'b) $\\nu\\approx0.3$: strongly paired SC, $\\Delta$=%.2f' % D03, 'N12', None),
          (A2, w2, 'c) $\\nu\\approx0.2$: BCS-like SC, $\\Delta$=%.2f' % D02, 'N8', None)]
for ax, (A, ww, title, key, mu_) in zip(axes, panels):
    im = ax.imshow(A.T, origin='lower', aspect='auto', extent=[s[0], s[-1], ww[0], ww[-1]], cmap='inferno', vmax=np.percentile(A, 99.5))
    ax.axhline(0, color='w', lw=0.6, ls='--'); ax.set_xticks(ticks); ax.set_xticklabels(['(0,0)', '(1/2,0)', '(1/2,1/2)', '(0,0)'])
    ax.set_title(title, fontsize=9); ax.set_ylabel('$\\omega/D$ (from $\\mu$)'); ax.set_ylim(ww[0], ww[-1])
    if d3:
        pts = ed_points(key, mu_ if mu_ is not None else mu_doped(key))
        if pts:
            P = np.array(pts); ax.scatter(P[:, 0], P[:, 1], s=60*P[:, 2], facecolors='none', edgecolors='cyan', lw=0.8, label='ED 3x3 poles (area = weight)')
            ax.legend(fontsize=7, loc='upper right')
fig.colorbar(im, ax=axes, fraction=0.02, label='A(k,$\\omega$)')
fig.savefig('../figures/arpes.png', dpi=150, bbox_inches='tight')
print('mu_half (gap midpoint, absolute) =', mu_half)

# ---------------- k-integrated spectrum at nu=1/2 versus the STS trace (a) ----------------
KXg, KYg = kgrid(400); Eg = eps(KXg, KYg).ravel()
Ag = A_half(KXg.ravel(), KYg.ravel(), w, eta=0.08, eta_sat=1.2).mean(0)
V = np.array(json.load(open('/home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem/measurements.json'))['measurements'][0]['spectra'][0]['bias'])
y = np.array(json.load(open('/home/yzyou/SciCode2/benchmarks/lattice-gap-mechanism/problem/measurements.json'))['measurements'][0]['spectra'][0]['dI_dV'])
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.plot(V, y, color='0.6', lw=0.8, label='STS (a) data')
Agn = Ag/Ag[(w > 3) & (w < 9)].max()
ax.plot(w, Agn, 'r-', lw=1, label='ED-calibrated spectrum, k-integrated (norm. to particle peak)')
Ep1 = 6+Eg/2; Eh1 = -6+Eg/2; m1 = 0.5*(Ep1.min()+Eh1.max())
A1k = (0.5*lor(w[None, :], (Ep1-m1)[:, None], 0.08) + 0.5*lor(w[None, :], (Eh1-m1)[:, None], 0.08)).mean(0)
ax.plot(w, A1k/A1k.max(), 'b--', lw=0.8, label='first-order theory (equal residues)')
ax.set_xlim(-12, 12); ax.set_xlabel('$\\omega/D$'); ax.set_ylabel('DOS (norm.)'); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig('../figures/sts_half_model.png', dpi=140)
hole_peak = Agn[(w < -3) & (w > -9)].max(); print('model k-integrated: hole-side peak / particle-side peak =', hole_peak)
