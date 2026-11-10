import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import json,numpy as np
from pathlib import Path
from scipy.optimize import least_squares,brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];dat=json.load(open((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')))['measurements'][0]['spectra'][2];x=np.array(dat['bias']);y=np.array(dat['dI_dV']);o=json.load(open(R/'data/sts_fit_results.json'));t,tp=o['normal']['params'][:2];old=o['low_models']['2']['BCS'];po=np.array(old['params'])
u=np.cos(2*np.pi*(np.arange(512)+.5)/512);co=np.cos(2*np.pi*np.arange(256)/256);eps=-2*t*(co[:,None]+co[None,:])-4*tp*co[:,None]*co[None,:]
def g(z):
 zz=z.real+1j*np.abs(z.imag);v=zz[:,None]+2*t*u[None,:];b=2*t+4*tp*u[None,:];v=np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1);return np.where(z.imag>=0,v,v.conj())
def fill(s,c,D):
 ec=s*eps+c;return np.mean(.5*(1-ec/np.sqrt(ec**2+D*D)))
def spec(s,c,D,eta,A,b0,b2):
 z=x+1j*eta;rr=np.sqrt(z-D)*np.sqrt(z+D)
 gf=.5*(1+z/rr)*g((rr-c)/s)/s+.5*(1-z/rr)*g((-rr-c)/s)/s
 return -A*gf.imag/np.pi+b0+b2*x*x
nu_fit=float(fill(*po[:3]))
lo=[.2,.1,.015,.01,-.08,-.001];hi=[2,7,.8,15,.2,.003]
def mod(p):
 s,D,eta,A,b0,b2=p;c=brentq(lambda c:fill(s,c,D)-.2,-20,20,xtol=1e-10)
 return spec(s,c,D,eta,A,b0,b2)
p0=po[[0,2,3,4,5,6]];r=least_squares(lambda p:mod(p)-y,p0,bounds=(lo,hi),max_nfev=150,x_scale='jac');s,D,eta,A,b0,b2=r.x;c=brentq(lambda c:fill(s,c,D)-.2,-20,20)
sig=float(np.sqrt(r.fun@r.fun/(len(x)-len(p0))));cov=np.linalg.pinv(r.jac.T@r.jac)*sig**2
out={'unconstrained_filling':nu_fit,'unconstrained_rms':old['rms'],'constrained_params':{'s':s,'c':c,'mu':-c,'Delta':D,'eta':eta,'amplitude':A,'b0':b0,'b2':b2},'constrained_rms':sig,'constrained_rss':float(r.fun@r.fun),'free_param_names':['s','Delta','eta','amp','b0','b2'],'covariance':cov.tolist(),'note':'Number equation evaluated at zero temperature on 256x256 Brillouin grid. Target filling .2 exact for test although sample label approximate. Normal band t,tp fixed; constant tunneling matrix element. Does not exclude orbital/matrix-element-dependent models.'}
json.dump(out,open(R/'data/sts_bcs_density_test.json','w'),indent=2);np.savez(R/'data/sts_bcs_density_test.npz',bias=x,observed=y,unconstrained=spec(*po),constrained=mod(r.x))
print(json.dumps(out,indent=2))
fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
axs[0].plot(x,y,color='.45',lw=.7,alpha=.6,label='Measurements');axs[0].plot(x,spec(*po),color='#2564a5',lw=1.4,label=f'Unconstrained BCS: filling {nu_fit:.3f}');axs[0].plot(x,mod(r.x),color='#bf643b',lw=1.4,label='BCS constrained to filling 0.200');axs[0].legend(frameon=False);axs[0].set_ylabel('Normalized dI/dV');axs[0].set_title(r'Nominal $\nu\simeq0.2$: density consistency test')
axs[1].plot(x,mod(r.x)-y,color='#bf643b',lw=.7);axs[1].axhline(0,color='k',lw=.5);axs[1].set_ylabel('Constrained - data');axs[1].set_xlabel('Bias / D');axs[1].set_xlim(-10,10);fig.tight_layout();fig.savefig(R/'figures/sts_bcs_density_test.png',dpi=190)
