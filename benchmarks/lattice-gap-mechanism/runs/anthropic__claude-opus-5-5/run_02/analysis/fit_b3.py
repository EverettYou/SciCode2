from fastdos import *
from scipy.optimize import least_squares
D=DOS(80)
V,G=sts('b'); Vs=V[::4]; Gs=G[::4]
t0,tp0,mu0=1.008,0.192,-0.912
def bcs_k(p,V=Vs):
    D0,D1,D2,D3,A,a,sig=p
    xi=D.eps(t0,tp0)-mu0
    Dk=D0+D1*(D.CX+D.CY)+D2*D.CX*D.CY+D3*D.C2
    E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=0.5*(1-xi/E)
    d=D.g(V,E,u2,sig)+D.g(V,-E,v2,sig)
    return A*d+a*np.abs(V)*(d<0.01*d.max())
rng=np.random.default_rng(1)
starts=[[3.4,-1.51,-1.42,0.0],[2.6,0,0,0],[0,2.6,0,0],[4,0,-1,0],[3,-1,-1,0.5],[3,-1,-1,-0.5],[2,1,-2,0]]
starts+= [list(rng.uniform(-4,4,size=4)) for _ in range(40)]
best=None
import time; t1=time.time()
for s in starts:
    p0=s+[3.0,0.012,0.12]
    r=least_squares(lambda p: bcs_k(p)-Gs,p0,x_scale='jac',max_nfev=400)
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    if best is None or s2<best[0]:
        best=(s2,r.x); print('best chi2/dof %.5f'%s2,np.round(r.x,3),flush=True)
print('time',time.time()-t1)
np.save('/app/analysis/fit_b_bcsk3.npy',best[1])
