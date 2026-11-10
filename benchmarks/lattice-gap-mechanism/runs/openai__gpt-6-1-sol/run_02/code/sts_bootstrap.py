import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
import numpy as np,json,time
from pathlib import Path
from scipy.optimize import least_squares
from scipy.integrate import quad
R=Path(__file__).resolve().parents[1];dat=json.load(open((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')))['measurements'][0]['spectra'];x=np.array(dat[0]['bias']);yh=np.array(dat[3]['dI_dV']);yl=np.array(dat[0]['dI_dV'])
o=json.load(open(R/'data/sts_fit_results.json'));ph=np.array(o['normal']['params']);pl=np.array(o['half_linear_weights']['params'])
u=np.cos(2*np.pi*(np.arange(512)+.5)/512)
def g(z,t,tp):
 v=z[:,None]+2*t*u[None,:];b=2*t+4*tp*u[None,:]
 return np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1)
def normal(p):
 t,tp,mu,eta,A,b0,b2=p
 return -A*g(x+mu+1j*eta,t,tp).imag/np.pi+b0+b2*x*x
def half(p,t,tp):
 s,V,r,eta,A,b0,b2=p;c=4*s*tp;zm=x-c+V+1j*eta;zp=x-c-V+1j*eta
 m=(.5-r*zm/s)*g(zm/s,t,tp)/s+(.5+r*zp/s)*g(zp/s,t,tp)/s
 return -A*m.imag/np.pi+b0+b2*x*x
loH=[.5,-.49,-3,.015,.1,0,-.003];hiH=[1.8,.49,3,.6,10,.5,.003]
loL=[.2,4,-.09,.015,.1,-.03,0];hiL=[1,8,.09,.5,10,.03,.003]
def area(t,tp,s,V,r):
 den=s-2*V*r;c=4*s*tp;ecut=-c/den
 def f(k):
  co=np.cos(k);th=-(ecut+2*t*co)/(2*t+4*tp*co)
  return np.arccos(np.clip(th,-1,1))/np.pi
 ar=quad(f,0,np.pi,epsabs=2e-8,limit=100)[0]/np.pi
 return ar,ecut
mh=normal(ph);ml=half(pl,*ph[:2]);rh=yh-mh;rl=yl-ml;rh-=rh.mean();rl-=rl.mean()
rng=np.random.default_rng(48127);samples=[];start=time.time()
N=120
for i in range(N):
 bh=mh+rng.choice(rh,len(x),replace=True)
 fitH=least_squares(lambda p:normal(p)-bh,ph,bounds=(loH,hiH),max_nfev=55,x_scale='jac',ftol=1e-6,xtol=1e-6)
 # Half residual bootstrap propagated through the independently refit normal band.
 bl=ml+rng.choice(rl,len(x),replace=True)
 fitL=least_squares(lambda p:half(p,*fitH.x[:2])-bl,pl,bounds=(loL,hiL),max_nfev=55,x_scale='jac',ftol=1e-6,xtol=1e-6)
 t,tp=fitH.x[:2];s,V,r=fitL.x[:3];ar,ec=area(t,tp,s,V,r)
 samples.append(np.r_[fitH.x,fitL.x,ar,ec,2*(V-4*s*t)])
 if i%20==19: print(i+1,'of',N,'seconds',round(time.time()-start,1),flush=True)
samples=np.array(samples);names=['t','tprime','mu_high','eta_high','amplitude_high','b0_high','b2_high','s','V','r','eta_half','amplitude_half','b0_half','b2_half','zero_area_fraction','zero_epsilon_threshold','full_STS_gap']
center=np.r_[ph,pl,*area(*ph[:2],*pl[:3]),2*(pl[1]-4*pl[0]*ph[0])]
summary={name:{'estimate':float(center[i]),'bootstrap_sd':float(np.std(samples[:,i],ddof=1)),'bootstrap_95_percentile':np.percentile(samples[:,i],[2.5,97.5]).tolist()} for i,name in enumerate(names)}
# Moment, positivity, sum-rule, grid-convergence checks at the central fit.
checks={};t,tp=ph[:2];s,V,r=pl[:3]
for Ngrid in [128,256,512,1024,2048]:
 co=np.cos(2*np.pi*np.arange(Ngrid)/Ngrid);eps=-2*t*(co[:,None]+co[None,:])-4*tp*co[:,None]*co[None,:]
 ef=(s-2*V*r)*eps+4*s*tp
 checks[str(Ngrid)]={'zero_area_fraction':float(np.mean(ef<0)), 'filling':float(np.mean(.5-r*eps)), 'min_pole_weight':float(np.min(.5-np.abs(r*eps)))}
out={'method':'120 iid residual bootstrap replicates, high-T fit refit first and t,tprime propagated into half fit. All reported intervals conditional on model, background and iid noise assumptions; not microscopic confidence bounds. Seed48127.','n_bootstrap':N,'summary':summary,'covariance_all':np.cov(samples,rowvar=False).tolist(),'names':names,'grid_checks':checks,'quadrature_area':float(area(t,tp,s,V,r)[0]),'wall_seconds':time.time()-start}
json.dump(out,open(R/'data/sts_bootstrap.json','w'),indent=2);np.savez(R/'data/sts_bootstrap_samples.npz',samples=samples,names=names)
print(json.dumps({'summary':summary,'grid_checks':checks},indent=2))
