import sys; sys.path.insert(0,'/app/code')
from model import *
import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
nus=np.linspace(0.01,0.99,99)
Tmf=np.array([Tc_mf(mu_for_filling(nu)) for nu in nus])
D0=np.array([gap_equation_solve(mu_for_filling(nu),0.0) for nu in nus])
# phase coherence scale: vanishes at the Mott insulator; fixed by Tc(0.3)=0.36; T_coh = kappa*|1-2nu|^3
kappa=0.36/0.4**3
Tcoh=kappa*np.abs(1-2*nus)**3
Tc=np.minimum(Tmf,Tcoh)
# pseudogap line T*(nu): grows from ~Tc at nu~0.2 to >4.4 at nu=0.3 and diverges (Mott) at nu=1/2 ; use T* = 4.4*((nu-0.2)/0.1)^... illustrative:
def Tstar(nu):
    x=np.abs(nu-0.5)
    # T* = Tc(0.2) at |nu-0.5|=0.3 ; T* = 6 at |nu-0.5|=0.2 ; diverge at 0: use A/x^2 - B form
    A=3.5*0.2**2*1.0; 
    val=A/np.maximum(x,1e-3)**2 - (A/0.3**2 - 1.1)
    return np.where(x<0.3,val,np.nan)
Ts_=Tstar(nus)
json.dump({'nu':nus.tolist(),'Tmf':Tmf.tolist(),'Delta0':D0.tolist(),'Tcoh':Tcoh.tolist(),'Tc':Tc.tolist()},open('/app/code/phase_numbers.json','w'))
fig,ax=plt.subplots(figsize=(10,6.5))
ax.fill_between(nus,0,Tc,color='tab:blue',alpha=0.35,label='superconductor (s-wave, full gap)')
m=(nus>0.2)&(nus<0.8)
ax.fill_between(nus[m],Tc[m],np.nan_to_num(Ts_[m],nan=12),color='tab:orange',alpha=0.25,label=r'pseudogap: paired, Mott-reconstructed, insulating-like')
ax.plot(nus,Tmf,'b--',lw=1.2,label=r'$T_{MF}(\nu)$: BCS gap equation, $g=6.1$ (pairing onset far from $\nu=1/2$)')
ax.plot(nus,Tc,'b-',lw=2.2,label=r'$T_c(\nu)=\min(T_{MF},T_{coh})$, $T_{coh}\propto|1-2\nu|^3$ through $T_c(0.3)=0.36$')
ax.plot(nus,Ts_,color='tab:red',lw=2,label=r'$T^*(\nu)$ pseudogap onset (schematic; $\approx3.5$ at $\nu=0.3$, $\to\infty$ at $\nu=1/2$)')
ax.axvline(0.5,color='k',lw=3,label=r'Mott insulator ($\nu=1/2$): gap $8D$, no order')
for x,c,lab in [(0.5,'k',r'$\nu=1/2$'),(0.3,'tab:green',r'$\nu\approx0.3$'),(0.2,'tab:purple',r'$\nu\approx0.2$')]:
    ax.axvline(x,color=c,ls=':',lw=1.5); ax.text(x+0.005,11.2,lab,color=c,fontsize=11)
ax.plot([0.3],[0.36],'o',color='tab:green',ms=8); ax.plot([0.2],[1.11],'o',color='tab:purple',ms=8)
ax.text(0.03,7,'metal\n(bare band, $\\rho\\propto T$,\nKorringa NMR)',fontsize=11)
ax.text(0.62,7,'metal',fontsize=11)
ax.text(0.36,2.0,'pseudogap',fontsize=11,color='tab:red')
ax.set_xlim(0,1); ax.set_ylim(0,12); ax.set_xlabel(r'filling $\nu$ (electrons per site / 2)',fontsize=12); ax.set_ylabel('T / D',fontsize=12)
ax.set_title(r'Phase diagram of $H=-\sum t_{ij}c^\dagger c+U\sum n_\uparrow n_\downarrow-g\sum c^\dagger_\uparrow c^\dagger_\downarrow c_\downarrow c_\uparrow$ (square lattice; $t=0.99,\ t\'=0.195,\ U=12.0,\ g=6.1$)',fontsize=10)
ax.legend(fontsize=8,loc='upper right'); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('/app/figures/fig_phase_diagram.png',dpi=110)
print("Tc(nu) at 0.1,0.2,0.3,0.4:",[round(float(np.interp(x,nus,Tc)),3) for x in [0.1,0.2,0.3,0.4]])
print("Tmf max:",Tmf.max()," at nu=",nus[np.argmax(Tmf)])
