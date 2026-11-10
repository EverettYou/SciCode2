import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss
from scipy.optimize import least_squares
from multiprocessing import Pool
ec = 0.5*(E0.min()+E0.max())
def Ftr(p):
    # translated copies E = +-Phi + s*(e-ec) + d0 ; weights BCS-like in e with center e0 and width w
    Phi, s, d0, e0, w, sig, amp, b = p
    x = E0 - ec
    Ep = Phi + s*x + d0; Em = -Phi + s*x + d0
    f = (E0 - e0)/np.sqrt((E0-e0)**2 + w**2)
    Zp = 0.5*(1+f); Zm = 0.5*(1-f)
    A = gauss(cic(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm])), sig)
    glo, ghi = Em.max(), Ep.min()
    return amp*A + b*np.abs(Vf)*((Vf<glo)|(Vf>ghi))
def Fmir(p):
    # mirror copies E+ = Phi + s*x + d0, E- = -(Phi + s*x) + d0 ; weights BCS-like
    Phi, s, d0, e0, w, sig, amp, b = p
    x = E0 - ec
    Ep = Phi + s*x + d0; Em = -(Phi + s*x) + d0
    f = (E0 - e0)/np.sqrt((E0-e0)**2 + w**2)
    Zp = 0.5*(1+f); Zm = 0.5*(1-f)
    A = gauss(cic(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm])), sig)
    glo, ghi = Em.max(), Ep.min()
    return amp*A + b*np.abs(Vf)*((Vf<glo)|(Vf>ghi))
models = {'translated': Ftr, 'mirror': Fmir}
def run(args):
    name, p0 = args
    f = models[name]
    try:
        s = least_squares(lambda p: f(p)-G, p0, bounds=([2,0.2,-1,-6,0.05,0.02,0.1,0],[8,1.0,1,4,10,0.6,30,0.05]), diff_step=1e-3, max_nfev=500)
        J = s.jac; dof = len(s.fun)-len(s.x); s2 = (s.fun**2).sum()/dof
        err = np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (name, 2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)))
    except Exception as e:
        return (name, 1e9, str(e), None)
if __name__ == '__main__':
    jobs = []
    for name in models:
        for e0 in [-2.0, -0.9, 0.0]:
            for w in [0.5, 2.0]:
                for s in [0.5]:
                    jobs.append((name, [4.55, s, 0.0, e0, w, 0.12, 3, 0.01]))
    with Pool(8) as pool: out = pool.map(run, jobs)
    for n in models:
        best = sorted([o for o in out if o[0]==n], key=lambda o:o[1])[0]
        print(n, 'SSE=%.4f'%best[1], 'params [Phi,s,d0,e0,w,sig,amp,b]=', best[2], ' err=', best[3])
        np.save('/app/analysis/fit_b5_%s.npy'%n, np.array(best[2]))
