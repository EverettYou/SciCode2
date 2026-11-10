"""Figures: data vs. effective-theory curves for STS, NMR, resistivity."""
import json, numpy as np, sys
sys.path.insert(0, '/app/theory'); from common import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.integrate import quad
with open('/app/measurements.json') as f: d = json.load(f)
sts = {s['panel']: s for s in d['measurements'][0]['spectra']}
nmr = {s['filling']: s for s in d['measurements'][1]['samples']}
res = {s['filling']: s for s in d['measurements'][2]['samples']}
N = 700; KX, KY = kgrid(N); E = eps_k(KX, KY).ravel()
egrid = np.arange(-14, 14, 0.01); de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(En, w):
    h,_ = np.histogram(En, bins=bins, weights=w); return h/de/En.size
def broaden(A, eta):
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    ker = (eta/np.pi)/(x**2+eta**2); ker/=ker.sum(); return np.convolve(A, ker, mode='same')
bc = band_constants()
def model_curve(panel, V):
    if panel == 'a':   # two-pole, canonical weights
        Ep = 6.0 + (E-bc['ebar'])/2; Em = -6.0 + (E-bc['ebar'])/2
        wm = 0.5*(1 - E/12.0); wp = 1-wm
        A = hist(np.concatenate([Ep,Em]), np.concatenate([wp,wm])); A = broaden(A, 0.085)
        scale, b, c0 = 6.82, 0.0013, 0.004
    elif panel == 'b':
        mu, Dpg, Dc, eta = -0.734, 4.32, 1.56, 0.21
        xi = E-mu; root = np.sqrt(xi**2/4 + Dpg**2); Ep = xi/2+root; Em = xi/2-root
        wp = 0.5*(1+xi/np.sqrt(xi**2+Dc**2)); wm = 1-wp
        mid = 0.5*(Ep.min()+Em.max())
        A = hist(np.concatenate([Ep-mid,Em-mid]), np.concatenate([wp,wm])); A = broaden(A, eta)
        scale, b, c0 = 6.14, 0.0011, 0.015
    elif panel == 'c':
        mu, D = -1.919, 1.965; xi = E-mu; Ek = np.sqrt(xi**2+D**2); u2 = 0.5*(1+xi/Ek)
        A = hist(np.concatenate([Ek,-Ek]), np.concatenate([u2,1-u2])); A = broaden(A, 0.083)
        scale, b, c0 = 5.97, 0.0012, 0.011
    elif panel == 'd':
        mu = -0.893; A = hist(E-mu, np.ones_like(E)); A = broaden(A, 0.101)
        scale, b, c0 = 3.38, 0.0014, 0.003
    return scale*np.interp(V, egrid, A) + b*V**2 + c0

fig, axs = plt.subplots(2, 2, figsize=(14, 9), constrained_layout=True)
titles = {'a': r'(a) $\nu=1/2$, low $T$: local-pair insulator, $U=12.0\,D$, bands $\pm U/2+\varepsilon_k/2$',
          'b': r'(b) $\nu\approx0.3$, low $T$: preformed-pair SC, $\Sigma=\Delta_{pg}^2/\omega$, $\Delta_{pg}=4.3\,D$',
          'c': r'(c) $\nu\approx0.2$, low $T$: BCS, $\Delta=1.97\,D$ on the bare band',
          'd': r'(d) $\nu\approx0.3$, high $T$: bare band, $t=1.00\,D$, $t^\prime=0.196\,D$'}
for ax, p in zip(axs.flat, 'abcd'):
    V = np.array(sts[p]['bias']); y = np.array(sts[p]['dI_dV'])
    ax.plot(V, y, lw=0.7, color='C0', label='data')
    ax.plot(V, model_curve(p, V), lw=1.2, color='C3', label='effective theory (+ $bV^2$ background)')
    ax.set_title(titles[p], fontsize=10); ax.set_xlabel('bias $V/D$'); ax.set_ylabel('$dI/dV$ (norm.)'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.savefig('/app/figures/fig_sts_fits.png', dpi=140)

# ---------------- NMR ----------------
def nmr_bcs(T, D0=1.965, Gamma=0.05, Tc=1.965/1.764):
    D = 0.0 if T >= Tc else D0*np.tanh(1.74*np.sqrt(Tc/T-1))
    w = np.linspace(-30, 30, 60001); dw = w[1]-w[0]; z = w + 1j*Gamma
    Ns = np.real(z/np.sqrt(z**2 - D**2)); Ms = np.real(D/np.sqrt(z**2 - D**2))
    f = 1/(np.exp(np.clip(w/T,-300,300))+1)
    return np.sum((Ns**2 + Ms**2)*f*(1-f))*dw
fig, axs = plt.subplots(1, 2, figsize=(14, 5.5), constrained_layout=True)
ax = axs[0]
cols = {'1/2':'C3', '≈0.3':'C2', '≈0.2':'C0'}
for nu in ['1/2','≈0.3','≈0.2']:
    s = nmr[nu]; T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    ax.errorbar(1/T, r/T, yerr=u/T, fmt='o', ms=3.5, color=cols[nu], label=rf'$\nu={nu}$ data')
Tm = np.linspace(0.19, 12, 600)
# nu=1/2: Arrhenius with Delta_s = 5.7 (1/T1T ∝ exp(-Delta_s/T)), normalised at T=4
ax.plot(1/Tm, np.exp(-5.7/Tm)/np.exp(-5.7/4), color='C3', lw=1.2, label=r'$\nu=1/2$: $e^{-\Delta_s/T}$, $\Delta_s=5.7\,D\approx|U|/2$')
ax.plot(1/Tm, np.minimum(1.0, 2.1*np.exp(-2.64/Tm)), color='C2', lw=1.2, label=r'$\nu\approx0.3$: $\min(1,\,2.1\,e^{-\Delta_s/T})$, $\Delta_s=2.64\,D\approx E_g/2$; gap closes at $T^*\approx3$')
m = np.array([nmr_bcs(t) for t in Tm]); m = m/ (np.interp(4.0, Tm, m)) * 4.0
ax.plot(1/Tm, m/Tm, color='C0', lw=1.2, label=r'$\nu\approx0.2$: BCS Hebel-Slichter, $\Delta=1.97\,D$, $\Gamma=0.05\,D$')
ax.set_yscale('log'); ax.set_ylim(1e-5, 3); ax.set_xlim(0, 5.2); ax.set_xlabel('$D/T$'); ax.set_ylabel('$1/(T_1T)$ (norm. at $T=4D$)'); ax.legend(fontsize=7.5); ax.grid(alpha=0.3)
ax.set_title('NMR spin-lattice relaxation')
# ---------------- resistivity ----------------
ax = axs[1]
for nu in ['1/2','≈0.3','≈0.2']:
    s = res[nu]; T = np.array(s['temperature']); r = np.array(s['resistivity']); u = np.array(s['uncertainty'])
    ax.errorbar(T, r, yerr=u, fmt='o', ms=3.5, color=cols[nu], label=rf'$\nu={nu}$ data')
Tr = np.linspace(0.42, 4.05, 400)
ax.plot(Tr, np.exp(3.72*(1/Tr - 1/4)), color='C3', lw=1.2, label=r'$\nu=1/2$: $\rho\propto e^{\Delta_\rho/T}$, $\Delta_\rho=3.72\,D\approx E_g/2$')
Tr2 = np.linspace(0.36, 4.05, 400); r2 = 0.16 + 0.70*np.exp(0.98/Tr2); r2 = r2/np.interp(4.0, Tr2, r2)
ax.plot(np.concatenate([[0.1,0.36],Tr2]), np.concatenate([[1e-3,1e-3],r2]), color='C2', lw=1.2, label=r'$\nu\approx0.3$: $\rho_0+a\,e^{0.98/T}$ above $T_c=0.36$')
Tr3 = np.linspace(1.11, 4.05, 300)
ax.plot(np.concatenate([[0.1,1.11],Tr3]), np.concatenate([[1e-3,1e-3],0.176+0.175*Tr3]), color='C0', lw=1.2, label=r'$\nu\approx0.2$: $\rho=0.18+0.175\,T$ above $T_c=1.11$')
ax.set_yscale('symlog', linthresh=0.3); ax.set_ylim(-0.02, 3000); ax.set_xlabel('$T/D$'); ax.set_ylabel(r'$\rho_{ab}$ (norm. at $T=4D$)'); ax.legend(fontsize=7.5); ax.grid(alpha=0.3)
ax.set_title('In-plane resistivity')
plt.savefig('/app/figures/fig_nmr_rho_fits.png', dpi=140)
print('figures written')
