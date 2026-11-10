import numpy as np,json
from scipy.optimize import least_squares,brentq
from scipy.special import expit
from pathlib import Path
R=Path(__file__).resolve().parent;q=json.load(open(R/'sts_pairing_diagnostics.json'));tn,tpn=q['fixed_normal_band']
N=240;k=2*np.pi*(np.arange(N)+.5)/N;u=np.cos(k)[:,None];v=np.cos(k)[None,:];d=u-v;xy2=(1-u*u)*(1-v*v)
results={}
for typ in ['d+id','s+id']:
 fit=q['fits'][typ+'_offset'];s=fit['params'][0];gs=np.array([fit['g1_if_selfconsistent_separable_attraction'],fit['g2_if_selfconsistent_separable_attraction']]);eps=-2*s*tn*(u+v)-4*s*tpn*u*v
 phisq=np.array([d*d,xy2]) if typ=='d+id' else np.array([np.ones_like(eps),d*d])
 per={}
 for nu in [.3,.2]:
  states=[]
  for active in [[0],[1],[0,1]]:
   def evals(p):
    c=p[0];Ds=np.zeros(2);Ds[active]=np.exp(p[1:]);xi=eps+c;E=np.sqrt(xi*xi+np.sum(Ds[:,None,None]**2*phisq,axis=0));density=np.mean(.5*(1-xi/E));K=np.mean(phisq/(2*E),axis=(1,2));F=np.sum(Ds*Ds/gs)+np.mean(xi-E)-2*c*nu
    return density,K,F,Ds,E
   def fun(p):
    density,K,*_=evals(p);return np.r_[density-nu,gs[active]*K[active]-1]
   p0=np.r_[2.,np.log([3.]*len(active))];rr=least_squares(fun,p0,bounds=(np.r_[-30.,[-10.]*len(active)],np.r_[30.,[3.5]*len(active)]),xtol=1e-11,ftol=1e-11,gtol=1e-11,max_nfev=150)
   density,K,F,Ds,E=evals(rr.x)
   states.append({'active_channels':active,'c_minus_mu':float(rr.x[0]),'Delta':Ds.tolist(),'density':float(density),'free_energy_per_site':float(F),'minimum_excitation':float(E.min()),'maximum_excitation':float(E.max()),'gap_equation_residual_norm':float(np.linalg.norm(rr.fun)),'inactive_channel_susceptibility_gK':(gs*K).tolist()})
  good=[s0 for s0 in states if s0['gap_equation_residual_norm']<1e-6]
  best=min(good,key=lambda z:z['free_energy_per_site']) if good else None
  def c_at_T(T):return brentq(lambda c:np.mean(expit(-(eps+c)/T))-nu,-100,100)
  def response(T,ch):
   c=c_at_T(T);xi=eps+c;fac=np.divide(np.tanh(xi/(2*T)),2*xi,out=np.full_like(xi,1/(4*T)),where=abs(xi)>1e-12);return gs[ch]*np.mean(phisq[ch]*fac)-1
  Tcs=[]
  for ch in [0,1]:
   lo=.01;hi=30.;f0=response(lo,ch);f1=response(hi,ch)
   tc=brentq(lambda T:response(T,ch),lo,hi) if f0*f1<0 else None
   Tcs.append(tc)
  per[str(nu)]={'stationary_states':states,'minimum_free_energy_within_trial_family':best,'normal_state_mean_field_Tc_by_channel':Tcs,'leading_mean_field_Tc':max(a for a in Tcs if a is not None)}
 results[typ]={'hopping_t':s*tn,'hopping_tprime':s*tpn,'couplings_g':gs.tolist(),'basis':'[coskx-cosky,sinkx*sinky]' if typ=='d+id' else '[1,coskx-cosky]','fillings':per}
out={'Hamiltonian':'H=sum_kσ (epsilon_k-mu)c†kσ ckσ - sum_α(gα/N) B†α Bα; Bα=sum_k φα(k)c_-k,down c_k,up. Only physical one-orbital c fermions. Pair interactions are infinite-range reduced-BCS interactions.','approximation':'Uniform BCS saddle, zero-T number and gap equations on240x240 grid; compare pure and mixed relative-phase pi/2 states, no claim of global minimum over all orders. Tc is normal-state linearized mean-field instability, not 2D BKT Tc.','important_limitation':'Couplings inferred from poor ν≈.3 unconstrained spectral fits at density≈.42. These checks test consequences; they do not constitute fitted common microscopic Hamiltonian. Hopping scale inherited from each fit differs from high-T reference band.','results':results}
json.dump(out,open(R/'sts_pairing_selfconsistency.json','w'),indent=2)
for typ,a in results.items():
 print(typ,'g',a['couplings_g'])
 for n,b in a['fillings'].items():print(n,'TcMF',b['leading_mean_field_Tc'],'best',b['minimum_free_energy_within_trial_family'])
