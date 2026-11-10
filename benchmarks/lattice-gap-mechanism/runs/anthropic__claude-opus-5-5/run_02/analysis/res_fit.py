from load import *
import numpy as np
from scipy.optimize import least_squares
T,r,e=res('1/2')
for p_fixed in [None,0,1,-1,0.5]:
    def resid(q):
        lnA,D=q[0],q[1]; p=q[2] if p_fixed is None else p_fixed
        mod=np.exp(lnA)*T**p*np.exp(D/T)
        return (mod-r)/e
    q0=[0,4,0] if p_fixed is None else [0,4]
    rr=least_squares(resid,q0)
    J=rr.jac; cov=np.linalg.pinv(J.T@J); chi2=np.sum(rr.fun**2)
    print('rho 1/2 p=',('free' if p_fixed is None else p_fixed),np.round(rr.x,3),'err',np.round(np.sqrt(np.diag(cov)),3),'chi2',round(chi2,1),'N',len(T))
# parallel-channel model: sigma = sigma_qp * exp(-D/T) + const?
def resid2(q):
    a,D,b=q
    sig=np.exp(a)*np.exp(-D/T)+b
    return (1/sig-r)/e
rr=least_squares(resid2,[0,4,0.0])
print('sigma=A exp(-D/T)+B :',rr.x,'chi2',np.sum(rr.fun**2))
# nu=0.3 normal state
T,r,e=res('≈0.3'); m=r>0
T,r,e=T[m],r[m],e[m]
for p_fixed in [None,0]:
    def resid(q):
        lnA,D=q[0],q[1]; p=q[2] if p_fixed is None else p_fixed
        mod=np.exp(lnA)*T**p*np.exp(D/T)
        return (mod-r)/e
    q0=[0,1,0] if p_fixed is None else [0,1]
    rr=least_squares(resid,q0); J=rr.jac; cov=np.linalg.pinv(J.T@J)
    print('rho 0.3 p=',('free' if p_fixed is None else p_fixed),np.round(rr.x,3),'err',np.round(np.sqrt(np.diag(cov)),3),'chi2',round(np.sum(rr.fun**2),1),'N',len(T))
T,r,e=res('≈0.2'); m=r>0
T,r,e=T[m],r[m],e[m]
p=np.polyfit(T,r,1,w=1/e); print('rho 0.2 linear fit a+bT:',p[::-1],' chi2',np.sum(((np.polyval(p,T)-r)/e)**2),'N',len(T))
