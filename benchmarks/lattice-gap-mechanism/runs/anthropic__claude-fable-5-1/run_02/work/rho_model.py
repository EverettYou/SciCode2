import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar
from models import spectrum_half, T_HOP, TP_HOP
from vizstyle import *
import matplotlib.pyplot as plt
setup()
d = json.load(open('/app/measurements.json'))
res = {s['filling']:(np.array(s['temperature']),np.array(s['resistivity']),np.array(s['uncertainty'])) for s in d['measurements'][2]['samples']}
nk=400; kx,ky = kgrid(nk)
def dfdw(w,T): x=np.clip(w/(2*T),-300,300); return 1/(4*T*np.cosh(x)**2)
grid=np.arange(-12,12.001,0.02)
def hist(E,W,sigma):
    dE=grid[1]-grid[0]; edges=np.concatenate([grid-dE/2,[grid[-1]+dE/2]])
    h,_=np.histogram(E.ravel(),bins=edges,weights=np.broadcast_to(W,E.shape).ravel()); h=h/E.size/dE
    n=int(5*sigma/dE)+1; x=np.arange(-n,n+1)*dE; g=np.exp(-x**2/(2*sigma**2)); g/=g.sum(); return np.convolve(h,g,mode='same')
# ---- nu=1/2: Boltzmann with velocity-weighted DOS of the Hubbard bands, constant scattering time
bands = spectrum_half(kx,ky,'free'); dk = 2*np.pi/nk
Nv = np.zeros_like(grid); N1 = np.zeros_like(grid)
for E,Z in bands:
    vx = np.gradient(E,dk,axis=0); vy = np.gradient(E,dk,axis=1)
    Nv += hist(E, Z*(vx**2+vy**2), 0.084); N1 += hist(E, Z, 0.084)
Tfine = np.linspace(0.3,4.5,200)
sig_v = np.array([np.trapezoid(dfdw(grid,T)*Nv,grid) for T in Tfine]); rho_v = 1/sig_v; rho_v/=np.interp(4.0,Tfine,rho_v)   # Boltzmann, const tau
rho_arr = np.exp(4.0*(1/Tfine-1/4.0))   # Arrhenius with half Mott gap Delta_M/2 = 4.0
sig_1 = np.array([np.trapezoid(dfdw(grid,T)*N1,grid) for T in Tfine]); rho_1 = 1/sig_1; rho_1/=np.interp(4.0,Tfine,rho_1)
T,r,u = res['1/2']
print("Mott rho: data/Arrhenius(4.0) at T:", " ".join(f"{Ti:.2f}:{ri/np.exp(4.0*(1/Ti-0.25)):.2f}" for Ti,ri in zip(T[::6],r[::6])))
print("Mott rho: data/model(v-weighted) at T:", " ".join(f"{Ti:.2f}:{ri/np.interp(Ti,Tfine,rho_v):.2f}" for Ti,ri in zip(T[::6],r[::6])))
# ---- nu~0.3: activated pair transport above Tc
T3,r3,u3 = res['≈0.3']; m3 = r3>0; Tc3 = 0.5*(T3[m3].min()+T3[~m3].max()); 
A = np.vstack([np.ones(m3.sum()), 1/T3[m3]]).T; wts = 1/(u3[m3]/r3[m3])
coef, resid, *_ = np.linalg.lstsq(A*wts[:,None], np.log(r3[m3])*wts, rcond=None); lnrho0, Ea = coef
cov = np.linalg.inv((A*wts[:,None]).T@(A*wts[:,None])); print(f"nu~0.3: Tc = {Tc3:.3f} (between {T3[~m3].max()} and {T3[m3].min()}), rho = {np.exp(lnrho0):.3f} exp({Ea:.3f}/T), Ea err {np.sqrt(cov[1,1]):.3f}")
# ---- nu~0.2: T-linear metal above Tc
T2,r2,u2 = res['≈0.2']; m2 = r2>0; Tc2 = 0.5*(T2[m2].min()+T2[~m2].max())
A2 = np.vstack([np.ones(m2.sum()), T2[m2]]).T; w2 = 1/u2[m2]
c2, *_ = np.linalg.lstsq(A2*w2[:,None], r2[m2]*w2, rcond=None); cov2 = np.linalg.inv((A2*w2[:,None]).T@(A2*w2[:,None]))
print(f"nu~0.2: Tc = {Tc2:.3f} (between {T2[~m2].max()} and {T2[m2].min()}), rho = {c2[0]:.3f} + {c2[1]:.3f} T  (errs {np.sqrt(cov2[0,0]):.3f}, {np.sqrt(cov2[1,1]):.3f})")
# Mott activation fit of data
m1 = r>0; A1 = np.vstack([np.ones(m1.sum()), 1/T[m1]]).T; w1 = 1/(u[m1]/r[m1]); c1,*_ = np.linalg.lstsq(A1*w1[:,None], np.log(r[m1])*w1, rcond=None); cov1=np.linalg.inv((A1*w1[:,None]).T@(A1*w1[:,None]))
print(f"nu=1/2 data: rho ∝ exp({c1[1]:.3f}/T) ± {np.sqrt(cov1[1,1]):.3f}")
# model slope
lr = np.log(rho_v); print("model (v-weighted) activation between T=0.45 and 1.0:", (np.interp(0.45,Tfine,lr)-np.interp(1.0,Tfine,lr))/(1/0.45-1/1.0), " between 1 and 4:", (np.interp(1.0,Tfine,lr)-np.interp(4.0,Tfine,lr))/(1/1.0-1/4.0))
np.savez('/app/work/rho_curves.npz', Tfine=Tfine, rho_v=rho_v, rho_1=rho_1, Tc3=Tc3, lnrho0=lnrho0, Ea=Ea, Tc2=Tc2, c2=c2)
fig, ax = plt.subplots(figsize=(8,6))
ax.errorbar(T, r, yerr=u, fmt='o', ms=4, color=C['half'], mfc='white', mew=1.2, elinewidth=0.8, label='data $\\nu=1/2$')
ax.plot(Tfine, rho_arr, color=C['half'], lw=2, label='theory: carriers activated across the Mott gap, $\\rho\\propto e^{\\Delta_M/2T}$, $\\Delta_M/2=4.0D$')
ax.plot(Tfine, rho_v, color=C['half'], lw=1.2, ls=':', label='theory: full Boltzmann evaluation with Hubbard-band $v_k^2$-weighted DOS (const. $\\tau$)')
ax.errorbar(T3, np.where(r3>0,r3,np.nan), yerr=u3, fmt='o', ms=4, color=C['03'], mfc='white', mew=1.2, elinewidth=0.8, label='data $\\nu\\approx0.3$')
Tt = np.linspace(Tc3,4.2,100); ax.plot(Tt, np.exp(lnrho0+Ea/Tt), color=C['03'], lw=2, label=f'theory: pair insulator above $T_c$={Tc3:.2f}: $\\rho\\propto e^{{E_a/T}}$, $E_a$={Ea:.2f}$D$')
ax.plot([0.1,Tc3],[1e-2,1e-2], color=C['03'], lw=2, ls='--')
ax.errorbar(T2, np.where(r2>0,r2,np.nan), yerr=u2, fmt='o', ms=4, color=C['02'], mfc='white', mew=1.2, elinewidth=0.8, label='data $\\nu\\approx0.2$')
Tt2 = np.linspace(Tc2,4.2,100); ax.plot(Tt2, c2[0]+c2[1]*Tt2, color=C['02'], lw=2, label=f'theory: metal above $T_c$={Tc2:.2f}: $\\rho=\\rho_0+\\rho_1T$')
ax.plot([0.1,Tc2],[1e-2*1.3,1e-2*1.3], color=C['02'], lw=2, ls='--')
ax.set_yscale('log'); ax.set_ylim(8e-3,3e3); ax.set_xlim(0,4.2); ax.set_xlabel('temperature $T/D$'); ax.set_ylabel('in-plane resistivity (normalised at $T=4D$)')
ax.text(0.45, 1.05e-2, '$\\rho=0$ below $T_c$ (superconducting), drawn at $10^{-2}$', fontsize=8, color=C['ink2'], va='center')
ax.legend(fontsize=7.5, loc='upper right'); ax.set_title('In-plane resistivity: data (points) and effective theory (lines)', loc='left', fontsize=11)
plt.savefig('/app/figures/fig_rho.png', dpi=150, bbox_inches='tight'); print("rho figure done")
