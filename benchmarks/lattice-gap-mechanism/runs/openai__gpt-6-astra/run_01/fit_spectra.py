"""Conditional spectral fits to measurements.json; no compound parameters used."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'measurements.json').read_text())
COS = np.cos(2*np.pi*(np.arange(768)+0.5)/768)

def lattice_g(z, t, tp):
    """Local resolvent of -2t(cos kx+cos ky)-4tp cos kx cos ky."""
    z = np.asarray(z, complex)
    a = z[..., None] + 2*t*COS
    b = 2*t + 4*tp*COS
    return np.mean(1/(np.sqrt(a-b)*np.sqrt(a+b)), axis=-1)

def normal_model(p, x):
    t,tp,mu,eta,scale,b0,b2 = p
    return -scale*lattice_g(x+mu+1j*eta,t,tp).imag/np.pi+b0+b2*x*x

def two_pole_model(p,x):
    t,tp,M,center,b,eta,scale,b0,b2 = p
    zp=x-center-M+1j*eta
    zm=x-center+M+1j*eta
    g=(.5+b*zp)*lattice_g(zp,t,tp)+(.5-b*zm)*lattice_g(zm,t,tp)
    return -scale*g.imag/np.pi+b0+b2*x*x

def bcs_model(p,x,t,tp):
    mu,delta,eta,scale,b0,b2=p
    z=x+1j*eta
    root=np.sqrt(z-delta)*np.sqrt(z+delta)
    g=.5*(1+z/root)*lattice_g(mu+root,t,tp)+.5*(1-z/root)*lattice_g(mu-root,t,tp)
    return -scale*g.imag/np.pi+b0+b2*x*x

def fit(fn,x,y,p0,bounds):
    res=least_squares(lambda p:fn(p,x)-y,p0,bounds=bounds,max_nfev=180,
                      ftol=2e-7,xtol=2e-7,gtol=2e-7,diff_step=2e-4)
    dof=len(y)-len(p0)
    sig=np.sqrt(np.sum(res.fun**2)/dof)
    cov=np.linalg.pinv(res.jac.T@res.jac)*sig**2
    res.covariance=cov
    return res, np.sqrt(np.diag(cov)), sig

def main():
    spectra=DATA['measurements'][0]['spectra']
    result={}
    fig,axs=plt.subplots(2,2,figsize=(12,8),sharex=True)
    s=spectra[3];x=np.array(s['bias']);y=np.array(s['dI_dV'])
    r,e,noise=fit(normal_model,x,y,[1,.2,-.8,.09,2,.015,.001],
                 ([.6,-.42,-3,.02,.1,-.1,0],[1.5,.6,1,.5,10,.15,.005]))
    print('normal',r.x,'errors',e,'rms',noise,flush=True)
    result['normal']={'parameters':r.x.tolist(),'conditional_errors':e.tolist(),'covariance':r.covariance.tolist(),'rms':noise,
      'names':['t','tp','mu','eta','scale','background_constant','background_quadratic']}
    ax=axs[1,1];ax.plot(x,y,lw=.7,label='data');ax.plot(x,normal_model(r.x,x),label='conditional band fit');ax.legend();ax.set_title('(d) high T')
    t,tp=r.x[:2]
    for idx in [0]:
        s=spectra[idx];x=np.array(s['bias']);y=np.array(s['dI_dV'])
        # The problem fixes mu at the gap midpoint.  For these poles that
        # requires center=4*tp, rather than an independently fitted offset.
        transform=np.zeros((9,8))
        transform[0,0]=transform[1,1]=transform[2,2]=1
        transform[3,1]=4
        for i in range(4,9):transform[i,i-1]=1
        r,e,noise=fit(lambda p,x:two_pole_model(transform@p,x),x,y,[.5,.1,6,.083,.06,4,0,.001],
                 ([.3,-.2,4,-.15,.02,.1,-.1,0],[.8,.3,8,.15,.3,10,.1,.003]))
        r.x=transform@r.x
        r.covariance=transform@r.covariance@transform.T
        e=np.sqrt(np.diag(r.covariance))
        print('two pole',r.x,'errors',e,'rms',noise,flush=True)
        result['half_two_pole']={'parameters':r.x.tolist(),'conditional_errors':e.tolist(),'covariance':r.covariance.tolist(),'rms':noise,
          'names':['t_effective','tp_effective','M','center','residue_slope','eta','scale','background_constant','background_quadratic']}
        ax=axs[0,0];ax.plot(x,y,lw=.7,label='data');ax.plot(x,two_pole_model(r.x,x),label='conditional two-pole fit');ax.legend();ax.set_title('(a) half filling')
    for idx in [1,2]:
        s=spectra[idx];x=np.array(s['bias']);y=np.array(s['dI_dV'])
        r,e,noise=fit(lambda p,x:bcs_model(p,x,t,tp),x,y,[-1.5,2.5 if idx==1 else 2,.06,3,.01,.001],
                     ([-6,.2,.02,.1,-.1,0],[3,6,.6,10,.2,.005]))
        print('bcs',s['panel'],r.x,'errors',e,'rms',noise,flush=True)
        result['bcs_'+s['panel']]={'parameters':r.x.tolist(),'conditional_errors':e.tolist(),'rms':noise,
          'names':['mu','gap','eta','scale','background_constant','background_quadratic']}
        ax=axs.ravel()[idx];ax.plot(x,y,lw=.7,label='data');ax.plot(x,bcs_model(r.x,x,t,tp),label='conditional BCS fit');ax.legend();ax.set_title('('+s['panel']+') '+s['filling'])
    for ax in axs.flat:
        ax.set_xlabel('bias / D');ax.set_ylabel('normalized conductance');ax.set_xlim(-10,10)
    fig.suptitle('Fits require assumptions about dispersion, residues and tunneling background',fontsize=12)
    fig.tight_layout();fig.savefig(ROOT/'conditional_spectral_fits.png',dpi=180);fig.savefig(ROOT/'conditional_spectral_fits.pdf');plt.close(fig)
    (ROOT/'spectral_fit_results.json').write_text(json.dumps(result,indent=2))

if __name__=='__main__':main()
