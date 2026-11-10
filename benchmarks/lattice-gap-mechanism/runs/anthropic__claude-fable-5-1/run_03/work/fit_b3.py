from fitlib import *
import numpy as np
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp)
def m_bog_lin(p,V):
    c,a,alpha,beta,sig,bg,Z=p
    E=c+a*eps; xi=alpha+beta*eps
    s_=np.clip(xi/E,-1,1)
    u2=0.5*(1+s_); v2=0.5*(1-s_)
    return Z*sample(dos(E,u2,sig)+dos(-E,v2,sig),V)+bg
def m_bog_lin2(p,V):
    # allow E quadratic
    c,a,b,alpha,beta,sig,bg,Z=p
    E=c+a*eps+b*eps**2; xi=alpha+beta*eps
    s_=np.clip(xi/E,-1,1)
    u2=0.5*(1+s_); v2=0.5*(1-s_)
    return Z*sample(dos(E,u2,sig)+dos(-E,v2,sig),V)+bg
def fit(model,p0,names,xs):
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=xs,diff_step=2e-2)
    p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.abs(np.diag(cov)))
    print("---",model.__name__,"rms resid",np.sqrt(np.mean(r.fun**2)))
    for n_,v,e in zip(names,p,err): print(f"   {n_:6s} = {v:.4f} +- {e:.4f}")
    return p,np.sqrt(np.mean(r.fun**2))
p1,r1=fit(m_bog_lin,[4.8,0.5,0.8,0.25,0.12,0.08,2.5],['c','a','alpha','beta','sigma','bg','Z'],[0.2,0.05,0.2,0.05,0.03,0.02,0.3])
p2,r2=fit(m_bog_lin2,[4.8,0.5,0.0,0.8,0.25,0.12,0.08,2.5],['c','a','b','alpha','beta','sigma','bg','Z'],[0.2,0.05,0.01,0.2,0.05,0.03,0.02,0.3])
for p,name in [(p1,'lin'),(p2,'lin2')]:
    if name=='lin': c,a,alpha,beta,sig,bg,Z=p; b=0
    else: c,a,b,alpha,beta,sig,bg,Z=p
    print(f"[{name}] at (0,0): eps={eps.min():.2f} E={c+a*eps.min()+b*eps.min()**2:.2f} xi~={alpha+beta*eps.min():.2f}; at vH: E={c+a*4*tp+b*(4*tp)**2:.2f} xi~={alpha+beta*4*tp:.2f}; at (pi,pi): E={c+a*eps.max()+b*eps.max()**2:.2f} xi~={alpha+beta*eps.max():.2f}")
    E=c+a*eps+b*eps**2; xi=alpha+beta*eps; Dk=np.sqrt(np.clip(E**2-xi**2,0,None))
    print(f"      implied Delta_k: min {Dk.min():.2f} max {Dk.max():.2f}; mean v^2 = {np.mean(0.5*(1-xi/E)):.3f}")
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,1,figsize=(12,7))
for ax,(m,p,r) in zip(axs,[(m_bog_lin,p1,r1),(m_bog_lin2,p2,r2)]):
    ax.plot(V,g,'k',lw=0.6); ax.plot(V,m(p,V),'r',lw=1); ax.set_xlim(-10,10); ax.set_title(f"{m.__name__} rms={r:.4f}"); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('fit_b3.png',dpi=80)
np.save('fit_b3.npy',p2)
