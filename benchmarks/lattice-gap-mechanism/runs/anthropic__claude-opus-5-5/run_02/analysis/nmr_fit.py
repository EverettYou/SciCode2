from load import *
import numpy as np
from scipy.optimize import least_squares
for f in ['1/2','≈0.3']:
    T,r,e=nmr(f)
    if f=='≈0.3':
        m=(T<0.36)
    else:
        m=T<4.5
    T=T[m]; r=r[m]; e=e[m]
    y=r/T; ey=e/T
    for p_fixed in [None,0,1,-1,2]:
        def res(q):
            lnA,D=q[0],q[1]; p=q[2] if p_fixed is None else p_fixed
            mod=np.exp(lnA)*T**p*np.exp(-D/T)
            return (mod-y)/ey
        q0=[0,5,0] if p_fixed is None else [0,5]
        rr=least_squares(res,q0)
        J=rr.jac; cov=np.linalg.pinv(J.T@J); chi2=np.sum(rr.fun**2)
        print(f, 'p=',('free' if p_fixed is None else p_fixed),'params',np.round(rr.x,3),'err',np.round(np.sqrt(np.diag(cov)),3),'chi2',round(chi2,1),'N',len(T))
