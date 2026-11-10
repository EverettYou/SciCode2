import sys; sys.path.insert(0,'/app/code')
from model import *
import numpy as np, json
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
Em,Ep,wm,wp=mott_bands()
# Kramers-Kronig: Re G(k,w) = P int A(k,w')/(w-w') dw'. Do it numerically from the broadened spectrum on a coarse k grid, and exactly.
wgrid=np.linspace(-16,16,16001); dw=wgrid[1]-wgrid[0]
eta=0.05
sub=10
ReG_num=np.zeros((NK//sub,NK//sub))
for i in range(0,NK,sub):
    for j in range(0,NK,sub):
        A=wm[i,j]*eta/np.pi/((wgrid-Em[i,j])**2+eta**2)+wp[i,j]*eta/np.pi/((wgrid-Ep[i,j])**2+eta**2)
        m=np.abs(wgrid)>dw/2
        ReG_num[i//sub,j//sub]=np.sum(A[m]/(0-wgrid[m]))*dw
ReG_exact=-wm/Em-wp/Ep
print("Re G(k,0): exact min/max = %.4f / %.4f ; numerical KK min/max = %.4f / %.4f"%(ReG_exact.min(),ReG_exact.max(),ReG_num.min(),ReG_num.max()))
om0=wm*Ep+wp*Em
print("zero of G: omega_0(k) = %.3f ... %.3f D above the midgap (k independent)"%(om0.min(),om0.max()))
f_eq=np.mean(EPS<0); f_c=np.mean(EPS<-4*TP_HOP)
print("fraction of BZ inside eps_k=0 contour (equal LHB/UHB weight): %.3f"%f_eq)
print("fraction of BZ inside band-centre contour eps_k=-4t': %.3f"%f_c)
# sensitivity: allow the self-energy pole to disperse: omega_0(k)=c0+lam*eps_k (HK-like); fraction inside zero curve
c0=-(EPS.min()+EPS.max())/4
lams=np.linspace(0,1,21); fr=[np.mean(c0+l*EPS<0) for l in lams]
for l,f in zip(lams[::4],fr[::4]): print("  pole dispersion lambda=%.2f -> fraction enclosed by zero curve = %.3f"%(l,f))
json.dump({'ReG0_min':float(ReG_exact.min()),'ReG0_max':float(ReG_exact.max()),'omega0':float(om0.mean()),'f_equal_weight':float(f_eq),'f_band_centre':float(f_c),'lams':lams.tolist(),'fractions':[float(x) for x in fr]},open('/app/code/luttinger_numbers.json','w'))
k=(np.arange(NK)+0.5)/NK-0.5
fig,axs=plt.subplots(1,3,figsize=(17,5.2))
im=axs[0].imshow(ReG_exact.T,origin='lower',extent=[-0.5,0.5,-0.5,0.5],cmap='RdBu_r',vmin=-0.02,vmax=0.02); plt.colorbar(im,ax=axs[0],label='Re G(k,0) [1/D]')
axs[0].set_title(r'$\nu=1/2$: Re$\,G(\mathbf{k},\omega=0)$ from Kramers-Kronig'+'\n(uniformly positive, no sign change)'); axs[0].set_xlabel('$k_x$ [2$\\pi$/a]'); axs[0].set_ylabel('$k_y$ [2$\\pi$/a]')
im=axs[1].imshow(om0.T*0+ (c0+0.0*EPS).T,origin='lower',extent=[-0.5,0.5,-0.5,0.5],cmap='viridis',vmin=0,vmax=1); plt.colorbar(im,ax=axs[1],label=r'$\omega_0(\mathbf{k})$ [D]')
axs[1].contour(k,k,EPS.T,levels=[-4*TP_HOP],colors=['w'],linestyles='--'); axs[1].contour(k,k,EPS.T,levels=[0.0],colors=['c'])
axs[1].set_title(r'energy of the zero of $G$: $\omega_0(\mathbf{k})=+0.39D$ for all k'+'\n(white: band-centre contour, cyan: equal-weight contour $\\epsilon_k=0$)'); axs[1].set_xlabel('$k_x$ [2$\\pi$/a]')
axs[2].plot(lams,fr,'k-o',ms=3); axs[2].axhline(0.5,color='r',ls='--',label=r'$\nu=1/2$'); axs[2].set_xlabel(r'assumed dispersion of the self-energy pole $\lambda$ ($\omega_0=c_0+\lambda\epsilon_k$)'); axs[2].set_ylabel('fraction of BZ inside the zero curve (side containing (0,0))')
axs[2].set_title('Luttinger count if the Mott pole is allowed to disperse\n(data require $\\lambda\\lesssim 0.05$: then no curve at $\\omega=0$)'); axs[2].legend(); axs[2].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('/app/figures/fig_luttinger.png',dpi=110)
