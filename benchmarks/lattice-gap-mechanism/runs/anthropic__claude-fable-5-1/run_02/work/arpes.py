import sys; sys.path.insert(0,'/app/work')
import numpy as np
from fitlib import ebar
from models import spectrum_half, spectrum_03, spectrum_02, SIGMA, T_HOP, TP_HOP
from vizstyle import *
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
setup()
# k-path (0,0)->(pi,0)->(pi,pi)->(0,0)
n1,n2,n3 = 300,300,424
seg1 = np.stack([np.linspace(0,np.pi,n1,endpoint=False), np.zeros(n1)],1)
seg2 = np.stack([np.full(n2,np.pi), np.linspace(0,np.pi,n2,endpoint=False)],1)
seg3 = np.stack([np.linspace(np.pi,0,n3), np.linspace(np.pi,0,n3)],1)
path = np.concatenate([seg1,seg2,seg3]); kx, ky = path[:,0], path[:,1]
dist = np.concatenate([[0],np.cumsum(np.hypot(np.diff(kx),np.diff(ky)))]); ticks = [0, dist[n1], dist[n1+n2], dist[-1]]
w = np.arange(-9, 9.0001, 0.02)
def intensity(bands, sigma):
    A = np.zeros((len(w), len(kx)))
    for E,Z in bands:
        A += Z[None,:]*np.exp(-(w[:,None]-E[None,:])**2/(2*sigma**2))/(np.sqrt(2*np.pi)*sigma)
    return A
sig = 0.15
A_half = intensity(spectrum_half(kx,ky,'free'), sig)
A_03 = intensity(spectrum_03(kx,ky), sig)
b02, xi02, D02 = spectrum_02(kx,ky); A_02 = intensity(b02, sig)
np.savez('/app/work/arpes_arrays.npz', dist=dist, w=w, A_half=A_half, A_03=A_03, A_02=A_02, ticks=ticks, kx=kx, ky=ky)
eb = ebar(kx,ky,T_HOP,TP_HOP)
fig, axes = plt.subplots(1,3, figsize=(15,6.2), sharey=True)
titles = [r'(a) $\nu=1/2$: Mott insulator', r'(b) $\nu\approx0.3$: paired (pseudogap) state', r'(c) $\nu\approx0.2$: BCS superconductor']
for ax, A, ttl in zip(axes, [A_half, A_03, A_02], titles):
    im = ax.imshow(A, origin='lower', aspect='auto', extent=[dist[0], dist[-1], w[0], w[-1]], cmap=SEQ, norm=PowerNorm(0.5, vmin=0, vmax=A.max()*0.9))
    ax.axhline(0, color=C['ink2'], lw=0.8, ls='--'); ax.set_xticks(ticks); ax.set_xticklabels(['(0,0)','(1/2,0)','(1/2,1/2)','(0,0)'])
    for tk in ticks[1:-1]: ax.axvline(tk, color=C['axis'], lw=0.6)
    ax.set_title(ttl, fontsize=11, loc='left'); ax.grid(False); ax.set_xlabel('momentum along path')
axes[0].set_ylabel(r'energy $\omega$ relative to $\mu$ (units of $D$)')
# annotations
axes[0].annotate('upper Hubbard band  $E_+=\\bar\\varepsilon_k/2+U/2$', xy=(dist[n1]*0.08, 2.3), color=C['ink'], fontsize=9, ha='left')
axes[0].annotate('lower Hubbard band  $E_-=\\bar\\varepsilon_k/2-U/2$', xy=(dist[n1]*0.08, -2.9), color=C['ink'], fontsize=9, ha='left')
axes[0].annotate('Mott gap 8.0$D$\n(no state at $\\mu$)', xy=(dist[n1+n2]*0.98, 0.4), color=C['ink2'], fontsize=9, ha='right')
axes[1].annotate('upper branch: weight $\\to 0$ near (0,0)', xy=(dist[n1]*0.5, 7.2), color=C['ink'], fontsize=9, ha='center')
axes[1].annotate('lower branch: weight $\\to 0$ beyond $\\bar\\varepsilon_k\\approx1.5$', xy=(dist[n1+n2]*0.75, -7.6), color=C['ink'], fontsize=9, ha='center')
axes[1].annotate('pair gap $2\\Delta_{pg}^{edge}=5.0D$\nno back-bending', xy=(dist[-1]*0.72, 0.4), color=C['ink2'], fontsize=9, ha='center')
axes[2].annotate('Bogoliubov bands $\\pm\\sqrt{\\xi_k^2+\\Delta^2}$, back-bending at $k_F$', xy=(dist[n1+n2]*0.5, -7.5), color=C['ink'], fontsize=9, ha='center')
axes[2].annotate('$2\\Delta=3.9D$', xy=(dist[-1]*0.9, 0.4), color=C['ink2'], fontsize=9, ha='right')
axes[2].annotate('van Hove at (1/2,0)\n$E\\approx3.3D$', xy=(dist[n1], 7.0), color=C['ink2'], fontsize=9, ha='center')
cb = fig.colorbar(im, ax=axes, fraction=0.025, pad=0.01); cb.set_label('$A(k,\\omega)$ (arb. units, sqrt scale)')
fig.suptitle('Predicted low-temperature ARPES intensity divided by the Fermi function (Gaussian resolution 0.15$D$)', fontsize=12, x=0.45)
plt.savefig('/app/figures/fig_arpes.png', dpi=160, bbox_inches='tight')
# weights along the path
fig2, axes2 = plt.subplots(1,3, figsize=(15,3.6), sharey=True)
for ax, bands, ttl, col in zip(axes2, [spectrum_half(kx,ky,'free'), spectrum_03(kx,ky), b02], titles, [C['half'],C['03'],C['02']]):
    (El,Zl),(Eu,Zu) = bands
    ax.plot(dist, Zl, color=col, lw=2, label='lower branch weight'); ax.plot(dist, Zu, color=col, lw=2, ls='--', label='upper branch weight')
    ax.set_xticks(ticks); ax.set_xticklabels(['(0,0)','(1/2,0)','(1/2,1/2)','(0,0)']); ax.set_title(ttl, fontsize=10, loc='left'); ax.set_ylim(0,1.5)
axes2[0].set_ylabel('spectral weight $Z_\\pm(k)$'); axes2[0].legend(loc='upper center', fontsize=9)
plt.savefig('/app/figures/fig_arpes_weights.png', dpi=140, bbox_inches='tight')
print("ARPES figures done; ticks", ticks)
# print a few numbers for the report
for name,(El,Zl),(Eu,Zu) in [('half',*spectrum_half(kx,ky,'free')),('03',*spectrum_03(kx,ky)),('02',*b02)]:
    for lab,i in [('(0,0)',0),('(1/2,0)',n1),('(1/2,1/2)',n1+n2)]:
        print(f"{name} {lab}: E_lower={El[i]:.2f} Z={Zl[i]:.2f} | E_upper={Eu[i]:.2f} Z={Zu[i]:.2f}")
