import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss
from scipy.optimize import least_squares
from multiprocessing import Pool
ec = 0.5*(E0.min()+E0.max())
M = len(E0)
def spec(a, m1, b, m2, Phi, D, Df=0.0):
    xi = a*(E0 - m1); eta = b*(E0 - m2)
    H = np.zeros((M,4,4))
    H[:,0,0]=xi; H[:,1,1]=eta; H[:,2,2]=-xi; H[:,3,3]=-eta
    H[:,0,1]=H[:,1,0]=Phi; H[:,2,3]=H[:,3,2]=-Phi
    H[:,0,2]=H[:,2,0]=D; H[:,1,3]=H[:,3,1]=Df
    w, U = np.linalg.eigh(H)
    Z = U[:,0,:]**2   # electron (particle) weight
    return w.ravel(), Z.ravel()
def Fan(p):
    a, m1, b, m2, Phi, D, sig, amp, bb = p
    w, Z = spec(a, m1, b, m2, Phi, D)
    A = gauss(cic(w, Z), sig)
    wpos = w[w>0].min(); wneg = -w[w<0].max(); g = min(wpos, wneg)
    return amp*A + bb*np.abs(Vf)*(np.abs(Vf) > g)
def run(p0):
    try:
        s = least_squares(lambda p: Fan(p)-G, p0, bounds=([0.1,-6,-1.5,-6,0,0,0.02,0.1,0],[1.5,6,1.5,6,8,8,0.6,30,0.05]), diff_step=1e-3, max_nfev=400)
        J = s.jac; dof = len(s.fun)-len(s.x); s2 = (s.fun**2).sum()/dof
        err = np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)))
    except Exception as e:
        return (1e9, str(e), None)
if __name__ == '__main__':
    jobs = []
    for a in [0.5, 1.0]:
        for b in [0.5, -0.5]:
            for Phi in [2.0, 4.0]:
                for D in [1.0, 2.5]:
                    jobs.append([a, -0.9, b, -0.8, Phi, D, 0.12, 3, 0.01])
    with Pool(8) as pool: out = pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:5]: print('SSE=%.4f'%o[0], '[a,m1,b,m2,Phi,D,sig,amp,bg]=', o[1], 'err', o[2])
    np.save('/app/analysis/fit_b8_best.npy', np.array(out[0][1]))
