from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,wmode):
    t,tp,c,Dl,Uw,A,a0,b,sig=p
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    if wmode=='NN': y=-2*t*(D.CX+D.CY)
    elif wmode=='eps': y=e
    Zp=0.5*(1+y/np.sqrt(y**2+Uw**2)); Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
def zero_frac(p,wmode,N=800):
    t,tp,c,Dl,Uw=p[:5]
    k=(np.arange(N)+0.5)/N*2*np.pi
    cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
    e=-2*t*(cx+cy)-4*tp*cx*cy; x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    y=-2*t*(cx+cy) if wmode=='NN' else e
    Zp=0.5*(1+y/np.sqrt(y**2+Uw**2))
    G0=-Zp/Ep-(1-Zp)/Em
    return np.mean(np.sign(G0)==np.sign(G0[0,0])),G0[0,0],G0[N//2,N//2],G0.min(),G0.max()
for wmode in ['NN','eps']:
    p0=[1.0,0.195,0.01,6.0,13.0,3.25,0.03,0.001,0.125]
    r=least_squares(lambda p: model(p,wmode)-Gs,p0,x_scale='jac')
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    J=r.jac; cov=np.linalg.pinv(J.T@J)*s2
    print(wmode,'chi2/dof=%.6f'%s2,np.round(r.x[:5],4),'+-',np.round(np.sqrt(np.diag(cov))[:5],4))
    print('   zero analysis: frac(Gamma side), G(Gam), G(M), Gmin, Gmax =',np.round(zero_frac(r.x,wmode),4))
