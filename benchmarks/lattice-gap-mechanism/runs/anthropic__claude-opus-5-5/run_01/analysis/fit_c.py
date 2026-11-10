import json, numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][2]
V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
Nk = 600
k = 2*np.pi*(np.arange(Nk)+0.5)/Nk
kx, ky = np.meshgrid(k, k, indexing='ij')
cx, cy = np.cos(kx).ravel(), np.cos(ky).ravel()
e = -2*(cx+cy) - 0.8*cx*cy   # t=1, tp=0.2
es = np.sort(e)
edges = np.append(V - dV/2, V[-1] + dV/2)
def bcs_dos(mu, D, sig, gam=0.0):
    xi = e - mu; E = np.sqrt(xi**2 + D**2)
    u2 = 0.5*(1+xi/E); v2 = 0.5*(1-xi/E)
    h1, _ = np.histogram(E, bins=edges, weights=u2)
    h2, _ = np.histogram(-E, bins=edges, weights=v2)
    n = (h1+h2)/len(e)/dV
    return gaussian_filter1d(n, max(sig/dV, 0.3))
def model(p, mask_bg=True):
    mu, D, sig, A, b0, b2 = p
    return A*bcs_dos(mu, D, sig) + np.where(np.abs(V) > 0, 1, 1)*0 + bg(b0, b2)
def bg(b0, b2):
    # background only outside the gap region (inside the gap the measured conductance is ~0)
    return (b0 + b2*V**2) * (np.abs(V) > 1.5)
def res(p): return model(p) - g
mu0 = es[int(0.2*len(es))]
sol = least_squares(res, [mu0, 2.0, 0.1, 3.0, 0.02, 0.001], diff_step=1e-3)
J = sol.jac; r = sol.fun; s2 = (r**2).sum()/(len(V)-6); cov = np.linalg.inv(J.T@J)*s2
for n_, v_, e_ in zip(['mu','Delta','sigma','A','b0','b2'], sol.x, np.sqrt(np.diag(cov))):
    print(f'{n_:6s} = {v_:.4f} +- {e_:.4f}')
mu = sol.x[0]
print('normal-state mu0(nu=0.2) =', mu0, '; fitted mu - band bottom =', mu - es[0])
xi = e - mu; E = np.sqrt(xi**2 + sol.x[1]**2)
print('implied occupation sum v^2 =', np.mean(0.5*(1-xi/E)), ' ; fraction with xi<0 =', np.mean(xi<0))
np.save('fit_c_params.npy', sol.x)
