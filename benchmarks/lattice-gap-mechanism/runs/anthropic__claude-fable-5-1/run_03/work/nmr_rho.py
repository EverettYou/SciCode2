from fitlib import *
import numpy as np
from scipy.integrate import trapezoid
from scipy.optimize import brentq
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('/app/measurements.json'))
nmr=d['measurements'][1]['samples']; res=d['measurements'][2]['samples']
t,tp,U=0.99,0.195,12.02
eps=band(t,tp)
def fermi_der(w,T):
    x=np.clip(w/T,-60,60); return 1/(4*T*np.cosh(x/2)**2)
# ---------- nu=1/2 : copies DOS ----------
c0=-(eps.min()+eps.max())/4
Em=-U/2+eps/2+c0; Ep=U/2+eps/2+c0; wm=0.5*(1-eps/U); wp=1-wm
rho_half=dos(Em,wm,0.05)+dos(Ep,wp,0.05)
Ts=np.linspace(0.4,4.6,60)
def T1T(rho,T): return trapezoid(rho**2*fermi_der(GRID,T),GRID)
def Neff(rho,T): return trapezoid(rho*fermi_der(GRID,T),GRID)
r_half=np.array([T1T(rho_half,T) for T in Ts]); n_half=np.array([Neff(rho_half,T) for T in Ts])
s=nmr[0]; Td=np.array(s['temperature']); rd=np.array(s['one_over_T1'])/Td; ud=np.array(s['uncertainty'])/Td
norm=np.interp(4.0,Ts,r_half)
fig,axs=plt.subplots(2,3,figsize=(16,9))
ax=axs[0,0]; ax.errorbar(1/Td,rd,ud,fmt='o',ms=3,label='data nu=1/2'); ax.plot(1/Ts,r_half/norm,label='int N^2 (-df/dw)')
ax.set_yscale('log'); ax.set_ylim(1e-5,3); ax.legend(); ax.set_title('NMR nu=1/2'); ax.set_xlabel('D/T')
# effective slope between T=0.5 and 1
i1=np.argmin(np.abs(Ts-1.0)); i2=np.argmin(np.abs(Ts-0.5))
print("nu=1/2 model: effective exponent between T=1 and 0.5:",(np.log(r_half[i1])-np.log(r_half[i2]))/(1/Ts[i2]-1/Ts[i1]))
# resistivity nu=1/2
s=res[0]; Tr=np.array(s['temperature']); rr=np.array(s['resistivity']); ur=np.array(s['uncertainty'])
ax=axs[1,0]; ax.errorbar(Tr,rr,ur,fmt='o',ms=3,label='data')
for lab,model in [('1/Neff',1/n_half),('T/Neff',Ts/n_half),('sqrt(T)/Neff',np.sqrt(Ts)/n_half)]:
    ax.plot(Ts,model/np.interp(4.0,Ts,model),label=lab)
ax.set_yscale('log'); ax.legend(); ax.set_title('rho nu=1/2'); ax.set_xlabel('T')
# ---------- nu=0.2 : BCS ----------
mu2=mu_for_filling(eps,0.4); xi2=eps-mu2
def gap_eq(Dl,T,gcoup):
    E=np.sqrt(xi2**2+Dl**2); return 1-gcoup*np.mean(np.tanh(E/(2*T))/(2*E))
gc=1/np.mean(1/(2*np.sqrt(xi2**2+1.967**2)))
print("g (nu=0.2) =",gc)
def Delta_T(T):
    if gap_eq(1e-6,T,gc)>0: return 0.0
    return brentq(lambda D: gap_eq(D,T,gc),1e-6,5)
Tc2=brentq(lambda T: gap_eq(1e-6,T,gc),0.2,3); print("Tc (nu=0.2) =",Tc2, " 2Delta/Tc=",2*1.967/Tc2)
Ts2=np.linspace(0.15,4.5,70); D2=np.array([Delta_T(T) for T in Ts2])
# NMR with BCS DOS incl coherence factor, Dynes broadening Gamma
def T1T_bcs(Dl,T,Gam=0.08):
    w=GRID+1j*Gam
    # use k-sum: N_s(E)=sum_k Re[|w|/sqrt(w^2-Dl^2)] * ... simpler: constant-DOS-like with actual band: build from Bogoliubov bands
    E=np.sqrt(xi2**2+Dl**2); E=np.maximum(E,1e-9); u2=0.5*(1+xi2/E); v2=1-u2
    Ns=dos(E,u2,Gam)+dos(-E,v2,Gam)
    # anomalous DOS M(w)=sum_k (Dl/2E)[delta(w-E)-delta(w+E)]
    Ms=dos(E,Dl/(2*E),Gam)-dos(-E,Dl/(2*E),Gam)
    return trapezoid((Ns**2+Ms**2)*fermi_der(GRID,T),GRID), Ns
r2=[]; n2=[]
for T,Dl in zip(Ts2,D2):
    val,Ns=T1T_bcs(Dl,T); r2.append(val); n2.append(Neff(Ns,T))
r2=np.array(r2); n2=np.array(n2)
s=nmr[2]; Td=np.array(s['temperature']); rd=np.array(s['one_over_T1'])/Td; ud=np.array(s['uncertainty'])/Td
ax=axs[0,1]; ax.errorbar(1/Td,rd,ud,fmt='o',ms=3,label='data nu=0.2'); ax.plot(1/Ts2,r2/np.interp(4.0,Ts2,r2),label='BCS N^2+M^2')
ax.set_yscale('log'); ax.set_ylim(1e-3,3); ax.legend(); ax.set_title('NMR nu=0.2'); ax.set_xlabel('D/T')
ax=axs[1,1]; ax.plot(Ts2,D2); ax.set_title('Delta(T) nu=0.2'); ax.set_xlabel('T')
# resistivity nu=0.2 above Tc: T/Neff normal
s=res[2]; Tr=np.array(s['temperature']); rr=np.array(s['resistivity']); ur=np.array(s['uncertainty'])
rho_free=dos(xi2,np.ones_like(xi2),0.05)
nfree=np.array([Neff(rho_free,T) for T in Ts2])
ax=axs[1,2]; ax.errorbar(Tr,rr,ur,fmt='o',ms=3,label='data')
for lab,model in [('T/Neff(free)',Ts2/nfree),('T',Ts2),('T/Neff(BCS)',Ts2/n2)]:
    mm=Ts2>Tc2; ax.plot(Ts2[mm],model[mm]/np.interp(4.0,Ts2,model),label=lab)
ax.legend(); ax.set_title('rho nu=0.2'); ax.set_xlabel('T')
# nu=0.3 NMR data for reference
s=nmr[1]; Td=np.array(s['temperature']); rd=np.array(s['one_over_T1'])/Td; ud=np.array(s['uncertainty'])/Td
ax=axs[0,2]; ax.errorbar(1/Td,rd,ud,fmt='o',ms=3,label='data nu=0.3')
# BCS at nu=0.3 with g from 0.2
mu3=mu_for_filling(eps,0.6); xi3=eps-mu3
def gap_eq3(Dl,T): E=np.sqrt(xi3**2+Dl**2); return 1-gc*np.mean(np.tanh(E/(2*T))/(2*E))
Tc3=brentq(lambda T: gap_eq3(1e-6,T),0.2,4); D03=brentq(lambda D: gap_eq3(D,0.05),1e-6,6)
print("nu=0.3 with same g: Delta(0)=",D03," Tc_MF=",Tc3)
r3=[]
for T in Ts2:
    Dl=0.0 if gap_eq3(1e-6,T)>0 else brentq(lambda D: gap_eq3(D,T),1e-6,6)
    E=np.sqrt(xi3**2+Dl**2); E=np.maximum(E,1e-9); u2=0.5*(1+xi3/E); v2=1-u2
    Ns=dos(E,u2,0.08)+dos(-E,v2,0.08); Ms=dos(E,Dl/(2*E),0.08)-dos(-E,Dl/(2*E),0.08)
    r3.append(trapezoid((Ns**2+Ms**2)*fermi_der(GRID,T),GRID))
r3=np.array(r3); ax.plot(1/Ts2,r3/np.interp(4.0,Ts2,r3),label=f'BCS same g: Delta0={D03:.2f}')
ax.set_yscale('log'); ax.set_ylim(1e-5,3); ax.legend(); ax.set_title('NMR nu=0.3'); ax.set_xlabel('D/T')
plt.tight_layout(); plt.savefig('nmr_rho.png',dpi=80)
# print HS peak height for nu=0.2 model
print("nu=0.2 model max 1/T1T (normalized at T=4):",(r2/np.interp(4.0,Ts2,r2)).max())
