import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from fitlib import kgrid, ebar, dos
from n0lib import N0_grid, hist_poles, broaden, bgfun
cand = sys.argv[1]
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['b']
t, tp = 1.0, -0.2
eg, N0 = N0_grid(t, tp, nk=1600, ne=3201); de = eg[1]-eg[0]
mask = np.abs(V) <= 10
NOISE = 0.012
def inner_edge(h):
    hm = h/h.max(); i0 = np.argmin(np.abs(V))
    up = np.where(hm[i0:] > 0.02)[0]; dn = np.where(hm[:i0][::-1] > 0.02)[0]
    a = V[i0+up[0]] if len(up) else 0.0; b = -V[i0-1-dn[0]] if len(dn) else 0.0
    return 0.5*(a+b)
def finish(h, b0, p):
    h = h/h.max(); return h + bgfun(V, b0, p, inner_edge(h))
x = eg/4.0  # scaled ebar in [-1,1]
if cand == 'B8':  # mirror bands, quadratic map, quadratic weights (clipped)
    names = ['a','b','c','p0','p1','p2','q0','q1','q2','sigma','b0','p']
    p0s = [[4.5,2.0,0.1, 0.5,0.5,0.0, 0.3,0.3,0.0, 0.12,0.05,1.0],
           [4.5,2.0,0.3, 0.6,0.6,0.1, 0.4,0.2,-0.1, 0.12,0.05,1.0],
           [4.5,2.0,0.0, 0.5,0.5,0.2, 0.3,0.4,0.2, 0.12,0.05,1.0]]
    def model(par):
        a,b,c,p0,p1,p2,q0,q1,q2,sigma,b0,p = par
        if sigma<=0.03: return None
        E = a + b*x + c*x**2
        Zp = np.clip(p0+p1*x+p2*x**2,0,None); Zm = np.clip(q0+q1*x+q2*x**2,0,None)
        h = hist_poles([E,-E],[Zp,Zm], N0, de, V, sigma)
        if h.max()<=0: return None
        return finish(h,b0,p)
elif cand == 'B9':  # independent bands, quadratic maps, quadratic weights
    names = ['a','b','c','a2','b2','c2','p0','p1','p2','q0','q1','q2','sigma','b0','p']
    p0s = [[4.5,2.0,0.1, -4.5,-2.0,-0.1, 0.5,0.5,0.0, 0.3,0.3,0.0, 0.12,0.05,1.0],
           [4.5,2.0,0.1, -4.5,2.0,0.1, 0.5,0.5,0.0, 0.5,-0.5,0.0, 0.12,0.05,1.0],
           [4.5,2.0,0.2, -4.5,-2.0,0.2, 0.6,0.6,0.1, 0.4,0.2,-0.1, 0.12,0.05,1.0]]
    def model(par):
        a,b,c,a2,b2,c2,p0,p1,p2,q0,q1,q2,sigma,b0,p = par
        if sigma<=0.03: return None
        E1 = a + b*x + c*x**2; E2 = a2 + b2*x + c2*x**2
        Zp = np.clip(p0+p1*x+p2*x**2,0,None); Zm = np.clip(q0+q1*x+q2*x**2,0,None)
        h = hist_poles([E1,E2],[Zp,Zm], N0, de, V, sigma)
        if h.max()<=0: return None
        return finish(h,b0,p)
def cost(par):
    m = model(par)
    if m is None or not np.all(np.isfinite(m)): return 1e9
    r = (m-g)[mask]; return np.sum(r**2)/NOISE**2/mask.sum()
best=None
for p0 in p0s:
    res = minimize(cost, p0, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
    for _ in range(3):
        res = minimize(cost, res.x, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
    print(cand, "->", np.round(res.x,4), "chi2/N=", round(res.fun,3), flush=True)
    if best is None or res.fun < best.fun: best = res
print(cand, "BEST:", dict(zip(names, np.round(best.x,4))), "chi2/N=", round(best.fun,3))
np.save(f'fit_b_{cand}.npy', best.x); np.save(f'fit_b_{cand}_model.npy', model(best.x))
