from load import *
import numpy as np
from scipy.optimize import brentq
V,G=sts('a')
# remove background a*|V| fitted outside bands, smooth, clip in gap
m=np.abs(V)>8.6
a=np.sum(G[m]*np.abs(V[m]))/np.sum(np.abs(V[m])**2)
print('bg slope a=',a)
k=7; Gs=np.convolve(G,np.ones(k)/k,mode='same')
rho=np.clip(Gs-a*np.abs(V),0,None)
rho[(V>-3.9)&(V<3.95)]=0.0
rho[np.abs(V)>8.3]=0.0
dV=V[1]-V[0]
n0=np.sum(rho[V<0])*dV; ntot=np.sum(rho)*dV
print('occupied fraction',n0/ntot)
def f(x): return 0.5*(1-np.tanh(x/2))
def mu_of_T(T):
    return brentq(lambda mu: np.sum(rho*f((V-mu)/T))*dV - n0, -3.5,3.5)
Ts=np.array([0.4472,0.5039,0.5769,0.6747,0.8125,1.0209,1.3732,2.0968,2.8467,4.0,4.4318])
out=[]
for T in Ts:
    mu=mu_of_T(T)
    mf=f((V-mu)/T)*(1-f((V-mu)/T))/T   # -df/dw
    K=np.sum(rho**2*mf)*dV
    sig=np.sum(rho*mf)*dV  # crude conductivity ~ DOS at thermal window
    out.append((T,mu,K,sig))
out=np.array(out)
K4=out[out[:,0]==4.0,2][0]; s4=out[out[:,0]==4.0,3][0]
Tn,rn,en=nmr('1/2'); Tr,rr,er=res('1/2')
for T,mu,K,s in out:
    i=np.argmin(abs(Tn-T)); j=np.argmin(abs(Tr-T))
    print(f'T={T:.3f} mu={mu:+.3f}  Korringa 1/T1T={K/K4:.3e}  data={rn[i]/Tn[i]:.3e} | rho~1/sig={s4/s:.3e} data={rr[j]:.3e} (T_res={Tr[j]:.3f})')
