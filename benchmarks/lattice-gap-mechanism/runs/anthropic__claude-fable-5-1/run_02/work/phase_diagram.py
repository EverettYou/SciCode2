import sys; sys.path.insert(0,'/app/work')
import numpy as np
from scipy.optimize import brentq
from scipy.interpolate import PchipInterpolator
from fitlib import kgrid, ebar
from models import T_HOP, TP_HOP
from vizstyle import *
import matplotlib.pyplot as plt
setup()
nk=400; kx,ky = kgrid(nk); eb = ebar(kx,ky,T_HOP,TP_HOP); gam = 0.5*(np.cos(kx)+np.cos(ky))
Es = np.sort(eb.ravel())
def mu_of_nu(nu): return Es[min(int(nu*Es.size), Es.size-1)]
# BCS extended-s: gap eq. 1 = V <gam^2 tanh(E/2T)/(2E)>_k,   Delta_k = D0*gam_k
def gap_rhs(D0, mu, T):
    xi = eb-mu; E = np.sqrt(xi**2+(D0*gam)**2); return np.mean(gam**2*np.tanh(E/(2*T))/(2*E))
mu02 = mu_of_nu(0.20)
# calibrate: FS-averaged gap at nu=0.2 equals 1.96 -> D0 such that mean gam on FS * D0 = 1.96
fs = np.abs(eb-mu02) < 0.05; gamFS = gam[fs].mean(); D0 = 1.9594/gamFS
V = 1/gap_rhs(D0, mu02, 0.01)
Tc_bcs02 = brentq(lambda T: V*gap_rhs(1e-6, mu02, T)-1, 0.02, 6)
print(f"extended-s BCS: gamma_FS={gamFS:.3f}, D0={D0:.3f}, V={V:.3f}, Tc(0.2)={Tc_bcs02:.3f}, 2Delta/Tc={2*1.9594/Tc_bcs02:.2f}")
# also constant-gap (on-site-like) channel for comparison
def gap_rhs_s(D, mu, T):
    xi=eb-mu; E=np.sqrt(xi**2+D**2); return np.mean(np.tanh(E/(2*T))/(2*E))
Vs = 1/gap_rhs_s(1.9594, mu02, 0.01); Tc_s = brentq(lambda T: Vs*gap_rhs_s(1e-6,mu02,T)-1, 0.02, 6)
print(f"isotropic-s BCS: Vs={Vs:.3f}, Tc(0.2)={Tc_s:.3f}, 2Delta/Tc={2*1.9594/Tc_s:.2f}")
nus = np.linspace(0.02,0.98,97)
Tmf = []; Dmf=[]
for nu in nus:
    mu = mu_of_nu(nu)
    f = lambda T: Vs*gap_rhs_s(1e-6, mu, T)-1
    Tmf.append(brentq(f, 0.005, 8) if f(0.005)>0 else 0.0)
    g = lambda D: Vs*gap_rhs_s(D, mu, 0.01)-1
    Dmf.append(brentq(g, 1e-4, 12) if g(1e-4)>0 else 0.0)
Tmf=np.array(Tmf); Dmf=np.array(Dmf)
# pseudogap (pair-formation) scale from data: Delta_pg(nu) interpolation (hole side), T* = 2 Delta_pg/3.5 ; mirror for electron side
pts_nu = np.array([0.20, 0.30, 0.50]); pts_D = np.array([1.9594, 4.15, 6.0])
def Dpg(nu):
    x = np.where(nu<=0.5, nu, 1-nu)
    out = np.empty_like(x)
    lo = x < 0.20
    out[lo] = np.interp(x[lo], nus, Dmf)   # BCS branch (isotropic s channel, V_s)
    pc = PchipInterpolator(pts_nu, pts_D); out[~lo] = pc(x[~lo])
    return out
Tstar = np.where(np.minimum(nus,1-nus)<0.2, np.array(Tmf), 0.65*Dpg(nus))
Ttheta = 5.6*np.abs(1-2*nus)**3
Tc = np.minimum(Tstar, Ttheta)
np.savez('/app/work/phase_curves.npz', nus=nus, Tstar=Tstar, Ttheta=Ttheta, Tc=Tc, Tmf=Tmf, Dmf=Dmf, V=V, D0=D0, Vs=Vs)
print("Tc at 0.2, 0.3:", np.interp(0.2,nus,Tc), np.interp(0.3,nus,Tc), " T* at 0.3:", np.interp(0.3,nus,Tstar), " BCS-BEC crossover nu where T*=Ttheta:", nus[np.argmin(np.abs(Tstar-Ttheta)[nus<0.45])])
fig, ax = plt.subplots(figsize=(11,6.5))
# regions
ax.fill_between(nus, 0, Tc, color=C['02'], alpha=0.35, lw=0, label='superconductor (s-like full gap)')
mask_pg = Tstar>Tc+1e-9
ax.fill_between(nus, Tc, np.where(mask_pg,Tstar,Tc), color=C['03'], alpha=0.25, lw=0, label='pseudogap: preformed pairs, no coherence (pair insulator)')
ax.plot(nus, Tc, color=C['02'], lw=2.2, label='$T_c(\\nu)$')
ax.plot(nus, Tstar, color=C['03'], lw=2, ls='--', label='$T^*(\\nu)\\approx0.65\\,\\Delta_{pg}(\\nu)$ (pair formation; $=T_c^{BCS}$ for $\\nu<0.2$)')
ax.plot(nus, Ttheta, color=C['violet'], lw=1.4, ls=':', label='$T_\\theta(\\nu)$ phase stiffness $\\propto(1-2\\nu)^3$')
ax.plot([0.5,0.5],[0,4.0], color=C['half'], lw=4, alpha=0.9); ax.text(0.512, 4.05, 'Mott insulator at $\\nu=1/2$\n(charge gap 8.0$D$, $U$=12$D$;\nparamagnetic, no broken symmetry)', color=C['half'], fontsize=9, va='bottom')
ax.plot([0.5,0.5],[4.0,6.0], color=C['half'], lw=1.2, ls='--'); ax.text(0.512, 5.55, 'gap thermally smeared,\nincoherent Hubbard-band\nparamagnet ($T\\gtrsim\\Delta_M/2$)', color=C['ink2'], fontsize=8)
for nu,lab in [(0.5,''),(0.3,'crystal $\\nu\\approx0.3$'),(0.2,'crystal $\\nu\\approx0.2$')]:
    ax.axvline(nu, color=C['ink2'], lw=0.9, ls='-.')
    if lab: ax.text(nu+0.004, 4.4, lab, rotation=90, va='top', fontsize=8.5, color=C['ink2'])
ax.text(0.5-0.02, 3.3, 'crystal $\\nu=1/2$', rotation=90, va='top', fontsize=8.5, color=C['ink2'])
ax.text(0.03, 2.2, 'metal\n(Korringa NMR,\n$\\rho\\propto T$)', fontsize=9, color=C['ink'])
ax.text(0.80, 2.2, 'metal (electron-doped\nside: mirror image\nunder $t^\\prime\\to-t^\\prime$)', fontsize=9, color=C['ink'])
ax.text(0.33, 0.9, 'preformed\npairs', fontsize=9, color=C['ink'])
ax.text(0.14, 0.4, 'SC (BCS)', fontsize=9, color=C['ink'])
ax.set_xlim(0,1); ax.set_ylim(0,6.6); ax.set_xlabel('filling fraction $\\nu$ (electrons per site = $2\\nu$)'); ax.set_ylabel('temperature $T/D$')
ax.set_title('Phase diagram of the effective theory (calibrated on the three crystals)', loc='left', fontsize=11)
ax.legend(fontsize=8, loc='upper left', bbox_to_anchor=(0.0,1.0), ncol=1)
plt.savefig('/app/figures/fig_phase_diagram.png', dpi=150, bbox_inches='tight'); print("phase diagram done")
