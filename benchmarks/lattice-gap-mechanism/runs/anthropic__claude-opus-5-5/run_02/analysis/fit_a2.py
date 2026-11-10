from smoothfit import *
from scipy.optimize import least_squares
V,G=sts('a')
Vs=V[::2]; Gs=G[::2]
def bg(V,a,mask): return a*np.abs(V)*mask
def model_lin(p,V=Vs):
    t,tp,c,Dl,gam,A,a,sig=p
    e=eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+gam*x); Zm=0.5*(1-gam*x)
    d=gdos(V,Ep,Zp,sig)+gdos(V,Em,Zm,sig)
    mask=(np.abs(V)>Dl+2.3)|(np.abs(V)<0)
    return A*d+bg(V,a,(d<0.01*d.max()))
def model_lin_alpha(p,V=Vs):
    t,tp,c,Dl,gam,A,a,sig,al=p
    e=eps(t,tp); x=e+4*tp
    Ep=al*x+c+Dl; Em=al*x+c-Dl
    Zp=0.5*(1+gam*x); Zm=0.5*(1-gam*x)
    d=gdos(V,Ep,Zp,sig)+gdos(V,Em,Zm,sig)
    return A*d+bg(V,a,(d<0.01*d.max()))
def model_h1(p,V=Vs):
    t,tp,e0,U,c,A,a,sig=p
    e=eps(t,tp); y=e-e0
    s=np.sqrt(y**2+U**2)
    Ep=(y+s)/2+c; Em=(y-s)/2+c
    Zp=0.5*(1+y/s); Zm=0.5*(1-y/s)
    d=gdos(V,Ep,Zp,sig)+gdos(V,Em,Zm,sig)
    return A*d+bg(V,a,(d<0.01*d.max()))
res={}
for name,model,p0 in [('linear',model_lin,[1.0,0.19,0.0,6.0,0.03,3.8,0.012,0.15]),
                      ('linear+alpha',model_lin_alpha,[1.0,0.19,0.0,6.0,0.03,3.8,0.012,0.15,0.5]),
                      ('HubbardI',model_h1,[1.0,0.19,0.0,12.0,0.4,3.8,0.012,0.2])]:
    r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac')
    J=r.jac; dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
    cov=np.linalg.pinv(J.T@J)*s2
    print(name,'chi2/dof',round(s2,6))
    for v,e in zip(r.x,np.sqrt(np.diag(cov))): print('   %.4f +- %.4f'%(v,e))
    res[name]=r.x
np.save('/app/analysis/fit_a2.npy',res,allow_pickle=True)
