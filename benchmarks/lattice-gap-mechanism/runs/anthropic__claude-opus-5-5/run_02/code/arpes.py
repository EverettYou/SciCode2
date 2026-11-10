"""Predicted low-T ARPES intensity (spectral function A(k,w), i.e. after division by the Fermi function)
along Gamma-X-M-Gamma for the three crystals, from the STS-calibrated theory spectral functions."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from model import *; from style import *; setup()
P=json.load(open(PARAMS_FILE)); F=np.load('/app/code/fitvec.npy',allow_pickle=True).item()
# path in units of 2pi/a: (0,0)->(1/2,0)->(1/2,1/2)->(0,0)
n1,n2,n3=240,240,340
s1=np.linspace(0,1,n1,endpoint=False); s2=np.linspace(0,1,n2,endpoint=False); s3=np.linspace(0,1,n3)
kx=np.concatenate([np.pi*s1,np.pi*np.ones(n2),np.pi*(1-s3)]); ky=np.concatenate([0*s1,np.pi*s2,np.pi*(1-s3)])
dist=np.concatenate([[0],np.cumsum(np.hypot(np.diff(kx),np.diff(ky)))])/(2*np.pi)
ticks=[0,dist[n1],dist[n1+n2],dist[-1]]
w=np.linspace(-9.5,9.5,1201)
def gauss(w,E,Z,sig):
    sig=np.broadcast_to(np.asarray(sig,float),E.shape)
    return Z[None,:]*np.exp(-(w[:,None]-E[None,:])**2/(2*sig[None,:]**2))/(np.sqrt(2*np.pi)*sig[None,:])
res_sig=0.10   # energy resolution added in quadrature
specs={}
# nu=1/2
t,tp,c,Dl,Uw,A,a0,b,sig=F['pa']
e=eps(kx,ky,t,tp); (Ep,Zp),(Em,Zm)=replica_poles(e,tp,c,Dl,Uw)
sg=np.hypot(0.08,res_sig)
specs['1/2']=dict(A=gauss(w,Ep,Zp,sg)+gauss(w,Em,Zm,sg),bands=[Ep,Em],label='ν = 1/2 (paired insulator)')
# nu=0.3
pb=F['pb']; tb,tpb=P['d']['t'],P['d']['tp']
e=eps(kx,ky,tb,tpb); xi,Dk,E,u2,v2,sk=nu03_parts(e,[pb[0]]+list(np.abs(pb[1:7])))
sg=np.hypot(sk,res_sig)
specs['≈0.3']=dict(A=gauss(w,E,u2,sg)+gauss(w,-E,v2,sg),bands=[E,-E,xi],label='ν ≈ 0.3 (strong-coupling SC)')
# nu=0.2
t,tp,mu,Dl,A,a0,b,sig=F['pc']
e=eps(kx,ky,t,tp); (Ep,u2),(Em,v2)=bcs_poles(e,mu,Dl)
sg=np.hypot(0.06,res_sig)
specs['≈0.2']=dict(A=gauss(w,Ep,u2,sg)+gauss(w,Em,v2,sg),bands=[Ep,Em,e-mu],label='ν ≈ 0.2 (BCS SC)')
fig,axs=plt.subplots(1,3,figsize=(14,5.2),sharey=True)
for ax,(key,sp) in zip(axs,specs.items()):
    I=sp['A']; I=I/np.percentile(I,99.7)
    im=ax.pcolormesh(dist,w,np.clip(I,0,1)**0.6,cmap=SEQ,shading='auto',vmin=0,vmax=1,rasterized=True)
    if len(sp['bands'])==3:
        ax.plot(dist,sp['bands'][2],color='#eb6834',lw=0.8,ls=(0,(2,2)),label='normal-state band ξ_k')
        ax.legend(loc='upper left',fontsize=7.5,frameon=True,facecolor='white',edgecolor='none',framealpha=0.85)
    ax.set_xticks(ticks); ax.set_xticklabels(['(0,0)','(½,0)','(½,½)','(0,0)'])
    ax.axhline(0,color=MUTED,lw=0.6); ax.grid(False)
    for tk in ticks[1:-1]: ax.axvline(tk,color='white',lw=0.6)
    ax.set_title(sp['label'],fontsize=10,loc='left'); ax.set_xlim(0,dist[-1])
axs[0].set_ylabel('ω − μ  (D)')
cb=fig.colorbar(im,ax=axs,fraction=0.02,pad=0.01); cb.set_label('A(k,ω) (norm., γ = 0.6 scale)')
fig.savefig('/app/fig5_arpes.png',bbox_inches='tight'); plt.close(fig)
# characteristic numbers
out={}
for key in ['≈0.3','≈0.2']:
    xi=specs[key]['bands'][2]
    idx=np.where(np.diff(np.sign(xi))!=0)[0]
    out[key]=dict(kF_path_positions=[float(dist[i]) for i in idx])
e2=eps(kx,ky,*F['pa'][:2]); out['1/2']=dict(direct_gap_min=float((specs['1/2']['bands'][0]-specs['1/2']['bands'][1]).min()),
     direct_gap_max=float((specs['1/2']['bands'][0]-specs['1/2']['bands'][1]).max()),
     lower_band_top=float(specs['1/2']['bands'][1].max()),upper_band_bottom=float(specs['1/2']['bands'][0].min()))
# Fermi velocity & coherence length for nu=0.2 along Gamma-X
t,tp,mu=F['pc'][:3]; Dl=F['pc'][3]
kk=np.linspace(0,np.pi,20001); xx=eps(kk,0*kk,t,tp)-mu; i=np.argmin(abs(xx)); vF=np.gradient(xx,kk)[i]
out['≈0.2'].update(kF_GX=float(kk[i]/(2*np.pi)),vF_GX=float(vF),xi0=float(vF/(np.pi*Dl)))
kd=np.linspace(0,np.pi,20001); xd=eps(kd,kd,t,tp)-mu; j=np.argmin(abs(xd)); vd=np.hypot(*[np.gradient(xd,kd)[j]/np.sqrt(2)]*2)
out['≈0.2'].update(kF_diag=float(kd[j]/(2*np.pi)),vF_diag=float(np.gradient(xd,kd)[j]/np.sqrt(2)))
pb=F['pb']; t,tp=tb,tpb; mu=pb[0]
xx=eps(kk,0*kk,t,tp)-mu; i=np.argmin(abs(xx)); vF=np.gradient(xx,kk)[i]
out['≈0.3'].update(kF_GX=float(kk[i]/(2*np.pi)),vF_GX=float(vF),xi_FS=float(vF/(np.pi*abs(pb[1]))))
json.dump(out,open('/app/code/arpes_numbers.json','w'),indent=1); print(json.dumps(out,indent=1))
