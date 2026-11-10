import numpy as np, matplotlib, json
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
import sys; sys.path.insert(0, '/app/theory')
from common import *

kx, ky, dist, ticks, labels = kpath(600)
fig, axs = plt.subplots(1, 3, figsize=(17, 6.2), constrained_layout=True)
specs = []
# --- nu = 1/2
w = np.linspace(-10, 10, 801)
A, (Em, Ep, wm, wp) = A_halffilling(kx, ky, w, U=12.0, eta=0.15)
specs.append(('nu = 1/2 : local-pair (Mott-type) insulator', w, A, [Em, Ep]))
# --- nu ~ 0.3
w2 = np.linspace(-8, 8, 801)
A2, (Em2, Ep2, _, _) = A_localpair(kx, ky, w2, mu=-0.75, Dpg=4.3, Dc=2.0, eta=0.15)
specs.append(('nu ~ 0.3 : preformed-pair superconductor', w2, A2, [Em2, Ep2]))
# --- nu ~ 0.2
w3 = np.linspace(-6, 7, 801)
A3, (Em3, Ep3, _, _) = A_bcs(kx, ky, w3, mu=mu_bare(0.2), Delta=1.965, eta=0.12)
specs.append(('nu ~ 0.2 : BCS superconductor', w3, A3, [Em3, Ep3]))

for ax, (title, ww, AA, bands) in zip(axs, specs):
    im = ax.pcolormesh(dist, ww, AA.T, shading='auto', cmap='magma', norm=PowerNorm(gamma=0.5, vmin=0, vmax=np.percentile(AA, 99.7)))
    for b in bands: ax.plot(dist, b, color='cyan', lw=0.6, alpha=0.6, ls='--')
    ax.axhline(0, color='w', lw=0.8, ls=':')
    ax.set_xticks(ticks); ax.set_xticklabels(labels); ax.set_title(title, fontsize=11)
    ax.set_ylabel(r'$\omega$ (units of $D$), measured from $\mu$')
    for t_ in ticks[1:-1]: ax.axvline(t_, color='w', lw=0.5, alpha=0.5)
    plt.colorbar(im, ax=ax, label=r'$A(k,\omega)$ (arb.)', shrink=0.8)
fig.suptitle(r'Predicted low-$T$ ARPES intensity divided by the Fermi function, $A(k,\omega)$, along (0,0)$\to$(1/2,0)$\to$(1/2,1/2)$\to$(0,0)', fontsize=12)
plt.savefig('/app/figures/fig_arpes.png', dpi=150)
# save the bands along the path for the report
np.savez('/app/theory/arpes_bands.npz', dist=dist, kx=kx, ky=ky, Em=Em, Ep=Ep, Em2=Em2, Ep2=Ep2, Em3=Em3, Ep3=Ep3, ticks=ticks)
# Print key numbers: band extrema along path
def report(name, Em, Ep):
    i = lambda arr, f: dist[f(arr)]
    print(f"{name}: lower band from {Em.min():.2f} to {Em.max():.2f}; upper band from {Ep.min():.2f} to {Ep.max():.2f}; gap = {Ep.min()-Em.max():.2f}")
    print(f"   lower-band top at path position {i(Em,np.argmax):.3f}, upper-band bottom at {i(Ep,np.argmin):.3f}  (ticks {np.round(ticks,3)})")
report('nu=1/2', Em, Ep); report('nu=0.3', Em2, Ep2); report('nu=0.2', Em3, Ep3)
# k_F crossing for nu=0.2 and 0.3 along path (where xi=0)
for nu, mu in [(0.2, mu_bare(0.2)), (0.32, -0.75)]:
    xi = eps_k(kx, ky) - mu
    s = np.where(np.diff(np.sign(xi))!=0)[0]
    print(f"nu={nu}: bare Fermi crossings along path at positions {np.round(dist[s],3)} ; mu_bare={mu:.3f}")
