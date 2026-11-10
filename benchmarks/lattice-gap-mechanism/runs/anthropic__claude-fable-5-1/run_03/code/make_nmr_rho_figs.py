import sys; sys.path.insert(0,'/app/code')
from model import *
import json, numpy as np
from scipy.integrate import trapezoid
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('/app/measurements.json')); nmr=d['measurements'][1]['samples']; res=d['measurements'][2]['samples']
def T1T(rho,T): return trapezoid(rho**2*fermi_der(GRID,T),GRID)
def Neff(rho,T): return trapezoid(rho*fermi_der(GRID,T),GRID)
out={}
Ts=np.linspace(0.18,10,160)
# ---- nu=1/2
rho_h=mott_dos(0.05)
r_h=np.array([T1T(rho_h,T) for T in Ts]); n_h=np.array([Neff(rho_h,T) for T in Ts])
# ---- nu=0.2 : BCS with Delta(T) from gap equation (g=6.1) at fixed mu
mu2=mu_for_filling(0.198); Tc2=Tc_mf(mu2); D20=gap_equation_solve(mu2,0.0)
print("nu=0.2: Delta(0)=",D20," Tc_MF=",Tc2," 2Delta/Tc=",2*D20/Tc2)
def bcs_nmr(mu,T,Gam=0.08):
    Dl=gap_equation_solve(mu,T)
    E,u2,v2,xi=bcs_bands(mu,Dl); E=np.maximum(E,1e-9)
    Ns=dos(E,u2,Gam)+dos(-E,v2,Gam); Ms=(dos(E,Dl/(2*E),Gam)-dos(-E,Dl/(2*E),Gam)) if Dl>0 else 0*Ns
    return trapezoid((Ns**2+Ms**2)*fermi_der(GRID,T),GRID),Dl,Ns
r_2=[];D_2=[]
for T in Ts:
    v,Dl,Ns=bcs_nmr(mu2,T); r_2.append(v); D_2.append(Dl)
r_2=np.array(r_2); D_2=np.array(D_2)
r_2n=np.array([T1T(free_dos(mu2,0.08),T) for T in Ts]); r_2=r_2/r_2n
rho_free2=free_dos(mu2,0.05); nfree2=np.array([Neff(rho_free2,T) for T in Ts])
# ---- nu=0.3 : pseudogap DOS (T independent below T*), free band above T*=7 (illustrative)
rho_pg=pg_dos(0.05); mu3=mu_for_filling(0.295); rho_free3=free_dos(mu3,0.05)
Tstar=3.5
r_3n=np.array([T1T(rho_free3,T) for T in Ts]); r_3=np.array([T1T(rho_pg if T<Tstar else rho_free3,T) for T in Ts])/r_3n; n_3=np.array([Neff(rho_pg if T<Tstar else rho_free3,T) for T in Ts])
nfree3=np.array([Neff(rho_free3,T) for T in Ts])
fig,axs=plt.subplots(2,3,figsize=(16,9))
labels=[r'$\nu=1/2$',r'$\nu\approx0.3$',r'$\nu\approx0.2$']
models_nmr=[r_h,r_3,r_2]
for i,(s,ax) in enumerate(zip(nmr,axs[0])):
    T=np.array(s['temperature']); r=np.array(s['one_over_T1'])/T; u=np.array(s['uncertainty'])/T
    ax.errorbar(1/T,r,u,fmt='o',ms=3,label='data '+labels[i])
    mdl=models_nmr[i]; ax.plot(1/Ts,mdl/np.interp(4.0,Ts,mdl),'r',label=(r'theory: $\int N(\omega)^2(-\partial f/\partial\omega)$' if i==0 else r'theory: $R_s(T)/R_n(T)$, gap from the fitted spectrum'+(' + coherence factors' if i==2 else '')))
    ax.set_yscale('log'); ax.set_ylim(1e-5,3); ax.set_xlabel('D/T'); ax.set_ylabel(r'$1/(T_1T)$ (norm. at $T=4D$)'); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    if i==1: ax.axvline(1/Tstar,color='gray',ls=':'); ax.text(1/Tstar+0.05,1.5,r'$T^*$',color='gray')
    if i==2: ax.axvline(1/Tc2,color='gray',ls=':'); ax.text(1/Tc2+0.05,1.5,r'$T_c^{MF}$',color='gray')
# resistivity
mdl_rho=[ (Ts/n_h, r'theory: $\rho\propto T/N_{eff}(T)$'), (Ts/n_3, r'theory: $\rho\propto T/N_{eff}(T)$ (pseudogap DOS)'), (Ts, r'theory: $\rho\propto T$ (T-linear scattering), $\rho=0$ below $T_c$') ]
for i,(s,ax) in enumerate(zip(res,axs[1])):
    T=np.array(s['temperature']); r=np.array(s['resistivity']); u=np.array(s['uncertainty'])
    ax.errorbar(T,r,u,fmt='o',ms=3,label='data '+labels[i])
    m,lab=mdl_rho[i]; norm=np.interp(4.0,Ts,m)
    if i==2:
        mm=Ts>Tc2; ax.plot(Ts[mm],m[mm]/norm,'r',label=lab); ax.plot([0,Tc2],[0,0],'r')
    elif i==1:
        Tc3=0.36; mm=Ts>Tc3; ax.plot(Ts[mm],m[mm]/norm,'r',label=lab); ax.plot([0,Tc3],[0,0],'r')
        ax.plot(Ts,(1/n_h/np.interp(4.0,Ts,1/n_h)) if False else np.nan*Ts)
    else:
        ax.plot(Ts,m/norm,'r',label=lab); ax.plot(Ts,(1/n_h)/np.interp(4.0,Ts,1/n_h),'r--',label=r'$\rho\propto 1/N_{eff}(T)$')
    ax.set_xlabel('T/D'); ax.set_ylabel(r'$\rho/\rho(4D)$'); ax.legend(fontsize=8); ax.grid(alpha=0.3); ax.set_xlim(0,4.5)
    if i==0: ax.set_yscale('log'); ax.set_ylim(0.5,3e3)
    if i==1: ax.set_yscale('log'); ax.set_ylim(0.5,30)
    if i==2: ax.set_ylim(-0.05,1.3)
plt.tight_layout(); plt.savefig('/app/figures/fig_nmr_rho.png',dpi=110)
# effective exponents of the models vs data over the data ranges
def slope(Tarr,yarr,Tlo,Thi):
    m=(Tarr>=Tlo)&(Tarr<=Thi); p=np.polyfit(1/Tarr[m],np.log(yarr[m]),1); return -p[0]
print("nu=1/2 NMR model slope (T 0.45-1.1):",slope(Ts,r_h,0.45,1.1)," data fit: 5.5+-0.4")
print("nu=0.3 NMR model slope (T 0.2-1.2):",slope(Ts,r_3,0.2,1.2)," data fit: 2.64+-0.07")
print("nu=0.2 NMR model slope (T 0.2-0.9):",slope(Ts,r_2,0.2,0.9)," data fit: 1.73+-0.04")
print("nu=1/2 rho model T/Neff slope (0.45-1.2):",-slope(Ts,Ts/n_h,0.45,1.2)," 1/Neff:",-slope(Ts,1/n_h,0.45,1.2)," data: 3.7 (p=0)")
print("nu=0.3 rho model T/Neff slope (0.4-1.2):",-slope(Ts,Ts/n_3,0.4,1.2)," data: 0.94 (p=0)")
print("nu=0.2 NMR model HS peak:",(r_2/np.interp(4.0,Ts,r_2)).max()," data: 1.8")
json.dump({'Tc2':Tc2,'D20':D20},open('/app/code/nmr_rho_numbers.json','w'))
