from fitlib import *
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
t,tp=0.99,0.195
eps=band(t,tp)
# free DOS rho0(eps) on fine grid
egrid=np.linspace(eps.min()-0.1,eps.max()+0.1,400)
rho0=dos(eps,np.ones_like(eps),0.06)  # on GRID
rho0_e=np.interp(egrid,GRID,rho0)
def smooth(y,n=9): return np.convolve(y,np.ones(n)/n,mode='same')
fig,axs=plt.subplots(2,2,figsize=(14,9))
# ---- panel a: E_- = -U/2+eps/2+c0, E_+ = U/2+eps/2+c0 ; c0 so that midgap=0
s=STS[0]; V=np.array(s['bias']); g=smooth(np.array(s['dI_dV']))-0.045
U=12.02; c0=-(eps.min()+eps.max())/4
Em=lambda e: -U/2+e/2+c0; Ep=lambda e: U/2+e/2+c0
wm=np.interp(Em(egrid),V,g)*0.5/np.maximum(rho0_e,1e-3)
wp=np.interp(Ep(egrid),V,g)*0.5/np.maximum(rho0_e,1e-3)
m=(egrid>eps.min()+0.3)&(egrid<eps.max()-0.3)
norm=np.mean((wm+wp)[m])
axs[0,0].plot(egrid[m],wm[m]/norm,label='w_- (LHB)'); axs[0,0].plot(egrid[m],wp[m]/norm,label='w_+ (UHB)')
axs[0,0].plot(egrid[m],0.5*(1-egrid[m]/U),'k--',label='(1-eps/U)/2'); axs[0,0].plot(egrid[m],0.5*(1+egrid[m]/U),'k:',label='(1+eps/U)/2')
axs[0,0].plot(egrid[m],(wm+wp)[m]/norm,'g',label='sum'); axs[0,0].set_title('panel a inverted weights vs eps_k'); axs[0,0].legend(); axs[0,0].set_xlabel('eps_k')
# ---- panel b: mirror E(eps)=c+a eps+b eps^2
s=STS[1]; V=np.array(s['bias']); g=smooth(np.array(s['dI_dV']))-0.06
c,a,b=4.688,0.5165,0.0247
E=lambda e: c+a*e+b*e*e; dE=lambda e: a+2*b*e
wp=np.interp(E(egrid),V,g)*dE(egrid)/np.maximum(rho0_e,1e-3)
wm=np.interp(-E(egrid),V,g)*dE(egrid)/np.maximum(rho0_e,1e-3)
norm=np.max((wm+wp)[m])
axs[0,1].plot(egrid[m],wp[m]/norm,label='w_+ (upper)'); axs[0,1].plot(egrid[m],wm[m]/norm,label='w_- (lower)')
axs[0,1].plot(egrid[m],(wm+wp)[m]/norm,'g',label='sum'); axs[0,1].plot(egrid[m],(wp-wm)[m]/norm,'r--',label='diff')
axs[0,1].set_title('panel b inverted weights (mirror disp. E=4.69+0.52eps+0.025eps^2)'); axs[0,1].legend(); axs[0,1].set_xlabel('eps_k')
# ratio and E
axs[1,1].plot(egrid[m],(wp/np.maximum(wm,1e-6))[m],label='w+/w-'); axs[1,1].set_ylim(0,4); axs[1,1].legend(); axs[1,1].set_xlabel('eps_k'); axs[1,1].set_title('ratio')
# alternative: free-band-like dispersion with Bogoliubov E=sqrt((eps-mu)^2+D^2)?? skip
# ---- panel c check: BCS weights
s=STS[2]; V=np.array(s['bias']); g=smooth(np.array(s['dI_dV']))-0.06
mu,Dl=-1.933,1.967
xi=egrid-mu; Eb=np.sqrt(xi**2+Dl**2); dEb=np.abs(xi)/Eb
# E not monotonic in eps (min at eps=mu) -> handle two branches separately: for eps<mu and eps>mu
wp=np.interp(Eb,V,g)*dEb/np.maximum(rho0_e,1e-3); wm=np.interp(-Eb,V,g)*dEb/np.maximum(rho0_e,1e-3)
mm=m&(np.abs(xi)>0.4)
norm=np.median((wm+wp)[mm])
axs[1,0].plot(egrid[mm],wp[mm]/norm,'.',label='u^2 data'); axs[1,0].plot(egrid[mm],wm[mm]/norm,'.',label='v^2 data')
axs[1,0].plot(egrid,0.5*(1+xi/Eb),'k--'); axs[1,0].plot(egrid,0.5*(1-xi/Eb),'k:'); axs[1,0].set_title('panel c inverted weights vs BCS'); axs[1,0].legend(); axs[1,0].set_ylim(-0.2,1.5)
plt.tight_layout(); plt.savefig('invert_weights.png',dpi=80)
# print tabulated panel-b weights
print("panel b: eps, w+, w-, sum (normalized to max sum)")
for e in np.linspace(eps.min()+0.3,eps.max()-0.3,12):
    i=np.argmin(np.abs(egrid-e)); print(f"  {e:6.2f}  {wp[i]/norm if False else 0:0.0f}",end='')
    print()
