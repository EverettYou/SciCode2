from fitlib import *
s=STS[0]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
def recenter(Em,Ep):
    mid=(Em.max()+Ep.min())/2; return Em-mid,Ep-mid
def model_HI(p,V):
    t,tp,U,sig,bg,sc=p
    eps=band(t,tp); R=np.sqrt(eps**2+U**2)
    Ep=(eps+R)/2; Em=(eps-R)/2; wp=0.5*(1+eps/R); wm=1-wp
    Em,Ep=recenter(Em,Ep)
    return sc*sample(dos(Em,wm,sig)+dos(Ep,wp,sig),V)+bg
def model_copies(p,V):
    t,tp,U,a,alpha,sig,bg,sc=p
    eps=band(t,tp)
    Ep=U/2+a*eps; Em=-U/2+a*eps; wm=0.5*(1-alpha*eps); wp=1-wm
    Em,Ep=recenter(Em,Ep)
    return sc*sample(dos(Em,wm,sig)+dos(Ep,wp,sig),V)+bg
def model_gen(p,V):
    # independent compressions and quadratic terms
    t,tp,U,am,ap,bm,bp,alpha,sig,bg,sc=p
    eps=band(t,tp)
    Ep=U/2+ap*eps+bp*eps**2; Em=-U/2+am*eps+bm*eps**2; wm=0.5*(1-alpha*eps); wp=1-wm
    Em,Ep=recenter(Em,Ep)
    return sc*sample(dos(Em,wm,sig)+dos(Ep,wp,sig),V)+bg
def fit(model,p0,names,xs):
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=xs,diff_step=2e-2)
    p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.diag(cov))
    print("---",model.__name__,"rms resid",np.sqrt(np.mean(r.fun**2)))
    for n_,v,e in zip(names,p,err): print(f"   {n_:6s} = {v:.4f} +- {e:.4f}")
    return p
pHI=fit(model_HI,[1.0,0.2,12.0,0.1,0.1,3.0],['t','tp','U','sigma','bg','scale'],[0.1,0.05,0.5,0.05,0.02,0.5])
pC=fit(model_copies,[1.0,0.2,12.0,0.5,0.08,0.1,0.1,3.0],['t','tp','U','a','alpha','sigma','bg','scale'],[0.1,0.05,0.5,0.05,0.02,0.05,0.02,0.5])
pG=fit(model_gen,[1.0,0.2,12.0,0.5,0.5,0.0,0.0,0.08,0.1,0.1,3.0],['t','tp','U','a-','a+','b-','b+','alpha','sigma','bg','scale'],[0.1,0.05,0.5,0.05,0.05,0.01,0.01,0.02,0.05,0.02,0.5])
np.save('fit_a_copies.npy',pC); np.save('fit_a_gen.npy',pG); np.save('fit_a_HI.npy',pHI)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(3,1,figsize=(12,10))
for ax,(m,p) in zip(axs,[(model_HI,pHI),(model_copies,pC),(model_gen,pG)]):
    ax.plot(V,g,'k',lw=0.6); ax.plot(V,m(p,V),'r',lw=1); ax.set_xlim(-10,10); ax.set_title(m.__name__)
plt.tight_layout(); plt.savefig('fit_a.png',dpi=80)
