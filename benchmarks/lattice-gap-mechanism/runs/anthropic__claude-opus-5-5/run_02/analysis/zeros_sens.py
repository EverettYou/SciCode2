from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p):
    t,tp,c,Dl,Uw,A,a0,b,sig=p
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    y=e; Zp=0.5*(1+y/np.sqrt(y**2+Uw**2)); Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
p0=[1.0,0.195,0.01,6.0,14.0,3.25,0.03,0.001,0.125]
r=least_squares(lambda p: model(p)-Gs,p0,x_scale='jac')
s2=np.sum(r.fun**2)/(len(Gs)-len(p0)); J=r.jac; cov=np.linalg.pinv(J.T@J)*s2
print('fit',np.round(r.x,4),'err',np.round(np.sqrt(np.diag(cov)),4))
N=600; k=(np.arange(N)+0.5)/N*2*np.pi-np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
def frac(p):
    t,tp,c,Dl,Uw=p[:5]
    e=-2*t*(cx+cy)-4*tp*cx*cy; x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+e/np.sqrt(e**2+Uw**2))
    G0=-Zp/Ep-(1-Zp)/Em
    # Gamma is at index nearest k=0
    i0=np.argmin(abs(k))
    if np.all(np.sign(G0)==np.sign(G0[i0,i0])): return 0.0
    # region connected? just count sign equal to Gamma's sign
    return np.mean(np.sign(G0)==np.sign(G0[i0,i0]))
print('best-fit fraction',frac(r.x))
rng=np.random.default_rng(3)
S=rng.multivariate_normal(r.x,cov,size=400)
F=np.array([frac(s) for s in S])
print('bootstrap: P(loop exists)=%.2f  median frac=%.3f  16-84%%: %.3f-%.3f'%(np.mean(F>0),np.median(F),np.percentile(F,16),np.percentile(F,84)))
for Uw in [12,13,14,15,16,18,20,25,30,50,1e4]:
    p=r.x.copy(); p[4]=Uw
    print('  Uw=%6g  fraction=%.3f'%(Uw,frac(p)))
