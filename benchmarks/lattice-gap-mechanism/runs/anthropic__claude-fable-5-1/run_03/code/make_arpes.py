import sys; sys.path.insert(0,'/app/code')
from model import *
import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
# k path Gamma(0,0) -> X(1/2,0) -> M(1/2,1/2) -> Gamma, in units 2pi/a
def kpath(n=240):
    G=np.array([0,0]); X=np.array([0.5,0]); M=np.array([0.5,0.5])
    segs=[(G,X),(X,M),(M,G)]; ks=[]; dist=[0]; ticks=[0]
    for a,b in segs:
        for i in range(n):
            ks.append(a+(b-a)*i/n)
        ticks.append(ticks[-1]+np.linalg.norm(b-a))
    ks.append(G); ks=np.array(ks)
    s=np.concatenate([[0],np.cumsum(np.linalg.norm(np.diff(ks,axis=0),axis=1))])
    return ks,s,ticks
ks,s,ticks=kpath()
kx=2*np.pi*ks[:,0]; ky=2*np.pi*ks[:,1]
epsk=band(kx=kx,ky=ky)
def lor(w,E,eta): return eta/np.pi/((w[:,None]-E[None,:])**2+eta**2)
eta=0.12
fig,axs=plt.subplots(1,3,figsize=(18,6))
# nu=1/2
w=np.linspace(-10,10,801)
c0=-(EPS.min()+EPS.max())/4
Em=-U_HUB/2+epsk/2+c0; Ep=U_HUB/2+epsk/2+c0; wm=0.5*(1-epsk/U_HUB); wp=1-wm
A=wm[None,:]*lor(w,Em,eta)+wp[None,:]*lor(w,Ep,eta)
im=axs[0].pcolormesh(s,w,A,shading='auto',cmap='inferno',vmax=np.percentile(A,99.5)); plt.colorbar(im,ax=axs[0],label='A(k,w) [1/D]')
axs[0].plot(s,Em,'c--',lw=0.7); axs[0].plot(s,Ep,'c--',lw=0.7); axs[0].axhline(0,color='w',lw=0.8,ls=':')
axs[0].set_title(r'$\nu=1/2$ (Mott insulator): Hubbard bands $\pm U/2+\epsilon_k/2$'+'\n'+r'weights $(1\mp\epsilon_k/U)/2$; no Fermi surface',fontsize=10)
# nu=0.3 low T
w3=np.linspace(-8,8,801)
p=PG; xi=epsk-p['mu']; Z=0.5*(1+xi/np.sqrt(xi**2+p['D1']**2)); E=p['c']+p['a']*epsk+p['b']*epsk**2; xt=p['alpha']+p['beta']*epsk
sgn=np.clip(xt/np.maximum(E,1e-6),-1,1); pp=0.5*(1+sgn); pm=0.5*(1-sgn)
A3=(Z*pp)[None,:]*lor(w3,E,eta)+(Z*pm)[None,:]*lor(w3,-E,eta)
im=axs[1].pcolormesh(s,w3,A3,shading='auto',cmap='inferno',vmax=np.percentile(A3,99.5)); plt.colorbar(im,ax=axs[1],label='A(k,w) [1/D]')
axs[1].plot(s,E,'c--',lw=0.7); axs[1].plot(s,-E,'c--',lw=0.7); axs[1].axhline(0,color='w',lw=0.8,ls=':')
mu3=mu_for_filling(0.295); axs[1].plot(s,epsk-mu3,'w:',lw=0.8,label=r'bare $\xi_k$ (high-$T$ band)')
axs[1].legend(loc='lower right',fontsize=8)
axs[1].set_title(r'$\nu\approx0.3$, low $T$ (pseudogap + SC): mirror bands $\pm E_k$, full gap $2\times2.4$'+'\n'+'low-energy weight transferred out of the Fermi sea',fontsize=10)
# nu=0.2 low T
w2=np.linspace(-7,7,801)
mu2=mu_for_filling(0.198); D2=1.967; xi2=epsk-mu2; E2=np.sqrt(xi2**2+D2**2); u2=0.5*(1+xi2/E2); v2=1-u2
A2=u2[None,:]*lor(w2,E2,eta)+v2[None,:]*lor(w2,-E2,eta)
im=axs[2].pcolormesh(s,w2,A2,shading='auto',cmap='inferno',vmax=np.percentile(A2,99.5)); plt.colorbar(im,ax=axs[2],label='A(k,w) [1/D]')
axs[2].plot(s,E2,'c--',lw=0.7); axs[2].plot(s,-E2,'c--',lw=0.7); axs[2].plot(s,xi2,'w:',lw=0.8,label=r'bare $\xi_k$'); axs[2].axhline(0,color='w',lw=0.8,ls=':')
axs[2].legend(loc='lower right',fontsize=8)
axs[2].set_title(r'$\nu\approx0.2$, low $T$ (BCS): Bogoliubov bands $\pm\sqrt{\xi_k^2+\Delta^2}$, $\Delta=1.97$'+'\n'+r'back-bending and particle-hole mixing at $k_F$',fontsize=10)
for ax in axs:
    ax.set_xticks(ticks); ax.set_xticklabels(['(0,0)','(1/2,0)','(1/2,1/2)','(0,0)']); ax.set_ylabel(r'$\omega$ / D (from $\mu$)')
    for tck in ticks[1:-1]: ax.axvline(tck,color='w',lw=0.5)
plt.tight_layout(); plt.savefig('/app/figures/fig_arpes.png',dpi=110)
# save k_F positions etc
def crossings(x,y):
    idx=np.where(np.diff(np.sign(y))!=0)[0]; return [(x[i],ks[i]) for i in idx]
print("nu=0.2 bare-band Fermi crossings along path (s, k):",crossings(s,xi2))
print("nu=0.3 bare-band Fermi crossings:",crossings(s,epsk-mu3))
print("nu=0.3 in-window weight Z along path: min %.3f max %.3f; at Gamma %.3f, X %.3f, M %.3f"%(Z.min(),Z.max(),Z[0],Z[len(Z)//3],Z[2*len(Z)//3]))
print("nu=1/2 gap along path: min E+ %.2f max E- %.2f"%(Ep.min(),Em.max()))
