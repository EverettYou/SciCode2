import json, numpy as np
from scipy.optimize import curve_fit
d = json.load(open('/app/measurements.json'))
nmr = d['measurements'][1]['samples']; rho = d['measurements'][2]['samples']
sts = d['measurements'][0]['spectra']

def fit(T, y, e, Tmin, Tmax, p=0, label=''):
    m = (T>=Tmin)&(T<=Tmax)&(e>0)
    x = 1/T[m]; ly = np.log(np.clip(y[m],1e-12,None)) - p*np.log(T[m])
    w = (y[m]/e[m])**2  # weight for log
    A = np.vstack([np.ones_like(x), -x]).T
    W = np.diag(w)
    cov = np.linalg.inv(A.T@W@A); beta = cov@A.T@W@ly
    res = ly - A@beta; chi2 = np.sum(w*res**2)/(m.sum()-2)
    print(f"{label:28s} T in [{Tmin},{Tmax}] prefactor T^{p}: Delta = {beta[1]:.3f} +- {np.sqrt(cov[1,1]*max(chi2,1)):.3f}  (chi2/dof={chi2:.2f}, n={m.sum()})")
    return beta[1]

for s in nmr:
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); e = np.array(s['uncertainty'])
    y = r/T; ey = e/T
    nu = s['filling']
    if nu=='1/2':
        for p in [0, 1, -0.5]:
            fit(T, y, ey, 0.55, 4.5, p, f'NMR 1/T1T nu={nu}')
        fit(T, y, ey, 0.55, 1.2, 0, f'NMR 1/T1T nu={nu} lowT')
        fit(T, y, ey, 1.2, 4.5, 0, f'NMR 1/T1T nu={nu} highT')
    elif nu=='≈0.3':
        fit(T, y, ey, 0.28, 1.1, 0, f'NMR 1/T1T nu={nu}')
        fit(T, y, ey, 0.28, 0.36, 0, f'NMR 1/T1T nu={nu} below Tc')
        fit(T, y, ey, 0.36, 1.1, 0, f'NMR 1/T1T nu={nu} above Tc')
        fit(T, y, ey, 1.0, 3.0, 0, f'NMR 1/T1T nu={nu} 1-3')
    else:
        fit(T, y, ey, 0.2, 0.45, 0, f'NMR 1/T1T nu={nu}')
        fit(T, y, ey, 0.2, 0.32, 0, f'NMR 1/T1T nu={nu} lowest')
for s in rho:
    T = np.array(s['temperature']); r = np.array(s['resistivity']); e = np.array(s['uncertainty'])
    nu = s['filling']
    m = r>0
    if nu=='1/2':
        # rho ~ exp(+Delta/T): fit log(1/rho)
        fit(T[m], 1/r[m], e[m]/r[m]**2, 0.4, 4.1, 0, f'rho nu={nu}')
        fit(T[m], 1/r[m], e[m]/r[m]**2, 0.4, 1.2, 0, f'rho nu={nu} lowT')
        fit(T[m], 1/r[m], e[m]/r[m]**2, 1.2, 4.1, 0, f'rho nu={nu} highT')
    elif nu=='≈0.3':
        fit(T[m], 1/r[m], e[m]/r[m]**2, 0.39, 1.2, 0, f'rho nu={nu} above Tc')
        fit(T[m], 1/r[m], e[m]/r[m]**2, 0.39, 4.1, 0, f'rho nu={nu} all normal')
