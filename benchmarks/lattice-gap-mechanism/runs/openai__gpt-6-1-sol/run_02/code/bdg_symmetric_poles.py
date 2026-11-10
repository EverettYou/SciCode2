"""Causal mirrored-pole ansatz E(k)=gap+s[eps(k)-eps_min].

Occupied residue w(k)=nu+r*eps(k); unoccupied residue 1-w(k).
This is a phenomenological fully gapped momentum-dependent BdG spectrum.
Its physical per-spin filling is exactly nu, since mean eps=0.
"""
import bdg_fit as base
from bdg_fit import np,json,ROOT,x,y,t,tp,g0,eps,least_squares,plt,time
emin=-4*t-4*tp;emax=4*t-4*tp

def green(z,s,gap,r,nu=.3):
    c=gap-s*emin;qp=(z-c)/s;qm=(-z-c)/s
    return (((1-nu)-r*qp)*g0(qp)-(nu+r*qm)*g0(qm)+2*r)/s

def model(p,nu=.3):
    s,gap,r,eta,amp,b0,b2=p
    return -amp*green(x+1j*eta,s,gap,r,nu).imag/np.pi+b0+b2*x*x

def main():
    starts=[[.5,2.7,.02,.08,5,0,.0013],[.5,2.7,-.02,.08,5,0,.0013],[.5,2.7,0,.08,5,0,.0013]]
    lo=[.1,.1,-.06,.015,.1,-.08,-.001];hi=[2.5,6,.06,.8,15,.2,.003]
    results=[]
    for i,p in enumerate(starts):
        tic=time.time();r=least_squares(lambda p:model(p)-y,p,bounds=(lo,hi),max_nfev=200,x_scale='jac',ftol=2e-10,xtol=2e-10)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        s,gap,wr,eta,A,b0,b2=r.x
        o={'params':r.x.tolist(),'param_names':['s','gap_minimum','weight_slope_per_D','eta','amplitude','background_constant','background_quadratic'],
           'c':gap-s*emin,'nu_physical_c':.3,'weight_range':[.3+wr*emin,.3+wr*emax],
           'rms':sig,'rss':rss,'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),
           'nfev':r.nfev,'success':bool(r.success),'bic':float(len(x)*np.log(rss/len(x))+len(p)*np.log(len(x)))}
        results.append(o);best=min(results,key=lambda q:q['rss'])
        json.dump({'multistart':results,'best':best,'t':t,'tprime':tp,
                   'definition':'E=gap+s*(eps-epsmin), negative residue w=nu+r*eps, positive residue1-w. Equivalent ξ=(1−2w)E, Δ(k)=2sqrt[w(1−w)]E; not a microscopic interacting Hamiltonian fit.'},open(ROOT/'data/bdg_symmetric_results.json','w'),indent=2)
        print(i,'elapsed',round(time.time()-tic,1),'rms',sig,'p',r.x,flush=True)
    p=np.array(best['params']);pred=model(p)
    np.savez(ROOT/'data/bdg_symmetric_best.npz',bias=x,observed=y,fit=pred,params=p,covariance=best['covariance'])
    fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    axs[0].plot(x,y,lw=.7,color='#188869',alpha=.6,label='Supplied STS');axs[0].plot(x,pred,lw=1.5,color='#172b4d',label='Mirrored poles, physical filling 0.3')
    axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
    axs[1].plot(x,pred-y,lw=.7,color='#172b4d');axs[1].axhline(0,color='.5',lw=.7)
    axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10));fig.tight_layout()
    fig.savefig(ROOT/'figures/bdg_symmetric_fit.png',dpi=200)
    # Exact algebra validation against an independent momentum-space sum.
    z=np.array([-5+.2j,4+.2j,1+.2j]);s,gap,wr=p[:3];E=gap+s*(eps-emin);w=.3+wr*eps
    direct=np.array([np.mean(w/(zz+E)+(1-w)/(zz-E)) for zz in z])
    print('resolvent validation',float(np.max(abs(direct-green(z,s,gap,wr)))),flush=True)

if __name__=='__main__':main()
