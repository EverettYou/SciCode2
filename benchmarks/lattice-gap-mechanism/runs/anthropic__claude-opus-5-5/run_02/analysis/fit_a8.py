from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,Uw,xwmode):
    t,tp,c,Dl,A,a0,b,sig=p
    e=D.eps(t,tp); x=e+4*tp
    xw=4*tp if xwmode=='mean' else 0.0
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    y=x-xw; Zp=0.5*(1+y/np.sqrt(y**2+Uw**2)); Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
for Uw in [12.0,14.6,1e6]:
  for xwmode in ['mean','center']:
    p0=[1.0,0.195,0.01,6.0,3.25,0.03,0.001,0.125]
    r=least_squares(lambda p: model(p,Uw,xwmode)-Gs,p0,x_scale='jac')
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('Uw=%g xw=%s chi2/dof=%.6f'%(Uw,xwmode,s2),np.round(r.x[:4],4))
