import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from scipy.optimize import minimize
from n0lib import N0_grid, hist_poles, bgfun
cand = sys.argv[1]
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, g = S['b']
eg, N0 = N0_grid(1.0, -0.2, nk=1600, ne=3201); de = eg[1]-eg[0]
mask = np.abs(V) <= 10; NOISE = 0.012
def inner_edge(h):
    hm = h/h.max(); i0 = np.argmin(np.abs(V))
    up = np.where(hm[i0:] > 0.02)[0]; dn = np.where(hm[:i0][::-1] > 0.02)[0]
    a = V[i0+up[0]] if len(up) else 0.0; b = -V[i0-1-dn[0]] if len(dn) else 0.0
    return 0.5*(a+b)
def finish(h, b0, p):
    h = h/h.max(); return h + bgfun(V, b0, p, inner_edge(h))
def pk(e0, w): 
    return 1/(1+np.exp(np.clip((eg-e0)/w, -50, 50)))
if cand == 'B10':   # same orientation, slope s, Fermi-like weights
    names = ['s','c','DM','e0','w','sigma','b0','p']
    p0s = [[0.5,0.0,4.5,-1.0,1.0,0.12,0.06,1.0],[0.6,0.1,4.4,-0.5,1.5,0.12,0.06,1.0],[0.5,0.0,4.5,0.0,0.7,0.12,0.06,1.0]]
    def model(par):
        s,c,DM,e0,w,sigma,b0,p = par
        if sigma<=0.03 or w<=0.05 or DM<=0: return None
        Em = s*eg + c - DM; Ep = s*eg + c + DM; P = pk(e0,w)
        return finish(hist_poles([Em,Ep],[P,1-P],N0,de,V,sigma), b0, p)
elif cand == 'B11':  # HK-like: slope 1 fixed
    names = ['c','DM','e0','w','sigma','b0','p']
    p0s = [[0.0,2.5,0.0,0.5,0.12,0.06,1.0],[-0.5,2.5,-0.5,1.0,0.12,0.06,1.0]]
    def model(par):
        c,DM,e0,w,sigma,b0,p = par
        if sigma<=0.03 or w<=0.05 or DM<=0: return None
        Em = eg + c - DM; Ep = eg + c + DM; P = pk(e0,w)
        return finish(hist_poles([Em,Ep],[P,1-P],N0,de,V,sigma), b0, p)
elif cand == 'B12':  # mirror orientation: E- = -(s*eg + c + DM)
    names = ['s','c','DM','e0','w','sigma','b0','p']
    p0s = [[0.5,0.0,4.5,-1.0,1.0,0.12,0.06,1.0],[0.5,0.0,4.5,0.0,0.7,0.12,0.06,1.0]]
    def model(par):
        s,c,DM,e0,w,sigma,b0,p = par
        if sigma<=0.03 or w<=0.05 or DM<=0: return None
        Ep = s*eg + c + DM; Em = -Ep; P = pk(e0,w)
        return finish(hist_poles([Em,Ep],[P,1-P],N0,de,V,sigma), b0, p)
elif cand == 'B13':  # same orientation with quadratic (convex) correction and Fermi weights, weights amplitude free
    names = ['s','c','q','DM','e0','w','r','sigma','b0','p']
    p0s = [[0.5,0.0,0.0,4.5,-1.0,1.0,1.0,0.12,0.06,1.0],[0.55,0.1,0.02,4.4,-0.5,1.5,0.8,0.12,0.06,1.0]]
    def model(par):
        s,c,q,DM,e0,w,r,sigma,b0,p = par
        if sigma<=0.03 or w<=0.05 or DM<=0 or r<=0: return None
        Em = s*eg + c - DM + q*eg**2; Ep = s*eg + c + DM + q*eg**2; P = pk(e0,w)
        return finish(hist_poles([Em,Ep],[r*P,1-P],N0,de,V,sigma), b0, p)
elif cand == 'B14':  # same orientation, slope s, linear-ramp weights p=clip((e2-e)/(e2-e1)), amplitude r
    names = ['s','c','DM','e1','e2','r','sigma','b0','p']
    p0s = [[0.6,0.0,4.15,-3.3,1.5,1.4,0.12,0.07,0.7],[0.55,0.0,4.2,-2.5,1.0,1.2,0.12,0.07,0.7],[0.6,0.0,4.1,-4.0,2.5,1.6,0.12,0.07,0.7]]
    def model(par):
        s,c,DM,e1,e2,r,sigma,b0,p = par
        if sigma<=0.03 or e2<=e1+0.2 or DM<=0 or r<=0: return None
        Em = s*eg + c - DM; Ep = s*eg + c + DM; P = np.clip((e2-eg)/(e2-e1),0,1)
        return finish(hist_poles([Em,Ep],[r*P,1-P],N0,de,V,sigma), b0, p)
elif cand == 'B15':  # B14 + quadratic convexity
    names = ['s','c','q','DM','e1','e2','r','sigma','b0','p']
    p0s = [[0.6,0.0,0.0,4.15,-3.3,1.5,1.4,0.12,0.07,0.7],[0.55,0.0,0.02,4.2,-2.5,1.0,1.2,0.12,0.07,0.7]]
    def model(par):
        s,c,q,DM,e1,e2,r,sigma,b0,p = par
        if sigma<=0.03 or e2<=e1+0.2 or DM<=0 or r<=0: return None
        Em = s*eg + c - DM + q*eg**2; Ep = s*eg + c + DM + q*eg**2; P = np.clip((e2-eg)/(e2-e1),0,1)
        return finish(hist_poles([Em,Ep],[r*P,1-P],N0,de,V,sigma), b0, p)
def cost(par):
    m = model(par)
    if m is None or not np.all(np.isfinite(m)): return 1e9
    r = (m-g)[mask]; return np.sum(r**2)/NOISE**2/mask.sum()
best=None
for p0 in p0s:
    res = minimize(cost, p0, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
    for _ in range(2):
        res = minimize(cost, res.x, method='Nelder-Mead', options={'xatol':1e-5,'fatol':1e-6,'maxiter':20000,'maxfev':30000})
    print(cand, "->", np.round(res.x,4), "chi2/N=", round(res.fun,3), flush=True)
    if best is None or res.fun < best.fun: best = res
print(cand, "BEST:", dict(zip(names, np.round(best.x,4))), "chi2/N=", round(best.fun,3))
np.save(f'fit_b_{cand}.npy', best.x); np.save(f'fit_b_{cand}_model.npy', model(best.x))
