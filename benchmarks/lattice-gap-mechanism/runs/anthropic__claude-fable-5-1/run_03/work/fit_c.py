from fitlib import *
s=STS[2]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
def model(p,V):
    t,tp,mu,Dl,sig,bg,sc=p
    eps=band(t,tp); xi=eps-mu; E=np.sqrt(xi**2+Dl**2)
    u2=0.5*(1+xi/E); v2=1-u2
    rho=dos(E,u2,sig)+dos(-E,v2,sig)
    return sc*sample(rho,V)+bg
def resid(p): return model(p,V)-g
p0=[1.0,0.2,-1.9,1.9,0.08,0.08,3.0]
r=least_squares(resid,p0,x_scale=[0.1,0.05,0.1,0.1,0.05,0.02,0.5],diff_step=2e-2)
p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.diag(cov))
for n_,v,e in zip(['t','tp','mu','Delta','sigma','bg','scale'],p,err): print(f"{n_:6s} = {v:.4f} +- {e:.4f}")
print("rms resid",np.sqrt(np.mean(r.fun**2)))
eps=band(p[0],p[1]); frac=(eps<p[2]).mean(); print("fraction of BZ below mu:",frac," nu=",frac)
# BCS occupancy
xi=eps-p[2]; E=np.sqrt(xi**2+p[3]**2); print("BCS n/2 = <v^2> =",np.mean(0.5*(1-xi/E)))
np.save('fit_c.npy',p)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.figure(figsize=(12,4)); plt.plot(V,g,'k',lw=0.6); plt.plot(V,model(p,V),'r',lw=1); plt.xlim(-10,10); plt.savefig('fit_c.png',dpi=80)
