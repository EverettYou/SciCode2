from fitlib import *
s=STS[3]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
def model(p,V):
    t,tp,mu,sig,bg,sc=p
    eps=band(t,tp)
    rho=dos(eps-mu,np.ones_like(eps),sig)
    return sc*sample(rho,V)+bg
def resid(p): return model(p,V)-g
p0=[1.0,0.2,-0.9,0.1,0.1,3.0]
r=least_squares(resid,p0,x_scale=[0.1,0.05,0.1,0.05,0.02,0.5],diff_step=2e-2)
p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p))
err=np.sqrt(np.diag(cov))
names=['t','tp','mu','sigma','bg','scale']
for n_,v,e in zip(names,p,err): print(f"{n_:6s} = {v:.4f} +- {e:.4f}")
print("rms resid",np.sqrt(np.mean(r.fun**2)))
eps=band(p[0],p[1]); frac=(eps<p[2]).mean(); print("fraction of BZ below mu:",frac," -> n =",2*frac," nu=",frac)
print("band bottom,top rel mu:",eps.min()-p[2],eps.max()-p[2], " vH(pi,0) rel mu:",4*p[1]-p[2])
np.save('fit_d.npy',p)
