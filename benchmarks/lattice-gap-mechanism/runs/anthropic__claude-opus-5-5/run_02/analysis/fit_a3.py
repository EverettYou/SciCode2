from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,V=Vs,gfix=None,bgmode='out'):
    if gfix is None:
        t,tp,c,Dl,gam,A,a,sig=p
    else:
        t,tp,c,Dl,A,a,sig=p; gam=gfix
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+gam*x); Zm=0.5*(1-gam*x)
    d=D.g(V,Ep,Zp,sig)+D.g(V,Em,Zm,sig)
    if bgmode=='out':
        return A*d+a*np.abs(V)*(d<0.01*d.max())
    else:  # background everywhere except inside gap
        gapmask=(V>c-Dl+2*t)&(V<c+Dl-2*t)
        return A*d+a*np.abs(V)*(~gapmask)
for bgmode in ['out','all']:
  for gfix in [None,0.0,1/12.]:
    p0=[1.03,0.2,0.0,6.0]+([0.05] if gfix is None else [])+[3.8,0.012,0.16]
    r=least_squares(lambda p: model(p,gfix=gfix,bgmode=bgmode)-Gs,p0,x_scale='jac')
    dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
    J=r.jac; cov=np.linalg.pinv(J.T@J)*s2; err=np.sqrt(np.diag(cov))
    print(bgmode,'gamma',gfix,'chi2/dof %.6f'%s2,' params',np.round(r.x,4),' err',np.round(err,4))
