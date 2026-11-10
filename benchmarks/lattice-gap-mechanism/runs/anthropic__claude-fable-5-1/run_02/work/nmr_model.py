import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar
from models import spectrum_half, spectrum_03, spectrum_02, T_HOP, TP_HOP
from vizstyle import *
import matplotlib.pyplot as plt
setup()
d = json.load(open('/app/measurements.json'))
nmr = {s['filling']:(np.array(s['temperature']),np.array(s['one_over_T1']),np.array(s['uncertainty'])) for s in d['measurements'][1]['samples']}
nk = 300; kx, ky = kgrid(nk); sh = nk//2
def dfdw(w,T): x=np.clip(w/(2*T),-300,300); return 1/(4*T*np.cosh(x)**2)
def gauss(x,s): return np.exp(-x**2/(2*s**2))/(np.sqrt(2*np.pi)*s)
grid = np.arange(-12,12.001,0.02)
def hist(E,W,sigma):
    dE=grid[1]-grid[0]; edges=np.concatenate([grid-dE/2,[grid[-1]+dE/2]])
    h,_=np.histogram(E.ravel(),bins=edges,weights=np.broadcast_to(W,E.shape).ravel()); h=h/E.size/dE
    n=int(5*sigma/dE)+1; x=np.arange(-n,n+1)*dE; g=np.exp(-x**2/(2*sigma**2)); g/=g.sum(); return np.convolve(h,g,mode='same')
Tfine = np.concatenate([np.linspace(0.2,1.0,41), np.linspace(1.05,10,60)])
# ---------- nu = 1/2 : Q=(pi,pi)-dominated relaxation and local bubble
bands = spectrum_half(kx,ky,'free'); sig=0.1
def rate_Q(T):
    tot=0.0
    for E,Z in bands:
        EQ=np.roll(np.roll(E,sh,0),sh,1); ZQ=np.roll(np.roll(Z,sh,0),sh,1)
        tot+=np.sum(Z*ZQ*gauss(E-EQ,sig)*dfdw(E,T))
    return tot
N_half = sum(hist(E,Z,0.084) for E,Z in bands)
def rate_loc(T, N): return np.trapezoid(dfdw(grid,T)*N**2, grid)
RQ = np.array([rate_Q(T) for T in Tfine]); Rloc = np.array([rate_loc(T,N_half) for T in Tfine])
i4 = np.argmin(np.abs(Tfine-4)); RQ/=RQ[i4]; Rloc/=Rloc[i4]
# ---------- nu ~ 0.3 : pair insulator: relaxation by thermally excited unpaired fermions, 1/(T1T)/Korringa = C exp(-Delta_pb(T)/T), Delta_pb(0)=2.5 (STS gap edge)
from scipy.optimize import minimize
T3,r3,u3 = nmr['≈0.3']; d3 = r3/T3; i43=np.argmin(np.abs(T3-4)); d3n=d3/d3[i43]; u3n=u3/T3/d3[i43]
Dedge = 2.5
def R03_model(T, C, Tstar):
    T = np.atleast_1d(T); f = np.where(T<Tstar, np.tanh(1.74*np.sqrt(np.clip(Tstar/T-1,0,None))), 0.0)
    return np.minimum(1.0, C*np.exp(-Dedge*f/T))
def cost3(par):
    C,Ts = par
    if C<=0 or Ts<1.5: return 1e9
    m = d3n>2*u3n
    return np.sum(((np.log(R03_model(T3[m],C,Ts))-np.log(d3n[m]))/(u3n[m]/d3n[m]))**2)
res3 = minimize(cost3,[1.7,2.9],method='Nelder-Mead'); C3,Tstar = res3.x
print(f"nu~0.3 NMR fit: C={C3:.2f}, T*={Tstar:.2f}, chi2={res3.fun:.1f} over {np.sum(d3n>2*u3n)} points")
R03 = R03_model(Tfine, C3, Tstar)
# ---------- nu ~ 0.2 : BCS with coherence factors (case II), Tc = 1.1, Delta0 = 1.96
Tc=1.1; D0=1.9594; eb = ebar(kx,ky,T_HOP,TP_HOP); xi = eb-(-1.1004); sigc=0.111
def R02(T):
    D = D0*np.tanh(1.74*np.sqrt(max(Tc/T-1,0))) if T<Tc else 0.0
    E = np.sqrt(xi**2+D**2); u2=0.5*(1+xi/E); v2=0.5*(1-xi/E); uv=0.5*D/E
    nu2=hist(E,u2,sigc); nv2=hist(E,v2,sigc); nuv=hist(E,uv,sigc)
    Phi = nu2**2+nv2**2+2*nuv**2
    En = np.abs(xi); nu2n=hist(En,0.5*(1+np.sign(xi)),sigc); nv2n=hist(En,0.5*(1-np.sign(xi)),sigc); Phin=nu2n**2+nv2n**2
    return np.trapezoid(dfdw(grid,T)*Phi,grid)/np.trapezoid(dfdw(grid,T)*Phin,grid)
R02v = np.array([R02(T) for T in Tfine])
np.savez('/app/work/nmr_curves.npz', Tfine=Tfine, RQ=RQ, Rloc=Rloc, R03=R03, R02=R02v)
# slopes
def slope(T,R,a,b):
    ia=np.argmin(np.abs(1/T-a)); ib=np.argmin(np.abs(1/T-b)); return (np.log(R[ia])-np.log(R[ib]))/(1/T[ib]-1/T[ia])
for name,R in [('half Q',RQ),('half local',Rloc),('0.3',R03),('0.2',R02v)]:
    print(name, "model slopes: 1/T 0.5-1:", round(slope(Tfine,R,0.5,1.0),2), " 1-2:", round(slope(Tfine,R,1.0,2.0),2), " 2-4:", round(slope(Tfine,R,2.0,4.0),2))
for key,(T,r,u) in nmr.items():
    data=r/T; i=np.argmin(np.abs(T-4)); data=data/data[i]; ud=u/T/ (r[i]/T[i])
    m = data>2*ud
    print(key, "data slopes: 1/T 0.5-1:", round(slope(T[m],data[m],0.5,1.0),2), " 1-2:", round(slope(T[m],data[m],1.0,2.0),2) if (1/T[m]).max()>2 else None)
# figure
fig, ax = plt.subplots(figsize=(8,6))
for key,col,R,lab in [('1/2',C['half'],RQ,'theory: Mott insulator, $(\\pi,\\pi)$-dominated'),('≈0.3',C['03'],R03,f'theory: pair insulator, $C e^{{-\\Delta_{{pb}}(T)/T}}$, $\\Delta_{{pb}}$=2.5$D$, $T^*$={Tstar:.1f}$D$'),('≈0.2',C['02'],R02v,'theory: BCS, $T_c=1.1D$, Hebel–Slichter')]:
    T,r,u = nmr[key]; data=r/T; i=np.argmin(np.abs(T-4)); norm=data[i]; data=data/norm; ud=u/T/norm
    ax.errorbar(1/T, data, yerr=ud, fmt='o', ms=4, color=col, mfc='white', mew=1.2, elinewidth=0.8, capsize=0, label=f'data {LABEL[{"1/2":"half","≈0.3":"03","≈0.2":"02"}[key]]}')
    ax.plot(1/Tfine, R, color=col, lw=2, label=lab)
ax.plot(1/Tfine, Rloc, color=C['half'], lw=1.2, ls=':', label='theory: Mott insulator, local (q-summed) bubble')
ax.set_yscale('log'); ax.set_ylim(1e-5,5); ax.set_xlim(0,5.2); ax.set_xlabel('$D/T$'); ax.set_ylabel('$1/(T_1T)$ normalised at $T=4D$')
ax.legend(fontsize=8, loc='lower left'); ax.set_title('Spin–lattice relaxation: data (points) and effective theory (lines)', loc='left', fontsize=11)
plt.savefig('/app/figures/fig_nmr.png', dpi=150, bbox_inches='tight'); print("nmr figure done")
