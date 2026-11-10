from fastdos import *
from scipy.optimize import least_squares
D=DOS(80)
V,G=sts('b'); Vs=V[::2]; Gs=G[::2]
t0,tp0=1.008,0.192
def gk(V,E,Z,sigk):
    A=np.exp(-(V[:,None]-E[None,:])**2/(2*sigk[None,:]**2))/(np.sqrt(2*np.pi)*sigk[None,:])
    return A@(Z*D.W)
def parts(p):
    mu,DF,Dinf,w,s0,s1,ws=p[:7]
    xi=D.eps(t0,tp0)-mu
    Dk=abs(DF)+(abs(Dinf)-abs(DF))*(1-np.exp(-xi**2/w**2))
    E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=1-u2
    sig=abs(s0)+abs(s1)*np.exp(-xi**2/ws**2)
    return xi,E,u2,v2,sig
def model(p,V=Vs):
    xi,E,u2,v2,sig=parts(p)
    A,a0,b=p[7:]
    d=gk(V,E,u2,sig)+gk(V,-E,v2,sig)
    gapmask=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gapmask)
best=None
for mu in [-0.912,-1.5,-2.0,-2.5]:
  for p0 in [[mu,3.0,5.0,1.5,0.1,0.7,1.1,3.0,0.02,0.001],[mu,2.6,4.8,1.0,0.1,0.9,1.0,3.0,0.02,0.001]]:
    r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac',max_nfev=500)
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('chi2/dof %.6f'%s2,np.round(r.x,3),flush=True)
    if best is None or s2<best[0]: best=(s2,r.x)
np.save('/app/analysis/fit_b8.npy',best[1])
p=best[1]; xi,E,u2,v2,sig=parts(p)
print('best',best[0],' filling at mu:',np.sum(D.W*(xi<0)),' sum v2:',np.sum(D.W*v2))
