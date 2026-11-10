import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['d']
kx, ky = kgrid(600)
def model(par):
    t, tp, mu, sigma, b0, p = par
    eb = ebar(kx, ky, t, tp) - mu
    h = dos([eb],[np.ones(1)], V, sigma); h = h/h.max()
    # background outside band
    Vlo, Vhi = -4*t-mu, 4*t-mu
    s = 0.5*(1+np.tanh((V-Vhi)/0.1)) + 0.5*(1-np.tanh((V-Vlo)/0.1))
    return h + b0*(np.abs(V)/5.0)**p*s
mask = np.abs(V)<=10
def cost(par):
    if par[3]<=0.02 or par[0]<=0: return 1e9
    r = (model(par)-g)[mask]; return np.sum(r**2)/0.03**2/mask.sum()
p0=[1.0,-0.2,0.0,0.1,0.05,1.0]
res = minimize(cost,p0,method='Nelder-Mead',options={'xatol':1e-4,'fatol':1e-5,'maxiter':4000})
print("panel d fit [t,tp,mu,sigma,b0,p]:", res.x, "chi2/N=",res.fun)
np.save('fit_d.npy',res.x)
best=res.fun; N=mask.sum()
for i,nm in enumerate(['t','tp','mu','sigma','b0','p']):
    out=[]
    for sgn in [+1,-1]:
        step=abs(res.x[i])*0.002+1e-3; x=res.x.copy()
        for j in range(300):
            x[i]+=sgn*step
            if (cost(x)-best)*N>1.0: break
        out.append(abs(x[i]-res.x[i]))
    print(f"  {nm}: {res.x[i]:.4f} +{out[0]:.4f} -{out[1]:.4f}")
