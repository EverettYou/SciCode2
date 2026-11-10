import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['a']
kx, ky = kgrid(600)
grid = V.copy()

def bgfun(V, b0, p, Vin, sigma):
    s = 0.5*(1+np.tanh((np.abs(V)-Vin)/max(sigma,0.05)))
    return b0*(np.abs(V)/5.0)**p * s

def model_a(par):
    t, tp, U, sigma, b0, p = par
    eb = ebar(kx, ky, t, tp)
    Ep = eb/2 + U/2; Em = eb/2 - U/2
    Zp = 0.5 + eb/(2*U); Zm = 0.5 - eb/(2*U)
    h = dos([Ep, Em], [Zp, Zm], grid, sigma)
    h = h/h.max()
    Vin = (U - 4*t)/2  # inner edge
    return h + bgfun(V, b0, p, Vin, sigma)

mask = np.abs(V) <= 10
def cost(par):
    if par[3] <= 0.02 or par[0] <= 0: return 1e9
    m = model_a(par)
    r = (m - g)[mask]
    return np.sum(r**2)/0.012**2/mask.sum()

p0 = [1.0, -0.2, 12.0, 0.12, 0.05, 1.26]
res = minimize(cost, p0, method='Nelder-Mead', options={'xatol':1e-4,'fatol':1e-4,'maxiter':4000})
print("panel a fit:", res.x, "chi2/N=", res.fun)
np.save('fit_a.npy', res.x)
# crude uncertainties: scan each parameter for chi2 increase by 1 (per point normalized -> use total chi2)
best = res.fun; N = mask.sum()
names = ['t','tp','U','sigma','b0','p']
for i,nm in enumerate(names):
    for sgn in [+1,-1]:
        step = abs(res.x[i])*0.002 + 1e-3
        x = res.x.copy()
        for j in range(200):
            x[i] += sgn*step
            c = cost(x)
            if (c-best)*N > 1.0:  # total chi2 +1
                break
        print(f"  {nm}: {res.x[i]:.4f}  {'+' if sgn>0 else '-'} {abs(x[i]-res.x[i]):.4f} (chi2tot+1, others fixed)")
