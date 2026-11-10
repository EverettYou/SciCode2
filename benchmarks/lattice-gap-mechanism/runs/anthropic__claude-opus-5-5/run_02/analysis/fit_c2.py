from fastdos import *
from scipy.optimize import least_squares
D=DOS(90)
V,G=sts('c'); Vs=V[::2]; Gs=G[::2]
def model(p,form):
    if form=='const':
        t,tp,mu,D0,A,a0,b,sig=p; Dk=D0*np.ones_like(D.CX)
    elif form=='ext':
        t,tp,mu,D1,A,a0,b,sig=p; Dk=D1*(D.CX+D.CY)/2
    elif form=='mix':
        t,tp,mu,D0,D1,A,a0,b,sig=p; Dk=D0+D1*(D.CX+D.CY)/2
    xi=D.eps(t,tp)-mu; E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=1-u2
    d=D.g(Vs,E,u2,sig)+D.g(Vs,-E,v2,sig)
    Emin=E.min()
    gapmask=np.abs(Vs)<Emin
    return A*d+(a0+b*Vs**2)*(~gapmask)
for form,p0 in [('const',[1.0,0.2,-1.9,1.96,3.0,0.013,0.0012,0.1]),('ext',[1.0,0.2,-1.9,2.0,3.0,0.013,0.0012,0.1]),('mix',[1.0,0.2,-1.9,1.96,0.0,3.0,0.013,0.0012,0.1])]:
    r=least_squares(lambda p: model(p,form)-Gs,p0,x_scale='jac')
    s2=np.sum(r.fun**2)/(len(Gs)-len(p0))
    J=r.jac; cov=np.linalg.pinv(J.T@J)*s2
    print(form,'chi2/dof %.6f'%s2,np.round(r.x,4),np.round(np.sqrt(np.diag(cov)),4))
