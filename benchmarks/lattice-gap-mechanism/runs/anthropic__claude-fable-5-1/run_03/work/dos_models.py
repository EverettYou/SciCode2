import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
d=json.load(open('/app/measurements.json'))
sts=d['measurements'][0]['spectra']
def band(t,tp,tpp=0.0,N=800):
    k=(np.arange(N)+0.5)/N*2*np.pi-np.pi
    kx,ky=np.meshgrid(k,k,indexing='ij')
    return -2*t*(np.cos(kx)+np.cos(ky))-4*tp*np.cos(kx)*np.cos(ky)-2*tpp*(np.cos(2*kx)+np.cos(2*ky))
def hist_dos(E,w,grid,eta=0.04):
    # gaussian-broadened histogram
    h,edges=np.histogram(E.ravel(),bins=np.append(grid-(grid[1]-grid[0])/2,grid[-1]+(grid[1]-grid[0])/2),weights=w.ravel())
    h=h/(grid[1]-grid[0])/E.size
    # gaussian smooth
    from scipy.ndimage import gaussian_filter1d
    return gaussian_filter1d(h,eta/(grid[1]-grid[0]))
grid=np.linspace(-12,12,2401)

# panel d: compare noninteracting DOS for n=0.6 with various t'
Vd=np.array(sts[3]['bias']); gd=np.array(sts[3]['dI_dV'])
fig,axs=plt.subplots(3,1,figsize=(12,12))
ax=axs[0]; ax.plot(Vd,gd,'k-',lw=0.6,label='panel d data')
for tp in [0.15,0.2,0.25]:
    eps=band(1.0,tp)
    es=np.sort(eps.ravel()); mu=es[int(0.3*es.size)]  # n=0.6 -> 30% of BZ filled per spin
    rho=hist_dos(eps-mu,np.ones_like(eps),grid,eta=0.05)
    ax.plot(grid,rho/rho.max(),label=f"t'={tp} mu={mu:.2f} bottom={es[0]-mu:.2f} top={es[-1]-mu:.2f}")
ax.set_xlim(-10,10); ax.legend(); ax.set_title('panel d vs free band n=0.6')
# panel c normal state: n=0.4
Vc=np.array(sts[2]['bias']); gc=np.array(sts[2]['dI_dV'])
ax=axs[1]; ax.plot(Vc,gc,'k-',lw=0.6,label='panel c data')
for tp in [0.2]:
    eps=band(1.0,tp)
    es=np.sort(eps.ravel()); mu=es[int(0.2*es.size)]
    rho=hist_dos(eps-mu,np.ones_like(eps),grid,eta=0.05)
    ax.plot(grid,rho/rho.max(),label=f"free t'={tp} mu={mu:.2f} bottom={es[0]-mu:.2f} top={es[-1]-mu:.2f}")
    # BCS on top
    xi=eps-mu; Dl=1.9; E=np.sqrt(xi**2+Dl**2); u2=0.5*(1+xi/E); v2=0.5*(1-xi/E)
    rho=hist_dos(E,u2,grid,eta=0.05)+hist_dos(-E,v2,grid,eta=0.05)
    ax.plot(grid,rho/rho.max(),label=f"BCS Delta={Dl}")
ax.set_xlim(-10,10); ax.legend(); ax.set_title('panel c vs free band n=0.4 and BCS')
# panel a: Hubbard-I, HK, copies
Va=np.array(sts[0]['bias']); ga=np.array(sts[0]['dI_dV'])
ax=axs[2]; ax.plot(Va,ga,'k-',lw=0.6,label='panel a data')
tp=0.21; U=12.0
eps=band(1.0,tp)
Ep=(eps+np.sqrt(eps**2+U**2))/2; Em=(eps-np.sqrt(eps**2+U**2))/2
wp=0.5*(1+eps/np.sqrt(eps**2+U**2)); wm=1-wp
mid=(Ep.min()+Em.max())/2
rho=hist_dos(Ep-mid,wp,grid,0.05)+hist_dos(Em-mid,wm,grid,0.05)
ax.plot(grid,rho/rho.max(),label=f'Hubbard-I t\'={tp} U={U}')
# HK with W=4 (t=0.5, t'=0.105), U=12
eps2=band(0.5,0.105); mid2=(eps2.max()+eps2.min()+U)/2
rho=hist_dos(eps2-mid2,0.5*np.ones_like(eps2),grid,0.05)+hist_dos(eps2+U-mid2,0.5*np.ones_like(eps2),grid,0.05)
ax.plot(grid,rho/rho.max(),label='HK t=0.5 t\'=0.105 U=12')
# copies with HI weights: E=+-U/2 + eps/2
rho=hist_dos(eps/2+U/2,wp,grid,0.05)+hist_dos(eps/2-U/2,wm,grid,0.05)
ax.plot(grid,rho/rho.max(),label='copies eps/2+-U/2 with HI weights')
ax.set_xlim(-10,10); ax.legend(); ax.set_title('panel a vs models')
plt.tight_layout(); plt.savefig('dos_models.png',dpi=90)
print("done")
