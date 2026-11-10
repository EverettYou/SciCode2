"""Q5: Green's function of the nu = 1/2 crystal recovered by Kramers-Kronig from the predicted spectral function,
zeros at omega = 0 (chemical potential at mid-gap), and the Brillouin-zone fraction they enclose."""
import numpy as np, json
from common import kgrid, eps_c, save_json, FIG, RES
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fit = json.load(open(f'{RES}/sts_fits.json'))
t = fit['d']['params']['t'][0]; tp = fit['d']['params']['tp'][0]; dtp = fit['d']['params']['tp'][1]
pa = {k: v[0] for k, v in fit['a']['translated_copies']['params'].items()}
w = np.linspace(-14, 14, 5601); dw = w[1] - w[0]


def spectral(e, ec, Phi, alpha, gam, shape='lorentz'):
    x = e - ec
    E = np.stack([Phi + x / 2, -Phi + x / 2], 1)
    Z = np.stack([0.5 * (1 + alpha * x), 0.5 * (1 - alpha * x)], 1)
    if shape == 'lorentz':
        k = (gam / np.pi) / ((w[None, None, :] - E[:, :, None]) ** 2 + gam ** 2)
    else:
        k = np.exp(-(w[None, None, :] - E[:, :, None]) ** 2 / (2 * gam ** 2)) / np.sqrt(2 * np.pi) / gam
    return (Z[:, :, None] * k).sum(1)                       # A(k, w)


def ReG_at(A, omega=0.0):
    """Kramers-Kronig: Re G(k, omega) = P int dw' A(k, w') / (omega - w')"""
    den = omega - w
    msk = np.abs(den) > 0.5 * dw                            # principal value: drop the singular point
    return (A[:, msk] / den[None, msk]).sum(1) * dw


def zero_fraction(t, tp, Phi, alpha, gam, shape='lorentz', N=300, shift=0.0):
    cx, cy = kgrid(N); e = eps_c(cx, cy, t, tp); ec = 0.5 * (e.min() + e.max())
    out = np.empty(len(e)); B = 4000
    for i in range(0, len(e), B):
        A = spectral(e[i:i + B], ec, Phi, alpha, gam, shape)
        out[i:i + B] = ReG_at(A, omega=shift)               # omega measured from the mid-gap chemical potential
    sG = out[np.argmin(e)]                                    # sign at Gamma (band bottom)
    return np.mean(np.sign(out) == np.sign(sG)), out, e, ec


res = {}
f0, ReG, e, ec = zero_fraction(t, tp, pa['Phi'], pa['alpha'], 0.10)
res['fraction_central'] = f0
variants = {}
for lab, kw in [('lorentz_0.05', dict(gam=0.05)), ('lorentz_0.2', dict(gam=0.2)), ('gauss_0.128', dict(gam=0.128, shape='gauss')),
                ('alpha=0', dict(gam=0.1, alpha=0.0)), ('tp+1sig', dict(gam=0.1, tp=tp + dtp)), ('tp-1sig', dict(gam=0.1, tp=tp - dtp))]:
    args = dict(t=t, tp=tp, Phi=pa['Phi'], alpha=pa['alpha'], gam=0.1); args.update(kw)
    variants[lab] = zero_fraction(**args)[0]
res['variants'] = variants
# exact contour statement: zeros at eps_k = band centre (-4t') -> fraction of BZ with eps_k < -4t'
cx, cy = kgrid(1200); ee = eps_c(cx, cy, t, tp)
res['fraction_band_centre_contour'] = float(np.mean(ee < -4 * tp))
res['fraction_tp0'] = float(np.mean(eps_c(cx, cy, t, 0.0) < 0.0))
res['nu'] = 0.5
# dependence on where the chemical potential sits inside the gap (Rosch): shift omega reference
# (analytic Kramers-Kronig of the Lorentzian-broadened poles; identical to the numerical KK used above)
def ReG_analytic(x, Phi, alpha, gam, shift):
    Ep, Em = Phi + x / 2 - shift, -Phi + x / 2 - shift
    Zp, Zm = 0.5 * (1 + alpha * x), 0.5 * (1 - alpha * x)
    return -Zp * Ep / (Ep ** 2 + gam ** 2) - Zm * Em / (Em ** 2 + gam ** 2)
xg = ee - (-4 * tp)
scan = []
for s in np.linspace(-3.8, 3.8, 77):
    r = ReG_analytic(xg, pa['Phi'], pa['alpha'], 0.1, s)
    sG = r[np.argmin(ee)]
    has_zero = (r.max() > 0) and (r.min() < 0)
    scan.append((float(s), float(np.mean(np.sign(r) == np.sign(sG))) if has_zero else None))
res['fraction_vs_mu_in_gap'] = scan
res['zero_window_half_width'] = float((8.0 * t / 4) * (1 - 2 * pa['alpha'] * pa['Phi']))  # zeros at omega=delta exist for |delta| < (W/4)(1-2 alpha Phi)
cG = (4 * tp - 2) / (2 + 4 * tp); cM = (-1 + np.sqrt(1 + 4 * tp ** 2)) / (2 * tp)
res['zeros_on_path'] = dict(GX=float(np.arccos(cG) / (2 * np.pi)), GM=float(np.arccos(cM) / (2 * np.pi)))
save_json(res, 'luttinger.json')

# figure
N = 300; cxs, cys = kgrid(N)
k = (np.arange(N) + 0.5) / N
ReGm = ReG.reshape(N, N); em = e.reshape(N, N)
# re-centre BZ to [-1/2, 1/2)
kk = k - 0.5; sh = N // 2
ReGc = np.roll(np.roll(ReGm, sh, 0), sh, 1); emc = np.roll(np.roll(em, sh, 0), sh, 1)
mu_half = np.quantile(ee, 0.5)
fig, axs = plt.subplots(1, 2, figsize=(13, 5.6))
ax = axs[0]
vm = np.abs(ReGc).max()
im = ax.pcolormesh(kk, kk, ReGc.T, cmap='RdBu_r', vmin=-vm, vmax=vm, shading='auto')
ax.contour(kk, kk, ReGc.T, levels=[0], colors='k', linewidths=2.2)
ax.contour(kk, kk, emc.T, levels=[mu_half], colors='lime', linewidths=1.3, linestyles='--')
ax.contour(kk, kk, emc.T, levels=[np.quantile(ee, 0.3)], colors='orange', linewidths=1.0, linestyles=':')
ax.plot([], [], 'k-', lw=2.2, label='zeros of $G(k,0)$ (Re$G$=0), area fraction %.3f' % f0)
ax.plot([], [], '--', color='lime', label=r'non-interacting Fermi surface at $\nu=1/2$ (area 0.500)')
ax.plot([], [], ':', color='orange', label=r'non-interacting Fermi surface at $\nu=0.3$')
ax.set_aspect('equal'); ax.set_xlabel(r'$k_x$ ($2\pi/a$)'); ax.set_ylabel(r'$k_y$ ($2\pi/a$)')
ax.set_title(r'Re$\,G(k,\omega=0)$ from Kramers–Kronig, $\nu=1/2$ (μ at mid-gap)', fontsize=10)
ax.legend(fontsize=7.5, loc='lower left'); fig.colorbar(im, ax=ax, shrink=0.8)
ax = axs[1]
s = np.array([a for a, b in res['fraction_vs_mu_in_gap']]); fr = np.array([np.nan if b is None else b for a, b in res['fraction_vs_mu_in_gap']])
ax.plot(s, fr, 'o-', ms=3, label='fraction enclosed by zeros (side containing Γ)')
ax.axvspan(-3.8, s[~np.isnan(fr)].min(), color='0.85'); ax.axvspan(s[~np.isnan(fr)].max(), 3.8, color='0.85')
ax.text(-3.6, 0.85, 'no zeros of $G$\nat $\\omega=\\mu$', fontsize=8); ax.text(1.4, 0.85, 'no zeros of $G$\nat $\\omega=\\mu$', fontsize=8)
ax.plot([0], [f0], 'r*', ms=12, label='μ at mid-gap: %.3f' % f0); ax.set_ylim(-0.02, 1.02); ax.set_xlim(-3.8, 3.8)
ax.axhline(0.5, color='g', ls='--', label=r'$\nu=1/2$ (Luttinger count)'); ax.axvline(0, color='k', ls=':')
ax.set_xlabel(r'position of $\mu$ inside the gap (from mid-gap), units of $D$'); ax.set_ylabel('BZ fraction')
ax.set_title('Zero-surface volume depends on μ within the gap (no particle–hole symmetry)', fontsize=10)
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig(f'{FIG}/fig5_luttinger.png', dpi=140)
print(json.dumps({k: v for k, v in res.items() if k != 'fraction_vs_mu_in_gap'}, indent=1))
print('fraction vs mu (None = no zeros):', [(round(a, 2), None if b is None else round(b, 3)) for a, b in res['fraction_vs_mu_in_gap'] if abs(a) < 1.2])
