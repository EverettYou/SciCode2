import numpy as np
from fitlib import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
t,tp,U=0.99,0.195,12.0
eps=band(t,tp)
def nambu_dos(mu,Delta,grid,eta=0.08,sub=4):
    e=eps[::sub,::sub].ravel()
    w=grid[:,None]+1j*eta
    # atomic-frame self energy Sigma_at(k,E)=U/2+(U^2-e^2)/(4(E-U/2)); E=w+mu for particle, mu-w for hole
    Sp=U/2+(U**2-e**2)/(4*(w+mu-U/2))
    Sh=U/2+(U**2-e**2)/(4*(np.conj(-w)+mu-U/2))   # Sigma_at(k, mu - w*)  (retarded hole part)
    Sh=np.conj(Sh)  # -> proper analytic structure: [Sigma(-w*)]^*
    a=w+mu-e-Sp            # particle diagonal
    d=w-mu+e+Sh            # hole diagonal
    det=a*d-Delta**2
    G11=d/det
    A=-G11.imag/np.pi
    return A.mean(axis=1)
grid=np.linspace(-12,12,1201)
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
fig,axs=plt.subplots(3,1,figsize=(12,11))
for ax,mu_list,Delta in [(axs[0],[2.0,3.0,4.0,5.0],2.4),(axs[1],[3.0,4.0],1.0),(axs[2],[3.0,4.0,5.0],4.0)]:
    ax.plot(V,g,'k',lw=0.7,label='panel b')
    for mu in mu_list:
        rho=nambu_dos(mu,Delta,grid)
        # filling: integrate occupied part
        n=2*np.trapz(rho[grid<0],grid[grid<0])
        ax.plot(grid,rho/rho.max(),label=f'mu={mu} Delta={Delta} n~{n:.2f}')
    ax.set_xlim(-12,12); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig('mott_bcs.png',dpi=80)
