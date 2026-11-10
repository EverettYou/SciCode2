from fitlib import *
import numpy as np
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp)
def model_gen(p,V):
    cp,ap,bp,cm,am,bm,wp0,wp1,wm0,wm1,sig,bg=p
    Ep=cp+ap*eps+bp*eps**2; Em=cm+am*eps+bm*eps**2
    wp=np.clip(wp0+wp1*eps,0,None); wm=np.clip(wm0+wm1*eps,0,None)
    return sample(dos(Ep,wp,sig)+dos(Em,wm,sig),V)+bg
def fit(model,p0,names,xs):
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=xs,diff_step=2e-2)
    p=r.x; J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.diag(cov))
    print("---",model.__name__,"rms resid",np.sqrt(np.mean(r.fun**2)))
    for n_,v,e in zip(names,p,err): print(f"   {n_:6s} = {v:.4f} +- {e:.4f}")
    return p
names=['c+','a+','b+','c-','a-','b-','wp0','wp1','wm0','wm1','sigma','bg']
p0=[4.8,0.5,0.0,-4.8,-0.5,0.0,1.5,0.2,1.0,0.1,0.12,0.1]
xs=[0.2,0.05,0.01,0.2,0.05,0.01,0.2,0.05,0.2,0.05,0.03,0.02]
pG=fit(model_gen,p0,names,xs)
# try mirror-constrained: Em=-Ep
def model_mirror(p,V):
    cp,ap,bp,wp0,wp1,wm0,wm1,sig,bg=p
    Ep=cp+ap*eps+bp*eps**2; Em=-Ep
    wp=np.clip(wp0+wp1*eps,0,None); wm=np.clip(wm0+wm1*eps,0,None)
    return sample(dos(Ep,wp,sig)+dos(Em,wm,sig),V)+bg
pM=fit(model_mirror,[4.8,0.5,0.0,1.5,0.2,1.0,0.1,0.12,0.1],['c+','a+','b+','wp0','wp1','wm0','wm1','sigma','bg'],[0.2,0.05,0.01,0.2,0.05,0.2,0.05,0.03,0.02])
np.save('fit_b_gen.npy',pG); np.save('fit_b_mirror.npy',pM)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(2,1,figsize=(12,7))
for ax,(m,p) in zip(axs,[(model_gen,pG),(model_mirror,pM)]):
    ax.plot(V,g,'k',lw=0.6); ax.plot(V,m(p,V),'r',lw=1); ax.set_xlim(-10,10); ax.set_title(m.__name__); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('fit_b.png',dpi=80)
# print weights at band bottom/top/vH in physical terms
cp,ap,bp,cm,am,bm,wp0,wp1,wm0,wm1,sig,bg=pG
for name,e in [('bottom(0,0)',eps.min()),('vH(pi,0)',4*tp),('top(pi,pi)',eps.max()),('eps=0',0.0)]:
    print(f"{name:12s} eps={e:6.2f}: E+={cp+ap*e+bp*e*e:6.2f} w+={wp0+wp1*e:6.3f}   E-={cm+am*e+bm*e*e:6.2f} w-={wm0+wm1*e:6.3f}  ratio w+/w-={(wp0+wp1*e)/(wm0+wm1*e):5.2f}")
