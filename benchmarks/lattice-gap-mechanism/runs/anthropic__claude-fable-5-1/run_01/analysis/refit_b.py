import json, numpy as np, sys
from scipy.optimize import least_squares
sys.path.insert(0,'/app/theory'); from common import *
with open('/app/measurements.json') as f: d = json.load(f)
s = [x for x in d['measurements'][0]['spectra'] if x['panel']=='b'][0]
V = np.array(s['bias']); y = np.array(s['dI_dV'])
N = 600; KX, KY = kgrid(N); E = eps_k(KX, KY).ravel()
egrid = np.arange(-14, 14, 0.01); de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(En, w):
    h,_ = np.histogram(En, bins=bins, weights=w); return h/de/En.size
def broaden(A, eta):
    eta = min(max(abs(eta),1e-3),0.8)
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    ker = (eta/np.pi)/(x**2+eta**2); ker/=ker.sum(); return np.convolve(A, ker, mode='same')
def energies(kind, mu, D):
    xi = E - mu
    if kind == 'sqrt':
        r = np.sqrt(xi**2/4 + D**2); Ep, Em = xi/2 + r, xi/2 - r
    else:
        Ep, Em = D + xi/2, -D + xi/2
    mid = 0.5*(Ep.min()+Em.max()); return Ep-mid, Em-mid, xi
def weights(wk, xi, p):
    if wk == 'tanh':   # w- = 1/2(1 - tanh((xi-x0)/Tw))
        x0, Tw = p; wm = 0.5*(1 - np.tanh((xi-x0)/Tw))
    elif wk == 'v2':   # BCS-like with own gap
        x0, Dc = p; wm = 0.5*(1 - (xi-x0)/np.sqrt((xi-x0)**2 + Dc**2))
    elif wk == 'tanh2': # a + b tanh form with asymmetry
        x0, Tw, a = p; wm = a*(1 - np.tanh((xi-x0)/Tw))
    return np.clip(wm, 0, 1)
def run(ek, wk, p0):
    def full(q):
        mu, D = q[0], q[1]; pw = q[2:2+len(p0)]; eta, scale, b, c0 = q[2+len(p0):]
        Ep, Em, xi = energies(ek, mu, D); wm = weights(wk, xi, pw); wp = 1-wm
        A = broaden(hist(np.concatenate([Ep,Em]), np.concatenate([wp,wm])), eta)
        return scale*np.interp(V, egrid, A) + b*V**2 + c0
    best = None
    for mu0 in [-0.75, -0.9]:
        for D0 in ([4.2] if ek=='sqrt' else [4.4]):
            q0 = [mu0, D0] + list(p0) + [0.1, 6.2, 0.0012, 0.01]
            r = least_squares(lambda q: full(q)-y, q0, diff_step=1e-2)
            if best is None or r.cost < best.cost: best = r
    rms = np.sqrt(2*best.cost/len(y))
    print(f"energies={ek:6s} weights={wk:6s} rms={rms:.4f} params={np.round(best.x,3)}")
    return best.x, rms
res = {}
for ek in ['sqrt','linear']:
    for wk, p0 in [('tanh',[0.0,1.0]), ('v2',[0.0,2.0]), ('tanh2',[0.0,1.0,0.5])]:
        res[(ek,wk)] = run(ek, wk, p0)
import pickle; pickle.dump(res, open('/app/analysis/refit_b.pkl','wb'))
