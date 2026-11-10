import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import numpy as np, json
from scipy.optimize import least_squares
from scipy.signal import savgol_filter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')
S=json.load(open(SOURCE))['measurements'][0]['spectra']
x=np.array(S[0]['bias'])
ys=[np.array(a['dI_dV']) for a in S]
cx=np.cos(2*np.pi*(np.arange(768)+.5)/768)
def g0(z,t,tp):
 z=np.asarray(z);sg=np.where(z.imag>=0,1.,-1.);zz=z.real+1j*np.abs(z.imag)
 v=zz[:,None]+2*t*cx[None,:];b=2*t+4*tp*cx[None,:]
 g=np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1)
 return np.where(sg>0,g,g.conj())
def model_normal(p):
 t,tp,mu,eta,amp,b0,b2=p
 dos=-g0(x+mu+1j*eta,t,tp).imag/np.pi
 return amp*dos+b0+b2*x*x
p0=[1,.2,-.8,.08,3,.08,0]
lo=[.5,-.49,-3,.015,.1,0,-.003];hi=[1.8,.49,3,.6,10,.5,.003]
r=least_squares(lambda p:model_normal(p)-ys[3],p0,bounds=(lo,hi),max_nfev=180,x_scale='jac')
p=r.x;res=r.fun;dof=len(x)-len(p);sigma=np.sqrt(np.dot(res,res)/dof)
cov=np.linalg.pinv(r.jac.T@r.jac)*sigma*sigma
out={'normal':{'param_names':['t','tprime','mu','eta','amplitude','background_constant','background_quadratic'],'params':p.tolist(),'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),'noise_sigma_assumed_iid_estimated_from_residual':sigma,'rss':float(res@res),'n':len(x),'note':'phenomenological broadening and additive background; uncertainties conditional on model and iid residual noise; high STS temperature unspecified'}}
np.savez(ROOT/'data/sts_normal_fit.npz',bias=x,observed=ys[3],fit=model_normal(p),params=p,covariance=cov)
json.dump(out,open(ROOT/'data/sts_fit_results.json','w'),indent=2)
print(json.dumps(out,indent=2))
fig,axs=plt.subplots(2,1,figsize=(8,5.8),gridspec_kw={'height_ratios':[3,1]},sharex=True)
axs[0].plot(x,ys[3],lw=.7,alpha=.65,color='#198754',label='Supplied high-T STS')
axs[0].plot(x,model_normal(p),color='#172b4d',lw=1.6,label='Square-lattice DOS + smooth background')
axs[0].set_ylabel('Normalized dI/dV');axs[0].legend(frameon=False);axs[0].set_title(r'High-temperature spectrum at $\nu\simeq0.3$')
axs[1].plot(x,res,lw=.7,color='#606c80');axs[1].axhline(0,color='k',lw=.5);axs[1].set_ylabel('Fit - data');axs[1].set_xlabel('Bias / D');axs[1].set_xlim(-10,10)
fig.tight_layout();fig.savefig(ROOT/'figures/sts_normal_fit.png',dpi=190)
