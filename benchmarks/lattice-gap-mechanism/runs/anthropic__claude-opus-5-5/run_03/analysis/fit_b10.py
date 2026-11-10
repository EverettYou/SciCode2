import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss, mu0
from scipy.optimize import least_squares
from multiprocessing import Pool
xi = E0 - mu0
def bcs(D):
    Ek = np.sqrt(xi**2 + D**2); return cic(np.concatenate([Ek,-Ek]), np.concatenate([0.5*(1+xi/Ek),0.5*(1-xi/Ek)]))
Dgrid = np.linspace(1.5, 6.5, 51)
LIB = np.array([bcs(D) for D in Dgrid])
def Fdist(p):
    Dmin, Dmax, w, pw, sig, amp, b = p
    Dm = np.clip(Dgrid, Dmin, Dmax)
    P = np.where((Dgrid>=Dmin)&(Dgrid<=Dmax), (np.clip(Dgrid-Dmin,0,None)+1e-9)**pw, 0.0)
    if P.sum()<=0: P = np.zeros_like(Dgrid)
    else: P = P/P.sum()*(1-w)
    j = np.argmin(np.abs(Dgrid-Dmax)); P2 = P.copy(); P2[j] += w
    A = gauss(P2@LIB, sig)
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > Dmin)
def run(p0):
    try:
        s = least_squares(lambda p: Fdist(p)-G, p0, bounds=([1.5,3,0,0,0.02,0.1,0],[4,6.4,1,4,0.6,30,0.05]), diff_step=1e-2, max_nfev=600)
        return (2*s.cost, list(np.round(s.x,4)))
    except Exception as e:
        return (1e9, str(e))
if __name__=='__main__':
    jobs=[[2.6,5.0,w,pw,0.12,3,0.01] for w in [0.2,0.5,0.8] for pw in [0.5,1.0,2.0]]
    with Pool(8) as pool: out = pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:4]: print('SSE=%.4f [Dmin,Dmax,w,pw,sig,amp,b]='%o[0], o[1])
    np.save('/app/analysis/fit_b10_best.npy', np.array(out[0][1]))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(10,4)); ax.plot(V,G,'k-',lw=0.5); ax.plot(Vf,Fdist(out[0][1]),'r-'); fig.savefig('/app/analysis/fit_b10.png',dpi=100)
