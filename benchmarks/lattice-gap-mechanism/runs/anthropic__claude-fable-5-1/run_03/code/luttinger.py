from fitlib import *
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
t,tp,U=0.99,0.195,12.02
eps=band(t,tp)
c0=-(eps.min()+eps.max())/4
Em=-U/2+eps/2+c0; Ep=U/2+eps/2+c0; wm=0.5*(1-eps/U); wp=1-wm
# KK: Re G(k,0) = P int A(k,w')/(0-w') dw' ; with delta-bands = -sum w/E
G0_exact=-wm/Em-wp/Ep
# numerical KK from broadened spectrum on a grid, for a few k, as a check
wgrid=np.linspace(-14,14,14001); dw=wgrid[1]-wgrid[0]
def A_k(i,j,eta=0.05):
    return wm[i,j]*eta/np.pi/((wgrid-Em[i,j])**2+eta**2)+wp[i,j]*eta/np.pi/((wgrid-Ep[i,j])**2+eta**2)
def KK0(A):  # principal value at w=0: int A(w')/(0-w') ; exclude |w'|<dw/2 symmetric -> fine since A smooth there
    m=np.abs(wgrid)>1e-9
    return np.sum(A[m]/(0-wgrid[m]))*dw
for (i,j),name in [((0,0),'Gamma'),((NK//2,0),'X=(pi,0)'),((NK//2,NK//2),'M')]:
    print(f"{name}: eps={eps[i,j]:.3f} ReG(k,0) exact={G0_exact[i,j]:.5f} numerical KK={KK0(A_k(i,j)):.5f}")
print("Re G(k,0): min",G0_exact.min()," max",G0_exact.max())
om0=wm*Ep+wp*Em
print("zero-energy surface omega0(k) (midgap frame): min",om0.min()," max",om0.max())
f0=np.mean(eps<0); fc=np.mean(eps<-4*tp); fmed=np.mean(eps<np.median(eps))
print(f"fraction of BZ with eps_k<0 (equal-weight contour): {f0:.4f}")
print(f"fraction of BZ with eps_k< band centre -4t' : {fc:.4f}")
# sensitivity: pole dispersion lambda (HK-like) -> omega0 = c0 + lam*(eps - eps_c) crossing
for lam in [0.05,0.1,0.2,0.5,1.0]:
    for epsc_name,epsc in [('centre',-4*tp),('0',0.0)]:
        om=c0+lam*(eps-epsc); frac=np.mean(om<0)
        print(f"  lambda={lam} eps_c={epsc_name}: fraction with omega0<0 (inside zero curve) = {frac:.3f}")
np.save('G0_map.npy',G0_exact)
# plot map of Re G(k,0) and of omega0
fig,axs=plt.subplots(1,2,figsize=(11,5))
k=(np.arange(NK)+0.5)/NK-0.5
im=axs[0].imshow(G0_exact.T,origin='lower',extent=[-0.5,0.5,-0.5,0.5],cmap='RdBu_r',vmin=-0.02,vmax=0.02); plt.colorbar(im,ax=axs[0]); axs[0].set_title('Re G(k, w=0) [1/D], nu=1/2 (midgap)')
axs[0].contour(k,k,eps.T,levels=[-4*tp,0.0],colors=['k','g'])
im=axs[1].imshow(om0.T,origin='lower',extent=[-0.5,0.5,-0.5,0.5],cmap='viridis'); plt.colorbar(im,ax=axs[1]); axs[1].set_title('energy of the zero of G, omega_0(k) [D]')
plt.tight_layout(); plt.savefig('luttinger_check.png',dpi=80)
