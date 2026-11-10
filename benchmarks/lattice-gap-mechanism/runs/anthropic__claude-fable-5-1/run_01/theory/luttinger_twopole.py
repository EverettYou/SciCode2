"""Kramers-Kronig reconstruction of Re G(k, 0) from the predicted nu=1/2 spectrum (two-pole strong-coupling model),
zeros of Re G(k, 0) with the chemical potential at mid-gap, and the enclosed BZ fraction, for several weight tilts."""
import numpy as np, sys, json
sys.path.insert(0, '/app/theory')
from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import ndimage

N = 240
KX, KY = kgrid(N)
w = np.arange(-14, 14, 0.01) + 0.005   # symmetric about 0 -> principal value
out = {}
fig, axs = plt.subplots(1, 3, figsize=(16, 5), constrained_layout=True)
cases = [('canonical strong-coupling weights (Dc = U = 12)', 12.0, 0.0),
         ('fitted weights (Dc = 16.2, centre -0.11)', 16.2, -0.11),
         ('intermediate (Dc = 14, centre -0.05)', 14.0, -0.05)]
for ax, (label, Dc, c) in zip(axs, cases):
    A, (Em, Ep, wm, wp) = A_halffilling(KX, KY, w, U=12.0, eta=0.084, Dc=Dc, tilt_center=c)
    # Kramers-Kronig: Re G(k, 0) = P int A(k,w')/(0 - w') dw' = - int A/w' dw'  (gap => no singularity at w'=0)
    ReG_KK = -np.trapz(A/w[None,None,:], w, axis=-1)
    ReG_exact = wm/(-Em) + wp/(-Ep)   # exact two-pole value
    sgn0 = np.sign(ReG_KK[N//2, N//2])
    lab, nlab = ndimage.label(np.sign(ReG_KK) == sgn0)
    frac = np.mean(lab == lab[N//2, N//2]); frac_same = np.mean(np.sign(ReG_KK) == sgn0)
    has_curve = (np.sign(ReG_KK).min() != np.sign(ReG_KK).max())
    out[label] = dict(Dc=Dc, centre=c, ReG_at_Gamma=float(ReG_KK[N//2,N//2]), ReG_at_M=float(ReG_KK[0,0]), ReG_at_X=float(ReG_KK[0,N//2]),
                      zero_curve_exists=bool(has_curve), fraction_containing_origin=float(frac), fraction_same_sign=float(frac_same), n_regions=int(nlab),
                      max_abs_diff_KK_vs_exact=float(np.max(np.abs(ReG_KK-ReG_exact))))
    print(label, json.dumps(out[label], indent=1))
    vm = np.max(np.abs(ReG_KK))
    im = ax.imshow(ReG_KK.T, origin='lower', extent=[-0.5,0.5,-0.5,0.5], cmap='RdBu_r', vmin=-vm, vmax=vm)
    if has_curve: ax.contour(KX[:,0]/(2*np.pi), KY[0,:]/(2*np.pi), ReG_KK.T, levels=[0], colors='k')
    # bare Fermi surface at half filling for reference
    E = eps_k(KX, KY); ax.contour(KX[:,0]/(2*np.pi), KY[0,:]/(2*np.pi), (E - mu_bare(0.5)).T, levels=[0], colors='lime', linestyles='--')
    ax.set_title(label + f'\nzero curve: {has_curve}; fraction with (0,0): {frac:.3f}', fontsize=9)
    ax.set_xlabel(r'$k_x$ ($2\pi/a$)'); ax.set_ylabel(r'$k_y$ ($2\pi/a$)')
    plt.colorbar(im, ax=ax, shrink=0.8, label=r'Re $G(k,0)$ (1/D)')
fig.suptitle(r'Two-pole strong-coupling spectrum at $\nu=1/2$: Re $G(k,\omega=0)$ from Kramers-Kronig ($\mu$ at mid-gap). Dashed green: bare Fermi surface at $\nu=1/2$ (encloses 0.5).')
plt.savefig('/app/figures/fig_luttinger_twopole.png', dpi=130)
json.dump(out, open('/app/theory/luttinger_twopole.json','w'), indent=1)
# Also the analytic condition: zero where w- E+ + w+ E- = 0 (pole of Sigma at mid-gap)
E = eps_k(KX, KY); bc = band_constants()
for label, Dc, c in cases:
    wp_pole = (E - bc['ebar'])/2 - 6.0*(E - c)/Dc     # omega_p(k) relative to mid-gap
    print(f"{label}: Sigma-pole position omega_p(k) ranges over [{wp_pole.min():.3f}, {wp_pole.max():.3f}] (crosses 0 -> zero curve) ")
