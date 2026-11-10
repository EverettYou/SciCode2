import json, numpy as np
from scipy.optimize import least_squares
with open('/app/measurements.json') as f:
    d = json.load(f)
sts = {s['panel']: s for s in d['measurements'][0]['spectra']}
V = np.array(sts['d']['bias']); y = np.array(sts['d']['dI_dV'])

N = 1000
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
c2x, c2y = np.cos(2*KX), np.cos(2*KY)

def eps(t, tp, tpp):
    return -2*t*(cx+cy) - 4*tp*cx*cy - 2*tpp*(c2x+c2y)

def dos_on_grid(E, w, egrid):
    # histogram
    de = egrid[1]-egrid[0]
    h, _ = np.histogram(E.ravel(), bins=np.concatenate([egrid-de/2, [egrid[-1]+de/2]]), weights=w.ravel())
    return h/de/E.size

def broaden(egrid, A, eta, kind='lorentz'):
    de = egrid[1]-egrid[0]
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    if kind=='lorentz':
        ker = (eta/np.pi)/(x**2+eta**2)
    else:
        ker = np.exp(-x**2/(2*eta**2))/np.sqrt(2*np.pi)/eta
    ker /= ker.sum()
    return np.convolve(A, ker, mode='same')

egrid = np.arange(-12, 12, 0.01)

def model_d(p):
    t, tp, tpp, mu, eta, scale, b, c0 = p
    E = eps(t, tp, tpp) - mu
    A = dos_on_grid(E, np.ones_like(E), egrid)
    A = broaden(egrid, A, abs(eta))
    Ai = np.interp(V, egrid, A)
    return scale*Ai + b*V**2 + c0

def resid(p):
    return model_d(p) - y

p0 = [1.0, 0.2, 0.0, -0.9, 0.1, 2.5, 0.0012, 0.0]
best=None
for tpp0 in [0.0, 0.05, -0.05]:
    for eta0 in [0.05, 0.15]:
        p0 = [1.0, 0.2, tpp0, -0.9, eta0, 2.5, 0.0012, 0.0]
        r = least_squares(resid, p0, x_scale=[0.1,0.05,0.05,0.2,0.05,0.5,0.0005,0.02], diff_step=2e-2)
        if best is None or r.cost < best.cost: best = r
r = best
names = ['t','tp','tpp','mu','eta','scale','b','c0']
J = r.jac; cov = np.linalg.pinv(J.T@J)*(2*r.cost/(len(y)-len(r.x)))
for n_, v_, e_ in zip(names, r.x, np.sqrt(np.diag(cov))):
    print(f"{n_:6s} = {v_: .4f} +- {e_:.4f}")
print("rms resid", np.sqrt(2*r.cost/len(y)))
t,tp,tpp,mu = r.x[:4]
E = eps(t,tp,tpp)
print("band bottom", E.min(), "top", E.max(), "width", E.max()-E.min(), "vHs (pi,0):", -2*t*(-1+1) - 4*tp*(-1)*1 - 2*tpp*(1+1))
print("filling at mu:", (E<mu).mean())
# also fit with tpp fixed 0
def resid2(p):
    return model_d([p[0],p[1],0.0,p[2],p[3],p[4],p[5],p[6]]) - y
r2 = least_squares(resid2, [1,0.2,-0.9,0.1,2.5,0.0012,0], x_scale=[0.1,0.05,0.2,0.05,0.5,0.0005,0.02], diff_step=2e-2)
J = r2.jac; cov = np.linalg.pinv(J.T@J)*(2*r2.cost/(len(y)-len(r2.x)))
print("--- tpp=0 fit")
for n_, v_, e_ in zip(['t','tp','mu','eta','scale','b','c0'], r2.x, np.sqrt(np.diag(cov))):
    print(f"{n_:6s} = {v_: .4f} +- {e_:.4f}")
print("rms resid", np.sqrt(2*r2.cost/len(y)))
t,tp,mu = r2.x[:3]
E = eps(t,tp,0)
print("filling at mu:", (E<mu).mean(), " width", E.max()-E.min())
np.save('/app/analysis/bare_fit.npy', r.x)
