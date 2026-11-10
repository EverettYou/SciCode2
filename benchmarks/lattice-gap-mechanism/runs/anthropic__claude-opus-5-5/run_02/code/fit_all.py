"""Fit all measured data sets; write params.json and the data/fit figures (fig1, fig2)."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from model import *
from scipy.optimize import least_squares, brentq
W=Wedge(80)
out={}
def fitcov(fun,p0,ndata):
    r=least_squares(fun,p0,x_scale='jac',max_nfev=2000)
    dof=ndata-len(p0); s2=np.sum(r.fun**2)/dof
    cov=np.linalg.pinv(r.jac.T@r.jac)*s2
    return r.x,np.sqrt(np.diag(cov)),s2,cov
noise_var=0.0132**2   # STS noise level measured in the gap / featureless regions (panels a-c)

# ---------- (d) high-T, nu~0.3: bare band ----------
V,G=sts('d'); Vs,Gs=V[::2],G[::2]
def mod_d(p,V=Vs):
    t,tp,mu,A,a0,b,sig=p
    d=W.gauss(V,W.eps(t,tp)-mu,np.ones_like(W.kx),sig)
    inband=(V>(-4*t-4*tp-mu)-0.3)&(V<(4*t-4*tp-mu)+0.3)
    return A*d+(a0+b*V**2)*(~inband)
pd,ed,s2d,_=fitcov(lambda p: mod_d(p)-Gs,[1.0,0.19,-0.9,3.4,0.01,0.001,0.12],len(Gs))
t,tp,mu=pd[:3]
e=eps(*np.meshgrid(np.linspace(-np.pi,np.pi,800,endpoint=False),np.linspace(-np.pi,np.pi,800,endpoint=False)),t,tp)
nu_d=float(np.mean(e<mu))
out['d']=dict(t=pd[0],dt=ed[0],tp=pd[1],dtp=ed[1],mu=pd[2],dmu=ed[2],sigma=pd[6],nu_from_mu=nu_d,chi2dof=s2d)
print('(d)',np.round(pd,4),np.round(ed,4),'nu=',nu_d,'chi2/dof',s2d)

# ---------- (a) half filling: paired-liquid replica bands ----------
V,G=sts('a'); Vs,Gs=V[::2],G[::2]
def mod_a(p,V=Vs):
    t,tp,c,Dl,Uw,A,a0,b,sig=p
    (Ep,Zp),(Em,Zm)=replica_poles(W.eps(t,tp),tp,c,Dl,Uw)
    d=W.gauss(V,Ep,Zp,sig)+W.gauss(V,Em,Zm,sig)
    gap=(V>c-Dl+2*t)&(V<c+Dl-2*t)
    return A*d+(a0+b*V**2)*(~gap)
pa,ea,s2a,cova=fitcov(lambda p: mod_a(p)-Gs,[1.0,0.195,0.01,6.0,14.0,3.25,0.03,0.001,0.125],len(Gs))
out['a']=dict(zip(['t','tp','c','Delta_half_splitting','Uw','A','a0','b','sigma'],pa.tolist()))
out['a_err']=dict(zip(['t','tp','c','Delta_half_splitting','Uw','A','a0','b','sigma'],ea.tolist()))
out['a']['chi2dof']=s2a; out['a_cov']=cova.tolist()
t,tp,c,Dl=pa[:4]
out['a']['lower_band']=[c-Dl-2*t,c-Dl+2*t]; out['a']['upper_band']=[c+Dl-2*t,c+Dl+2*t]
print('(a)',np.round(pa,4),np.round(ea,4),'chi2/dof',s2a)

# ---------- (c) nu~0.2: BCS, k-independent gap ----------
V,G=sts('c'); Vs,Gs=V[::2],G[::2]
def mod_c(p,V=Vs):
    t,tp,mu,Dl,A,a0,b,sig=p
    (Ep,u2),(Em,v2)=bcs_poles(W.eps(t,tp),mu,Dl)
    d=W.gauss(V,Ep,u2,sig)+W.gauss(V,Em,v2,sig)
    gap=np.abs(V)<abs(Dl)
    return A*d+(a0+b*V**2)*(~gap)
pc,ec,s2c,_=fitcov(lambda p: mod_c(p)-Gs,[1.0,0.2,-1.9,1.96,3.0,0.013,0.0012,0.1],len(Gs))
t,tp,mu,Dl=pc[:4]
e=eps(*np.meshgrid(np.linspace(-np.pi,np.pi,800,endpoint=False),np.linspace(-np.pi,np.pi,800,endpoint=False)),t,tp)
xi=e-mu; Ek=np.sqrt(xi**2+Dl**2)
out['c']=dict(zip(['t','tp','mu','Delta','A','a0','b','sigma'],pc.tolist())); out['c_err']=dict(zip(['t','tp','mu','Delta','A','a0','b','sigma'],ec.tolist()))
out['c'].update(chi2dof=s2c,nu_normal=float(np.mean(xi<0)),nu_bcs_fixed_mu=float(np.mean(0.5*(1-xi/Ek))))
# effective BCS coupling reproducing Delta at fixed mu
Ueff=brentq(lambda U: U*np.mean(1/(2*Ek))-1 if False else U*np.mean(1/(2*np.sqrt(xi**2+Dl**2)))-1,1,30)
out['c']['U_eff_BCS']=Ueff
print('(c)',np.round(pc,4),np.round(ec,4),'chi2/dof',s2c,' U_eff(BCS)=',Ueff)

# ---------- (b) nu~0.3: phenomenological strong-coupling SC ----------
V,G=sts('b'); Vs,Gs=V[::2],G[::2]
tb,tpb=out['d']['t'],out['d']['tp']
def mod_b(p,V=Vs):
    q=p[:7]; A,a0,b=p[7:]
    xi,Dk,E,u2,v2,sig=nu03_parts(W.eps(tb,tpb),np.abs(q))
    q=np.array(q); q[0]=p[0]
    xi,Dk,E,u2,v2,sig=nu03_parts(W.eps(tb,tpb),[p[0]]+list(np.abs(p[1:7])))
    d=W.gauss(V,E,u2,sig)+W.gauss(V,-E,v2,sig)
    gap=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gap)
pb,eb,s2b,_=fitcov(lambda p: mod_b(p)-Gs,[-1.03,3.5,5.07,1.52,0.11,0.64,1.09,3.3,0.0,0.002],len(Gs))
names_b=['mu','Delta_FS','Delta_inf','w','s0','s1','ws','A','a0','b']
out['b']=dict(zip(names_b,pb.tolist())); out['b_err']=dict(zip(names_b,eb.tolist())); out['b']['chi2dof']=s2b
print('(b)',np.round(pb,3),np.round(eb,3),'chi2/dof',s2b)
out['noise_var']=noise_var

# ---------- NMR ----------
def act_fit(T,y,ey):
    r=least_squares(lambda q:(np.exp(q[0])*np.exp(-q[1]/T)-y)/ey,[0,5]); J=r.jac
    cov=np.linalg.pinv(J.T@J); return r.x,np.sqrt(np.diag(cov)),np.sum(r.fun**2)
T,r,er=nmr('1/2'); qa,eqa,c2=act_fit(T,r/T,er/T)
out['nmr_half']=dict(Delta=qa[1],dDelta=eqa[1],chi2=c2,N=len(T))
# nu=0.3: pseudogap Delta(T)=D0*tanh(1.74*sqrt(T*/T-1)), 1/T1T = exp(-Delta(T)/T)
T,r,er=nmr('≈0.3')
def pg(T,D0,Ts):
    Dt=np.where(T<Ts,D0*np.tanh(1.74*np.sqrt(np.clip(Ts/T-1,0,None))),0.0); return Dt
def mod_n3(q,T): return np.exp(q[2])*np.exp(-pg(T,q[0],q[1])/T)
r3=least_squares(lambda q:(mod_n3(q,T)-r/T)/(er/T),[2.6,3.0,0.0]); cov=np.linalg.pinv(r3.jac.T@r3.jac)
out['nmr_03']=dict(Delta0=r3.x[0],dDelta0=np.sqrt(cov[0,0]),Tstar=r3.x[1],dTstar=np.sqrt(cov[1,1]),chi2=float(np.sum(r3.fun**2)),N=len(T))
# nu=0.2: BCS Hebel-Slichter with Dynes broadening, Delta0 from STS, Tc from resistivity
def hs(T,D0,Tc,Gam):
    E=np.linspace(-12,12,24001); dE=E[1]-E[0]
    vals=[]
    for Ti in np.atleast_1d(T):
        D=D0*np.tanh(1.74*np.sqrt(max(Tc/Ti-1,0))) if Ti<Tc else 0.0
        z=E+1j*Gam
        N=np.real(z/np.sqrt(z**2-D**2+0j)); N=np.abs(N)
        M=np.real(D/np.sqrt(z**2-D**2+0j))
        f=1/(np.exp(E/Ti)+1); w=f*(1-f)/Ti
        vals.append(np.sum((N**2+M**2)*w)*dE)
    return np.array(vals)
T,r,er=nmr('≈0.2')
def mod_n2(q,T): return np.exp(q[2])*hs(T,1.9587,q[0],abs(q[1]))
r2=least_squares(lambda q:(mod_n2(q,T)-r/T)/(er/T),[1.1,0.15,0.0]); cov=np.linalg.pinv(r2.jac.T@r2.jac)
out['nmr_02']=dict(Tc=r2.x[0],dTc=np.sqrt(cov[0,0]),Dynes=abs(r2.x[1]),dDynes=np.sqrt(cov[1,1]),chi2=float(np.sum(r2.fun**2)),N=len(T))
print('NMR',out['nmr_half'],out['nmr_03'],out['nmr_02'])

# ---------- resistivity ----------
T,r,er=res('1/2'); q,eq,c2=act_fit(1/T,1/r,er/r**2)  # placeholder (not used)
rr=least_squares(lambda q:(np.exp(q[0])*np.exp(q[1]/T)-r)/er,[0,4]); cov=np.linalg.pinv(rr.jac.T@rr.jac)
out['rho_half']=dict(Ea=rr.x[1],dEa=np.sqrt(cov[1,1]),chi2=float(np.sum(rr.fun**2)),N=len(T))
T,r,er=res('≈0.3'); m=r>0
rr3=least_squares(lambda q:(np.exp(q[0])*np.exp(q[1]/T[m])-r[m])/er[m],[0,1]); cov=np.linalg.pinv(rr3.jac.T@rr3.jac)
out['rho_03']=dict(Ea=rr3.x[1],dEa=np.sqrt(cov[1,1]),Tc_bracket=[float(T[~m].max()),float(T[m].min())])
T,r,er=res('≈0.2'); m=r>0
p=np.polyfit(T[m],r[m],1,w=1/er[m]); out['rho_02']=dict(a=p[1],b=p[0],Tc_bracket=[float(T[~m].max()),float(T[m].min())])
print('rho',out['rho_half'],out['rho_03'],out['rho_02'])
json.dump(out,open(PARAMS_FILE,'w'),indent=1,default=float)
np.save('/app/code/fitvec.npy',dict(pd=pd,pa=pa,pc=pc,pb=pb,qn3=r3.x,qn2=r2.x,qa=qa,rr=rr.x,rr3=rr3.x,p02=p),allow_pickle=True)
