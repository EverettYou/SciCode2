from fastdos import *
from scipy.optimize import least_squares
D=DOS(80)
V,G=sts('b'); Vs=V[::2]; Gs=G[::2]
def gk(V,E,Z,sigk):
    A=np.exp(-(V[:,None]-E[None,:])**2/(2*sigk[None,:]**2))/(np.sqrt(2*np.pi)*sigk[None,:])
    return A@(Z*D.W)
def model(p,V=Vs):
    t,tp,mu,Dl,s0,s1,w,A,a0,b=p
    xi=D.eps(t,tp)-mu; E=np.sqrt(xi**2+Dl**2)
    u2=0.5*(1+xi/E); v2=1-u2
    sig=np.abs(s0)+np.abs(s1)*np.exp(-xi**2/w**2)
    d=gk(V,E,u2,sig)+gk(V,-E,v2,sig)
    gapmask=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gapmask)
best=None
for p0 in [[1.0,0.195,-0.912,4.9,0.12,0.9,1.0,3.0,0.02,0.001],
           [1.0,0.195,-0.912,4.5,0.12,1.2,1.5,3.0,0.02,0.001],
           [1.0,0.195,-0.912,5.0,0.1,0.8,0.7,3.0,0.02,0.001]]:
    r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac',max_nfev=600)
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('chi2/dof %.6f'%s2,np.round(r.x,3))
    if best is None or s2<best[0]: best=(s2,r.x)
np.save('/app/analysis/fit_b5.npy',best[1])
p=best[1]
t,tp,mu,Dl=p[:4]
xi=D.eps(t,tp)-mu; E=np.sqrt(xi**2+Dl**2)
print('filling at mu',np.sum(D.W*(xi<0)),' sum v2',np.sum(D.W*0.5*(1-xi/E)))
