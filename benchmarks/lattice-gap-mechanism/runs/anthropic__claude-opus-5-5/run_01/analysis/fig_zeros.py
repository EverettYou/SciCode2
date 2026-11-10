"""Task 5 figure: zeros of G(k, w=0) at nu=1/2 (from the predicted spectrum, KK-reconstructed)."""
import numpy as np, sys, json
import os
import vizstyle as vs
vs.apply()
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm

OUT = '/app/figures'
fmain = sys.argv[1] if len(sys.argv) > 1 else 'cgf_fin_half_3x2_Gfine.npy'
lab = sys.argv[2] if len(sys.argv) > 2 else '12-site'
fctrl = 'cgf_ctrl_tp0_2x2_Gfine.npy'
G = np.load(fmain); Gc = np.load(fctrl)
nf = G.shape[0]
kf = (-np.pi + 2 * np.pi * (np.arange(nf) + 0.5) / nf) / (2 * np.pi)  # units of 2pi/a
KX, KY = np.meshgrid(kf, kf, indexing='ij')


def frac(Gm):
    s0 = np.sign(Gm[nf // 2, nf // 2]); return float(np.mean(np.sign(Gm) == s0))


def bare(kx, ky, tp=0.2):
    k1, k2 = 2 * np.pi * kx, 2 * np.pi * ky
    return -2 * (np.cos(k1) + np.cos(k2)) - 4 * tp * np.cos(k1) * np.cos(k2)


Nn = 2000; kk = 2 * np.pi * (np.arange(Nn) + 0.5) / Nn; A1, A2 = np.meshgrid(kk, kk, indexing='ij')
eall = np.sort((-2 * (np.cos(A1) + np.cos(A2)) - 0.8 * np.cos(A1) * np.cos(A2)).ravel())
mu_half = eall[len(eall) // 2]
fig = plt.figure(figsize=(14, 12.5))
gsp = fig.add_gridspec(2, 2, hspace=0.50, wspace=0.28, top=0.96, bottom=0.06)
axs = [fig.add_subplot(gsp[0, 0]), fig.add_subplot(gsp[0, 1]), fig.add_subplot(gsp[1, 0]), fig.add_subplot(gsp[1, 1])]
for ax, Gm, title, tp in [(axs[0], G, r'$t^\prime=0.2$ (this crystal), ' + lab + ' CPT', 0.2),
                          (axs[1], Gc, r'control: $t^\prime=0$ (particle–hole symmetric)', 0.0)]:
    Gn = Gm / np.abs(Gm).max()
    im = ax.pcolormesh(KX, KY, Gn, cmap=vs.DIV, norm=TwoSlopeNorm(0, -1, 1), shading='auto', rasterized=True)
    ax.contour(KX, KY, Gm, levels=[0], colors=vs.INK, linewidths=1.8)
    eb = bare(KX, KY, tp)
    mu_ref = mu_half if tp != 0 else 0.0
    ax.contour(KX, KY, eb - mu_ref, levels=[0], colors=vs.INK2, linewidths=1.0, linestyles=[(0, (4, 3))])
    f = frac(Gm)
    ax.set_title(title, loc='left', fontsize=10)
    ax.text(0.0, 0.0, 'Γ', ha='center', va='center', fontsize=11, color=vs.INK)
    ax.text(0.455, 0.455, 'M', ha='center', va='center', fontsize=11, color=vs.INK)
    ax.text(0.0, -0.40, f'Γ side of zero curve: {f:.3f} of BZ', fontsize=9.5, color=vs.INK, ha='center',
            bbox=dict(boxstyle='round,pad=0.3', fc=vs.SURFACE, ec=vs.GRID))
    ax.set_aspect('equal'); ax.set_xlim(-0.5, 0.5); ax.set_ylim(-0.5, 0.5)
    ax.set_xlabel(r'$k_x$ ($2\pi/a$)'); ax.set_ylabel(r'$k_y$ ($2\pi/a$)'); ax.grid(False)
cax = fig.add_axes([0.2, 0.495, 0.6, 0.012])
cb = fig.colorbar(im, cax=cax, orientation='horizontal')
cb.set_label(r'Re $G(\mathbf{k},\omega=0)$ / max$|$Re $G|$   (red > 0: lower-band dominated;  blue < 0: upper-band dominated)')
axs[0].plot([], [], color=vs.INK, lw=1.8, label=r'zeros of $G(\mathbf{k},0)$')
axs[0].plot([], [], color=vs.INK2, lw=1.0, ls=(0, (4, 3)), label=r'non-interacting FS at $\nu=1/2$ (encloses 0.5)')
axs[0].legend(loc='upper center', fontsize=7.5, frameon=True, facecolor=vs.SURFACE, edgecolor=vs.GRID, bbox_to_anchor=(0.5, 0.93))
# path cut
ax = axs[2]
def path_vals(Gm):
    idx = lambda x: int(np.clip(np.round((x + 0.5) * nf - 0.5), 0, nf - 1))
    pts = [(x, 0) for x in np.linspace(0, 0.5, 60, endpoint=False)] + [(0.5, y) for y in np.linspace(0, 0.5, 60, endpoint=False)] + \
          [(s, s) for s in np.linspace(0.5, 0, 85)]
    v = np.array([Gm[idx(px), idx(py)] for px, py in pts])
    d = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(np.array(pts), axis=0), axis=1))])
    return d, v
d, v = path_vals(G); d0, v0 = path_vals(Gc)
ax.plot(d, v, color=vs.C_HALF, lw=2.0, label=r'$t^\prime=0.2$')
ax.plot(d0, v0, color=vs.INK2, lw=1.2, label=r'$t^\prime=0$ control')
if os.path.exists('edgk_fin_eval.json'):
    ed = json.load(open('edgk_fin_eval.json'))
    pmap = {(0.0, 0.0): 0.0, (0.5, 0.0): 0.5, (0.5, 0.5): 1.0, (0.25, 0.25): 1.0 + 0.5 * np.sqrt(2) * 0.5}
    xs_ = []; ys_ = []
    for pt in ed['points']:
        key = tuple(np.round(pt['K_over_2pi'], 3))
        if key in pmap:
            xs_.append(pmap[key]); ys_.append(pt['G_mid'])
    xs_.append(d[-1]); ys_.append([p['G_mid'] for p in ed['points'] if np.allclose(p['K_over_2pi'], [0, 0])][0])
    ax.plot(xs_, ys_, 'D', color=vs.C_03, ms=8, mec=vs.INK, mew=0.8, label='exact 16-site periodic cluster (ED)', zorder=6)
ax.axhline(0, color=vs.MUTED, lw=0.8)
for x in [0.5, 1.0]:
    ax.axvline(x, color=vs.GRID, lw=0.8)
ax.set_xticks([0, 0.5, 1.0, d[-1]]); ax.set_xticklabels([r'$\Gamma$', r'$X$', r'$M$', r'$\Gamma$'])
ax.set_ylabel(r'Re $G(\mathbf{k},\omega=0)$'); ax.set_title('cut along Γ–X–M–Γ', loc='left', fontsize=10)
ax.legend(fontsize=8.5)
# (d) Luttinger count versus position of mu in the gap
fj = fmain.replace('_Gfine.npy', '_frac_vs_mu.json')
import os
if os.path.exists(fj):
    fv = np.array(json.load(open(fj)))
    ax = axs[3]
    ax.plot(fv[:, 0], fv[:, 1], color=vs.C_HALF, lw=2.0, marker='o', ms=4)
    ax.axhline(0.5, color=vs.INK2, lw=0.9)
    ax.axvline(0.0, color=vs.MUTED, lw=0.9)
    f0 = np.interp(0.0, fv[:, 0], fv[:, 1])
    ax.plot([0], [f0], 'o', color=vs.C_HALF, ms=9, mec=vs.SURFACE, mew=1.5, zorder=5)
    ax.annotate(f'T→0 chemical potential (midgap):\nfraction = {f0:.2f}', xy=(0, f0), xytext=(0.25, 0.92), fontsize=8.5,
                color=vs.INK, arrowprops=dict(arrowstyle='->', color=vs.INK2, lw=0.8))
    xh = np.interp(-0.5, -fv[:, 1], fv[:, 0])
    ax.annotate(f'count = ν = 1/2 only if μ sat\n{xh:+.2f} above midgap', xy=(xh, 0.5), xytext=(0.55, 0.62), fontsize=8.5,
                color=vs.INK, arrowprops=dict(arrowstyle='->', color=vs.INK2, lw=0.8))
    ax.text(0.98, 0.5, r'$\nu=1/2$', color=vs.INK2, fontsize=8.5, va='bottom', ha='right', transform=ax.get_yaxis_transform())
    ax.set_xlim(-1.0, 1.6); ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel(r'reference energy $\omega_{\rm ref}$ − midgap  ($D$)')
    ax.set_ylabel(r'fraction of BZ with $G(\mathbf{k},\omega_{\rm ref})>0$')
    ax.set_title('Luttinger count vs. position of μ in the gap (zero band)', loc='left', fontsize=10)
plt.savefig(f'{OUT}/fig5_zeros.png', dpi=130, bbox_inches='tight')
print(json.dumps({'frac_main': frac(G), 'frac_control': frac(Gc), 'mu_half_bare': float(mu_half)}))
