"""General affine normal dispersions plus common singlet pairing gap."""
import bdg_fit as base
from bdg_fit import np,json,ROOT,x,y,t,tp,g0,eps,least_squares,plt,time

def normal_green(z,s,a,c,b,V):
    if abs(a)<1e-6:return g0((z-c-V*V/(z-b))/s)/s
    d=np.sqrt((s*(z-b)-a*(z-c))**2+4*s*a*V*V)
    r1=(s*(z-b)+a*(z-c)+d)/(2*s*a)
    r2=(s*(z-b)+a*(z-c)-d)/(2*s*a)
    A=(r1-(z-b)/a)/(s*(r1-r2));B=1/s-A
    return A*g0(r1)+B*g0(r2)

def model(p):
    s,a,c,b,V,D,eta,amp,b0,b2=p
    z=x+1j*eta;r=np.sqrt(z-D)*np.sqrt(z+D)
    G=.5*(1+z/r)*normal_green(r,s,a,c,b,V)+.5*(1-z/r)*normal_green(-r,s,a,c,b,V)
    return -amp*G.imag/np.pi+b0+b2*x*x

def filling(p):
    s,a,c,b,V,D=p[:6];C=((s+a)*eps+c+b)/2;d=((s-a)*eps+c-b)/2;R=np.sqrt(d*d+V*V)
    w=(1+d/R)/2;lp=C+R;lm=C-R
    return float(np.mean(w*(1-lp/np.sqrt(lp*lp+D*D))/2+(1-w)*(1-lm/np.sqrt(lm*lm+D*D))/2))

def main():
    shared=json.load(open(ROOT/'data/bdg_fit_results.json'))['best']['physical_params']
    starts=[[shared[k] for k in ['s','a','c','b','V','Delta','eta','amplitude','background_constant','background_quadratic']],
            [.5,.3,1,-1,4,2.7,.08,5,0,.0013],
            [.7,-.7,1,-1,3,2.7,.08,5,0,.0013],
            [.9,-1.06,1.36,-1.4,4.8,.5,.7,4.5,-.036,.001],
            [1,.1,1.8,-.5,2.5,2.7,.08,5,0,.0013],
            [.3,1,1,-1,3,2.7,.1,5,0,.0013]]
    lo=[.1,-2.5,-6,-6,.05,.05,.015,.1,-.08,-.001]
    hi=[2.5,2.5,6,6,9,6,.8,15,.2,.003]
    results=[]
    for i,p in enumerate(starts):
        tic=time.time();r=least_squares(lambda p:model(p)-y,p,bounds=(lo,hi),max_nfev=220,x_scale='jac',ftol=2e-8,xtol=2e-8)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        o={'params':r.x.tolist(),'param_names':['s','a','c','b','V','Delta','eta','amplitude','background_constant','background_quadratic'],
           'rms':sig,'rss':rss,'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),
           'nu_physical_c':filling(r.x),'nfev':r.nfev,'success':bool(r.success)}
        results.append(o);best=min(results,key=lambda q:q['rss'])
        json.dump({'multistart':results,'best':best,'t':t,'tprime':tp},open(ROOT/'data/bdg_general_results.json','w'),indent=2)
        print(i,'elapsed',round(time.time()-tic,1),'rms',sig,'nu',filling(r.x),'p',r.x,flush=True)
    pred=model(np.array(best['params']))
    np.savez(ROOT/'data/bdg_general_best.npz',bias=x,observed=y,fit=pred,params=best['params'])
    fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    axs[0].plot(x,y,lw=.7,color='#188869',alpha=.6,label='Supplied STS');axs[0].plot(x,pred,lw=1.5,color='#172b4d',label='Four-pole BdG fit')
    axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
    axs[1].plot(x,pred-y,lw=.7,color='#172b4d');axs[1].axhline(0,color='.5',lw=.7)
    axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10));fig.tight_layout()
    fig.savefig(ROOT/'figures/bdg_general_fit.png',dpi=200)

if __name__=='__main__':main()
