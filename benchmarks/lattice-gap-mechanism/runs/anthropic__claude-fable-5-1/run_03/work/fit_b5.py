from fitlib import *
import numpy as np
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp); mu0=mu_for_filling(eps,0.6)
def model(p,V):
    c,a,b,D1,alpha,beta,mu,sig,bg,sc=p
    xi=eps-mu; Z=0.5*(1+xi/np.sqrt(xi**2+D1**2))      # in-window weight = u_k^2 of BCS on bare band
    E=c+a*eps+b*eps**2; xt=alpha+beta*eps
    s_=np.clip(xt/E,-1,1); pp=0.5*(1+s_); pm=0.5*(1-s_)
    return sc*sample(dos(E,Z*pp,sig)+dos(-E,Z*pm,sig),V)+bg
names=['c','a','b','D1','alpha','beta','mu','sigma','bg','sc']
best=None
for D10 in [1.5,2.5,4.0]:
  for al0,be0 in [(0.5,0.3),(1.5,0.4),(0.0,0.5)]:
    p0=[4.8,0.5,0.0,D10,al0,be0,mu0,0.15,0.06,3.0]
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=[0.2,0.05,0.01,0.3,0.2,0.05,0.2,0.03,0.02,0.3],diff_step=2e-2,
                    bounds=([0,0.1,-0.1,0.1,-5,-2,-5,0.03,0,0.1],[10,1.5,0.1,10,5,2,5,0.6,0.3,20]))
    rms=np.sqrt(np.mean(r.fun**2))
    if best is None or rms<best[0]: best=(rms,r)
rms,r=best; p=r.x
J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.abs(np.diag(cov)))
print("rms",rms)
for n_,v,e in zip(names,p,err): print(f"  {n_:6s} = {v:.4f} +- {e:.4f}")
c,a,b,D1,alpha,beta,mu,sig,bg,sc=p
xi=eps-mu; Z=0.5*(1+xi/np.sqrt(xi**2+D1**2)); E=c+a*eps+b*eps**2; xt=alpha+beta*eps; s_=np.clip(xt/E,-1,1)
print("Z at Gamma,vH,M:",Z.min(),0.5*(1+(4*tp-mu)/np.sqrt((4*tp-mu)**2+D1**2)),Z.max())
print("<Z>=",Z.mean()," lower weight <Z pm>=",np.mean(Z*0.5*(1-s_))," upper <Z pp>=",np.mean(Z*0.5*(1+s_)), " missing (UHB) <1-Z>=",np.mean(1-Z))
print("E range",E.min(),E.max()," xtilde range",xt.min(),xt.max())
np.save('fit_b5.npy',p)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.figure(figsize=(12,4)); plt.plot(V,g,'k',lw=0.6); plt.plot(V,model(p,V),'r'); plt.xlim(-10,10); plt.grid(alpha=0.3); plt.title(f'Mott-BCS: Z=u^2(bare,D1), mirror compressed bands; rms={rms:.4f}'); plt.savefig('fit_b5.png',dpi=80)
