import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss
from scipy.optimize import least_squares
from multiprocessing import Pool
ec = 0.5*(E0.min()+E0.max())
x = E0 - ec
def bcs_parts(xi, D):
    E = np.sqrt(xi**2 + D**2); return E, 0.5*(1+xi/E), 0.5*(1-xi/E)
def F4(p):
    Phi, s, mu, D, sig, amp, b = p
    xb = -Phi + s*x - mu; xa = Phi + s*x - mu
    Eb, ub, vb = bcs_parts(xb, D); Ea, ua, va = bcs_parts(xa, D)
    EE = np.concatenate([Eb, -Eb, Ea, -Ea]); ZZ = 0.5*np.concatenate([ub, vb, ua, va])
    A = gauss(cic(EE, ZZ), sig)
    g = min(Eb.min(), Ea.min())
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > g)
def run(p0):
    try:
        s = least_squares(lambda p: F4(p)-G, p0, bounds=([0,0.2,-9,0.1,0.02,0.1,0],[8,1.2,9,8,0.6,30,0.05]), diff_step=1e-3, max_nfev=500)
        J = s.jac; dof = len(s.fun)-len(s.x); s2 = (s.fun**2).sum()/dof
        err = np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)))
    except Exception as e:
        return (1e9, str(e), None)
if __name__ == '__main__':
    jobs = []
    for Phi in [0.5, 2.0, 4.0]:
        for mu in [-4.0, -2.0, 0.0]:
            for D in [2.6, 4.0]:
                jobs.append([Phi, 0.5, mu, D, 0.12, 3, 0.01])
    with Pool(8) as pool: out = pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:5]: print('SSE=%.4f'%o[0], '[Phi,s,mu,D,sig,amp,b]=', o[1], 'err', o[2])
