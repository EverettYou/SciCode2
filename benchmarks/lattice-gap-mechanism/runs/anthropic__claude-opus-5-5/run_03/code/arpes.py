"""Predicted low-temperature ARPES intensity (after division by the Fermi function) = A(k, w) (matrix elements
set to 1, layer-summed; t_perp = 0 so bonding/antibonding coincide) along Gamma-X-M-Gamma for nu = 1/2, ~0.3, ~0.2."""
import numpy as np, json
from common import eps_k, save_json, FIG, RES, twogap_delta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fit = json.load(open(f'{RES}/sts_fits.json'))
t = fit['d']['params']['t'][0]; tp = fit['d']['params']['tp'][0]
pa = {k: v[0] for k, v in fit['a']['translated_copies']['params'].items()}
pc = {k: v[0] for k, v in fit['c']['params'].items()}
pb = {k: v[0] for k, v in fit['b']['params'].items()}
ec = -4 * tp

# momentum path (units of 2pi/a)
G, X, M = np.array([0, 0]), np.array([0.5, 0]), np.array([0.5, 0.5])
segs = [(G, X), (X, M), (M, G)]
ks, dist, ticks = [], [], [0.0]; d0 = 0.0
for (a, b) in segs:
    L = np.linalg.norm(b - a); n = int(400 * L)
    for s in np.linspace(0, 1, n, endpoint=False):
        ks.append(a + s * (b - a)); dist.append(d0 + s * L)
    d0 += L; ticks.append(d0)
ks.append(G); dist.append(d0)
ks, dist = np.array(ks), np.array(dist)
kx, ky = ks[:, 0], ks[:, 1]
cx, cy = np.cos(2 * np.pi * kx), np.cos(2 * np.pi * ky)
e = eps_k(kx, ky, t, tp)
w = np.linspace(-9.5, 9.5, 1901)
gam = 0.10   # Lorentzian half-width (lifetime + resolution)

def lor(w, E, Z):
    return Z[:, None] * (gam / np.pi) / ((w[None, :] - E[:, None]) ** 2 + gam ** 2)

# nu = 1/2 : rung-singlet (SMG) insulator, leading-order strong coupling, energies from mid-gap
x = e - ec
Ep, Em = pa['Phi'] + 0.5 * x, -pa['Phi'] + 0.5 * x
Zp, Zm = 0.5 * (1 + pa['alpha'] * x), 0.5 * (1 - pa['alpha'] * x)
A_half = lor(w, Ep, Zp) + lor(w, Em, Zm)
# nu ~ 0.2 : BCS
xi = pc['g'] * e - pc['mu']; E = np.sqrt(xi ** 2 + pc['Delta'] ** 2)
A_02 = lor(w, E, 0.5 * (1 + xi / E)) + lor(w, -E, 0.5 * (1 - xi / E))
# nu ~ 0.3 : strong-coupling two-gap s-wave state
xi3 = e - pb['mu']; D3 = twogap_delta(xi3, cx, cy, pb['DF0'], pb['DF1'], pb['Dinf_plus'], pb['Dinf_minus'], pb['w'])
E3 = np.sqrt(xi3 ** 2 + D3 ** 2)
A_03 = lor(w, E3, 0.5 * (1 + xi3 / E3)) + lor(w, -E3, 0.5 * (1 - xi3 / E3))

# characteristic momenta along the path
def crossings(f):
    s = np.where(np.sign(f[:-1]) != np.sign(f[1:]))[0]
    return [(float(dist[i]), [float(kx[i]), float(ky[i])]) for i in s]
info = dict(
    nu_half=dict(lower_band_at_G=float(Em[0]), lower_band_at_X=float(Em[np.argmin(np.abs(dist - 0.5))]),
                 lower_band_at_M=float(Em[np.argmin(np.abs(dist - 1.0))]), Z_lower_G=float(Zm[0]), Z_lower_M=float(Zm[np.argmin(np.abs(dist - 1.0))]),
                 luttinger_surface_crossings=crossings(e - ec)),
    nu_0p3=dict(kF_crossings=crossings(xi3), gap_at_kF=[float(D3[np.argmin(np.abs(dist - c[0]))]) for c in crossings(xi3)],
                occ_band_at_G=float(-E3[0]), occ_band_at_X=float(-E3[np.argmin(np.abs(dist - 0.5))]), occ_band_at_M=float(-E3[np.argmin(np.abs(dist - 1.0))])),
    nu_0p2=dict(kF_crossings=crossings(xi), gap=pc['Delta'], occ_band_at_G=float(-E[0]), occ_band_at_X=float(-E[np.argmin(np.abs(dist - 0.5))]),
                occ_band_at_M=float(-E[np.argmin(np.abs(dist - 1.0))])))
save_json(info, 'arpes_features.json')

labels = [r'$\Gamma$', 'X', 'M', r'$\Gamma$']
def panel(ax, A, title, wmin, wmax, marks=()):
    m = (w >= wmin) & (w <= wmax)
    im = ax.pcolormesh(dist, w[m], A[:, m].T, shading='auto', cmap='magma', vmin=0, vmax=np.percentile(A[:, m], 99.3))
    for tk in ticks: ax.axvline(tk, color='w', lw=0.6, alpha=0.6)
    ax.axhline(0, color='c', lw=0.8, ls='--')
    for (d, lab, col) in marks: ax.axvline(d, color=col, lw=0.9, ls=':'); ax.text(d, wmin + 0.4, lab, color=col, fontsize=8, ha='center')
    ax.set_xticks(ticks); ax.set_xticklabels(labels); ax.set_title(title, fontsize=11); ax.set_ylim(wmin, wmax)
    return im

marks_half = [(c[0], 'zeros', 'lime') for c in info['nu_half']['luttinger_surface_crossings']]
marks_03 = [(c[0], r'$k_F$', 'cyan') for c in info['nu_0p3']['kF_crossings']]
marks_02 = [(c[0], r'$k_F$', 'cyan') for c in info['nu_0p2']['kF_crossings']]
for wmin, wmax, fname in [(-9.5, 1.5, 'fig4_arpes.png'), (-9.5, 9.5, 'fig4b_arpes_full_spectral_function.png')]:
    fig, axs = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
    panel(axs[0], A_half, r'$\nu=1/2$: SMG (rung-singlet) insulator', wmin, wmax, marks_half)
    panel(axs[1], A_03, r'$\nu\approx0.3$: strong-coupling s-wave SC (two-gap)', wmin, wmax, marks_03)
    im = panel(axs[2], A_02, r'$\nu\approx0.2$: BCS s-wave SC', wmin, wmax, marks_02)
    axs[0].set_ylabel(r'$\omega$ (energy from chemical potential, units of $D$)')
    if wmax > 2:
        for ax in axs: ax.axhspan(0.6, wmax, color='w', alpha=0.08)
        axs[0].text(0.03, 1.0, 'ω>0: not accessible by ARPES at low T (f(ω)→0); shown for completeness', color='w', fontsize=7.5)
    fig.colorbar(im, ax=axs, shrink=0.8, label='A(k,ω) (arb. units)')
    fig.savefig(f'{FIG}/{fname}', dpi=140, bbox_inches='tight')

# EDCs
fig, axs = plt.subplots(1, 3, figsize=(15, 4.6), sharey=False)
def edc(ax, A, idxs, title):
    for i, (j, lab) in enumerate(idxs):
        ax.plot(w, A[j] + 0.0 * i, label=lab)
    ax.set_xlim(-9.5, 1.5); ax.set_title(title); ax.set_xlabel(r'$\omega$'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
iX = np.argmin(np.abs(dist - 0.5)); iM = np.argmin(np.abs(dist - 1.0))
iF3 = np.argmin(np.abs(dist - info['nu_0p3']['kF_crossings'][0][0])); iF2 = np.argmin(np.abs(dist - info['nu_0p2']['kF_crossings'][0][0]))
iL = np.argmin(np.abs(dist - info['nu_half']['luttinger_surface_crossings'][0][0]))
edc(axs[0], A_half, [(0, r'$\Gamma$'), (iL, 'zero surface ($\\Gamma$X)'), (iX, 'X'), (iM, 'M')], r'EDCs, $\nu=1/2$')
edc(axs[1], A_03, [(0, r'$\Gamma$'), (iF3, r'$k_F$ ($\Gamma$X)'), (iX, 'X'), (iM, 'M')], r'EDCs, $\nu\approx0.3$')
edc(axs[2], A_02, [(0, r'$\Gamma$'), (iF2, r'$k_F$ ($\Gamma$X)'), (iX, 'X'), (iM, 'M')], r'EDCs, $\nu\approx0.2$')
fig.tight_layout(); fig.savefig(f'{FIG}/fig4c_arpes_edcs.png', dpi=140)
print(json.dumps(info, indent=1))
