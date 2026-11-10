# Fit the high-T (d) spectrum by bare tight-binding DOS: eps = -2t(cx+cy) - 4t' cx cy - mu
from load import *
import numpy as np
from scipy.optimize import least_squares
V,G=sts('d')
N=600
k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
def dos(eps, w, bins, sigma):
    h,_=np.histogram(eps.ravel(),bins=bins,weights=w.ravel() if w is not None else None)
    h=h/(eps.size*(bins[1]-bins[0]))
    # gaussian broaden
    x=np.arange(-40,41)*(bins[1]-bins[0])
    g=np.exp(-x**2/(2*sigma**2)); g/=g.sum()
    return np.convolve(h,g,mode='same')
dV=V[1]-V[0]
bins=np.concatenate([V-dV/2,[V[-1]+dV/2]])
def model(p):
    t,tp,mu,A,a,sig=p
    eps=-2*t*(cx+cy)-4*tp*cx*cy-mu
    d=dos(eps,None,bins,abs(sig))
    return A*d + a*np.abs(V)*(d<1e-3)
def resid(p):
    return model(p)-G
p0=[1.0,0.2,-1.2,3.0,0.012,0.05]
r=least_squares(resid,p0)
print('fit t,tp,mu,A,bgslope,sigma =',r.x)
J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p0))
print('errors',np.sqrt(np.diag(cov)))
t,tp,mu=r.x[:3]
eps=-2*t*(cx+cy)-4*tp*cx*cy
print('band bottom',(-4*t-4*tp)-mu,'top',(4*t-4*tp)-mu,'vHs',4*tp-mu)
print('filling (per spin) at mu:',np.mean(eps<mu))
np.save('/app/analysis/fit_d.npy',r.x)
