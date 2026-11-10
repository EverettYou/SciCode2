import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import numpy as np,json
from pathlib import Path
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];S=json.load(open((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')))['measurements'][0]['spectra'];x=np.array(S[0]['bias']);y=np.array(S[0]['dI_dV'])
path=R/'data/sts_fit_results.json';out=json.load(open(path));t,tp=out['normal']['params'][:2]
u=np.cos(2*np.pi*(np.arange(768)+.5)/768)
def g(z):
 v=z[:,None]+2*t*u[None,:];b=2*t+4*tp*u[None,:]
 return np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1)
def mod(p):
 s,V,r,eta,A,b0,b2=p;c=4*s*tp
 zm=x-c+V+1j*eta;zp=x-c-V+1j*eta
 m=(.5-r*zm/s)*g(zm/s)/s+(.5+r*zp/s)*g(zp/s)/s
 return -A*m.imag/np.pi+b0+b2*x*x
p0=[.5,6,.03,.08,3.5,0,.0013];lo=[.2,4,-.09,.015,.1,-.03,0];hi=[1,8,.09,.5,10,.03,.003]
r=least_squares(lambda p:mod(p)-y,p0,bounds=(lo,hi),max_nfev=200,x_scale='jac');rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p0)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig**2
fit={'names':['scale','V','residue_slope','eta','amplitude','b0','b2'],'params':r.x.tolist(),'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),'rss':rss,'rms':sig,'bic':float(len(x)*np.log(rss/len(x))+len(p0)*np.log(len(x))),'physical_note':'Pole energies E±=s*(bare epsilon+4tprime)±V. Residues w±=.5±r*bare epsilon enforce number n=.5 since average bare epsilon=0. Positive residues enforced over fitted bandwidth.'}
out['half_linear_weights']=fit
json.dump(out,open(path,'w'),indent=2)
np.savez(R/'data/sts_half_linear_weights.npz',bias=x,observed=y,fit=mod(r.x),params=r.x,covariance=cov)
print(json.dumps(fit,indent=2))
fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
axs[0].plot(x,y,color='.4',lw=.7,alpha=.65,label='Measurements');axs[0].plot(x,mod(r.x),color='#a12438',lw=1.5,label='Two rigid poles with linear spectral weights');axs[0].legend(frameon=False)
axs[0].set_title(r'Half filling: number- and gap-center-consistent fit');axs[0].set_ylabel('Normalized dI/dV')
axs[1].plot(x,mod(r.x)-y,color='#a12438',lw=.7);axs[1].axhline(0,color='k',lw=.5);axs[1].set_ylabel('Fit - data');axs[1].set_xlabel('Bias / D');axs[1].set_xlim(-10,10)
fig.tight_layout();fig.savefig(R/'figures/sts_half_linear_weights.png',dpi=190)
