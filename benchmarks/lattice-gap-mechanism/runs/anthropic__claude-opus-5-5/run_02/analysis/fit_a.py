from load import *
import numpy as np
from scipy.optimize import least_squares
V,G=sts('a')
N=500
k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
dV=V[1]-V[0]
bins=np.concatenate([V-dV/2,[V[-1]+dV/2]])
def dos(E, w, sigma):
    h,_=np.histogram(E.ravel(),bins=bins,weights=w.ravel())
    h=h/(E.size*dV)
    x=np.arange(-60,61)*dV
    g=np.exp(-x**2/(2*sigma**2)); g/=g.sum()
    return np.convolve(h,g,mode='same')
t,tp=1.008,0.192
eps=-2*t*(cx+cy)-4*tp*cx*cy
ec=-4*tp   # band center
x=eps-ec
def model_lin(p):
    alpha,c,Dl,gam,A,a,sig=p
    Ep=alpha*x+c+Dl; Em=alpha*x+c-Dl
    Zp=0.5*(1+gam*x); Zm=0.5*(1-gam*x)
    d=dos(Ep,Zp,abs(sig))+dos(Em,Zm,abs(sig))
    return A*d + a*np.abs(V)*(d<1e-3)
def model_hub1(p):
    # Hubbard-I at half filling: poles of 1/(w' - (eps - e0) - U^2/(4 w')), w measured from w'=0 shifted by c
    U,e0,c,A,a,sig=p
    y=eps-e0
    s=np.sqrt(y**2+U**2)
    Ep=(y+s)/2+c; Em=(y-s)/2+c
    Zp=0.5*(1+y/s); Zm=0.5*(1-y/s)
    d=dos(Ep,Zp,abs(sig))+dos(Em,Zm,abs(sig))
    return A*d + a*np.abs(V)*(d<1e-3)
for name,model,p0 in [('linear',model_lin,[0.5,0.0,6.0,0.0,3.0,0.012,0.08]),
                      ('linear gam fixed 1/12',None,None),
                      ('HubbardI',model_hub1,[12.0,0.0,0.0,3.0,0.012,0.08])]:
    if model is None:
        def m2(p):
            return model_lin([p[0],p[1],p[2],1/12.,p[3],p[4],p[5]])
        model=m2; p0=[0.5,0.0,6.0,3.0,0.012,0.08]
    r=least_squares(lambda p: model(p)-G,p0,diff_step=1e-3)
    chi2=np.sum(r.fun**2)
    print(name,'params',np.round(r.x,4),'chi2',round(chi2,4))
