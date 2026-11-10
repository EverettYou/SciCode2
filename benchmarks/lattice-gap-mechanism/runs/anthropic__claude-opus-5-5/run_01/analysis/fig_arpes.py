"""Task 4: predicted low-T ARPES intensity / f(w) (= A(k,w), top layer) along G-X-M-G for the three fillings."""
import numpy as np, os, json, sys
import vizstyle as vs
vs.apply()
import matplotlib.pyplot as plt

OUT = '/app/figures'


def eps(k, t=1.0, tp=0.2):
    return -2 * t * (np.cos(k[:, 0]) + np.cos(k[:, 1])) - 4 * tp * np.cos(k[:, 0]) * np.cos(k[:, 1])


def kf_cross(dist, f):
    s = np.sign(f); idx = np.where(np.diff(s) != 0)[0]
    return [dist[i] + (dist[i + 1] - dist[i]) * (-f[i]) / (f[i + 1] - f[i]) for i in idx]


def draw(ax, z, title, vmax, overlay=None):
    w = z['w'] - float(z['midgap']); A = z['A']; dist = z['dist']; ticks = z['ticks']
    im = ax.imshow(A.T, origin='lower', aspect='auto', extent=[dist[0], dist[-1], w[0], w[-1]], cmap=vs.SEQ,
                   vmin=0, vmax=vmax, interpolation='bilinear')
    ax.axhline(0, color=vs.MUTED, lw=0.6)
    ax.set_xticks(ticks); ax.set_xticklabels([r'$\Gamma$' + '\n(0,0)', r'$X$' + '\n' + r'$(\frac{1}{2},0)$',
                                               r'$M$' + '\n' + r'$(\frac{1}{2},\frac{1}{2})$', r'$\Gamma$' + '\n(0,0)'])
    for x in ticks[1:-1]:
        ax.axvline(x, color=vs.GRID, lw=0.6)
    ax.set_ylim(-10, 10); ax.set_title(title, loc='left', fontsize=10.5); ax.grid(False)
    return im


if __name__ == '__main__':
    half = sys.argv[1] if len(sys.argv) > 1 else 'cgf_fin_half_3x2_analysis.npz'
    halflab = sys.argv[2] if len(sys.argv) > 2 else '12-site'
    zh = np.load(half); z3 = np.load('sc_akw_nu0.3.npz'); z2 = np.load('sc_akw_nu0.2.npz')
    vmax = 0.55 * max(np.percentile(zh['A'], 99.5), np.percentile(z3['A'], 99.5), np.percentile(z2['A'], 99.5))
    fig, axs = plt.subplots(1, 3, figsize=(16.5, 6.0), sharey=True)
    im = draw(axs[0], zh, r'$\nu=1/2$  rung-singlet insulator' + f'\n(CPT, {halflab} bilayer cluster)', vmax)
    # first-order strong-coupling bands for comparison
    kp = zh['kpath']; e = eps(kp); ec = -0.8
    Eex = 12.1
    for sgn in (+1, -1):
        axs[0].plot(zh['dist'], sgn * Eex / 2 + (e - ec) / 2 - sgn * 0.0, color=vs.C_03, lw=0.9, ls=(0, (1, 2)),
                    label=r'$\pm E_{ex}/2+(\epsilon_k-\epsilon_c)/2$' if sgn > 0 else None)
    im = draw(axs[1], z3, r'$\nu\approx0.3$  s$^{\pm}$ superconductor, strong pairing' + '\n' +
              r'($\Delta_0=2.85$ at $k_F$, local scale $5.2$)', vmax)
    im = draw(axs[2], z2, r'$\nu\approx0.2$  s$^{\pm}$ superconductor, BCS-like' + '\n' + r'($\Delta=2.0$)', vmax)
    for ax, z in [(axs[1], z3), (axs[2], z2)]:
        kp = z['kpath']; xi = eps(kp) - float(z['mu0'])
        ax.plot(z['dist'], xi, color=vs.C_03, lw=0.9, ls=(0, (1, 2)), label=r'bare band $\epsilon_k-\mu$')
        for x in kf_cross(z['dist'], xi):
            ax.axvline(x, color=vs.INK2, lw=0.7, ymin=0.42, ymax=0.58)
        ax.text(0.98, 0.035, r'ticks at $\omega=0$: underlying $k_F$', transform=ax.transAxes, ha='right', fontsize=7.5,
                color=vs.INK2)
    axs[0].set_ylabel(r'$\omega$ relative to $\mu$  ($D$)')
    for ax in axs:
        ax.legend(loc='upper left', fontsize=7.5, frameon=True, facecolor=vs.SURFACE, edgecolor=vs.GRID)
        ax.set_xlabel(r'momentum along $\Gamma$–$X$–$M$–$\Gamma$  (units of $2\pi/a$)')
    cb = fig.colorbar(im, ax=axs, fraction=0.012, pad=0.01, extend='max')
    cb.set_label(r'$I_{\rm ARPES}/f(\omega)=A(\mathbf{k},\omega)$, common linear scale')
    plt.savefig(f'{OUT}/fig4_arpes_predictions.png', dpi=130, bbox_inches='tight')
    print('ok')
