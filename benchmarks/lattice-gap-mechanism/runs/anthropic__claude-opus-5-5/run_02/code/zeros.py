"""Q5: Green's function at nu=1/2 from the predicted spectrum via Kramers-Kronig;
zeros of Re G(k, w=0) (w measured from the T->0 chemical potential = mid-gap)."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from model import *; from style import *; setup()
P=json.load(open(PARAMS_FILE)); F=np.load('/app/code/fitvec.npy',allow_pickle=True).item()
cov=np.array(P['a_cov'])
w=np.linspace(-14,14,5601); dw=w[1]-w[0]
def ReG0_KK(kx,ky,p,sig=0.08):
    """Re G(k,0) = P int dw' A(k,w')/(0-w') ; A built from the predicted (broadened) spectrum"""
    t,tp,c,Dl,Uw=p[:5]
    e=eps(kx,ky,t,tp); (Ep,Zp),(Em,Zm)=replica_poles(e,tp,c,Dl,Uw)
    out=np.zeros(e.shape)
    kern=np.where(np.abs(w)>1e-9,-1.0/np.where(np.abs(w)>1e-9,w,1),0.0)
    for (E,Z) in [(Ep,Zp),(Em,Zm)]:
        A=Z[...,None]*np.exp(-(w-E[...,None])**2/(2*sig**2))/(np.sqrt(2*np.pi)*sig)
        out+= (A*kern).sum(-1)*dw
    return out
def ReG0_poles(kx,ky,p):
    t,tp,c,Dl,Uw=p[:5]
    e=eps(kx,ky,t,tp); (Ep,Zp),(Em,Zm)=replica_poles(e,tp,c,Dl,Uw)
    return -Zp/Ep-Zm/Em
N=361; ks=np.linspace(-np.pi,np.pi,N); KX,KY=np.meshgrid(ks,ks,indexing='ij')
p0=F['pa']
G_kk=np.concatenate([ReG0_KK(KX[i:i+19],KY[i:i+19],p0) for i in range(0,N,19)])
G_po=ReG0_poles(KX,KY,p0)
print('max |KK - poles| =',np.abs(G_kk-G_po).max(),' typical |G| =',np.abs(G_po).mean())
def gamma_side_fraction(G):
    g0=G[N//2,N//2]
    if np.all(np.sign(G)==np.sign(g0)): return 0.0, False
    from scipy import ndimage
    lab,nl=ndimage.label(np.sign(G)==np.sign(g0)); region=lab==lab[N//2,N//2]
    # periodic BZ: count grid cells (excluding duplicated boundary row/col)
    return region[:-1,:-1].mean(), True
frac,exists=gamma_side_fraction(G_kk)
print('Gamma-side fraction (best fit, KK) =',frac,exists,' G(Gamma)=',G_kk[N//2,N//2],' G(M)=',G_kk[0,0])
# bootstrap over the fitted-parameter covariance
rng=np.random.default_rng(7); S=rng.multivariate_normal(p0,cov,size=600)
fr=[]; ex=[]
for s in S:
    f,e_=gamma_side_fraction(ReG0_poles(KX,KY,s)); fr.append(f); ex.append(e_)
fr=np.array(fr); ex=np.array(ex)
print('bootstrap: P(closed curve)=%.2f  median=%.3f  mean=%.3f  16/84%%=%.3f/%.3f'%(ex.mean(),np.median(fr),fr.mean(),np.percentile(fr,16),np.percentile(fr,84)))
# sensitivity: weight asymmetry (Uw) and the two limits
sens=[]
for Uw in [12,13,13.5,14,14.2,14.5,15,16,18,20,25,30,50,100,1e5]:
    p=p0.copy(); p[4]=Uw; f,e_=gamma_side_fraction(ReG0_poles(KX,KY,p)); sens.append((Uw,f))
print('sensitivity',[(u,round(f,3)) for u,f in sens])
t,tp=p0[:2]
ek=eps(KX,KY,t,tp)
frac_center=np.mean((ek+4*tp<0)[:-1,:-1]); mu_half=np.quantile(ek[:-1,:-1],0.5)
frac_mean=np.mean((ek<0)[:-1,:-1])
res=dict(best_fraction=frac,closed_curve=exists,G_Gamma=float(G_kk[N//2,N//2]),G_M=float(G_kk[0,0]),
         bootstrap=dict(P_closed=float(ex.mean()),median=float(np.median(fr)),p16=float(np.percentile(fr,16)),p84=float(np.percentile(fr,84))),
         equal_weight_limit_band_centre_contour=float(frac_center),mean_energy_contour=float(frac_mean),
         sensitivity=[dict(Uw=u,frac=f) for u,f in sens],zero_surface_energy_offset=float(np.median(ReG0_poles(KX,KY,p0))))
json.dump(res,open('/app/code/zeros.json','w'),indent=1)
print(json.dumps({k:v for k,v in res.items() if k!='sensitivity'},indent=1))
# ------------ figure -------------
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(11.5,4.8),gridspec_kw=dict(width_ratios=[1.1,1]))
X=KX/(2*np.pi); Y=KY/(2*np.pi)
vm=np.abs(G_kk).max()
im=ax1.pcolormesh(X,Y,G_kk,cmap=DIV,vmin=-vm,vmax=vm,shading='auto',rasterized=True)
ax1.contour(X,Y,G_kk,[0],colors=[INK],linewidths=2)
ax1.contour(X,Y,ek+4*tp,[0],colors=['#eb6834'],linewidths=1.2,linestyles='--')
ax1.contour(X,Y,ek-mu_half,[0],colors=[MUTED],linewidths=1.0,linestyles=':')
ax1.set_aspect('equal'); ax1.set_xlabel('k_x (2π/a)'); ax1.set_ylabel('k_y (2π/a)'); ax1.grid(False)
ax1.set_title('Re G(k, ω=0) at ν = ½ (KK of predicted A(k,ω))',fontsize=9.5,loc='left')
cb=fig.colorbar(im,ax=ax1,fraction=0.046,pad=0.02); cb.set_label('Re G(k,0)  (1/D)')
from matplotlib.lines import Line2D
ax1.legend(handles=[Line2D([],[],color=INK,lw=2,label=f'zero curve (Γ side = {frac:.3f} of BZ)'),
                    Line2D([],[],color='#eb6834',lw=1.2,ls='--',label=f'band-centre contour ({frac_center:.3f})'),
                    Line2D([],[],color=MUTED,lw=1,ls=':',label='non-interacting ν=½ FS (0.500)')],
           fontsize=7.5,loc='lower left',frameon=True,facecolor='white',edgecolor='none',framealpha=0.9)
u=np.array([s[0] for s in sens]); f=np.array([s[1] for s in sens])
ax2.semilogx(np.minimum(u,1e3),f,'o-',color=S1,ms=5,lw=1.5)
ax2.axvspan(p0[4]-np.sqrt(cov[4,4]),p0[4]+np.sqrt(cov[4,4]),color='#cde2fb',lw=0)
ax2.axhline(0.5,color=INK2,lw=1); ax2.text(13,0.51,'ν = ½ (Luttinger count)',fontsize=8,color=INK2,va='bottom')
ax2.axhline(frac_center,color='#eb6834',lw=1); ax2.text(100,frac_center+0.01,'equal weights (Z± = ½)',fontsize=8,color=INK2,ha='center')
ax2.set_xlabel('weight scale U_w in Z± = ½[1 ± ε_k/√(ε_k²+U_w²)]  (D)'); ax2.set_ylabel('BZ fraction on the Γ side of the zero curve')
ax2.set_title('Sensitivity of the zero-curve area; band = STS-fitted U_w',fontsize=9.5,loc='left'); ax2.set_ylim(-0.02,0.6)
ax2.text(12.2,0.02,'no zero at ω=0\n(U_w ≤ 13.6)',fontsize=7.5,color=INK2)
fig.tight_layout(); fig.savefig('/app/fig6_zeros.png'); plt.close(fig)
