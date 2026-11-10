import numpy as np, sys
sys.path.insert(0,'/app/analysis')
from fit_b9 import Fg, lo, hi, G
from scipy.optimize import least_squares
from multiprocessing import Pool
def run(p0):
    try:
        s = least_squares(lambda p: Fg(p)-G, p0, bounds=(lo,hi), diff_step=1e-3, max_nfev=500)
        return (2*s.cost, list(np.round(s.x,4)))
    except Exception as e: return (1e9, str(e))
if __name__=='__main__':
    rng=np.random.default_rng(7); jobs=[]
    for i in range(64):
        a=1.0; m1=rng.uniform(-1.2,-0.6); b=rng.choice([0.5,0.0,-0.5,1.0]); m2=rng.uniform(-1.5,0.5)
        Phi=rng.uniform(2,6); Dc=rng.uniform(1.5,3.5); Df=rng.uniform(-5,5); Dcf=rng.uniform(-3,3)
        jobs.append([a,m1,b,m2,Phi,Dc,Df,Dcf,0.12,3.0,0.011])
    with Pool(8) as pool: out=pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:6]: print('SSE=%.4f'%o[0], '[a,m1,b,m2,Phi,Dc,Df,Dcf,sig,amp,bg]=', o[1])
    np.save('/app/analysis/fit_b12_best.npy', np.array(out[0][1]))
