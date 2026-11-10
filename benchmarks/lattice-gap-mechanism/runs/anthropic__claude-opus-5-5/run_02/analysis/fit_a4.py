from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,V=Vs,ret_parts=False):
    t,tp,c,Dl,gam,xw,A,a,sig=p
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+gam*(x-xw)); Zm=1-Zp
    d=D.g(V,Ep,Zp,sig)+D.g(V,Em,Zm,sig)
    gapmask=(V>c-Dl+2*t)&(V<c+Dl-2*t)
    return A*d+a*np.abs(V)*(~gapmask)
p0=[0.99,0.19,0.02,6.0,0.05,0.0,3.2,0.0128,0.12]
r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac')
dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
J=r.jac; cov=np.linalg.pinv(J.T@J)*s2; err=np.sqrt(np.diag(cov))
names=['t','tp','c','Delta','gamma','x_w','A','bg','sig']
print('chi2/dof %.6f'%s2)
for n,v,e in zip(names,r.x,err): print(f'  {n:6s} {v:9.4f} +- {e:.4f}')
np.save('/app/analysis/fit_a4.npy',r.x); np.save('/app/analysis/fit_a4_cov.npy',cov)
# implied zero line and fraction
t,tp,c,Dl,gam,xw=r.x[:6]
N=1000; k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
x=-2*t*(cx+cy)-4*tp*cx*cy+4*tp
Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl; Zp=0.5*(1+gam*(x-xw)); Zm=1-Zp
G0=-Zp/Ep-Zm/Em
gam_=G0[0,0]
print('G(Gamma,0)=',G0[0,0],' G(M,0)=',G0[N//2,N//2])
print('fraction with sign of G equal to sign at Gamma:',np.mean(np.sign(G0)==np.sign(G0[0,0])))
# Monte Carlo over parameter covariance
rng=np.random.default_rng(0)
fr=[]
for s in rng.multivariate_normal(r.x,cov,size=200):
    t,tp,c,Dl,gam,xw=s[:6]
    x=-2*t*(cx+cy)-4*tp*cx*cy+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl; Zp=0.5*(1+gam*(x-xw)); Zm=1-Zp
    G0=-Zp/Ep-Zm/Em
    fr.append(np.mean(np.sign(G0)==np.sign(G0[0,0])))
print('fraction mean %.4f std %.4f'%(np.mean(fr),np.std(fr)))
