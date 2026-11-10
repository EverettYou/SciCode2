import sys; sys.path.insert(0,'/app/work')
import numpy as np
from fitlib import kgrid, ebar
from models import spectrum_half, T_HOP, TP_HOP, U_HUB
from vizstyle import *
import matplotlib.pyplot as plt
setup()
nk = 400; kx, ky = kgrid(nk); eb = ebar(kx,ky,T_HOP,TP_HOP); ek = eb + 4*TP_HOP
sigma = 0.084
# Kramers-Kronig of a Gaussian-broadened pole at E: ReG(0) = P∫ A(w')/(0-w') dw'  -> computed numerically on a fine grid
wgrid = np.arange(-14, 14.0001, 0.002)
def KK0(E):
    """Re G(k,0) contribution of unit-weight Gaussian pole at E (vectorized over E via interpolation table)"""
    Et = np.linspace(-13, 13, 5201); vals = np.zeros_like(Et)
    for i,e in enumerate(Et):
        A = np.exp(-(wgrid-e)**2/(2*sigma**2))/(np.sqrt(2*np.pi)*sigma)
        m = np.abs(wgrid) > 1e-9
        vals[i] = np.trapezoid(A[m]/(0-wgrid[m]), wgrid[m])
    return np.interp(E, Et, vals)
quad = np.load('/app/work/fit_a_quad.npy')
def spectrum_quad(kx,ky):
    a1,a2,a3 = quad[6],quad[7],quad[8]; dlt = a3+a1*eb+a2*eb**2
    return [(eb/2-U_HUB/2, 0.5-dlt),(eb/2+U_HUB/2, 0.5+dlt)]
variants = {'free (best-fit linear weights)':spectrum_half(kx,ky,'free'), 'quadratic-weight fit':spectrum_quad(kx,ky),
            'Hubbard-I weights':spectrum_half(kx,ky,'HI'), 'constant weights 1/2':spectrum_half(kx,ky,'const')}
results = {}
for name,bands in variants.items():
    ReG = np.zeros_like(eb)
    for E,Z in bands: ReG += Z*KK0(E)
    omega_z = sum(Z*E for E,Z in bands)  # Z-E+ + Z+E- = zero of G (since Z-+Z+=1): omega_z = Z_- E_+ + Z_+ E_-
    (Em,Zm),(Ep,Zp) = bands; omega_z = Zm*Ep + Zp*Em
    sign00 = np.sign(ReG[nk//2, nk//2])  # k=(0,0) is at index nk//2 (grid from -pi to pi)
    frac_same = np.mean(np.sign(ReG) == sign00)
    frac_pos = np.mean(ReG > 0)
    results[name] = (ReG, omega_z, frac_same, frac_pos)
    print(f"{name}: ReG(0,0)={ReG[nk//2,nk//2]:+.4f}, ReG(pi,pi)={ReG[0,0]:+.4f}, ReG(pi,0)={ReG[0,nk//2]:+.4f}; fraction with sign of (0,0): {frac_same:.4f}; fraction ReG>0: {frac_pos:.4f}; Luttinger count 2*frac(ReG>0) = {2*frac_pos:.3f}; omega_z range [{omega_z.min():.3f},{omega_z.max():.3f}]")
# reference contours fractions
print("fraction ebar<0:", np.mean(eb<0), " fraction eps_k<0:", np.mean(ek<0), " fraction ebar<-1.87:", np.mean(eb<-1.87), " fraction ebar<-2.0:", np.mean(eb<-2.0))
np.savez('/app/work/luttinger_arrays.npz', kx=kx, ky=ky, eb=eb, **{f"ReG_{i}":results[n][0] for i,n in enumerate(results)}, names=np.array(list(results.keys())))
# figure: Re G(k,0) for the best-fit spectrum with zero contour, plus omega_z(ebar) for variants
fig, axes = plt.subplots(1,2, figsize=(14.5,5.8), gridspec_kw={'wspace':0.42})
ReG = results['free (best-fit linear weights)'][0]
vmax = np.abs(ReG).max()
im = axes[0].pcolormesh(kx/np.pi, ky/np.pi, ReG, cmap=DIV, vmin=-vmax, vmax=vmax, shading='auto')
axes[0].contour(kx/np.pi, ky/np.pi, ReG, levels=[0], colors=C['ink'], linewidths=2)
axes[0].contour(kx/np.pi, ky/np.pi, eb, levels=[0], colors=C['ink2'], linewidths=1, linestyles='--')
axes[0].contour(kx/np.pi, ky/np.pi, ek, levels=[0], colors=C['muted'], linewidths=1, linestyles=':')
axes[0].set_xlabel('$k_x$ (units of $2\\pi/a$)'); axes[0].set_ylabel('$k_y$ (units of $2\\pi/a$)'); axes[0].set_aspect('equal'); axes[0].grid(False)
axes[0].set_xticks([-1,-0.5,0,0.5,1]); axes[0].set_xticklabels(['-1/2','-1/4','0','1/4','1/2']); axes[0].set_yticks([-1,-0.5,0,0.5,1]); axes[0].set_yticklabels(['-1/2','-1/4','0','1/4','1/2'])
axes[0].set_title('(a) Re$\\,G(k,\\omega=0)$ at $\\nu=1/2$ from Kramers–Kronig of the predicted spectrum', fontsize=10, loc='left')
cb = fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04); cb.set_label('Re$\\,G(k,0)$  ($D^{-1}$)', labelpad=2)
axes[0].annotate('zeros of $G$ (Luttinger surface)\nfraction inside = %.3f' % results['free (best-fit linear weights)'][2], xy=(0,0.62), ha='center', fontsize=9, color=C['ink'])
axes[0].annotate('dashed: $\\bar\\varepsilon_k=0$ (31%)\ndotted: $\\varepsilon_k=0$ (42%)', xy=(0,-0.75), ha='center', fontsize=9, color=C['ink2'])
ebl = np.linspace(-4,4,200)
cols = [C['half'], C['violet'], C['03'], C['02']]
for (name,(ReGv,oz,fs,fp)),col in zip(results.items(), cols):
    # omega_z as function of ebar: bin
    idx = np.digitize(eb.ravel(), ebl); ozm = np.array([oz.ravel()[idx==i].mean() if np.any(idx==i) else np.nan for i in range(1,len(ebl))])
    axes[1].plot(0.5*(ebl[1:]+ebl[:-1]), ozm, color=col, lw=2, label=f"{name}: enclosed fraction {fs:.2f}" if fs<0.999 else f"{name}: no zero at $\\omega=0$")
axes[1].axhline(0, color=C['ink2'], lw=0.8, ls='--'); axes[1].set_xlabel('$\\bar\\varepsilon_k$ (bare band energy measured from band midpoint)'); axes[1].set_ylabel('$\\omega_z(k)$: energy at which $G(k,\\omega)=0$  ($D$)')
axes[1].set_title('(b) Surface of zeros $\\omega_z(k)$ for different spectral-weight assignments', fontsize=10, loc='left'); axes[1].legend(fontsize=8, loc='upper left')
plt.savefig('/app/figures/fig_luttinger.png', dpi=150, bbox_inches='tight')
print("luttinger figure done")
