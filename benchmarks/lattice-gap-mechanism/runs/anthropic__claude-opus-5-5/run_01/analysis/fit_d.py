import json, numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][3]
V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
Nk = 800
k = 2*np.pi*(np.arange(Nk)+0.5)/Nk
kx, ky = np.meshgrid(k, k, indexing='ij')
cx, cy = np.cos(kx).ravel(), np.cos(ky).ravel()
edges = np.append(V - dV/2, V[-1] + dV/2)
def dos(t, tp, nu, sig):
    e = -2*t*(cx+cy) - 4*tp*cx*cy
    es = np.sort(e); mu = es[int(nu*len(es))]
    h, _ = np.histogram(e - mu, bins=edges)
    n = h/len(e)/dV
    return gaussian_filter1d(n, max(sig/dV, 0.3))
def model(p):
    t, tp, nu, sig, A, b0, b2 = p
    return A*dos(t, tp, nu, sig) + b0 + b2*V**2
def res(p): return model(p) - g
p0 = [1.0, 0.2, 0.3, 0.1, 3.0, 0.02, 0.001]
sol = least_squares(res, p0, x_scale=[0.05,0.02,0.02,0.05,0.5,0.01,0.0005], diff_step=1e-3)
J = sol.jac; r = sol.fun; dof = len(V) - len(p0); s2 = (r**2).sum()/dof
cov = np.linalg.inv(J.T@J)*s2
names = ['t','tp','nu','sigma','A','b0','b2']
for n_, v_, e_ in zip(names, sol.x, np.sqrt(np.diag(cov))):
    print(f'{n_:6s} = {v_:.4f} +- {e_:.4f}')
print('residual rms', np.sqrt(s2))
# profile scan in t' to be robust against numerical histogram noise
for tp in [0.15, 0.18, 0.2, 0.22, 0.25]:
    f = lambda q: model([q[0], tp, q[1], q[2], q[3], q[4], q[5]]) - g
    s_ = least_squares(f, [1.0, 0.3, 0.1, 3.0, 0.02, 0.001], diff_step=1e-3)
    print(f"tp={tp}: chi2={np.sum(s_.fun**2)/s2:.1f}  t={s_.x[0]:.3f} nu={s_.x[1]:.3f}")
np.save('fit_d_params.npy', sol.x)
