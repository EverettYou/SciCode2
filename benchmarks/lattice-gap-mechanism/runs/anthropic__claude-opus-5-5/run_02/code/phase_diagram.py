"""Semi-quantitative phase diagram of the attractive t-t'-U Hubbard model (with the doping-screened
attraction U_eff(nu) inferred from the three crystals).
  T*(nu): pair-formation crossover = BCS mean-field pairing temperature, crossing over to the
          local-pair dissociation scale |U|/(2 ln 3) at strong coupling.
  Tc(nu): min(T*, T_theta);  T_theta = A * D_s(nu) * S(m): phase-coherence scale from the
          BCS-Leggett (T=0, self-consistent mu) superfluid stiffness D_s, times the SO(4)
          suppression factor S(m)=8/ln(C/delta_eff), delta_eff = delta0 + (m/m_c)^2, m=|nu-1/2|,
          delta0 = J'/J = (t'/t)^2 (t'-induced easy-plane anisotropy at half filling).
          A and m_c are calibrated on Tc(nu=0.3)=0.36 and Tc(1/2)=T_KT^strong-coupling."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from scipy.optimize import brentq
from style import *; setup()
P=json.load(open('/app/code/params.json'))
t,tp=1.0,0.197
N=220; k=(np.arange(N)+0.5)/N*2*np.pi
cx=np.cos(k)[:,None]; cy=np.cos(k)[None,:]
e=(-2*t*(cx+cy)-4*tp*cx*cy).ravel(); d2=(2*t*cx+4*tp*cx*cy).ravel()   # d^2 eps/dkx^2
es=np.sort(e)
U0,kap=12.0,22.1
def Ueff(nu): return U0-kap*(np.sqrt((nu-0.5)**2+0.03**2)-0.03)
def mu0(nu): return es[int(nu*len(es))]
def bcs_T0(U,mu):
    f=lambda D: U*np.mean(1/(2*np.sqrt((e-mu)**2+D**2)))-1
    return brentq(f,1e-6,80) if f(1e-6)>0 else 0.0
def bcs_Tc(U,mu):
    def f(T):
        x=(e-mu); x=np.where(np.abs(x)<1e-9,1e-9,x)
        return U*np.mean(np.tanh(x/(2*T))/(2*x))-1
    return brentq(f,1e-3,40) if f(1e-3)>0 else 0.0
def leggett(U,nu):
    """T=0 BCS-Leggett with self-consistent mu; returns Delta, mu, D_s"""
    def gap(mu):
        f=lambda D: U*np.mean(1/(2*np.sqrt((e-mu)**2+D**2)))-1
        return brentq(f,1e-8,80) if f(1e-8)>0 else 1e-8
    def ne(mu):
        D=gap(mu); x=e-mu; return np.mean(1-x/np.sqrt(x**2+D**2))-2*nu
    mu=brentq(ne,-30,30); D=gap(mu); x=e-mu; nk=1-x/np.sqrt(x**2+D**2)
    Ds=np.mean(d2*nk)/4.0
    return D,mu,Ds
nus=np.linspace(0.03,0.97,95)
rows=[]
for nu in nus:
    U=Ueff(nu); m=mu0(nu)
    D0=bcs_T0(U,m); Tmf=bcs_Tc(U,m)
    Tloc=U/(2*np.log(3)); w=np.clip((U-6)/6,0,1)**2
    Ts=Tmf+(Tloc-Tmf)*w
    Dl,mul,Ds=leggett(U,nu)
    rows.append([nu,U,D0,Tmf,Ts,Ds])
rows=np.array(rows)
delta0=(tp/t)**2
J0=4*t**2/U0; TKT_half=0.24*J0          # S=1/2 easy-plane XXZ with delta0~(t'/t)^2 (Cuccoli et al. 2003)
W=8.0*t
c_bec,q_x,m_s=0.45,6.0,0.05
def S(mm,S0): return (S0+mm/m_s)/(1+mm/m_s)
def Tcoh(nu,S0):
    U=Ueff(nu); J=4*t**2/U; nb=nu if nu<=0.5 else 1-nu
    return c_bec*J*4*nb*(1-nb)*(1+(W/U)**q_x)*S(abs(nu-0.5),S0)
S0=TKT_half/Tcoh(0.5,1.0)
i_half=np.argmin(abs(rows[:,0]-0.5))
Tth=np.array([Tcoh(nu,S0) for nu in rows[:,0]])
Tc=np.minimum(rows[:,4],Tth)
A=c_bec; mc=m_s
out=dict(U0=U0,kappa=kap,c_bec=c_bec,q_x=q_x,m_s=m_s,S0=S0,delta0=delta0,TKT_half=TKT_half,
         table=[dict(nu=float(r[0]),Ueff=float(r[1]),Delta0=float(r[2]),T_MF=float(r[3]),T_star=float(r[4]),D_s=float(r[5]),T_theta=float(th),Tc=float(tc)) for r,th,tc in zip(rows,Tth,Tc)])
json.dump(out,open('/app/code/phase_diagram.json','w'),indent=1)
for nu in [0.2,0.3,0.5,0.7,0.8]:
    j=np.argmin(abs(rows[:,0]-nu)); print('nu=%.2f Ueff=%.2f Delta0=%.2f Tmf=%.2f T*=%.2f Ds=%.3f Ttheta=%.2f Tc=%.2f'%(rows[j,0],rows[j,1],rows[j,2],rows[j,3],rows[j,4],rows[j,5],Tth[j],Tc[j]))
print('S0=',S0,'TKT_half=',TKT_half)
# ------------- plot -------------
fig,ax=plt.subplots(figsize=(8.6,5.2))
x=rows[:,0]
ax.fill_between(x,0,Tc,color='#cde2fb',lw=0)
ax.fill_between(x,Tc,rows[:,4],color='#fbe0d3',lw=0)
ax.plot(x,rows[:,4],color=S2,lw=2,label='T*: pair formation / pseudogap crossover')
ax.plot(x,Tc,color=S1,lw=2,label='T_c: superconducting (phase-coherence) transition')
ax.plot([0.5,0.5],[TKT_half,rows[i_half,4]],color=INK,lw=3,solid_capstyle='butt')
ax.text(0.505,2.7,'insulating liquid of\npreformed local pairs\n(ν = ½ exactly; CDW and\nSC nearly degenerate)',fontsize=8,color=INK,va='center')
ax.text(0.15,0.25,'s-wave SC',fontsize=10,color='#184f95'); ax.text(0.72,0.35,'s-wave SC',fontsize=10,color='#184f95')
ax.text(0.33,1.6,'pseudogap metal\n(preformed pairs)',fontsize=9,color='#9a3412',ha='center')
ax.text(0.22,4.2,'normal metal (unpaired electrons)',fontsize=9,color=INK2)
for nu,lab,c in [(0.5,'ν = ½',S1),(0.3,'ν ≈ 0.3',S2),(0.2,'ν ≈ 0.2',S3)]:
    ax.axvline(nu,color=c,lw=1.2,ls='-',alpha=0.9); ax.text(nu+0.004,6.55,lab,color=INK,fontsize=8.5,rotation=90,va='top')
# measured points
ax.errorbar([0.3,0.2],[0.36,1.11],yerr=[[0.04,0.04],[0.04,0.07]],fmt='D',color=INK,ms=6,capsize=2,label='measured T_c (ρ = 0)')
ax.errorbar([0.3],[2.27],yerr=[0.16],fmt='s',color=INK,mfc='white',ms=6,capsize=2,label='measured T* (NMR pseudogap fit)')
ax.annotate('',xy=(0.5,6.2),xytext=(0.5,4.45),arrowprops=dict(arrowstyle='->',color=INK2,lw=1))
ax.text(0.39,4.6,'ν=½: gap still\nopen at T = 4.4',fontsize=7.5,color=INK2)
ax.plot([0.5],[TKT_half],'o',color=INK,ms=5); ax.annotate('T_KT(½) ≈ 0.08 (predicted)',xy=(0.5,TKT_half),xytext=(0.56,0.62),fontsize=7.5,color=INK2,arrowprops=dict(arrowstyle='-',color=INK2,lw=0.7))
ax.text(0.005,0.06,'band\ninsulator',fontsize=6.5,color=INK2); ax.text(0.94,0.06,'band\ninsulator',fontsize=6.5,color=INK2)
ax.set_xlim(0,1); ax.set_ylim(0,6.6); ax.set_xlabel('filling fraction ν (ν = 1: two electrons per site)'); ax.set_ylabel('temperature T / D')
ax.set_title('Phase diagram of the attractive t–t′–U model (U_eff screened away from ν = ½); band insulators at ν = 0, 1',fontsize=8.5,loc='left')
ax.legend(fontsize=7.5,loc='upper right')
fig.tight_layout(); fig.savefig('/app/fig4_phase_diagram.png'); plt.close(fig)
