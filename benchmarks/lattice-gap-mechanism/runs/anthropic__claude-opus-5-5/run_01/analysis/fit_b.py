import json, numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][1]
V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
Nk = 500
k = 2*np.pi*(np.arange(Nk)+0.5)/Nk
kx, ky = np.meshgrid(k, k, indexing='ij')
e = (-2*(np.cos(kx)+np.cos(ky)) - 0.8*np.cos(kx)*np.cos(ky)).ravel()
mu0 = np.sort(e)[int(0.3*len(e))]
edges = np.append(V - dV/2, V[-1] + dV/2)
def dos(D0, Dinf, wid, sig, mu=mu0):
    xi = e - mu
    D = Dinf - (Dinf - D0)*np.exp(-np.abs(xi)/max(wid,1e-3))
    E = np.sqrt(xi**2 + D**2)
    h1, _ = np.histogram(E, bins=edges, weights=0.5*(1+xi/E))
    h2, _ = np.histogram(-E, bins=edges, weights=0.5*(1-xi/E))
    return gaussian_filter1d((h1+h2)/len(e)/dV, max(sig/dV, 0.3))
def model(p):
    D0, Dinf, wid, sig, A, b0, b2 = p
    return A*dos(D0, Dinf, wid, sig) + (b0 + b2*V**2)*(np.abs(V) > 2.0)
sol = least_squares(lambda p: model(p) - g, [2.6, 5.0, 0.8, 0.15, 3.0, 0.03, 0.001], diff_step=1e-3,
                    bounds=([0.5, 0.5, 0.01, 0.01, 0.1, -1, -1], [8, 10, 10, 2, 50, 1, 1]))
r = sol.fun; s2 = (r**2).sum()/(len(V)-7); cov = np.linalg.inv(sol.jac.T@sol.jac)*s2
for n_, v_, e_ in zip(['Delta0','Delta_inf','width','sigma','A','b0','b2'], sol.x, np.sqrt(np.diag(cov))):
    print(f'{n_:9s} = {v_:.4f} +- {e_:.4f}')
print('rms resid', np.sqrt(s2), ' mu0=', mu0)
# constant-gap BCS for comparison
sol2 = least_squares(lambda p: p[2]*dos(p[0], p[0], 1.0, p[1]) + (p[3]+p[4]*V**2)*(np.abs(V)>2) - g, [2.6, 0.15, 3.0, 0.03, 0.001], diff_step=1e-3)
print('constant-gap BCS: Delta=%.3f rms=%.4f' % (sol2.x[0], np.sqrt((sol2.fun**2).sum()/(len(V)-5))))
np.save('fit_b_params.npy', sol.x)
