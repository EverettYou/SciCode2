import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss
from scipy.optimize import least_squares
from multiprocessing import Pool
M = len(E0)
def spec(a, m1, b, m2, Phi, Dc, Df, Dcf):
    xi = a*(E0 - m1); eta = b*(E0 - m2)
    H = np.zeros((M,4,4))
    H[:,0,0]=xi; H[:,1,1]=eta; H[:,2,2]=-xi; H[:,3,3]=-eta
    H[:,0,1]=H[:,1,0]=Phi; H[:,2,3]=H[:,3,2]=-Phi
    H[:,0,2]=H[:,2,0]=Dc; H[:,1,3]=H[:,3,1]=Df
    H[:,0,3]=H[:,3,0]=Dcf; H[:,1,2]=H[:,2,1]=Dcf
    w, U = np.linalg.eigh(H)
    return w.ravel(), (U[:,0,:]**2).ravel()
def Fg(p):
    a, m1, b, m2, Phi, Dc, Df, Dcf, sig, amp, bb = p
    w, Z = spec(a, m1, b, m2, Phi, Dc, Df, Dcf)
    A = gauss(cic(w, Z), sig)
    g = min(w[w>0].min(), -w[w<0].max())
    return amp*A + bb*np.abs(Vf)*(np.abs(Vf) > g)
lo = [0.1,-6,-1.5,-6,0,-6,-6,-6,0.02,0.1,0]; hi = [1.5,6,1.5,6,8,6,6,6,0.6,30,0.05]
def run(p0):
    try:
        s = least_squares(lambda p: Fg(p)-G, p0, bounds=(lo,hi), diff_step=1e-3, max_nfev=400)
        return (2*s.cost, list(np.round(s.x,4)))
    except Exception as e:
        return (1e9, str(e))
if __name__ == '__main__':
    rng = np.random.default_rng(1)
    jobs = []
    for i in range(32):
        p0 = [rng.choice([0.5,1.0]), rng.uniform(-2,0.5), rng.choice([0.5,-0.5,1.0]), rng.uniform(-2,0.5),
              rng.uniform(0,6), rng.uniform(0,4), rng.uniform(0,4), rng.uniform(0,4), 0.12, 3.0, 0.01]
        jobs.append(p0)
    with Pool(8) as pool: out = pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:6]: print('SSE=%.4f'%o[0], '[a,m1,b,m2,Phi,Dc,Df,Dcf,sig,amp,bg]=', o[1])
    np.save('/app/analysis/fit_b9_best.npy', np.array(out[0][1]))
