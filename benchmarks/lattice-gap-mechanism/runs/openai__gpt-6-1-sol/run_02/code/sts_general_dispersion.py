import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import numpy as np,json,time
from scipy.optimize import least_squares
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
S=json.load(open((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')))['measurements'][0]['spectra']
x=np.array(S[0]['bias']);ys=[np.array(s['dI_dV']) for s in S]
path=ROOT/'data/sts_fit_results.json';out=json.load(open(path));tn,tpn=out['normal']['params'][:2]
u=np.cos(2*np.pi*(np.arange(256)+.5)/256)[None,:]
def J(z):
 zz=z.real+1j*np.abs(z.imag);a=1/(np.sqrt(zz-1)*np.sqrt(zz+1));return np.where(z.imag>=0,a,a.conj())
def gf(z,tc,tpc,tf,tpf,c,b,V):
 z=z[:,None];Bc=-2*tc-4*tpc*u;Bf=-2*tf-4*tpf*u;Cc=c-2*tc*u;Cf=b-2*tf*u
 sc=Bc*(z-Cf);af=Bf*(z-Cc)
 d=np.sqrt((sc-af)**2+4*Bc*Bf*V*V)
 r1=(sc+af+d)/(2*Bc*Bf);r2=(sc+af-d)/(2*Bc*Bf)
 A=(r1-(z-Cf)/Bf)/(Bc*(r1-r2));B=1/Bc-A
 return np.mean(A*J(r1)+B*J(r2),axis=1)
def mod(p):
 tc,tpc,tf,tpf,c,b,V,eta,amp,b0,b2=p
 return -amp*gf(x+1j*eta,tc,tpc,tf,tpf,c,b,V).imag/np.pi+b0+b2*x*x
lo=[.2,-.5,-2,-.5,-5,-5,.5,.025,.1,-.08,-.001]
hi=[2,.5,2,.5,5,5,9,.8,10,.2,.003]
fits={}
for idx in [1,0]:
 q=out['low_models'][str(idx)]['general']['expanded_params'];s,a,c,b,V,eta,amp,b0,b2=q
 ps=[[s*tn,s*tpn,a*tn,a*tpn,c,b,V,eta,amp,b0,b2]]
 if idx==1:
  ps+=[[1,.2,-1,.2,.7,.7,4,.08,4,0,.0013], [1,.2,.2,-.2,.5,.5,4,.08,4,0,.0013], [1,.2,-.3,-.2,1,-1,3,.08,4,0,.0013]]
 best=None
 for j,p0 in enumerate(ps):
  start=time.time();r=least_squares(lambda p:mod(p)-ys[idx],p0,bounds=(lo,hi),max_nfev=150,x_scale='jac',ftol=1.e-7,xtol=1.e-7)
  rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p0)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig**2
  fit={'names':['tc','tpc','tf','tpf','c','b','V','eta','amp','b0','b2'],'params':r.x.tolist(),'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),'rss':rss,'rms':sig,'bic':float(len(x)*np.log(rss/len(x))+len(p0)*np.log(len(x))),'nfev':r.nfev,'success':bool(r.success)}
  print(idx,j,'sec',round(time.time()-start,1),'rms',sig,'p',r.x,flush=True)
  if best is None or rss<best['rss']:best=fit
  fits[str(idx)]=best;out['general_dispersion']=fits;json.dump(out,open(path,'w'),indent=2)
 p=best['params'];m=mod(p)
 np.savez(ROOT/f'data/sts_general_dispersion_{idx}.npz',bias=x,observed=ys[idx],fit=m,params=p,covariance=best['covariance'])
 fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
 axs[0].plot(x,ys[idx],color='.4',lw=.7,alpha=.6,label='Measurements');axs[0].plot(x,m,color='#163c69',lw=1.5,label='Independent-dispersion two-pole model');axs[0].legend(frameon=False)
 axs[0].set_title('Low-T STS at '+S[idx]['filling']);axs[0].set_ylabel('Normalized dI/dV')
 axs[1].plot(x,m-ys[idx],color='#163c69',lw=.7);axs[1].set_ylabel('Fit - data');axs[1].set_xlabel('Gap-centered bias / D');axs[1].axhline(0,color='k',lw=.5);axs[1].set_xlim(-10,10)
 fig.tight_layout();fig.savefig(ROOT/f'figures/sts_general_dispersion_{idx}.png',dpi=190)
