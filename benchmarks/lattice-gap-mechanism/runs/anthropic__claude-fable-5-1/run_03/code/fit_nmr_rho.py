import json, numpy as np
from scipy.optimize import curve_fit
d=json.load(open('/app/measurements.json'))
nmr=d['measurements'][1]['samples']; res=d['measurements'][2]['samples']
print("=== NMR: fit 1/T1T = A * T^p * exp(-Delta/T) on low-T part (T<Tmax)")
for s,Tmax in zip(nmr,[1.1,1.2,0.9]):
    T=np.array(s['temperature']); r=np.array(s['one_over_T1'])/np.array(s['temperature']); u=np.array(s['uncertainty'])/np.array(s['temperature'])
    m=(T<Tmax)&(r>0)
    # fit in log space with weights
    y=np.log(r[m]); sy=u[m]/r[m]
    for p_fixed in [0,1,2]:
        f=lambda T,lnA,Dl: lnA+p_fixed*np.log(T)-Dl/T
        popt,pcov=curve_fit(f,T[m],y,p0=[0,2],sigma=sy,absolute_sigma=True)
        chi2=np.sum(((y-f(T[m],*popt))/sy)**2)
        print(f"  nu={s['filling']:5s} p={p_fixed}: Delta={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f}  lnA={popt[0]:.2f} chi2/dof={chi2/(m.sum()-2):.2f}")
    f=lambda T,lnA,p,Dl: lnA+p*np.log(T)-Dl/T
    try:
        popt,pcov=curve_fit(f,T[m],y,p0=[0,1,2],sigma=sy,absolute_sigma=True)
        chi2=np.sum(((y-f(T[m],*popt))/sy)**2)
        print(f"  nu={s['filling']:5s} free p: Delta={popt[2]:.3f}+-{np.sqrt(pcov[2,2]):.3f} p={popt[1]:.2f}+-{np.sqrt(pcov[1,1]):.2f} chi2/dof={chi2/(m.sum()-3):.2f}")
    except Exception as e: print("  free p fit failed",e)
print("=== NMR high-T values (1/T1T):")
for s in nmr:
    T=np.array(s['temperature']); r=np.array(s['one_over_T1'])/T
    print(f"  nu={s['filling']}: ", [(round(t,2),round(x,3)) for t,x in zip(T,r) if t>0.9])
print("=== Resistivity: Tc bracket (last zero, first nonzero)")
for s in res:
    T=np.array(s['temperature']); r=np.array(s['resistivity']); u=np.array(s['uncertainty'])
    z=np.where(r==0)[0]
    if len(z): print(f"  nu={s['filling']}: rho=0 up to T={T[z].max():.4f}; first nonzero T={T[z.max()+1]:.4f} rho={r[z.max()+1]:.3f}")
    else: print(f"  nu={s['filling']}: no zeros")
    # activated fit rho = A T^p exp(Delta/T) over nonzero points below some T
    m=(r>0)&(T<1.2)
    y=np.log(r[m]); sy=u[m]/r[m]
    for p_fixed in [0,1,-1]:
        f=lambda T,lnA,Dl: lnA+p_fixed*np.log(T)+Dl/T
        try:
            popt,pcov=curve_fit(f,T[m],y,p0=[0,2],sigma=sy,absolute_sigma=True)
            chi2=np.sum(((y-f(T[m],*popt))/sy)**2)
            print(f"     activated fit T<1.2, p={p_fixed}: Delta_rho={popt[1]:.3f}+-{np.sqrt(pcov[1,1]):.3f} chi2/dof={chi2/(m.sum()-2):.2f}")
        except Exception as e: print("     fit failed",e)
    # high-T: power law fit T>1.5
    m=(r>0)&(T>1.3)
    f=lambda T,lnA,q: lnA+q*np.log(T)
    popt,pcov=curve_fit(f,T[m],np.log(r[m]),p0=[0,1],sigma=u[m]/r[m],absolute_sigma=True)
    print(f"     power law T>1.3: rho ~ T^{popt[1]:.2f}+-{np.sqrt(pcov[1,1]):.2f}")
