from smoothfit import *
from scipy.optimize import least_squares
V,G=sts('b')
Vs=V[::2]; Gs=G[::2]
def bcs_k(p,V=Vs):
    t,tp,mu,D0,D1,D2,A,a,sig=p
    xi=eps(t,tp)-mu
    Dk=D0+D1*(CX+CY)+D2*CX*CY
    E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=0.5*(1-xi/E)
    d=gdos(V,E,u2,sig)+gdos(V,-E,v2,sig)
    return A*d+a*np.abs(V)*(d<0.01*d.max())
best=None
for p0 in [[1.0,0.19,-0.9,2.6,0.0,0.0,3.0,0.012,0.1],
           [1.0,0.19,-0.9,2.5,1.3,-2.3,3.0,0.012,0.1],
           [1.0,0.19,-0.9,-2.3,2.6,2.5,3.0,0.012,0.1],
           [1.0,0.19,-0.9,5.0,0.0,0.0,3.0,0.012,0.1],
           [1.0,0.19,-2.0,4.0,1.0,0.0,3.0,0.012,0.1]]:
    r=least_squares(lambda p: bcs_k(p)-Gs,p0,x_scale='jac')
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('start',p0[3:6],'-> chi2/dof %.5f'%s2,np.round(r.x,3))
    if best is None or s2<best[0]: best=(s2,r.x)
np.save('/app/analysis/fit_b_bcsk.npy',best[1])
