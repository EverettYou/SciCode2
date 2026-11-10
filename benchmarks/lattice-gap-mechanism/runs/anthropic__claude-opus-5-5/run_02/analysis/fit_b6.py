from fastdos import *
from scipy.optimize import least_squares
D=DOS(70)
V,G=sts('b'); Vs=V[::2]; Gs=G[::2]
def dos_cl(V,t,tp,mu,Dsc,Dpg,gam,eta):
    xi=D.eps(t,tp)-mu
    w=V[:,None]+1j*eta
    Sig=Dsc**2/(w+xi[None,:])+Dpg**2/(w+xi[None,:]+1j*gam)
    Gk=1/(w-xi[None,:]-Sig)
    return -(Gk.imag@D.W)/np.pi
def model(p,V=Vs,fixband=True):
    if fixband:
        Dsc,Dpg,gam,A,a0,b,eta=p; t,tp,mu=1.008,0.192,-0.912
    else:
        t,tp,mu,Dsc,Dpg,gam,A,a0,b,eta=p
    d=dos_cl(V,t,tp,mu,abs(Dsc),abs(Dpg),abs(gam),abs(eta))
    gapmask=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gapmask)
best=None
for p0 in [[2.65,4.2,1.0,3.0,0.02,0.001,0.08],[2.0,4.5,2.0,3.0,0.02,0.001,0.08],[3.0,3.5,0.5,3.0,0.02,0.001,0.08],[1.5,4.8,1.5,3.0,0.02,0.001,0.08]]:
    r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac',max_nfev=400)
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    print('fixed band chi2/dof %.6f'%s2,np.round(r.x,3),flush=True)
    if best is None or s2<best[0]: best=(s2,r.x)
p=best[1]
q0=[1.008,0.192,-0.912]+list(p)
r=least_squares(lambda q: model(q,fixband=False)-Gs,q0,x_scale='jac',max_nfev=400)
s2=np.sum(r.fun**2)/(len(Gs)-len(q0))
print('free band chi2/dof %.6f'%s2,np.round(r.x,3))
np.save('/app/analysis/fit_b6.npy',r.x)
