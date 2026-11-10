import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['c']
kx, ky = kgrid(600)
def model(par):
    t, tp, mu, Delta, sigma, b0, p = par
    xi = ebar(kx, ky, t, tp) - mu
    E = np.sqrt(xi**2+Delta**2)
    u2 = 0.5*(1+xi/E); v2 = 0.5*(1-xi/E)
    h = dos([E,-E],[u2,v2], V, sigma); h=h/h.max()
    s = 0.5*(1+np.tanh((np.abs(V)-abs(Delta))/0.1))
    return h + b0*(np.abs(V)/5.0)**p*s
mask = np.abs(V)<=10
def cost(par):
    if par[4]<=0.02 or par[0]<=0 or par[3]<0: return 1e9
    r=(model(par)-g)[mask]; return np.sum(r**2)/0.012**2/mask.sum()
p0=[1.0,-0.2,-1.1,1.95,0.08,0.05,1.0]
res=minimize(cost,p0,method='Nelder-Mead',options={'xatol':1e-4,'fatol':1e-5,'maxiter':6000})
print("panel c fit [t,tp,mu,Delta,sigma,b0,p]:",res.x,"chi2/N=",res.fun)
np.save('fit_c.npy',res.x)
best=res.fun; N=mask.sum()
for i,nm in enumerate(['t','tp','mu','Delta','sigma','b0','p']):
    out=[]
    for sgn in [+1,-1]:
        step=abs(res.x[i])*0.002+1e-3; x=res.x.copy()
        for j in range(300):
            x[i]+=sgn*step
            if (cost(x)-best)*N>1.0: break
        out.append(abs(x[i]-res.x[i]))
    print(f"  {nm}: {res.x[i]:.4f} +{out[0]:.4f} -{out[1]:.4f}")
# filling implied
t,tp,mu = res.x[:3]
kx2,ky2 = kgrid(1200); xi = ebar(kx2,ky2,t,tp)-mu
E=np.sqrt(xi**2+res.x[3]**2); print("filling nu (BCS) =", np.mean(0.5*(1-xi/E)), " normal-state nu =", np.mean(xi<0))
