"""Diagnostic: mirrored dispersions with distinct positive/negative linewidths."""
import bdg_symmetric_poles as base
from bdg_symmetric_poles import np,json,ROOT,x,y,t,tp,g0,eps,emin,emax,least_squares,plt,time

def model(p,nu=.3):
    s,gap,r,eta_plus,eta_minus,amp,b0,b2=p
    c=gap-s*emin;qp=(x+1j*eta_plus-c)/s;qm=(-x-1j*eta_minus-c)/s
    G=(((1-nu)-r*qp)*g0(qp)-(nu+r*qm)*g0(qm)+2*r)/s
    return -amp*G.imag/np.pi+b0+b2*x*x

def main():
    results=[]
    for free_nu in [False,True]:
        p=[.5,2.7,0,.07,.2,5,0,.0013]
        lo=[.1,.1,-.06,.015,.015,.1,-.08,-.001];hi=[2.5,6,.06,.8,.8,15,.2,.003]
        if free_nu:p+=[.35];lo+=[.1];hi+=[.8]
        def mod(q):return model(q[:-1],q[-1]) if free_nu else model(q)
        tic=time.time();r=least_squares(lambda p:mod(p)-y,p,bounds=(lo,hi),max_nfev=200,x_scale='jac',ftol=2e-10,xtol=2e-10)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        nu=r.x[-1] if free_nu else .3
        names=['s','gap_minimum','weight_slope_per_D','eta_plus','eta_minus','amplitude','background_constant','background_quadratic']+(['nu'] if free_nu else [])
        o={'params':r.x.tolist(),'param_names':names,'nu_physical_c':nu,'rms':sig,'rss':rss,'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),
           'nfev':r.nfev,'success':bool(r.success),'bic':float(len(x)*np.log(rss/len(x))+len(p)*np.log(len(x))),
           'weight_range':[nu+r.x[2]*emin,nu+r.x[2]*emax]}
        results.append(o)
        json.dump({'fits':results,'t':t,'tprime':tp},open(ROOT/'data/bdg_symmetric_widths_results.json','w'),indent=2)
        print('free nu',free_nu,'sec',round(time.time()-tic,1),'rms',sig,'p',r.x,flush=True)
        pred=mod(r.x);np.savez(ROOT/f'data/bdg_symmetric_widths_{int(free_nu)}.npz',bias=x,observed=y,fit=pred,params=r.x,covariance=cov)
        fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
        axs[0].plot(x,y,lw=.7,color='#188869',alpha=.6,label='Supplied STS');axs[0].plot(x,pred,lw=1.5,color='#172b4d',label='Mirrored poles, unequal linewidths')
        axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
        axs[1].plot(x,pred-y,lw=.7,color='#172b4d');axs[1].axhline(0,color='.5',lw=.7)
        axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10));fig.tight_layout()
        fig.savefig(ROOT/f'figures/bdg_symmetric_widths_{int(free_nu)}.png',dpi=200);plt.close(fig)

if __name__=='__main__':main()
