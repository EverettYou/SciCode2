import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['a']; kx, ky = kgrid(600); mask = np.abs(V)<=10
def bgfun(V, b0, p, Vin, sigma):
    s = 0.5*(1+np.tanh((np.abs(V)-Vin)/max(sigma,0.05))); return b0*(np.abs(V)/5.0)**p*s
def model(par):
    t, tp, U, sigma, b0, p, a1, a2, a3 = par   # Z+ = 1/2 + a1*eb + a2*eb^2 + a3  (delta(eb) = a3 + a1 eb + a2 eb^2)
    if sigma<=0.02 or t<=0: return None
    eb = ebar(kx,ky,t,tp); Ep = eb/2+U/2; Em = eb/2-U/2
    dlt = a3 + a1*eb + a2*eb**2; Zp = 0.5+dlt; Zm = 0.5-dlt
    if Zp.min()<0 or Zm.min()<0: return None
    h = dos([Ep,Em],[Zp,Zm],V,sigma); h=h/h.max()
    return h + bgfun(V,b0,p,(U-4*t)/2,sigma)
def cost(par):
    m = model(par)
    if m is None: return 1e9
    r=(m-g)[mask]; return np.sum(r**2)/0.012**2/mask.sum()
p0=[1.0,-0.2,12.0,0.084,0.048,1.45, 1/(2*15.4), 0.0, -0.53/(2*15.4)]
res=minimize(cost,p0,method='Nelder-Mead',options={'xatol':1e-6,'fatol':1e-7,'maxiter':40000,'maxfev':60000})
res=minimize(cost,res.x,method='Nelder-Mead',options={'xatol':1e-6,'fatol':1e-7,'maxiter':40000,'maxfev':60000})
names=['t','tp','U','sigma','b0','p','a1','a2','a3']
print("quadratic weights:", dict(zip(names,np.round(res.x,5))), "chi2/N=",round(res.fun,3))
np.save('fit_a_quad.npy',res.x)
t,tp,U,sigma,b0,p,a1,a2,a3 = res.x
# zero surface omega_z(eb) = eb/2 - U*delta(eb)
eb = np.linspace(-4,4,17); dlt = a3+a1*eb+a2*eb**2
print("omega_z(ebar):", np.round(eb,2), np.round(eb/2 - U*dlt,3))
