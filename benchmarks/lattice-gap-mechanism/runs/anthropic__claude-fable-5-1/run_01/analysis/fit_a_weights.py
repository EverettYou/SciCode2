import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.optimize import least_squares
with open('/app/measurements.json') as f: d = json.load(f)
sts = {s['panel']: s for s in d['measurements'][0]['spectra']}
V = np.array(sts['a']['bias']); y = np.array(sts['a']['dI_dV'])
N = 700
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
EPS = (-2*(cx+cy) - 4*0.196*cx*cy).ravel()
ebar = (EPS.min()+EPS.max())/2
egrid = np.arange(-14, 14, 0.01); de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(E, w):
    h,_ = np.histogram(E, bins=bins, weights=w); return h/de/E.size
def broaden(A, eta, kind):
    eta = min(max(abs(eta),1e-3),0.8)
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    if kind=='L': ker = (eta/np.pi)/(x**2+eta**2)
    elif kind=='G': ker = np.exp(-x**2/(2*eta**2))
    ker/=ker.sum(); return np.convolve(A, ker, mode='same')

def spectrum(wkind, p):
    U2 = p[0]
    Ep = U2 + (EPS-ebar)/2; Em = -U2 + (EPS-ebar)/2
    if wkind == 'lin':        # w- = 1/2 (1 - (eps-mu)/Dc)
        mu, Dc = p[1:3]; wm = 0.5*(1-(EPS-mu)/Dc)
    elif wkind == 'canon':    # w- = 1/2 (1 - eps/sqrt(eps^2+U^2)) with U = 2*U2 (Hubbard-I canonical), eps from mean
        wm = 0.5*(1 - EPS/np.sqrt(EPS**2 + (2*U2)**2))
    elif wkind == 'canonlin': # w- = 1/2(1 - eps/U)
        wm = 0.5*(1 - EPS/(2*U2))
    elif wkind == 'quad':
        mu, Dc, c = p[1:4]; x = EPS-mu; wm = 0.5*(1 - x/Dc) + c*x**2
    elif wkind == 'tanh':
        mu, Tw = p[1:3]; wm = 0.5*(1 - np.tanh((EPS-mu)/Tw))
    elif wkind == 'nk':       # w- = 1 - 1/2 n0 ... weights from bare occupation: w- = a + b*theta(mu0-eps)
        mu, a, b = p[1:4]; wm = a + b*(EPS<mu)
    wm = np.clip(wm, 0, 1); wp = 1-wm
    mid = 0.5*(Ep.min()+Em.max())
    return hist(np.concatenate([Ep-mid,Em-mid]), np.concatenate([wp,wm]))

def fit(wkind, p0, bk):
    def full(q):
        n = len(p0); p = q[:n]; eta, scale, b, c0 = q[n:]
        A = broaden(spectrum(wkind, p), eta, bk)
        return scale*np.interp(V, egrid, A) + b*V**2 + c0
    q0 = list(p0)+[0.09, 6.8, 0.0014, 0.002]
    r = least_squares(lambda q: full(q)-y, q0, diff_step=1e-2)
    rms = np.sqrt(2*r.cost/len(y))
    J = r.jac; cov = np.linalg.pinv(J.T@J)*(2*r.cost/(len(y)-len(r.x))); err = np.sqrt(np.abs(np.diag(cov)))
    return r.x, err, rms, full(r.x)

results = {}
for bk in ['L','G']:
    for wkind, p0 in [('lin',[6.0,0.0,16.0]), ('canon',[6.0]), ('canonlin',[6.0]), ('quad',[6.0,0.0,16.0,0.0]), ('tanh',[6.0,0.0,8.0]), ('nk',[6.0,0.47,0.3,0.4])]:
        x, err, rms, model = fit(wkind, p0, bk)
        print(f"broadening {bk}, weights {wkind:9s}: rms={rms:.4f}  params={np.round(x,4)}  err={np.round(err,4)}")
        results[(bk,wkind)] = (x, rms, model)
# plot residuals of a few
fig, axs = plt.subplots(3,1, figsize=(12,10), sharex=True)
axs[0].plot(V, y, lw=0.7, label='data a')
for key, c in [(('L','lin'),'C1'), (('L','canon'),'C2'), (('G','lin'),'C3')]:
    x, rms, model = results[key]
    axs[0].plot(V, model, lw=0.8, label=f'{key} rms={rms:.4f}', color=c)
    axs[1].plot(V, y-model, lw=0.7, label=str(key), color=c)
axs[0].legend(); axs[1].legend(); axs[1].set_ylabel('residual')
x, rms, model = results[('L','canon')]
axs[2].plot(V, y-model, lw=0.7, label='canon resid', color='C2'); axs[2].legend()
for a in axs: a.grid(alpha=0.3); a.set_xticks(np.arange(-10,11,1))
plt.savefig('/app/analysis/fit_a_weights.png', dpi=110)
