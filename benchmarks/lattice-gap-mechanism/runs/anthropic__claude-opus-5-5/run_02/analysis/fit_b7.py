from fastdos import *
from scipy.optimize import least_squares
D=DOS(80)
V,G=sts('b'); Vs=V[::2]; Gs=G[::2]
t0,tp0,mu0=1.008,0.192,-0.912
xi0=D.eps(t0,tp0)-mu0
def gk(V,E,Z,sigk):
    A=np.exp(-(V[:,None]-E[None,:])**2/(2*sigk[None,:]**2))/(np.sqrt(2*np.pi)*sigk[None,:])
    return A@(Z*D.W)
def parts(p):
    DF,Dinf,w,s0,s1,ws,A,a0,b=p
    xi=xi0
    Dk=abs(DF)+(abs(Dinf)-abs(DF))*(1-np.exp(-xi**2/w**2))
    E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=1-u2
    sig=abs(s0)+abs(s1)*np.exp(-xi**2/ws**2)
    return E,u2,v2,sig
def model(p,V=Vs):
    E,u2,v2,sig=parts(p)
    A,a0,b=p[6:]
    d=gk(V,E,u2,sig)+gk(V,-E,v2,sig)
    gapmask=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gapmask)
best=None
for p0 in [[2.65,5.0,1.0,0.1,0.8,1.0,3.0,0.02,0.001],[3.0,5.0,1.5,0.1,0.6,0.7,3.0,0.02,0.001],[2.2,4.9,0.8,0.1,1.0,1.2,3.0,0.02,0.001],[3.3,5.1,2.0,0.12,0.5,1.5,3.0,0.02,0.001]]:
    r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac',max_nfev=500)
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('chi2/dof %.6f'%s2,np.round(r.x,3),flush=True)
    if best is None or s2<best[0]: best=(s2,r.x)
np.save('/app/analysis/fit_b7.npy',best[1])
J=None
