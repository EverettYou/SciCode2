import numpy as np, sys
sys.path.insert(0,'/app/analysis')
from fit_b4 import S, V, G, CX, CY, E0, Vf, cic, gauss, mu0
from scipy.optimize import least_squares
from multiprocessing import Pool
DW = (CX-CY)**2/4.0     # 0 on diagonal, 1 at X
def Dk(xi, p):
    DF0, DF1, Dp, Dm, w = p
    DF = DF0 + DF1*DW
    Dinf = np.where(xi>=0, Dp, Dm)
    return np.sqrt(DF**2 + np.clip(Dinf**2-DF**2, 0, None)*xi**2/(xi**2+w**2))
def F(p):
    q = p[:5]; mu, sig, amp, b = p[5:]
    xi = E0 - mu; D = Dk(xi, q)
    Ek = np.sqrt(xi**2 + D**2); u2 = 0.5*(1+xi/Ek); v2 = 0.5*(1-xi/Ek)
    A = gauss(cic(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2])), sig)
    return amp*A + b*np.abs(Vf)*(np.abs(Vf) > Ek.min())
lo=[1.0,-3,2,2,0.05,-2.5,0.02,0.1,0]; hi=[5,4,8,8,4,0.5,0.6,30,0.05]
def run(p0):
    try:
        s = least_squares(lambda p: F(p)-G, p0, bounds=(lo,hi), diff_step=1e-3, max_nfev=600)
        J=s.jac; dof=len(s.fun)-len(s.x); s2=(s.fun**2).sum()/dof; err=np.sqrt(np.abs(np.diag(np.linalg.pinv(J.T@J))*s2))
        return (2*s.cost, list(np.round(s.x,4)), list(np.round(err,4)))
    except Exception as e: return (1e9, str(e), None)
if __name__=='__main__':
    jobs=[]
    for DF0 in [2.6,3.0]:
        for DF1 in [-1.0,1.0,2.0]:
            for w in [0.5,1.0]:
                for mu in [-1.4,-0.9]:
                    jobs.append([DF0,DF1,4.9,5.7,w,mu,0.15,3.0,0.011])
    with Pool(8) as pool: out=pool.map(run, jobs)
    out.sort(key=lambda o:o[0])
    for o in out[:4]: print('SSE=%.4f'%o[0], '[DF0,DF1,Dinf+,Dinf-,w,mu,sig,amp,b]=', o[1], 'err', o[2])
    np.save('/app/analysis/fit_b14_best.npy', np.array(out[0][1]))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig,ax=plt.subplots(2,1,figsize=(11,7)); ax[0].plot(V,G,'k-',lw=0.5); ax[0].plot(Vf,F(out[0][1]),'r-'); ax[1].plot(V,G-F(out[0][1]),'r-',lw=0.6); ax[1].axhline(0,color='k')
    fig.savefig('/app/analysis/fit_b14.png',dpi=100)
    p=out[0][1]; xi=E0-p[5]; D=Dk(xi,p[:5]); E=np.sqrt(xi**2+D**2); print('BCS number nu=%.4f'%(np.mean(1-xi/E)/2))
