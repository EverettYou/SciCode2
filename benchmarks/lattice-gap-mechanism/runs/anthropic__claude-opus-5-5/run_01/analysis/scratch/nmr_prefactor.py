import json, numpy as np
from scipy.optimize import least_squares
d = json.load(open('/app/measurements.json'))
s = d['measurements'][1]['samples'][0]
T = np.array(s['temperature']); r = np.array(s['one_over_T1']); e = np.array(s['uncertainty'])
y = r/T; ey = e/T
m = (y/ey > 1.0)
def res(p, fixp=None):
    lnA, D, pp = p if fixp is None else (p[0], p[1], fixp)
    model = np.exp(lnA)*T[m]**pp*np.exp(-D/T[m])
    return (y[m]-model)/ey[m]
for fixp in [None, 0, 0.5, 1, 1.5, 2, -0.5, -1]:
    p0 = [0, 5, 0] if fixp is None else [0,5]
    sol = least_squares(lambda p: res(p, fixp), p0)
    chi2 = np.sum(sol.fun**2)/(m.sum()-len(p0))
    J = sol.jac; cov = np.linalg.inv(J.T@J)
    print(f"p={'free' if fixp is None else fixp}: params={np.round(sol.x,3)}  err={np.round(np.sqrt(np.diag(cov)),3)}  chi2/dof={chi2:.3f}")
# Also: atomic-limit attractive-U singly-occupied fraction model: y = A * T^p / (1+exp(U/2T))
for p in [0, -1, 1]:
    sol = least_squares(lambda q: (y[m]-np.exp(q[0])*T[m]**p/(1+np.exp(q[1]/(2*T[m]))))/ey[m], [0, 11])
    chi2 = np.sum(sol.fun**2)/(m.sum()-2)
    print(f"atomic singly-occupied model p={p}: |U|={sol.x[1]:.2f} chi2/dof={chi2:.3f}")
