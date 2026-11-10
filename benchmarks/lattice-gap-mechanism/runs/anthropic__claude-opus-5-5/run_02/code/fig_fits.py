"""Figure 1: STS data with the theory fits; Figure 2: NMR and resistivity with model curves."""
import numpy as np, json, sys
sys.path.insert(0,'/app/code')
from model import *; from style import *; setup()
P=json.load(open(PARAMS_FILE)); F=np.load('/app/code/fitvec.npy',allow_pickle=True).item()
W=Wedge(80)
def mod_d(p,V):
    t,tp,mu,A,a0,b,sig=p
    d=W.gauss(V,W.eps(t,tp)-mu,np.ones_like(W.kx),sig)
    inband=(V>(-4*t-4*tp-mu)-0.3)&(V<(4*t-4*tp-mu)+0.3)
    return A*d+(a0+b*V**2)*(~inband)
def mod_a(p,V):
    t,tp,c,Dl,Uw,A,a0,b,sig=p
    (Ep,Zp),(Em,Zm)=replica_poles(W.eps(t,tp),tp,c,Dl,Uw)
    d=W.gauss(V,Ep,Zp,sig)+W.gauss(V,Em,Zm,sig)
    gap=(V>c-Dl+2*t)&(V<c+Dl-2*t)
    return A*d+(a0+b*V**2)*(~gap)
def mod_c(p,V):
    t,tp,mu,Dl,A,a0,b,sig=p
    (Ep,u2),(Em,v2)=bcs_poles(W.eps(t,tp),mu,Dl)
    d=W.gauss(V,Ep,u2,sig)+W.gauss(V,Em,v2,sig)
    gap=np.abs(V)<abs(Dl)
    return A*d+(a0+b*V**2)*(~gap)
tb,tpb=P['d']['t'],P['d']['tp']
def mod_b(p,V):
    xi,Dk,E,u2,v2,sig=nu03_parts(W.eps(tb,tpb),[p[0]]+list(np.abs(p[1:7])))
    A,a0,b=p[7:]
    d=W.gauss(V,E,u2,sig)+W.gauss(V,-E,v2,sig)
    gap=np.abs(V)<2.6
    return A*d+(a0+b*V**2)*(~gap)
fig,axs=plt.subplots(2,2,figsize=(10,6.6),sharex=True)
panels=[('a','(a) ν = 1/2, low T — paired-liquid replica bands',mod_a,F['pa'],S1),
        ('b','(b) ν ≈ 0.3, low T — strong-coupling s-wave SC (phenomenological)',mod_b,F['pb'],S2),
        ('c','(c) ν ≈ 0.2, low T — BCS, k-independent Δ = 1.96',mod_c,F['pc'],S3),
        ('d','(d) ν ≈ 0.3, high T — bare band t = 1.01, t′ = 0.20',mod_d,F['pd'],S2)]
for ax,(pn,title,mf,p,col) in zip(axs.ravel(),panels):
    V,G=sts(pn)
    ax.plot(V,G,color=MUTED,lw=0.8,label='data')
    ax.plot(V,mf(p,V),color=col,lw=1.8,label='model')
    ax.set_title(title,fontsize=9.5,color=INK,loc='left')
    ax.set_ylim(-0.05,1.15); ax.set_xlim(-10,10)
    ax.legend(loc='upper left',fontsize=8)
for ax in axs[1]: ax.set_xlabel('bias V / D')
for ax in axs[:,0]: ax.set_ylabel('dI/dV (norm.)')
fig.tight_layout(); fig.savefig('/app/fig1_sts_fits.png'); plt.close(fig)

# ---------------- Figure 2 ----------------
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10.5,4.2))
x=np.linspace(0.2,5.2,300)
for f in ['1/2','≈0.3','≈0.2']:
    T,r,er=nmr(f); y=r/T; ey=er/T
    ax1.errorbar(1/T,y,yerr=ey,fmt=MARK[f],ms=4.5,color=CRYSTAL[f],mfc=CRYSTAL[f],mec='white',mew=0.6,elinewidth=0.6,capsize=0,label=('ν = 1/2' if f=='1/2' else 'ν '+f.replace('≈','≈ ')))
Tg=1/x
qa=F['qa']; ax1.plot(x,np.exp(qa[0])*np.exp(-qa[1]*x),color=S1,lw=1.5)
q3=F['qn3']
def pg(T,D0,Ts): return np.where(T<Ts,D0*np.tanh(1.74*np.sqrt(np.clip(Ts/T-1,0,None))),0.0)
ax1.plot(x,np.exp(q3[2])*np.exp(-pg(Tg,q3[0],q3[1])/Tg),color=S2,lw=1.5)
# BCS Hebel-Slichter
def hs(T,D0,Tc,Gam):
    E=np.linspace(-12,12,24001); dE=E[1]-E[0]; vals=[]
    for Ti in np.atleast_1d(T):
        D=D0*np.tanh(1.74*np.sqrt(max(Tc/Ti-1,0))) if Ti<Tc else 0.0
        z=E+1j*Gam; N=np.abs(np.real(z/np.sqrt(z**2-D**2+0j))); M=np.real(D/np.sqrt(z**2-D**2+0j))
        f=1/(np.exp(E/Ti)+1); w=f*(1-f)/Ti; vals.append(np.sum((N**2+M**2)*w)*dE)
    return np.array(vals)
q2=F['qn2']; ax1.plot(x,np.exp(q2[2])*hs(Tg,1.9587,q2[0],abs(q2[1])),color=S3,lw=1.5)
ax1.set_yscale('log'); ax1.set_ylim(1e-5,5); ax1.set_xlim(0,5.2)
ax1.set_xlabel('D / T'); ax1.set_ylabel('1/(T₁T)  (norm. at T = 4D)')
ax1.set_title('NMR 1/(T₁T): activated (½), pseudogap (0.3), BCS Hebel–Slichter (0.2)',fontsize=8.5,loc='left')
ax1.text(0.12,2.5e-3,'Δ_s = 5.54 ± 0.13',color=INK2,fontsize=8); ax1.text(3.6,1.5e-3,'Δ(0)=2.42, T*=2.3',color=INK2,fontsize=8); ax1.text(3.3,0.25,'Δ=1.96 (STS), T_c=1.18',color=INK2,fontsize=8)
ax1.legend(fontsize=8,loc='lower left')
for f in ['1/2','≈0.3','≈0.2']:
    T,r,er=res(f)
    ax2.errorbar(T,np.where(r>0,r,np.nan),yerr=er,fmt=MARK[f],ms=4.5,color=CRYSTAL[f],mec='white',mew=0.6,elinewidth=0.6,label=('ν = 1/2' if f=='1/2' else 'ν '+f.replace('≈','≈ ')))
    z=T[r==0]
    if len(z): ax2.plot(z,np.full_like(z,0.03),MARK[f],ms=4.5,color=CRYSTAL[f],mfc='none')
Tx=np.linspace(0.45,4,200); rr=F['rr']; ax2.plot(Tx,np.exp(rr[0])*np.exp(rr[1]/Tx),color=S1,lw=1.5)
Tx=np.linspace(0.4,4,200); r3=F['rr3']; ax2.plot(Tx,np.exp(r3[0])*np.exp(r3[1]/Tx),color=S2,lw=1.5)
Tx=np.linspace(1.15,4,50); p02=F['p02']; ax2.plot(Tx,np.polyval(p02,Tx),color=S3,lw=1.5)
ax2.set_yscale('log'); ax2.set_ylim(0.02,5e3); ax2.set_xlabel('T / D'); ax2.set_ylabel('ρ (norm. at T = 4D)')
ax2.set_title('ρ: Arrhenius E_a = 3.72 (½), 0.90 (0.3); 0.18(1+T) (0.2); open = ρ = 0',fontsize=8.5,loc='left')
ax2.legend(fontsize=8)
fig.tight_layout(); fig.savefig('/app/fig2_nmr_resistivity.png'); plt.close(fig)
print('done')
