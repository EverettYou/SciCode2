from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
def rep(V,t,tp,c,Dl,Uw,sig):
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+e/np.sqrt(e**2+Uw**2)) if Uw<1e5 else 0.5*np.ones_like(e)
    return D.g(V,Ep,Zp,sig)+D.g(V,Em,1-Zp,sig)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,mode):
    if mode=='ME_equal':
        t,tp,c,Dl,A,beta,a0,b,sig=p; Uw=1e9
    elif mode=='ME_HI':
        t,tp,c,Dl,Uw,A,beta,a0,b,sig=p
    d=rep(Vs,t,tp,c,Dl,Uw,sig)*(1+beta*Vs**2)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
for mode,p0 in [('ME_equal',[1.0,0.195,0.01,6.0,3.0,0.01,0.02,0.001,0.125]),('ME_HI',[1.0,0.195,0.01,6.0,14.0,3.0,0.0,0.02,0.001,0.125])]:
    r=least_squares(lambda p: model(p,mode)-Gs,p0,x_scale='jac')
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0)); J=r.jac; cov=np.linalg.pinv(J.T@J)*s2
    print(mode,'chi2/dof %.6f'%s2,np.round(r.x,4),'+-',np.round(np.sqrt(np.diag(cov)),4))
