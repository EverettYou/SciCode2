import numpy as np
from scipy.optimize import brentq
N=200
k=2*np.pi*(np.arange(N)+0.5)/N; KX,KY=np.meshgrid(k,k,indexing='ij')
t,tp=0.9993,0.1945
def eps(kx,ky): return -2*t*(np.cos(kx)+np.cos(ky))-4*tp*np.cos(kx)*np.cos(ky)
V0=6.0  # singlet rung binding 3J/4
def Epair(Qx,Qy):
    e2 = eps(Qx/2+KX,Qy/2+KY)+eps(Qx/2-KX,Qy/2-KY)
    f=lambda E: 1-V0*np.mean(1/(e2-E))
    return brentq(f, -40, e2.min()-1e-9)
E0=Epair(0,0); EM=Epair(np.pi,np.pi); EX=Epair(np.pi,0)
print('pair energies: Gamma %.4f  X %.4f  M %.4f ; two-particle continuum bottom %.4f'%(E0,EX,EM,2*eps(0,0)))
# fit to boson dispersion E(Q) = c - 2 tb (cosQx+cosQy) - 4 tb' cosQx cosQy
A=np.array([[1,-4,-4],[1,0,4],[1,4,-4]]); c,tb,tbp=np.linalg.solve(A,[E0,EX,EM])
print('effective pair hopping t_b=%.4f, t_b\'=%.4f ; binding relative to continuum = %.3f'%(tb,tbp,2*eps(0,0)-E0))
# effective mass along Gamma-X
q=0.2; Eq=Epair(q,0); print('m* from curvature: 1/(2m*) = %.4f (vs t_b for cos dispersion)'%((Eq-E0)/q**2))
