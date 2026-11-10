from smoothfit import *
from scipy.optimize import least_squares
V,G=sts('b')
Vs=V[::2]; Gs=G[::2]
t0,tp0,mu0=1.008,0.192,-0.912
C2=np.cos(2*KX)+np.cos(2*KY)
def bcs_k(p,V=Vs,free_band=False):
    if free_band:
        t,tp,mu,D0,D1,D2,D3,A,a,sig=p
    else:
        D0,D1,D2,D3,A,a,sig=p; t,tp,mu=t0,tp0,mu0
    xi=eps(t,tp)-mu
    Dk=D0+D1*(CX+CY)+D2*CX*CY+D3*C2
    E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=0.5*(1-xi/E)
    d=gdos(V,E,u2,sig)+gdos(V,-E,v2,sig)
    return A*d+a*np.abs(V)*(d<0.01*d.max())
best=None
rng=np.random.default_rng(0)
starts=[[3.4,-1.51,-1.42,0.0],[2.6,0,0,0],[0,2.6,0,0],[4,0,-1,0],[3,-1,-1,0.5],[3,-1,-1,-0.5],[2,1,-2,0]]
for _ in range(25):
    starts.append(list(rng.uniform(-4,4,size=4)))
for s in starts:
    p0=s+[3.0,0.012,0.1]
    try:
        r=least_squares(lambda p: bcs_k(p)-Gs,p0,x_scale='jac',max_nfev=300)
    except Exception as ex:
        continue
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    if best is None or s2<best[0]:
        best=(s2,r.x); print('new best chi2/dof %.5f'%s2,np.round(r.x,3))
np.save('/app/analysis/fit_b_bcsk2.npy',best[1])
# free band refinement
p0=[t0,tp0,mu0]+list(best[1][:4])+list(best[1][4:])
r=least_squares(lambda p: bcs_k(p,free_band=True)-Gs,p0,x_scale='jac')
print('free band: chi2/dof %.5f'%(np.sum(r.fun**2)/(len(Gs)-len(p0))),np.round(r.x,3))
