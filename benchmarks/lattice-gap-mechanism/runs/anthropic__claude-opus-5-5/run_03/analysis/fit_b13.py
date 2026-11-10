import numpy as np, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss, mu0
from scipy.optimize import least_squares
from multiprocessing import Pool
def Dtwo(xi, DF, Dp, Dm, w):
    Dinf = np.where(xi>=0, Dp, Dm)
    return np.sqrt(DF**2 + (Dinf**2-DF**2)*xi**2/(xi**2+w**2))
def F2g(p, mufix=None):
    if mufix is None: DF, Dp, Dm, w, mu, sig, amp, b = p
    else: DF, Dp, Dm, w, sig, amp, b = p; mu = mufix
    xi = E0 - mu; D = Dtwo(xi, DF, Dp, Dm, w)
    Ek = np.sqrt(xi**2 + D**2); u2 = 0.5*(1+xi/Ek); v2 = 0.5*(1-xi/Ek)
    A = gauss(cic(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2])), sig)
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > Ek.min())
def run(args):
    p0, mufix = args
    lo=[1.0,2,2,0.05]+([] if mufix is not None else [-2.5])+[0.02,0.1,0]
    hi=[4.5,8,8,4]+([] if mufix is not None else [0.5])+[0.6,30,0.05]
    try:
        s = least_squares(lambda p: F2g(p, mufix)-G, p0, bounds=(lo,hi), diff_step=1e-3, max_nfev=600)
        J=s.jac; dof=len(s.fun)-len(s.x); s2=(s.fun**2).sum()/dof; err=np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)), mufix)
    except Exception as e: return (1e9, str(e), None, mufix)
if __name__=='__main__':
    jobs=[]
    for DF in [2.6,3.0]:
        for Dinf in [4.5,5.5]:
            for w in [0.3,1.0,2.0]:
                jobs.append(([DF,Dinf,Dinf,w,0.15,3.0,0.011], mu0))
                jobs.append(([DF,Dinf,Dinf,w,mu0,0.15,3.0,0.011], None))
    with Pool(8) as pool: out=pool.map(run, jobs)
    for mf in [mu0, None]:
        best=sorted([o for o in out if o[3]==mf], key=lambda o:o[0])[0]
        print('mu fixed' if mf is not None else 'mu free', 'SSE=%.4f'%best[0], best[1], 'err', best[2])
        np.save('/app/analysis/fit_b13_%s.npy'%('fix' if mf is not None else 'free'), np.array(best[1]))
