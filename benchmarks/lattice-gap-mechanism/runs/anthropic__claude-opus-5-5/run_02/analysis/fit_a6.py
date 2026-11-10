from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,xwmode='free'):
    if xwmode=='free':
        t,tp,c,Dl,gam,xw,A,a0,b,sig=p
    elif xwmode=='mean':
        t,tp,c,Dl,gam,A,a0,b,sig=p; xw=4*tp
    elif xwmode=='zero':
        t,tp,c,Dl,A,a0,b,sig=p; xw=0; gam=0
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+gam*(x-xw)); Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
for mode,p0 in [('free',[1.0,0.195,0.01,6.0,0.05,0.0,3.2,0.013,0.0012,0.12]),
                ('mean',[1.0,0.195,0.01,6.0,0.05,3.2,0.013,0.0012,0.12]),
                ('zero',[1.0,0.195,0.01,6.0,3.2,0.013,0.0012,0.12])]:
    r=least_squares(lambda p: model(p,mode)-Gs,p0,x_scale='jac')
    dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
    J=r.jac; cov=np.linalg.pinv(J.T@J)*s2; err=np.sqrt(np.diag(cov))
    print(mode,'chi2/dof %.6f'%s2); print('  ',np.round(r.x,4)); print('  ',np.round(err,4))
