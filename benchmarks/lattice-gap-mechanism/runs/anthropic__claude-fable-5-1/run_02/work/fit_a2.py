import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['a']
kx, ky = kgrid(600)
def bgfun(V, b0, p, Vin, sigma):
    s = 0.5*(1+np.tanh((np.abs(V)-Vin)/max(sigma,0.05)))
    return b0*(np.abs(V)/5.0)**p * s
mask = np.abs(V) <= 10
variant = sys.argv[1]
def model(par):
    if variant == 'ek':      # HI weights referenced to bare level (eps_k = ebar - 4tp... general)
        t, tp, U, sigma, b0, p = par; e0 = -4*tp*1.0  # ebar - eps_k = -(eps_mid) = -4tp  -> e0 = -4tp (=0.8 for tp=-0.2)
        Uw = U
    elif variant == 'free':  # free weight reference and weight scale
        t, tp, U, sigma, b0, p, e0, Uw = par
    elif variant == 'exactHIw':  # exact HI weights 1/2 ± eps/(4R), linear poles
        t, tp, U, sigma, b0, p = par; e0 = -4*tp; Uw=None
    if sigma<=0.02 or t<=0: return None
    eb = ebar(kx, ky, t, tp)
    Ep = eb/2 + U/2; Em = eb/2 - U/2
    if variant == 'exactHIw':
        ek = eb - e0; R = np.sqrt(ek**2/4 + U**2/4); Zp = 0.5 + ek/(4*R); Zm = 0.5 - ek/(4*R)
    else:
        Zp = 0.5 + (eb-e0)/(2*Uw); Zm = 0.5 - (eb-e0)/(2*Uw)
        if Zp.min()<0 or Zm.min()<0: return None
    h = dos([Ep, Em], [Zp, Zm], V, sigma); h = h/h.max()
    return h + bgfun(V, b0, p, (U-4*t)/2, sigma)
def cost(par):
    m = model(par)
    if m is None: return 1e9
    r = (m-g)[mask]; return np.sum(r**2)/0.012**2/mask.sum()
p0 = [1.0,-0.2,12.0,0.08,0.085,0.5] + ([0.8, 12.0] if variant=='free' else [])
res = minimize(cost, p0, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
res = minimize(cost, res.x, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
names = ['t','tp','U','sigma','b0','p'] + (['e0','Uw'] if variant=='free' else [])
print(variant, dict(zip(names, np.round(res.x,4))), "chi2/N=", round(res.fun,3))
np.save(f'fit_a_{variant}.npy', res.x)
if variant=='free':
    best=res.fun; N=mask.sum()
    for i,nm in enumerate(names):
        out=[]
        for sgn in [+1,-1]:
            step=abs(res.x[i])*0.002+1e-3; x=res.x.copy()
            for j in range(400):
                x[i]+=sgn*step
                if (cost(x)-best)*N>1.0: break
            out.append(abs(x[i]-res.x[i]))
        print(f"  {nm}: {res.x[i]:.4f} +{out[0]:.4f} -{out[1]:.4f}")
    # integrated weight ratio for best model
    m = model(res.x)
