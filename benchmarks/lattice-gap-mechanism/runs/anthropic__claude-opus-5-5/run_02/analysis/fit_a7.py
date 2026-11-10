from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('a'); Vs=V[::2]; Gs=G[::2]
def model(p,form):
    t,tp,c,Dl,w,xw,A,a0,b,sig=p
    e=D.eps(t,tp); x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    y=x-xw
    if form=='sqrt': Zp=0.5*(1+y/np.sqrt(y**2+w**2))
    else: Zp=0.5*(1+y/w)
    Zm=1-Zp
    d=D.g(Vs,Ep,Zp,sig)+D.g(Vs,Em,Zm,sig)
    gapmask=(Vs>c-Dl+2*t)&(Vs<c+Dl-2*t)
    return A*d+(a0+b*Vs**2)*(~gapmask)
def zero_fraction(p,form):
    t,tp,c,Dl,w,xw=p[:6]
    N=600; k=(np.arange(N)+0.5)/N*2*np.pi
    cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
    x=-2*t*(cx+cy)-4*tp*cx*cy+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl; y=x-xw
    Zp=0.5*(1+y/np.sqrt(y**2+w**2)) if form=='sqrt' else 0.5*(1+y/w)
    G0=-Zp/Ep-(1-Zp)/Em
    s0=np.sign(G0[0,0])
    return np.mean(np.sign(G0)==s0), G0[0,0], G0[N//2,N//2]
for form in ['sqrt','lin']:
    for xwfix in [None,0.0]:
        p0=[1.0,0.195,0.01,6.0,14.0 if form=='sqrt' else 14.0,0.0,3.25,0.03,0.001,0.125]
        if xwfix is None:
            f=lambda p: model(p,form)-Gs; q0=p0
        else:
            f=lambda p: model(np.insert(p,5,xwfix),form)-Gs; q0=p0[:5]+p0[6:]
        r=least_squares(f,q0,x_scale='jac')
        p=r.x if xwfix is None else np.insert(r.x,5,xwfix)
        s2=np.sum(r.fun**2)/(len(Gs)-len(q0))
        fr,g0,gm=zero_fraction(p,form)
        print(form,'xw',('free' if xwfix is None else xwfix),'chi2/dof %.6f'%s2,'w=%.2f xw=%.3f c=%.3f D=%.3f'%(p[4],p[5],p[2],p[3]),' frac(Gamma side)=%.3f G(Gam)=%.4f G(M)=%.4f'%(fr,g0,gm))
