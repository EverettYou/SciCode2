from fitlib import *
import numpy as np
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp)
def bog(E,xi,sig,bg,sc,Z=1.0):
    u2=0.5*(1+xi/E); v2=1-u2
    return sc*sample(dos(E,Z*u2,sig)+dos(-E,Z*v2,sig),V)+bg
def m_free_kgap(p,V):
    mu,D0,D1,D2,sig,bg,sc=p
    xi=eps-mu; Dk=D0+D1*(CX+CY)+D2*CX*CY
    E=np.sqrt(xi**2+Dk**2)
    return bog(E,xi,sig,bg,sc)
def m_free_egap(p,V):
    mu,D0,D1,sig,bg,sc=p
    xi=eps-mu; Dk=D0+D1*eps
    E=np.sqrt(xi**2+Dk**2)
    return bog(E,xi,sig,bg,sc)
def m_comp(p,V):
    # Bogoliubov on a compressed band a*eps - mu~ with constant gap
    a,mu,D0,sig,bg,sc=p
    xi=a*eps-mu; E=np.sqrt(xi**2+D0**2)
    return bog(E,xi,sig,bg,sc)
def m_comp_kgap(p,V):
    a,mu,D0,D1,D2,sig,bg,sc=p
    xi=a*eps-mu; Dk=D0+D1*(CX+CY)+D2*CX*CY; E=np.sqrt(xi**2+Dk**2)
    return bog(E,xi,sig,bg,sc)
def fit(model,p0,names,xs):
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=xs,diff_step=2e-2)
    p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.diag(cov))
    print("---",model.__name__,"rms resid",np.sqrt(np.mean(r.fun**2)))
    for n_,v,e in zip(names,p,err): print(f"   {n_:6s} = {v:.4f} +- {e:.4f}")
    return p,np.sqrt(np.mean(r.fun**2))
res={}
res['free_kgap']=fit(m_free_kgap,[-0.93,3.9,-1.5,-0.9,0.12,0.08,2.0],['mu','D0','D1','D2','sigma','bg','sc'],[0.2,0.3,0.3,0.3,0.03,0.02,0.3])
res['free_egap']=fit(m_free_egap,[-0.93,3.9,0.7,0.12,0.08,2.0],['mu','D0','D1','sigma','bg','sc'],[0.2,0.3,0.1,0.03,0.02,0.3])
res['comp']=fit(m_comp,[0.5,-0.5,2.4,0.12,0.08,2.0],['a','mu','D0','sigma','bg','sc'],[0.05,0.2,0.3,0.03,0.02,0.3])
res['comp_kgap']=fit(m_comp_kgap,[0.5,-0.5,3.0,-1.0,-0.5,0.12,0.08,2.0],['a','mu','D0','D1','D2','sigma','bg','sc'],[0.05,0.2,0.3,0.3,0.3,0.03,0.02,0.3])
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(4,1,figsize=(12,13))
for ax,(name,m) in zip(axs,[('free_kgap',m_free_kgap),('free_egap',m_free_egap),('comp',m_comp),('comp_kgap',m_comp_kgap)]):
    p,rms=res[name]; ax.plot(V,g,'k',lw=0.6); ax.plot(V,m(p,V),'r',lw=1); ax.set_xlim(-10,10); ax.set_title(f"{name} rms={rms:.4f}"); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('fit_b2.png',dpi=80)
