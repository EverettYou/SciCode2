import json, numpy as np, sys
from scipy.optimize import least_squares
with open('/app/measurements.json') as f:
    d = json.load(f)
sts = {s['panel']: s for s in d['measurements'][0]['spectra']}
N = 600
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
t, tp = 1.0, 0.196
EPS = (-2*t*(cx+cy) - 4*tp*cx*cy).ravel()
ebar = (EPS.min()+EPS.max())/2
egrid = np.arange(-14, 14, 0.01)
de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(E, w):
    h,_ = np.histogram(E, bins=bins, weights=w); return h/de/E.size
def broaden(A, eta):
    eta = min(max(abs(eta), 1e-3), 0.8)
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    ker = (eta/np.pi)/(x**2+eta**2); ker/=ker.sum()
    return np.convolve(A, ker, mode='same')

def spectrum(kind, p):
    """returns A(omega) on egrid, with origin at the midgap"""
    if kind == 'alpha':   # E± = (1-a)xi/2 ± sqrt((1+a)^2 xi^2/4 + D^2), w± = (1 ± xi/sqrt(xi^2+Dc^2))/2
        mu, a, D, Dc = p
        xi = EPS - mu
        root = np.sqrt((1+a)**2*xi**2/4 + D**2)
        Ep = (1-a)*xi/2 + root; Em = (1-a)*xi/2 - root
        wp = 0.5*(1 + xi/np.sqrt(xi**2+Dc**2)); wm = 1-wp
    elif kind == 'linear':  # E± = ±D + xi/2 ; w± = (1 ± xi/Dc)/2
        mu, D, Dc = p
        xi = EPS - mu
        Ep = D + xi/2; Em = -D + xi/2
        wp = 0.5*(1 + xi/Dc); wm = 1-wp
    elif kind == 'linear2':  # E± = ±D + xi/2 ; w± = (1 ± xi/sqrt(xi^2+Dc^2))/2
        mu, D, Dc = p
        xi = EPS - mu
        Ep = D + xi/2; Em = -D + xi/2
        wp = 0.5*(1 + xi/np.sqrt(xi**2+Dc**2)); wm = 1-wp
    elif kind == 'linear3':  # E± = ±D + xi/2 ; w- = a - b*xi, w+ = 1 - w-
        mu, D, a, b = p
        xi = EPS - mu
        Ep = D + xi/2; Em = -D + xi/2
        wm = np.clip(a - b*xi, 0, 1); wp = 1-wm
    elif kind == 'bcs2':  # BCS energies, weights with own scale
        mu, D, Dc = p
        xi = EPS - mu
        E = np.sqrt(xi**2 + D**2)
        Ep, Em = E, -E
        wp = 0.5*(1 + xi/np.sqrt(xi**2+Dc**2)); wm = 1-wp
    elif kind == 'bcs':
        mu, D = p
        xi = EPS - mu
        E = np.sqrt(xi**2 + D**2)
        Ep, Em = E, -E
        wp = 0.5*(1+xi/E); wm = 1-wp
    mid = 0.5*(Ep.min() + Em.max())
    A = hist(np.concatenate([Ep-mid, Em-mid]), np.concatenate([wp, wm]))
    return A, mid, (Em.min()-mid, Em.max()-mid, Ep.min()-mid, Ep.max()-mid)

def fit(panel, kind, p0, scales):
    V = np.array(sts[panel]['bias']); y = np.array(sts[panel]['dI_dV'])
    def full(q):
        p = q[:-4]; eta, scale, b, c0 = q[-4:]
        A,_,_ = spectrum(kind, p)
        A = broaden(A, abs(eta))
        return scale*np.interp(V, egrid, A) + b*V**2 + c0
    q0 = list(p0) + [0.1, 2.5, 0.0013, 0.0]
    xs = list(scales) + [0.05, 0.5, 0.0005, 0.02]
    r = least_squares(lambda q: full(q)-y, q0, x_scale=xs, diff_step=1e-2)
    J = r.jac; cov = np.linalg.pinv(J.T@J)*(2*r.cost/(len(y)-len(r.x)))
    err = np.sqrt(np.abs(np.diag(cov)))
    rms = np.sqrt(2*r.cost/len(y))
    A, mid, edges = spectrum(kind, r.x[:-4])
    return r.x, err, rms, mid, edges

names = {'alpha':['mu','alpha','Delta','Delta_c'], 'linear':['mu','Delta','Delta_c'], 'linear2':['mu','Delta','Delta_c'], 'bcs':['mu','Delta'], 'bcs2':['mu','Delta','Delta_c'], 'linear3':['mu','Delta','a','b']}
tail = ['eta','scale','b','c0']
results = {}
import sys
for panel in sys.argv[1:]:
    print(f"\n######## panel {panel}")
    for kind, p0s, sc in [('alpha', [[ebar,0.0,6.0,12.0],[ebar,0.0,4.0,3.0],[-0.9,0.0,4.0,2.5],[-0.9,1.0,2.0,2.0],[-1.9,1.0,2.0,2.0],[-0.9,0.3,4.0,3.0]], [0.2,0.1,0.3,0.5]),
                         ('linear',[[ebar,6.0,12.0],[0.0,6.0,16.0],[-0.9,4.5,3.0],[-0.9,4.5,8.0],[-1.9,2.0,2.0]], [0.2,0.3,0.5]),
                         ('linear2',[[ebar,6.0,12.0],[0.0,6.0,16.0],[-0.9,4.5,3.0],[-0.9,4.5,8.0],[-1.9,2.0,2.0]], [0.2,0.3,0.5]),
                         ('linear3',[[0.0,6.0,0.5,0.03],[-0.9,4.5,0.3,0.1],[-0.9,4.5,0.34,0.05]], [0.2,0.3,0.05,0.02]),
                         ('bcs', [[ebar,4.0],[-0.9,2.5],[-1.9,2.0]], [0.2,0.2]),
                         ('bcs2', [[ebar,4.0,4.0],[-0.9,2.5,2.5],[-1.9,2.0,2.0]], [0.2,0.2,0.3])]:
        best=None
        for p0 in p0s:
            try:
                res = fit(panel, kind, p0, sc)
            except Exception as e:
                print("fail", e); continue
            if best is None or res[2] < best[2]: best = res
        if best is None:
            print(f"  [{kind}] all fits failed"); continue
        x, err, rms, mid, edges = best
        print(f"  [{kind}] rms={rms:.4f}  midgap offset={mid:.3f}  edges: lower [{edges[0]:.2f},{edges[1]:.2f}] upper [{edges[2]:.2f},{edges[3]:.2f}]")
        for n_, v_, e_ in zip(names[kind]+tail, x, err):
            print(f"      {n_:8s} = {v_: .4f} +- {e_:.4f}")
        mu = x[0]; print(f"      filling of bare band below mu: {(EPS<mu).mean():.4f}")
        results[(panel,kind)] = (x, err, rms)
import pickle
pickle.dump(results, open('/app/analysis/fit_gapped_%s.pkl' % ''.join(sys.argv[1:]),'wb'))
