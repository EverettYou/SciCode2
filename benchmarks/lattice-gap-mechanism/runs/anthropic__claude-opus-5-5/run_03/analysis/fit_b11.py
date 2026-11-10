import numpy as np, json, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss, mu0
from scipy.optimize import least_squares
from multiprocessing import Pool
def Dxi(xi, p):
    D0, ap, bp, cp, am, bm, cm = p
    x = np.abs(xi)
    return np.where(xi>=0, D0 + ap*x + bp*x**2 + cp*x**3, D0 + am*x + bm*x**2 + cm*x**3)
def Fx(p):
    q = p[:7]; mu, sig, amp, b = p[7:]
    xi = E0 - mu
    D = np.clip(Dxi(xi, q), 0.05, None)
    Ek = np.sqrt(xi**2 + D**2); u2 = 0.5*(1+xi/Ek); v2 = 0.5*(1-xi/Ek)
    A = gauss(cic(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2])), sig)
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > Ek.min())
lo=[1.0,-2,-2,-1,-2,-2,-1,-2.5,0.02,0.1,0]; hi=[5,6,2,1,6,2,1,0.5,0.6,30,0.05]
def run(p0):
    try:
        s = least_squares(lambda p: Fx(p)-G, p0, bounds=(lo,hi), diff_step=1e-3, max_nfev=800)
        return (2*s.cost, list(np.round(s.x,4)))
    except Exception as e: return (1e9, str(e))
if __name__=='__main__':
    rng=np.random.default_rng(3); jobs=[]
    for i in range(24):
        jobs.append([rng.uniform(2.4,3.2), rng.uniform(0,3), rng.uniform(-0.5,0.5), 0, rng.uniform(0,3), rng.uniform(-0.5,0.5), 0, mu0, 0.12, 3.0, 0.01])
    with Pool(8) as pool: out=pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:4]: print('SSE=%.4f'%o[0], o[1])
    np.save('/app/analysis/fit_b11_best.npy', np.array(out[0][1]))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,axs=plt.subplots(1,2,figsize=(13,4)); axs[0].plot(V,G,'k-',lw=0.5); axs[0].plot(Vf,Fx(out[0][1]),'r-')
    xx=np.linspace(-3.9,4.2,200); axs[1].plot(xx, Dxi(xx,out[0][1][:7])); axs[1].set_xlabel('xi'); axs[1].set_ylabel('Delta(xi)')
    fig.savefig('/app/analysis/fit_b11.png',dpi=100)
