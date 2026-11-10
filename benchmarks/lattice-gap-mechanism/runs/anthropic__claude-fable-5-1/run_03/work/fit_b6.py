from fitlib_fast import *
import numpy as np
s=STS[1]; V=np.array(s['bias']); g=np.array(s['dI_dV'])
t,tp=0.99,0.195
eps=band(t,tp); mu0=mu_for_filling(eps,0.6)
def make_model(D1,mu):
    def model(p,V):
        c,a,b,alpha,beta,sig,bg,sc=p
        xi=eps-mu; Z=0.5*(1+xi/np.sqrt(xi**2+D1**2))
        E=c+a*eps+b*eps**2; xt=alpha+beta*eps
        s_=np.clip(xt/np.maximum(E,1e-6),-1,1); pp=0.5*(1+s_); pm=0.5*(1-s_)
        return sc*sample(dos(E,Z*pp,sig)+dos(-E,Z*pm,sig),V)+bg
    return model
for D1,mu in [(2.45,mu0),(1.5,mu0),(3.5,mu0),(2.45,-1.26)]:
    model=make_model(D1,mu)
    p0=[4.6,0.6,0.0,0.9,0.6,0.15,0.06,3.5]
    r=least_squares(lambda p: model(p,V)-g,p0,x_scale=[0.2,0.05,0.01,0.2,0.05,0.03,0.02,0.3],diff_step=2e-2,
                    bounds=([0,0.1,-0.1,-5,-2,0.03,0,0.1],[10,1.5,0.1,5,2,0.6,0.3,20]))
    rms=np.sqrt(np.mean(r.fun**2)); p=r.x
    J=r.jac; cov=np.linalg.pinv(J.T@J)*np.sum(r.fun**2)/(len(V)-len(p)); err=np.sqrt(np.abs(np.diag(cov)))
    c,a,b,alpha,beta,sig,bg,sc=p
    xi=eps-mu; Z=0.5*(1+xi/np.sqrt(xi**2+D1**2)); E=c+a*eps+b*eps**2; xt=alpha+beta*eps; s_=np.clip(xt/np.maximum(E,1e-6),-1,1)
    print(f"D1={D1} mu={mu:.3f}: rms={rms:.4f}  c={c:.3f}+-{err[0]:.3f} a={a:.3f}+-{err[1]:.3f} b={b:.4f}+-{err[2]:.4f} alpha={alpha:.3f}+-{err[3]:.3f} beta={beta:.3f}+-{err[4]:.3f} sigma={sig:.3f} bg={bg:.3f}")
    print(f"    E(Gamma)={E.min():.2f} E(M)={E.max():.2f} E(vH)={c+a*4*tp+b*(4*tp)**2:.2f}; Z(Gamma)={Z.min():.3f} Z(M)={Z.max():.3f}; <Z>={Z.mean():.3f} lower={np.mean(Z*0.5*(1-s_)):.3f} upper={np.mean(Z*0.5*(1+s_)):.3f}; xt range {xt.min():.2f}..{xt.max():.2f}")
    np.save(f'fit_b6_D{D1}_mu{mu:.2f}.npy',p)
