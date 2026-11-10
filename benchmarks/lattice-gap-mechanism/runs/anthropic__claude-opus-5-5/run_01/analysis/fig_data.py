"""Figures: (1) STS data vs effective-theory spectra; (2) NMR and resistivity vs fits / theory."""
import json, os, numpy as np
from scipy.ndimage import uniform_filter1d, gaussian_filter1d
import vizstyle as vs
vs.apply()
import matplotlib.pyplot as plt

d = json.load(open('/app/measurements.json'))
sts = d['measurements'][0]['spectra']; nmr = d['measurements'][1]['samples']; rho = d['measurements'][2]['samples']
OUT = '/app/figures'
os.makedirs(OUT, exist_ok=True)


def bare_dos(V, t=1.0, tp=0.195, nu=0.3, sig=0.14, Nk=800):
    k = 2 * np.pi * (np.arange(Nk) + 0.5) / Nk
    kx, ky = np.meshgrid(k, k, indexing='ij')
    e = (-2 * t * (np.cos(kx) + np.cos(ky)) - 4 * tp * np.cos(kx) * np.cos(ky)).ravel()
    mu = np.sort(e)[int(nu * len(e))]
    dV = V[1] - V[0]
    h, _ = np.histogram(e - mu, bins=np.append(V - dV / 2, V[-1] + dV / 2))
    return gaussian_filter1d(h / len(e) / dV, sig / dV)


def bcs_dos(V, mu, D, sig, t=1.0, tp=0.2, Nk=600):
    k = 2 * np.pi * (np.arange(Nk) + 0.5) / Nk
    kx, ky = np.meshgrid(k, k, indexing='ij')
    e = (-2 * t * (np.cos(kx) + np.cos(ky)) - 4 * tp * np.cos(kx) * np.cos(ky)).ravel()
    xi = e - mu; E = np.sqrt(xi ** 2 + D ** 2)
    dV = V[1] - V[0]; edges = np.append(V - dV / 2, V[-1] + dV / 2)
    h1, _ = np.histogram(E, bins=edges, weights=0.5 * (1 + xi / E))
    h2, _ = np.histogram(-E, bins=edges, weights=0.5 * (1 - xi / E))
    return gaussian_filter1d((h1 + h2) / len(e) / dV, sig / dV)


def cpt_dos(fn):
    if not os.path.exists(fn):
        return None
    z = np.load(fn)
    return z['w'] - z['midgap'], z['dos']


def scale_to(Vd, gd, wm, dm, win=9.0):
    m = np.interp(Vd, wm, dm, left=0, right=0)
    sel = np.abs(Vd) < win
    a = np.sum(m[sel] * gd[sel]) / np.sum(m[sel] ** 2)
    return a * m


def fig_sts(files):
    fig, axs = plt.subplots(2, 2, figsize=(12, 7.5), sharex=True)
    titles = {'a': r'(a) $\nu=1/2$, low $T$', 'b': r'(b) $\nu\approx0.3$, low $T$',
              'c': r'(c) $\nu\approx0.2$, low $T$', 'd': r'(d) $\nu\approx0.3$, high $T$'}
    col = {'a': vs.C_HALF, 'b': vs.C_03, 'c': vs.C_02, 'd': vs.C_03}
    for ax, s in zip(axs.ravel(), sts):
        p = s['panel']; V = np.array(s['bias']); g = np.array(s['dI_dV'])
        ax.plot(V, uniform_filter1d(g, 5), color=vs.MUTED, lw=1.0, label='STS data')
        if p == 'd':
            m = scale_to(V, g, V, bare_dos(V))
            ax.plot(V, m, color=col[p], lw=1.6, label=r'bare band, $t=1.00$, $t^\prime=0.20$, $\nu=0.30$')
        if p == 'c':
            pc = np.load('fit_c_params.npy')
            m = scale_to(V, g, V, bcs_dos(V, pc[0], pc[1], pc[2]))
            ax.plot(V, m, color=col[p], lw=1.6, label=r'BCS on bare band, $\mu=\mu_0(0.2)$, $\Delta=1.96$ (fit)')
            m2 = scale_to(V, g, V, bcs_dos(V, pc[0], 2.03, pc[2]))
            ax.plot(V, m2, color=vs.INK2, lw=1.0, ls=(0, (4, 2)), label=r'model: $J_\perp=6.6$ mean field, $\Delta=2.03$')
        if p == 'b':
            pb = np.load('fit_b_params.npy')
            import fit_b_model as fbm
            m = scale_to(V, g, V, fbm.dos(pb[0], pb[1], pb[2], pb[3]))
            ax.plot(V, m, color=col[p], lw=1.6, label=r'Bogoliubov, two-scale gap: $\Delta_0=2.85$ at $k_F$, $\Delta_\infty=5.2$')
            mu03 = fbm.mu0
            m2 = scale_to(V, g, V, bcs_dos(V, mu03, 2.44, 0.13))
            ax.plot(V, m2, color=vs.INK2, lw=1.0, ls=(0, (4, 2)), label=r'model: $J_\perp=6.6$ mean field, $\Delta=2.44$ (const.)')
        if p in files and files[p] is not None:
            r = cpt_dos(files[p][0])
            if r is not None:
                m = scale_to(V, g, *r)
                ax.plot(V, m, color=vs.INK if p != 'c' else vs.INK2, lw=1.2,
                        ls='-', label=files[p][1])
        ax.set_title(titles[p], loc='left')
        ax.set_xlim(-10, 10); ax.set_ylim(-0.03, 1.15)
        ax.legend(fontsize=8, loc='upper left')
        if p in 'cd':
            ax.set_xlabel(r'bias $V/D$  (energy relative to midgap / $\mu$)')
        if p in 'ac':
            ax.set_ylabel(r'$dI/dV$ (normalized)')
    plt.tight_layout()
    plt.savefig(f'{OUT}/fig1_sts_vs_theory.png', dpi=130)
    plt.close()


def fig_nmr_rho():
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axs[0]
    labs = {'1/2': r'$\nu=1/2$', '≈0.3': r'$\nu\approx0.3$', '≈0.2': r'$\nu\approx0.2$'}
    keys = {'1/2': '1/2', '≈0.3': '0.3', '≈0.2': '0.2'}
    for s in nmr:
        k = keys[s['filling']]
        T = np.array(s['temperature']); y = np.array(s['one_over_T1']) / T; e = np.array(s['uncertainty']) / T
        ok = y / e > 1.0
        ax.errorbar(1 / T[ok], y[ok], e[ok], fmt=vs.MARK[k], ms=5, color=vs.CRYSTAL[k], lw=0.8, capsize=2,
                    label=labs[s['filling']])
    # model curves
    x = np.linspace(0.2, 5.0, 300); T = 1 / x
    ax.plot(x, np.exp(1.376) * np.exp(-5.54 / T), color=vs.C_HALF, lw=1.4)
    ax.text(2.25, 3e-5, r'$e^{-\Delta_s/T}$, $\Delta_s=5.5$' + '\n(rung-triplet gap)', color=vs.INK2, fontsize=8)
    xx = x[(T < 1.2)]
    ax.plot(xx, 0.154 * np.exp(-2.70 * (xx - 0.98)), color=vs.C_03, lw=1.4)
    ax.text(3.0, 2.5e-3, r'$e^{-2.7/T}$ (pair gap,' + '\nunchanged at $T_c=0.36$)', color=vs.INK2, fontsize=8)
    if os.path.exists('nmr_bcs_curve.npy'):
        c = np.load('nmr_bcs_curve.npy')
        ax.plot(1 / c[0], c[1], color=vs.C_02, lw=1.4)
        ax.text(1.35, 2.3, 'BCS + Hebel–Slichter\n' + r'$\Delta(0)=1.98$, $T_c=1.11$', color=vs.INK2, fontsize=8)
    ax.set_yscale('log'); ax.set_ylim(1e-5, 6); ax.set_xlim(0, 5.2)
    ax.set_xlabel(r'$D/T$'); ax.set_ylabel(r'$1/(T_1T)$ (normalized at $T=4D$)')
    ax.set_title('NMR spin-lattice relaxation', loc='left'); ax.legend(loc='upper right', fontsize=9)
    ax = axs[1]
    for s in rho:
        k = keys[s['filling']]
        T = np.array(s['temperature']); r = np.array(s['resistivity']); e = np.array(s['uncertainty'])
        pos = r > 0
        ax.errorbar(T[pos], r[pos], e[pos], fmt=vs.MARK[k], ms=4, color=vs.CRYSTAL[k], lw=0.8, capsize=2,
                    label=labs[s['filling']])
        ax.plot(T[~pos], np.full((~pos).sum(), 1.2e-2), vs.MARK[k], ms=4, mfc='none', color=vs.CRYSTAL[k])
    Tm = np.linspace(0.42, 4, 200)
    ax.plot(Tm, np.exp(3.72 * (1 / Tm - 1 / 4)), color=vs.C_HALF, lw=1.4)
    ax.text(0.75, 900, r'$\rho\propto e^{\Delta_\rho/T}$, $\Delta_\rho=3.7\approx E_g/2$', color=vs.INK2, fontsize=8)
    ax.axvline(0.36, color=vs.C_03, lw=0.8); ax.axvline(1.11, color=vs.C_02, lw=0.8)
    ax.text(0.38, 0.03, r'$T_c=0.36$', color=vs.INK2, fontsize=8); ax.text(1.13, 0.03, r'$T_c=1.11$', color=vs.INK2, fontsize=8)
    ax.set_yscale('log'); ax.set_ylim(1e-2, 5e3); ax.set_xlim(0, 4.2)
    ax.set_xlabel(r'$T/D$'); ax.set_ylabel(r'$\rho/\rho(4D)$  (open symbols: $\rho=0$)')
    ax.set_title('In-plane resistivity', loc='left'); ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout(); plt.savefig(f'{OUT}/fig2_nmr_rho_fits.png', dpi=130); plt.close()


if __name__ == '__main__':
    import sys
    files = {}
    if os.path.exists('cgf_fin_half_4x2_analysis.npz'):
        files['a'] = ('cgf_fin_half_4x2_analysis.npz', 'model, CPT 16-site bilayer cluster ($U=1.8$, $J_\\perp=6.5$)')
    else:
        files['a'] = ('cgf_fin_half_3x2_analysis.npz', 'model, CPT 12-site bilayer cluster ($U=1.8$, $J_\\perp=6.5$)')

    fig_sts(files)
    fig_nmr_rho()
    print('figures written')
