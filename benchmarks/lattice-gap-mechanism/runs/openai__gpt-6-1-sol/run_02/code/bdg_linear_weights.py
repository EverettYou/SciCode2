"""BdG of rigid split poles with physical positive momentum-dependent residues."""
import bdg_fit as base
from bdg_fit import np,json,ROOT,x,y,t,tp,g0,eps,least_squares,plt,time
emin=-4*t-4*tp;emax=4*t-4*tp

def weights(wlo,whi):
    r=(whi-wlo)/(emax-emin);w0=wlo-r*emin
    return w0,r

def normal_green(z,s,c,V,wlo,whi):
    w0,r=weights(wlo,whi);qp=(z-c-V)/s;qm=(z-c+V)/s
    return ((w0+r*qp)*g0(qp)+(1-w0-r*qm)*g0(qm))/s

def model(p):
    s,c,V,wlo,whi,D,eta,amp,b0,b2=p
    z=x+1j*eta;r=np.sqrt(z-D)*np.sqrt(z+D)
    G=.5*(1+z/r)*normal_green(r,s,c,V,wlo,whi)+.5*(1-z/r)*normal_green(-r,s,c,V,wlo,whi)
    return -amp*G.imag/np.pi+b0+b2*x*x

def filling(p):
    s,c,V,wlo,whi,D=p[:6];w0,r=weights(wlo,whi);w=w0+r*eps
    lp=s*eps+c+V;lm=s*eps+c-V
    return float(np.mean(w*(1-lp/np.sqrt(lp*lp+D*D))/2+(1-w)*(1-lm/np.sqrt(lm*lm+D*D))/2))

def main():
    starts=[[.5,.4,4,.56,.8,2,.08,5,0,.0013],
            [.5,.4,4.5,.56,.8,1,.08,5,0,.0013],
            [.5,.4,3.5,.56,.8,3,.08,5,0,.0013],
            [.6,1,4,.6,.6,2,.08,5,0,.0013],
            [.5,-1,4,.6,.8,2,.08,5,0,.0013],
            [.5,1,4,.8,.5,2,.08,5,0,.0013]]
    lo=[.1,-6,.05,.001,.001,.05,.015,.1,-.08,-.001]
    hi=[2.5,6,9,.999,.999,6,.8,15,.2,.003]
    results=[]
    for i,p in enumerate(starts):
        tic=time.time();r=least_squares(lambda p:model(p)-y,p,bounds=(lo,hi),max_nfev=250,x_scale='jac',ftol=2e-8,xtol=2e-8)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        w0,wr=weights(r.x[3],r.x[4])
        o={'params':r.x.tolist(),'param_names':['s','c','V','w_at_eps_min','w_at_eps_max','Delta','eta','amplitude','background_constant','background_quadratic'],
           'w0':w0,'weight_slope_per_D':wr,'rms':sig,'rss':rss,'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),
           'nu_physical_c':filling(r.x),'nfev':r.nfev,'success':bool(r.success)}
        results.append(o);best=min(results,key=lambda q:q['rss'])
        json.dump({'multistart':results,'best':best,'t':t,'tprime':tp},open(ROOT/'data/bdg_linear_weights_results.json','w'),indent=2)
        print(i,'elapsed',round(time.time()-tic,1),'rms',sig,'nu',filling(r.x),'p',r.x,flush=True)
    pred=model(np.array(best['params']))
    np.savez(ROOT/'data/bdg_linear_weights_best.npz',bias=x,observed=y,fit=pred,params=best['params'])
    fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    axs[0].plot(x,y,lw=.7,color='#188869',alpha=.6,label='Supplied STS');axs[0].plot(x,pred,lw=1.5,color='#172b4d',label='Four-pole BdG fit, linear normal weights')
    axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
    axs[1].plot(x,pred-y,lw=.7,color='#172b4d');axs[1].axhline(0,color='.5',lw=.7)
    axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10));fig.tight_layout()
    fig.savefig(ROOT/'figures/bdg_linear_weights_fit.png',dpi=200)

if __name__=='__main__':main()
