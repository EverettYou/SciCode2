import numpy as np
from scipy.optimize import brentq
N=600
k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
def run(t,tp,label):
    e=(-2*t*(cx+cy)-4*tp*cx*cy).ravel()
    mu=lambda nu: np.quantile(e,nu)
    def gap(U,m):
        f=lambda D: U*np.mean(1/(2*np.sqrt((e-m)**2+D**2)))-1
        return brentq(f,1e-5,60) if f(1e-5)>0 else 0
    # |U| that gives Delta=1.9587 at nu=0.2 (fixed mu)
    U02=brentq(lambda U: gap(U,mu(0.2))-1.9587,2,20)
    print(label,'t=%.4f tp=%.4f : |U| for Delta(0.2)=1.9587 ->'%(t,tp),round(U02,4))
    for nu in [0.2,0.3,0.4,0.5]:
        print('    nu=%.2f  Delta(fixed mu, |U|=%.3f)=%.3f'%(nu,U02,gap(U02,mu(nu))))
    # two-body binding for |U|=12 and 6
    emin=e.min()
    for U in [6,12]:
        f=lambda E: U*np.mean(1/(2*e-E))-1
        E2=brentq(f,-60,2*emin-1e-9)
        print('    |U|=%d: two-body E2=%.3f, binding below continuum Eb=%.3f, Eb/2=%.3f'%(U,E2,2*emin-E2,(2*emin-E2)/2))
run(1.0026,0.2007,'fit(c)')
run(1.008,0.192,'fit(d)')
