from fastdos import *
from scipy.optimize import least_squares
D=DOS(80)
V,G=sts('b'); Vs=V[::4]; Gs=G[::4]
t0,tp0,mu0=1.008,0.192,-0.912
xi0=D.eps(t0,tp0)-mu0
def twopole(xi,eta,Dl):
    # G=1/(w-xi-Dl^2/(w-eta)); poles and weights
    s=np.sqrt(((xi-eta)/2)**2+Dl**2)
    Ep=(xi+eta)/2+s; Em=(xi+eta)/2-s
    Zp=(Ep-eta)/(Ep-Em); Zm=(eta-Em)/(Ep-Em)
    return Ep,Em,Zp,Zm
def model_iv(p,V=Vs):
    lam,eta0,Dl,dmu,A,a,sig=p
    xi=xi0-dmu
    Ep,Em,Zp,Zm=twopole(xi,lam*xi+eta0,Dl)
    d=D.g(V,Ep,Zp,sig)+D.g(V,Em,Zm,sig)
    return A*d+a*np.abs(V)*(d<0.01*d.max())
rng=np.random.default_rng(2)
best=None
starts=[[-1,0,2.6,0],[0,0,4,0],[-0.5,0,3,0],[1,0,3,0],[-1,0,4,1],[0.5,1,3,0],[-0.3,-1,3,0]]
starts+=[[rng.uniform(-1.5,1.5),rng.uniform(-3,3),rng.uniform(1,6),rng.uniform(-2,2)] for _ in range(30)]
for s in starts:
    p0=s+[3.0,0.012,0.12]
    try:
        r=least_squares(lambda p: model_iv(p)-Gs,p0,x_scale='jac',max_nfev=400)
    except Exception: continue
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    if best is None or s2<best[0]:
        best=(s2,r.x); print('best chi2/dof %.5f'%s2,np.round(r.x,3),flush=True)
np.save('/app/analysis/fit_b_iv.npy',best[1])
