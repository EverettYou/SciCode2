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

def finish(h, par_bg, Vin):
    h = h/h.max()
    return h + bgfun(V, par_bg[0], par_bg[1], Vin)

def inner_edge(h):
    # inner gap edge from model: first energy above 0 where h > 2% of max, symmetric average
    hm = h/h.max()
    i0 = np.argmin(np.abs(V))
    up = np.where(hm[i0:] > 0.02)[0]; dn = np.where(hm[:i0][::-1] > 0.02)[0]
    a = V[i0+up[0]] if len(up) else 0.0; b = -V[i0-1-dn[0]] if len(dn) else 0.0
    return 0.5*(a+b)

if cand == 'B1':   # BCS s-wave on bare band
    names = ['mu','Delta','sigma','b0','p']
    p0s = [[0.0,2.5,0.1,0.05,1.0],[-1.0,2.5,0.1,0.05,1.0],[1.0,2.5,0.1,0.05,1.0]]
    def model(par):
        mu, Delta, sigma, b0, p = par
        if sigma<=0.02 or Delta<0: return None
        xi = eg - mu; E = np.sqrt(xi**2+Delta**2)
        h = hist_poles([E,-E],[0.5*(1+xi/E),0.5*(1-xi/E)], N0, de, V, sigma)
        return finish(h,(b0,p),inner_edge(h))
elif cand == 'B2':  # exact two-pole, flat level
    names = ['mu','w0','Delta','s','sigma','b0','p']
    p0s = [[0.0,0.0,4.0,0.0,0.1,0.05,1.0],[0.5,0.0,4.0,0.0,0.1,0.05,1.0],[-0.5,0.3,4.0,0.0,0.1,0.05,1.0]]
    def model(par):
        mu, w0, Delta, s, sigma, b0, p = par
        if sigma<=0.02 or Delta<0: return None
        xi = eg - mu
        R = np.sqrt((xi-w0)**2/4+Delta**2)
        Ep = (xi+w0)/2+R; Em = (xi+w0)/2-R
        Zp = (Ep-w0)/(Ep-Em); Zm = -(Em-w0)/(Ep-Em)
        h = hist_poles([Ep+s,Em+s],[Zp,Zm], N0, de, V, sigma)
        return finish(h,(b0,p),inner_edge(h))
elif cand == 'B3':  # mirror two-pole-like with linear vanishing weights
    names = ['Delta','s','cp','cm','r','sigma','b0','p']
    p0s = [[4.0,0.0,4.5,4.5,0.7,0.1,0.05,1.0],[4.0,0.2,5.0,4.0,0.6,0.1,0.05,1.0],[4.0,-0.2,4.0,6.0,0.8,0.1,0.05,1.0]]
    def model(par):
        Delta, s, cp, cm, r, sigma, b0, p = par
        if sigma<=0.02 or Delta<0 or cp<=0 or cm<=0 or r<0: return None
        E = eg/2+np.sqrt(eg**2/4+Delta**2)+s
        Zp = np.clip(1+eg/cp,0,None); Zm = r*np.clip(1+eg/cm,0,None)
        h = hist_poles([E,-E],[Zp,Zm], N0, de, V, sigma)
        return finish(h,(b0,p),inner_edge(h))
elif cand == 'B4':  # Nambu + Mott (normal self-energy pole + anomalous gap)
    names = ['mu','w0','DM','DSC','eta','b0','p']
    p0s = [[0.0,0.0,3.0,2.0,0.08,0.05,1.0],[0.0,0.0,2.0,3.0,0.08,0.05,1.0],[0.5,0.5,3.5,1.5,0.08,0.05,1.0],[-1.0,0.0,2.5,2.5,0.08,0.05,1.0]]
    W = V[:,None]
    def model(par):
        mu, w0, DM, DSC, eta, b0, p = par
        if eta<=0.02 or DM<0 or DSC<0: return None
        xi = (eg - mu)[None,:]
        w = W + 1j*eta
        Sig = DM**2/(w - w0); Sigm = -DM**2/(w + w0)   # Sigma_22(w) = -Sigma(-w)
        a = w - xi - Sig; bb = w + xi + Sigm
        G11 = bb/(a*bb - DSC**2)
        A = -G11.imag/np.pi
        h = (A*N0[None,:]).sum(1)*de
        return finish(h,(b0,p),inner_edge(h))
elif cand == 'B5':  # YRZ-like: Sigma = Delta_k^2/(w - wp(k)), wp = alpha*ebar+beta, Delta_k = D0 + D1*ebar
    names = ['mu','alpha','beta','D0','D1','s','sigma','b0','p']
    p0s = [[0.0,-0.6,0.0,3.0,0.0,0.0,0.1,0.05,1.0],[0.0,0.0,0.0,4.0,0.3,0.0,0.1,0.05,1.0],[0.0,-1.0,0.0,2.0,0.5,0.0,0.1,0.05,1.0],[0.0,0.5,0.0,3.0,-0.3,0.0,0.1,0.05,1.0],[-1.5,-0.6,0.0,3.0,0.5,0.0,0.1,0.05,1.0]]
    def model(par):
        mu, alpha, beta, D0, D1, s, sigma, b0, p = par
        if sigma<=0.02: return None
        xi = eg - mu; wp = alpha*eg+beta; Dk = D0 + D1*eg
        R = np.sqrt((xi-wp)**2/4+Dk**2)
        Ep = (xi+wp)/2+R; Em = (xi+wp)/2-R
        Zp = (Ep-wp)/(Ep-Em); Zm = -(Em-wp)/(Ep-Em)
        h = hist_poles([Ep+s,Em+s],[Zp,Zm], N0, de, V, sigma)
        return finish(h,(b0,p),inner_edge(h))
elif cand == 'B6':  # anisotropic BCS on k-grid
    kx, ky = kgrid(500); eb = ebar(kx,ky,t,tp); ck = (np.cos(kx)+np.cos(ky))/2; cc = np.cos(kx)*np.cos(ky)
    names = ['mu','D0','D1','D2','sigma','b0','p']
    p0s = [[0.0,2.5,1.0,0.0,0.1,0.05,1.0],[0.0,2.0,0.0,2.0,0.1,0.05,1.0],[-1.0,3.0,-1.0,0.0,0.1,0.05,1.0],[0.0,1.0,3.0,0.0,0.1,0.05,1.0]]
    def model(par):
        mu, D0, D1, D2, sigma, b0, p = par
        if sigma<=0.02: return None
        xi = eb-mu; Dk = D0 + D1*ck + D2*cc; E = np.sqrt(xi**2+Dk**2)
        h = dos([E,-E],[0.5*(1+xi/E),0.5*(1-xi/E)], V, sigma)
        return finish(h,(b0,p),inner_edge(h))

def cost(par):
    m = model(par)
    if m is None: return 1e9
    r = (m-g)[mask]; return np.sum(r**2)/NOISE**2/mask.sum()

best=None
for p0 in p0s:
    res = minimize(cost, p0, method='Nelder-Mead', options={'xatol':1e-4,'fatol':1e-5,'maxiter':8000,'maxfev':12000})
    res = minimize(cost, res.x, method='Nelder-Mead', options={'xatol':1e-4,'fatol':1e-5,'maxiter':8000,'maxfev':12000})
    print(cand, "start", p0, "->", np.round(res.x,4), "chi2/N=", round(res.fun,3), flush=True)
    if best is None or res.fun < best.fun: best = res
print(cand, "BEST:", dict(zip(names, np.round(best.x,4))), "chi2/N=", round(best.fun,3))
np.save(f'fit_b_{cand}.npy', best.x)
np.save(f'fit_b_{cand}_model.npy', model(best.x))
