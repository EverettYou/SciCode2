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
resfile=ROOT/'data/sts_fit_results.json';out=json.load(open(resfile))
t,tp=out['normal']['params'][:2]
cx=np.cos(2*np.pi*(np.arange(384)+.5)/384)
def g0(z):
 z=np.asarray(z);sg=np.where(z.imag>=0,1.,-1.);zz=z.real+1j*np.abs(z.imag)
 v=zz[:,None]+2*t*cx[None,:];b=2*t+4*tp*cx[None,:]
 g=np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1)
 return np.where(sg>0,g,g.conj())
def green(z,s,a,c,b,V):
 if abs(a)<1.e-6: return g0((z-c-V*V/(z-b))/s)/s
 d=np.sqrt((s*(z-b)-a*(z-c))**2+4*s*a*V*V)
 r1=(s*(z-b)+a*(z-c)+d)/(2*s*a)
 r2=(s*(z-b)+a*(z-c)-d)/(2*s*a)
 A=(r1-(z-b)/a)/(s*(r1-r2));B=1/s-A
 return A*g0(r1)+B*g0(r2)
def expand(p,typ):
 if typ=='rigid':
  s,c,V,eta,amp,b0,b2=p;return [s,s,c,c,V,eta,amp,b0,b2]
 if typ=='BCS':
  s,c,V,eta,amp,b0,b2=p;return [s,-s,c,-c,V,eta,amp,b0,b2]
 if typ=='flat':
  s,c,b,V,eta,amp,b0,b2=p;return [s,0.,c,b,V,eta,amp,b0,b2]
 return list(p)
def model(p,typ):
 s,a,c,b,V,eta,amp,b0,b2=expand(p,typ)
 return -amp*green(x+1j*eta,s,a,c,b,V).imag/np.pi+b0+b2*x*x
fits={};bestparams=[]
for idx in range(3):
 fits[str(idx)]={}; y=ys[idx]
 for typ in ['rigid','BCS','flat','general']:
  if typ in ['rigid','BCS']:
   p0=[.5,.4,6,.04,6,0,.0013] if idx==0 else [1,1.8,2 if idx==2 else 3,.04,4,0,.0013]
   lo=[.15,-5,.1,.015,.01,-.08,-.001];hi=[2,5,9,.8,15,.2,.003]
   names=['dispersion_scale','center','hybridization','eta','amplitude','background_constant','background_quadratic']
  elif typ=='flat':
   p0=[1,.8,0,6 if idx==0 else 3,.04,6,0,.0013]
   lo=[.15,-5,-5,.1,.015,.01,-.08,-.001];hi=[2.5,5,5,9,.8,15,.2,.003]
   names=['dispersion_scale','c','b','hybridization','eta','amplitude','background_constant','background_quadratic']
  else:
   winner=min(fits[str(idx)].values(),key=lambda q:q['rss'])
   p0=list(winner['expanded_params']);p0[1]+=.03
   lo=[.15,-2.5,-5,-5,.1,.015,.01,-.08,-.001];hi=[2.5,2.5,5,5,9,.8,15,.2,.003]
   names=['s','a','c','b','hybridization','eta','amplitude','background_constant','background_quadratic']
  start=time.time()
  r=least_squares(lambda p:model(p,typ)-y,p0,bounds=(lo,hi),max_nfev=180,x_scale='jac',ftol=2e-8,xtol=2e-8)
  rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p0)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig**2
  fits[str(idx)][typ]={'param_names':names,'params':r.x.tolist(),'expanded_params':expand(r.x,typ),'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),'rss':rss,'rms':sig,'bic':float(len(x)*np.log(rss/len(x))+len(p0)*np.log(len(x))),'nfev':r.nfev,'success':bool(r.success),'note':'t,tprime fixed at high-T fit; iid Gaussian residual model; model mismatch included in estimated residual scale'}
  np.savez(ROOT/f'data/sts_low_{idx}_{typ}.npz',bias=x,observed=y,fit=model(r.x,typ),params=r.x,expanded_params=expand(r.x,typ),covariance=cov)
  print(idx,typ,'sec',round(time.time()-start,1),'rms',round(sig,5),'p',r.x,flush=True)
  out['low_models']=fits;json.dump(out,open(resfile,'w'),indent=2)
 fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
 axs[0].plot(x,y,color='.5',lw=.7,alpha=.6,label='Measurements')
 for typ,col in zip(['rigid','BCS','flat','general'],['#9467bd','#268b77','#dc8249','#163c69']):
  pfit=fits[str(idx)][typ]['params'];m=model(pfit,typ)
  axs[0].plot(x,m,lw=1.2,color=col,label=typ)
  if typ=='general':axs[1].plot(x,m-y,lw=.7,color=col)
 axs[0].set_title('Low-T STS at '+S[idx]['filling']);axs[0].set_ylabel('Normalized dI/dV');axs[0].legend(frameon=False,ncol=3)
 axs[1].set_ylabel('General - data');axs[1].set_xlabel('Gap-centered bias / D');axs[1].axhline(0,color='k',lw=.5);axs[1].set_xlim(-10,10)
 fig.tight_layout();fig.savefig(ROOT/f'figures/sts_low_{idx}_comparison.png',dpi=190)
