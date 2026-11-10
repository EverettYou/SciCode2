import numpy as np
from fitlib_fast import *
from hk_bcs import spectral_pair
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
grid=np.linspace(-12,12,961)
t,tp=0.99,0.195
eps=band(t,tp); sub=eps[::6,::6].ravel()
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
fig,axs=plt.subplots(2,2,figsize=(14,9))
for ax,(U,mu) in zip(axs.ravel(),[(12,-0.93),(12,1.5),(8,-0.93),(16,-0.93)]):
    ax.plot(V,g,'k',lw=0.7,label='panel b')
    for Delta in [3.0,4.5,6.0]:
        rho=np.zeros_like(grid); ntot=0
        for e in sub:
            A,nk=spectral_pair(e-mu,U,Delta,0.05,grid,0.12); rho+=A; ntot+=nk
        rho/=len(sub); ntot/=len(sub)
        ax.plot(grid,rho/rho.max(),label=f'Delta={Delta} n={ntot:.2f}')
    ax.set_title(f'HK+BCS exact per pair, U={U}, mu={mu}'); ax.legend(fontsize=8); ax.set_xlim(-12,12)
plt.tight_layout(); plt.savefig('hk_bcs2.png',dpi=80); print('done')
