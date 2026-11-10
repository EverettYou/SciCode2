from smoothfit import *
from scipy.optimize import least_squares
V,G=sts('c')
Vs=V[::2]; Gs=G[::2]
def model_bcs(p,V=Vs,ret=False):
    t,tp,mu,Dl,A,a,sig,wscale=p
    xi=eps(t,tp)-mu
    E=np.sqrt(xi**2+Dl**2)
    u2=0.5*(1+xi/E); v2=0.5*(1-xi/E)
    d=gdos(V,E,u2,sig)+gdos(V,-E,v2,sig)
    out=A*d+a*np.abs(V)*(d<0.01*d.max())
    return out
p0=[1.0,0.19,-2.0,1.9,3.0,0.012,0.08,1.0]
r=least_squares(lambda p: model_bcs(p)-Gs,p0,x_scale='jac')
J=r.jac; dof=len(Gs)-len(p0); s2=np.sum(r.fun**2)/dof
cov=np.linalg.pinv(J.T@J)*s2
print('BCS const gap chi2/dof',s2)
for n,v,e in zip(['t','tp','mu','Delta','A','bg','sig','-'],r.x,np.sqrt(np.diag(cov))): print('  %s %.4f +- %.4f'%(n,v,e))
t,tp,mu,Dl=r.x[:4]
xi=eps(t,tp)-mu; E=np.sqrt(xi**2+Dl**2)
print('normal-state filling at this mu:',np.sum(WK*(xi<0)))
print('BCS filling sum v2:',np.sum(WK*0.5*(1-xi/E)))
print('band bottom/top rel mu:',xi.min(),xi.max())
np.save('/app/analysis/fit_c.npy',r.x)
