"""Four-pole BdG diagnostic with independent c/f square-lattice dispersions."""
import bdg_fit as base
from bdg_fit import np,json,ROOT,x,y,t,tp,eps,least_squares,plt,time
u=np.cos(2*np.pi*(np.arange(192)+.5)/192)[None,:]
kk=np.cos(2*np.pi*(np.arange(160)+.5)/160)
summ=kk[:,None]+kk[None,:];prod=kk[:,None]*kk[None,:]

def J(z):
    zz=z.real+1j*np.abs(z.imag);a=1/(np.sqrt(zz-1)*np.sqrt(zz+1));return np.where(z.imag>=0,a,a.conj())

def normal_green(z,tc,tpc,tf,tpf,c,b,V):
    z=z[:,None];Bc=-2*tc-4*tpc*u;Bf=-2*tf-4*tpf*u;Cc=c-2*tc*u;Cf=b-2*tf*u
    sc=Bc*(z-Cf);af=Bf*(z-Cc)
    d=np.sqrt((sc-af)**2+4*Bc*Bf*V*V)
    r1=(sc+af+d)/(2*Bc*Bf);r2=(sc+af-d)/(2*Bc*Bf)
    A=(r1-(z-Cf)/Bf)/(Bc*(r1-r2));B=1/Bc-A
    return np.mean(A*J(r1)+B*J(r2),axis=1)

def model(p):
    tc,tpc,tf,tpf,c,b,V,D,eta,amp,b0,b2=p
    z=x+1j*eta;r=np.sqrt(z-D)*np.sqrt(z+D)
    G=.5*(1+z/r)*normal_green(r,tc,tpc,tf,tpf,c,b,V)+.5*(1-z/r)*normal_green(-r,tc,tpc,tf,tpf,c,b,V)
    return -amp*G.imag/np.pi+b0+b2*x*x

def filling(p):
    tc,tpc,tf,tpf,c,b,V,D=p[:8]
    ec=-2*tc*summ-4*tpc*prod+c;ef=-2*tf*summ-4*tpf*prod+b
    C=(ec+ef)/2;d=(ec-ef)/2;R=np.sqrt(d*d+V*V);w=(1+d/R)/2;lp=C+R;lm=C-R
    return float(np.mean(w*(1-lp/np.sqrt(lp*lp+D*D))/2+(1-w)*(1-lm/np.sqrt(lm*lm+D*D))/2))

def main():
    general=json.load(open(ROOT/'data/bdg_general_results.json'))['best']['params']
    s,a,c,b,V,D,eta,A,b0,b2=general
    starts=[[s*t,s*tp,a*t,a*tp,c,b,V,D,eta,A,b0,b2],
            [.4717,.1475,.332,-.1334,1.402,-1.251,4.892,.3,.234,3.551,-.011,.00131],
            [.4717,.1475,.332,-.1334,1.402,-1.251,3.5,2.7,.12,3.551,-.011,.00131],
            [1,.2,-.3,.2,1,-1,3,2.7,.1,5,0,.0013]]
    lo=[.1,-.7,-2,-.7,-6,-6,.05,.05,.015,.1,-.08,-.001]
    hi=[2.5,.7,2.5,.7,6,6,9,6,.8,15,.2,.003]
    results=[]
    for i,p in enumerate(starts):
        tic=time.time();r=least_squares(lambda p:model(p)-y,p,bounds=(lo,hi),max_nfev=250,x_scale='jac',ftol=2e-8,xtol=2e-8)
        rss=float(r.fun@r.fun);sig=np.sqrt(rss/(len(x)-len(p)));cov=np.linalg.pinv(r.jac.T@r.jac)*sig*sig
        o={'params':r.x.tolist(),'param_names':['tc','tpc','tf','tpf','c','b','V','Delta','eta','amplitude','background_constant','background_quadratic'],
           'rms':sig,'rss':rss,'stderr':np.sqrt(np.diag(cov)).tolist(),'covariance':cov.tolist(),
           'nu_physical_c':filling(r.x),'nfev':r.nfev,'success':bool(r.success)}
        results.append(o);best=min(results,key=lambda q:q['rss'])
        json.dump({'multistart':results,'best':best,'t':t,'tprime':tp},open(ROOT/'data/bdg_expanded_results.json','w'),indent=2)
        print(i,'elapsed',round(time.time()-tic,1),'rms',sig,'nu',filling(r.x),'p',r.x,flush=True)
    pred=model(np.array(best['params']))
    np.savez(ROOT/'data/bdg_expanded_best.npz',bias=x,observed=y,fit=pred,params=best['params'])
    fig,axs=plt.subplots(2,1,figsize=(8,5.8),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    axs[0].plot(x,y,lw=.7,color='#188869',alpha=.6,label='Supplied STS');axs[0].plot(x,pred,lw=1.5,color='#172b4d',label='Four-pole BdG fit')
    axs[0].set(title=r'Low-temperature STS at $\nu\simeq0.3$',ylabel='Normalized dI/dV');axs[0].legend(frameon=False)
    axs[1].plot(x,pred-y,lw=.7,color='#172b4d');axs[1].axhline(0,color='.5',lw=.7)
    axs[1].set(xlabel='Gap-centered bias / D',ylabel='Fit - data',xlim=(-10,10));fig.tight_layout()
    fig.savefig(ROOT/'figures/bdg_expanded_fit.png',dpi=200)

if __name__=='__main__':main()
