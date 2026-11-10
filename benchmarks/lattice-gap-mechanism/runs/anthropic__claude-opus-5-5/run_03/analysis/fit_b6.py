import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss, mu0
from scipy.optimize import least_squares
from multiprocessing import Pool
ec = 0.5*(E0.min()+E0.max())
def comps(Phi, alpha, Delta, mu):
    x = E0 - ec
    Ep = Phi + x/2; Em = -Phi + x/2
    Zp = 0.5*(1+alpha*x); Zm = 0.5*(1-alpha*x)
    Am = cic(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm]))
    xi = E0 - mu; Ek = np.sqrt(xi**2+Delta**2)
    Ab = cic(np.concatenate([Ek,-Ek]), np.concatenate([0.5*(1+xi/Ek),0.5*(1-xi/Ek)]))
    return Am, Ab, min(Em.max()*-1, Ep.min()), Ek.min()
def Fsup(p):
    w, Phi, alpha, Delta, mu, sig, amp, b = p
    Am, Ab, gm, gb = comps(Phi, alpha, Delta, mu)
    A = gauss(w*Am + (1-w)*Ab, sig)
    g = min(gm, gb)
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > g)
def run(p0):
    try:
        s = least_squares(lambda p: Fsup(p)-G, p0, bounds=([0,2,-0.2,0.5,-3,0.02,0.1,0],[1,8,0.2,8,1,0.6,30,0.05]), diff_step=1e-3, max_nfev=500)
        J = s.jac; dof = len(s.fun)-len(s.x); s2 = (s.fun**2).sum()/dof
        err = np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)))
    except Exception as e:
        return (1e9, str(e), None)
if __name__ == '__main__':
    jobs = []
    for w in [0.3, 0.6, 0.9]:
        for Phi in [4.5, 6.0]:
            for D in [2.6, 5.0]:
                jobs.append([w, Phi, 0.05, D, mu0, 0.12, 3, 0.01])
    with Pool(8) as pool: out = pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:4]: print('SSE=%.4f'%o[0], '[w,Phi,alpha,Delta,mu,sig,amp,b]=', o[1], 'err', o[2])
    np.save('/app/analysis/fit_b6_best.npy', np.array(out[0][1]))
