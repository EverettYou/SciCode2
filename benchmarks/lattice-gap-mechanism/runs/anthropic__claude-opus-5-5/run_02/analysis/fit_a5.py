from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def bgfun(V,c,Dl,t,a):
    gapmask=(V>c-Dl+2*t)&(V<c+Dl-2*t)
    return a*np.abs(V)*(~gapmask)
def lin(p,mode):
    if mode=='xw_mean':
        t,tp,c,Dl,gam,A,a,sig=p; xw=4*tp
    elif mode=='HIweights':
        t,tp,c,Dl,Uw,A,a,sig=p; xw=4*tp
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    if mode=='HIweights':
        y=x-xw; Zp=0.5*(1+y/np.sqrt(y**2+Uw**2))
    else:
        Zp=0.5*(1+gam*(x-xw))
    Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    return A*d+bgfun(Vs,c,Dl,t,a)
def hub1(p):
    t,tp,e0,U,c,A,a,sig=p
    e=D.eps(t,tp); y=e-e0
    s=np.sqrt(y**2+U**2)
    Ep=(y+s)/2+c; Em=(y-s)/2+c
    Zp=0.5*(1+y/s); Zm=0.5*(1-y/s)
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>Em.max())&(Vs<Ep.min())
    return A*d+a*np.abs(Vs)*(~gapmask)
for name,f,p0 in [('linear, x_w=4tp, free gamma',lambda p: lin(p,'xw_mean'),[1.0,0.195,0.01,6.0,0.07,3.2,0.0128,0.12]),
                  ('linear, HubbardI-type weights, free Uw',lambda p: lin(p,'HIweights'),[1.0,0.195,0.01,6.0,12.0,3.2,0.0128,0.12]),
                  ('Hubbard-I exact',hub1,[1.0,0.2,0.0,12.0,0.4,3.2,0.0128,0.12])]:
    r=least_squares(lambda p: f(p)-Gs,p0,x_scale='jac')
    dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
    J=r.jac; cov=np.linalg.pinv(J.T@J)*s2; err=np.sqrt(np.diag(cov))
    print(name,' chi2/dof %.6f'%s2); print('   ',np.round(r.x,4)); print('   ',np.round(err,4))
