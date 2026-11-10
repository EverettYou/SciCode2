"""Combined Luttinger-surface figure: CPT (2x2, 2x4, [3x4 if available]) for U=-12 and the two-pole model variants."""
import numpy as np, json, glob, sys
sys.path.insert(0,'/app/theory'); from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import ndimage
N = 240; KX, KY = kgrid(N); E = eps_k(KX, KY); muh = mu_bare(0.5)
tags = [t for t in ['2x2_U-12','2x4_U-12','3x4_U-12','2x2_U12','2x4_U12','3x4_U12'] if glob.glob(f'/app/theory/cpt_{t}.npz')]
fig, axs = plt.subplots(2, 4, figsize=(20, 9.5), constrained_layout=True)
axs = axs.ravel()
summary = {}
for ax, tag in zip(axs, tags):
    z = np.load(f'/app/theory/cpt_{tag}.npz'); ReG = z['ReG']; kg = z['kg']; Ng = len(kg)
    if tag[0] != tag[2]:   # rectangular cluster: restore C4 by averaging over the two cluster orientations
        ReG = 0.5*(ReG + ReG.T)
        lab, nl = ndimage.label(np.sign(ReG) == np.sign(ReG[Ng//2, Ng//2])); z = dict(z); z['frac'] = np.mean(lab == lab[Ng//2, Ng//2])
    vm = np.max(np.abs(ReG))
    im = ax.imshow(ReG.T, origin='lower', extent=[-0.5,0.5,-0.5,0.5], cmap='RdBu_r', vmin=-vm, vmax=vm)
    ax.contour(kg/(2*np.pi), kg/(2*np.pi), ReG.T, levels=[0], colors='k', linewidths=1.5)
    ax.contour(KX[:,0]/(2*np.pi), KY[0,:]/(2*np.pi), (E-muh).T, levels=[0], colors='lime', linestyles='--', linewidths=1)
    frac = float(z['frac']); summary[tag] = dict(fraction=frac, gap=float(z['hi']-z['lo']), mu_mid=float(z['mu_mid']))
    ax.set_title(f'CPT {tag.replace("_"," ")}' + (' (C4-symmetrised)' if tag[0]!=tag[2] else '') + f': zeros of Re G(k,0)\nfraction containing (0,0) = {frac:.3f}; gap = {float(z["hi"])-float(z["lo"]):.2f} D', fontsize=9)
    ax.set_xlabel(r'$k_x$ ($2\pi/a$)'); ax.set_ylabel(r'$k_y$ ($2\pi/a$)')
    plt.colorbar(im, ax=ax, shrink=0.75)
# two-pole variants in remaining axes
cases = [('two-pole, canonical weights ($D_c=U$)', 12.0, 0.0), ('two-pole, fitted weights ($D_c=16.2$)', 16.2, -0.11)]
for ax, (label, Dc, c) in zip(axs[len(tags):], cases):
    A, (Em, Ep, wm, wp) = A_halffilling(KX, KY, np.array([0.0]), U=12.0, eta=0.084, Dc=Dc, tilt_center=c)
    ReG = wm/(-Em) + wp/(-Ep)
    vm = np.max(np.abs(ReG))
    im = ax.imshow(ReG.T, origin='lower', extent=[-0.5,0.5,-0.5,0.5], cmap='RdBu_r', vmin=-vm, vmax=vm)
    has = np.sign(ReG).min() != np.sign(ReG).max()
    if has:
        ax.contour(KX[:,0]/(2*np.pi), KY[0,:]/(2*np.pi), ReG.T, levels=[0], colors='k', linewidths=1.5)
        lab, nl = ndimage.label(np.sign(ReG) == np.sign(ReG[N//2,N//2])); frac = float(np.mean(lab == lab[N//2,N//2]))
    else: frac = float('nan')
    ax.contour(KX[:,0]/(2*np.pi), KY[0,:]/(2*np.pi), (E-muh).T, levels=[0], colors='lime', linestyles='--', linewidths=1)
    ax.set_title(label + f'\nzero curve: {"yes" if has else "none"}; fraction = {frac:.3f}', fontsize=9)
    ax.set_xlabel(r'$k_x$ ($2\pi/a$)'); ax.set_ylabel(r'$k_y$ ($2\pi/a$)'); plt.colorbar(im, ax=ax, shrink=0.75)
    summary[label] = dict(fraction=frac, zero_curve=bool(has))
for ax in axs[len(tags)+len(cases):]: ax.axis('off')
fig.suptitle(r'$\nu=1/2$: Re $G(k,\omega=0)$ with $\mu$ at mid-gap (red > 0, blue < 0). Black: Luttinger surface of zeros. Dashed green: bare Fermi surface at $\nu=1/2$ (encloses exactly 0.5).', fontsize=12)
plt.savefig('/app/figures/fig_luttinger.png', dpi=130)
json.dump(summary, open('/app/theory/luttinger_summary.json','w'), indent=1)
print(json.dumps(summary, indent=1))
