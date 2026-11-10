"""Four-pole singlet BdG ansatz for the nu~0.3 local spectrum.

This is a phenomenological physical-electron spectral model, not a validated
microscopic Hamiltonian or thermodynamic solution.
"""
from pathlib import Path
import json, os, time
os.environ.setdefault('MPLCONFIGDIR','/tmp/bdg-mpl-cache')
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
S=json.load(open((Path(__file__).resolve().parents[1] / 'data' / 'measurements.json')))['measurements'][0]['spectra'][1]
x=np.asarray(S['bias']);y=np.asarray(S['dI_dV'])
t,tp=json.load(open(ROOT/'data/sts_fit_results.json'))['normal']['params'][:2]
cx=np.cos(2*np.pi*(np.arange(192)+.5)/192)
kk=np.cos(2*np.pi*(np.arange(160)+.5)/160)
eps=-2*t*(kk[:,None]+kk[None,:])-4*tp*kk[:,None]*kk[None,:]

def g0(z):
    z=np.asarray(z);sg=np.where(z.imag>=0,1.,-1.);zz=z.real+1j*np.abs(z.imag)
    v=zz[:,None]+2*t*cx[None,:];b=2*t+4*tp*cx[None,:]
    g=np.mean(1/(np.sqrt(v-b)*np.sqrt(v+b)),axis=1)
    return np.where(sg>0,g,g.conj())

def normal_green(z,s,C,R,w):
    return (w*g0((z-C-R)/s)+(1-w)*g0((z-C+R)/s))/s

def dos(z,s,C,R,w,Delta):
    r=np.sqrt(z-Delta)*np.sqrt(z+Delta)
    green=.5*(1+z/r)*normal_green(r,s,C,R,w)+.5*(1-z/r)*normal_green(-r,s,C,R,w)
    return -green.imag/np.pi

def model(p):
    s,C,R,w,Delta,eta,amp,b0,b2=p
    return amp*dos(x+1j*eta,s,C,R,w,Delta)+b0+b2*x*x

def filling(p):
    s,C,R,w,Delta=p[:5]
    lp=s*eps+C+R;lm=s*eps+C-R
    return float(np.mean(w*(1-lp/np.sqrt(lp*lp+Delta*Delta))/2+(1-w)*(1-lm/np.sqrt(lm*lm+Delta*Delta))/2))

def physparams(p):
    s,C,R,w,D,eta,A,b0,b2=p
    delta=R*(2*w-1)
    return {'s':s,'a':s,'c':C+delta,'b':C-delta,
            'V':2*R*np.sqrt(w*(1-w)),'Delta':D,'eta':eta,
            'amplitude':A,'background_constant':b0,'background_quadratic':b2,
            'nu_physical_c':filling(p)}

def main():
    bounds=([.15,-5,.01,.01,.05,.015,.1,-.08,-.001],[2.5,5,9,.99,6,.8,15,.2,.003])
    starts=[ [.5,1,4,.5,2.7,.08,5,0,.0013],
             [.5,0,4,.65,2.7,.08,5,0,.0013],
             [.5,1,3.5,.7,3,.1,5,0,.0013],
             [1,1,3,.6,2.7,.15,5,0,.0013],
             [.5,0,5,.5,.5,.08,5,0,.0013] ]
    fits=[]
    for i,p in enumerate(starts):
        tic=time.time()
        r=least_squares(lambda p:model(p)-y,p,bounds=bounds,max_nfev=150,x_scale='jac',ftol=2e-8,xtol=2e-8)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        fit={'param_names':['shared_dispersion_scale','C','R','upper_c_weight','Delta','eta','amplitude','background_constant','background_quadratic'],
             'params':r.x.tolist(),'physical_params':physparams(r.x),'rss':rss,'rms':sig,'stderr':np.sqrt(np.diag(cov)).tolist(),
             'covariance':cov.tolist(),'success':bool(r.success),'nfev':r.nfev,
             'bic':float(len(x)*np.log(rss/len(x))+len(p)*np.log(len(x)))}
        fits.append(fit)
        print(i,'elapsed',round(time.time()-tic,2),'rms',round(sig,6),'nu',filling(r.x),'params',r.x,flush=True)
        best=min(fits,key=lambda z:z['rss'])
        json.dump({'shared_slope_multistart':fits,'best':best,'t':t,'tprime':tp,
                   'note':'Phenomenological four-pole ansatz. Covariance conditional on iid residual noise and fixed high-T hopping parameters.'},open(ROOT/'data/bdg_fit_results.json','w'),indent=2)
    best=min(fits,key=lambda z:z['rss']);p=np.array(best['params']);pred=model(p)
    np.savez(ROOT/'data/bdg_best_shared.npz',bias=x,observed=y,fit=pred,params=p)
    fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    axs[0].plot(x,y,color='#188869',lw=.8,alpha=.6,label='Supplied STS')
    axs[0].plot(x,pred,color='#172b4d',lw=1.4,label='Four-pole singlet BdG fit')
    axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
    axs[1].plot(x,pred-y,color='#172b4d',lw=.7);axs[1].axhline(0,color='.5',lw=.7)
    axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10))
    fig.tight_layout();fig.savefig(ROOT/'figures/bdg_shared_fit.png',dpi=200)

if __name__=='__main__':main()
