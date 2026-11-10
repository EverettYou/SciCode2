import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import json,numpy as np,time
from pathlib import Path
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;old=json.load(open(R/'data/sts_prior_spectral_fit_results.json'));tn,tpn=old['normal']['params'][:2]
dat=json.load(open(R/'data/measurements.json'))['measurements'][0]['spectra'][1];x=np.array(dat['bias']);y=np.array(dat['dI_dV']);u=np.cos(2*np.pi*(np.arange(256)+.5)/256)[None,:]
def J(z):
 zz=z.real+1j*np.abs(z.imag);g=1/(np.sqrt(zz-1)*np.sqrt(zz+1));return np.where(z.imag>=0,g,g.conj())
def gf(z,s,c,D1,D2,typ):
 z=z[:,None];t=s*tn;tp=s*tpn;C=c-2*t*u;B=-2*t-4*tp*u
 if typ=='d+id':a0=D1*D1*u*u+D2*D2*(1-u*u);a1=-2*D1*D1*u;a2=D1*D1-D2*D2*(1-u*u)
 else:a0=D1*D1+D2*D2*u*u;a1=-2*D2*D2*u;a2=D2*D2
 q2=-B*B-a2;q1=-2*C*B-a1;q0=z*z-C*C-a0
 disc=np.sqrt(q1*q1-4*q2*q0);r1=(-q1+disc)/(2*q2);r2=(-q1-disc)/(2*q2)
 A=(z+C+B*r1)/(q2*(r2-r1));BB=-B/q2-A
 return np.mean(A*J(r1)+BB*J(r2),axis=1)
def mod(p,typ):
 s,c,D1,D2,eta,A,b0,b2=p[:8];delta=p[8] if len(p)>8 else 0
 return -A*gf(x+delta+1j*eta,s,c,D1,D2,typ).imag/np.pi+b0+b2*x*x
lo=[.3,-5,0,0,.025,.1,-.03,0];hi=[1.8,6,6,8,.6,10,.1,.003]
fits={}
for typ in ['d+id','s+id']:
 starts=[[1,1.8,2.3,3.5,.08,3.5,0,.0013],[.8,2.,2.5,4,.1,3.5,0,.0013]] if typ=='d+id' else [[1,1.8,2.8,2.,.08,3.5,0,.0013]]
 best=None
 for j,p0 in enumerate(starts):
  st=time.time();res=least_squares(lambda p:mod(p,typ)-y,p0,bounds=(lo,hi),max_nfev=180,x_scale='jac',ftol=2e-7,xtol=2e-7)
  rss=float(res.fun@res.fun);sig=np.sqrt(rss/(len(x)-len(p0)));cov=np.linalg.pinv(res.jac.T@res.jac)*sig*sig
  fit=dict(params=res.x.tolist(),rms=sig,rss=rss,covariance=cov.tolist(),stderr=np.sqrt(np.diag(cov)).tolist(),nfev=res.nfev,success=bool(res.success))
  print(typ,j,'seconds',round(time.time()-st,1),'rms',sig,'params',res.x,flush=True)
  if best is None or rss<best['rss']:best=fit
 fits[typ]=best
 # Independently allow midpoint-to-chemical-potential offset.
 p0=best['params']+[0.];st=time.time();res=least_squares(lambda p:mod(p,typ)-y,p0,bounds=(lo+[-2],hi+[2]),max_nfev=150,x_scale='jac',ftol=2e-7,xtol=2e-7)
 rss=float(res.fun@res.fun);sig=np.sqrt(rss/(len(x)-len(p0)));cov=np.linalg.pinv(res.jac.T@res.jac)*sig*sig
 fits[typ+'_offset']=dict(params=res.x.tolist(),rms=sig,rss=rss,covariance=cov.tolist(),stderr=np.sqrt(np.diag(cov)).tolist(),nfev=res.nfev,success=bool(res.success))
 print(typ,'offset','seconds',round(time.time()-st,1),'rms',sig,'params',res.x,flush=True)
 json.dump(fits,open(R/'sts_pairing_diagnostics.json','w'),indent=2)
# Physical number and gap equations at T=0; separable attraction -g/N Bdag B convention.
cg=np.cos(2*np.pi*np.arange(512)/512);u2=cg[:,None];v2=cg[None,:]
for key,fit in fits.items():
 typ=key.split('_')[0];s,c,D1,D2=fit['params'][:4];eps=-2*s*tn*(u2+v2)-4*s*tpn*u2*v2;xi=eps+c
 if typ=='d+id':phi1=u2-v2;phi2sq=(1-u2*u2)*(1-v2*v2);gapsq=D1*D1*phi1*phi1+D2*D2*phi2sq
 else:phi1=np.ones_like(xi);phi2sq=(u2-v2)**2;gapsq=D1*D1+D2*D2*phi2sq
 E=np.sqrt(xi*xi+gapsq);n=np.mean(.5*(1-xi/E));F1=np.mean(phi1*phi1/(2*E));F2=np.mean(phi2sq/(2*E))
 fit.update(number_per_spin=float(n),min_positive_excitation=float(E.min()),max_excitation=float(E.max()),g1_if_selfconsistent_separable_attraction=float(1/F1),g2_if_selfconsistent_separable_attraction=float(1/F2))
fitmeta={'description':'Single physical electronic orbital; ordinary BCS Nambu Green function, with complex momentum-dependent pairing. Diagnostic fit only, not a solution of one common microscopic Hamiltonian. d+id gap = D1(cos kx-cos ky)+i D2 sin kx sin ky; s+id gap = D1+i D2(cos kx-cos ky).','param_names':['dispersion_scale','c=-mu','D1','D2','eta','amplitude','b0','b2','delta_omega_from_gap_midpoint'],'fixed_normal_band':[tn,tpn],'fits':fits,'noise_model':'iid residual Gaussian; uncertainty model-conditional and band fixed','offset_note':'omega=x+delta. Ordinary fully gapped BdG predicts a global gap symmetric around omega=0; fitting delta is a robustness test, not assumed physical freedom.'}
json.dump(fitmeta,open(R/'sts_pairing_diagnostics.json','w'),indent=2)
fig,axs=plt.subplots(2,1,figsize=(8.4,6),sharex=True,gridspec_kw={'height_ratios':[3,1]})
axs[0].plot(x,y,color='.5',lw=.7,label='Supplied STS');cols=['#164d85','#a02c47']
for typ,col in zip(['d+id','s+id'],cols):
 f=fits[typ+'_offset'];m=mod(f['params'],typ);axs[0].plot(x,m,lw=1.4,color=col,label=f'{typ}: RMS {f["rms"]:.3f}, n/2={f["number_per_spin"]:.3f}');axs[1].plot(x,m-y,lw=.65,color=col)
axs[0].set_title(r'One-orbital momentum-dependent pairing diagnostics at $\nu\simeq0.3$');axs[0].set_ylabel('Normalized dI/dV');axs[0].legend(frameon=False,fontsize=9)
axs[1].set_ylabel('Fit - data');axs[1].set_xlabel('Gap-centered bias / D');axs[1].axhline(0,color='k',lw=.5);axs[1].set_xlim(-10,10);fig.tight_layout();fig.savefig(R/'sts_pairing_diagnostics.png',dpi=190)
print(json.dumps(fitmeta,indent=2))
