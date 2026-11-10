import numpy as np, sys
sys.path.insert(0,'/app/analysis')
from fit_b13 import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pf = np.load('/app/analysis/fit_b13_free.npy'); px = np.load('/app/analysis/fit_b13_fix.npy')
fig,ax=plt.subplots(2,1,figsize=(11,7))
ax[0].plot(V,G,'k-',lw=0.5,label='(b) data'); ax[0].plot(Vf,F2g(pf),'r-',label='two-gap, mu free'); ax[0].plot(Vf,F2g(px,mu0),'b--',label='two-gap, mu=-0.907'); ax[0].legend()
ax[1].plot(V,G-F2g(pf),'r-',lw=0.6); ax[1].plot(V,G-F2g(px,mu0),'b-',lw=0.4,alpha=0.6); ax[1].axhline(0,color='k')
fig.savefig('/app/analysis/fit_b13.png',dpi=100)
# number check
for p,mu in [(pf,pf[4]),(px,mu0)]:
    xi=E0-mu; D=Dtwo(xi,p[0],p[1],p[2],p[3]); E=np.sqrt(xi**2+D**2)
    print('mu=%.3f  n(BCS) = %.4f  -> nu=%.4f ; normal-state nu at this mu = %.4f'%(mu, np.mean(1-xi/E), np.mean(1-xi/E)/2, np.mean(E0<mu)))
