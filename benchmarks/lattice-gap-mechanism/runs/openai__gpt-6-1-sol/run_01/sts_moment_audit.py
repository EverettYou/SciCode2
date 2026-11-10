import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
from pathlib import Path
import numpy as np,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent
OLD=R/'data'
q=json.load(open(OLD/'sts_prior_spectral_fit_results.json'));t,tp=q['normal']['params'][:2];s,V,r=q['half_linear_weights']['params'][:3]
bs=np.load(OLD/'sts_prior_spectral_bootstrap_samples.npz');samples=bs['samples'];names=list(bs['names'])
def scalar(t,tp,s,V,r):
 evar=4*(t*t+tp*tp);eabs=4*(t+tp);q1=s+2*V*r;c=4*s*tp
 vmean=V*V*(1-4*r*r*evar);vmin=V*V*(1-4*r*r*eabs*eabs);vmax=V*V
 local_M1=c;local_M2=c*c+q1*q1*evar+vmean
 return dict(M1_dispersion_coefficient=q1,M1_constant=c,variance_min=vmin,variance_max=vmax,variance_mean=vmean,variance_range=vmax-vmin,relative_variance_range=(vmax-vmin)/vmean,U_apparent_min=2*np.sqrt(vmin),U_apparent_max=2*np.sqrt(vmax),U_from_local_moments_redefined_band=2*np.sqrt(vmean),U_from_local_moments_highT_band=2*np.sqrt(local_M2-c*c-evar),local_M1=local_M1,local_M2=local_M2,eps_second_moment=evar)
a=scalar(t,tp,s,V,r);boot={k:[] for k in a}
for row in samples:
 vals=scalar(*[row[names.index(k)] for k in ['t','tprime','s','V','r']])
 for k,v in vals.items():boot[k].append(v)
summary={k:dict(value=float(v),bootstrap_sd=float(np.std(boot[k],ddof=1)),bootstrap_95=np.percentile(boot[k],[2.5,97.5]).tolist()) for k,v in a.items()}
N=512;k=2*np.pi*np.arange(N)/N;co=np.cos(k);ep=-2*t*(co[:,None]+co[None,:])-4*tp*co[:,None]*co[None,:]
e=s*(ep+4*tp);Em=e-V;Ep=e+V;wm=.5-r*ep;wp=.5+r*ep;M1=wm*Em+wp*Ep;M2=wm*Em**2+wp*Ep**2;C=M2-M1**2
checks={'M0_max_error':float(np.max(np.abs(wm+wp-1))),'M1_analytic_max_error':float(np.max(np.abs(M1-((s+2*V*r)*ep+4*s*tp)))),'central_variance_analytic_max_error':float(np.max(np.abs(C-V*V*(1-4*r*r*ep**2)))),'occupied_weight':float(wm.mean())}
ref='https://arxiv.org/abs/cond-mat/9702188'
out={'purpose':'Audit previous successful half-filled two-pole spectral interpolation against exact one-orbital Hubbard moment identities; this does not test measurements directly.', 'exact_hubbard':{'M0':'1','M1':'epsilon_k + U*n_opposite - mu','M2_minus_M1_squared':'U^2*n_opposite*(1-n_opposite)','half_filling':'n_opposite=1/2, hence variance=U^2/4 independent of k'},'prior_ansatz':{'E_plus_minus':'s*(epsilon_k+4*tprime) +/- V','w_plus_minus':'1/2 +/- r*epsilon_k','M1':'(s+2*V*r)*epsilon_k+4*s*tprime','M2_minus_M1_squared':'V^2*(1-4*r^2*epsilon_k^2)'},'summary':summary,'checks':checks,'conclusion':'The prior exact two-pole interpolation cannot be an exact spectrum of an onsite-U-only one-orbital Hubbard Hamiltonian, even allowing hopping renormalization, because its second central moment varies with momentum. A true Hubbard spectral function can redistribute unmeasured weight/linewidths and need not equal that interpolation, so this is not a rejection of Hubbard physics by STS data.','reference':ref,'broadening_warning':'Moment identities are applied before observational Lorentz broadening. Lorentzians have divergent full second moments; integrating broadened curves over finite windows is not an exact moment test.'}
json.dump(out,open(R/'sts_moment_audit.json','w'),indent=2)
# Path plot.
points=[(0,0),(.5,0),(.5,.5),(0,0)];kp=[]
for p0,p1 in zip(points[:-1],points[1:]):
 for f in np.linspace(0,1,200,endpoint=False):kp.append(np.array(p0)*(1-f)+np.array(p1)*f)
kp=np.array(kp+[[0,0]]);d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(kp,axis=0),axis=1))];cx=np.cos(2*np.pi*kp[:,0]);cy=np.cos(2*np.pi*kp[:,1]);ee=-2*t*(cx+cy)-4*tp*cx*cy;v=V*V*(1-4*r*r*ee**2)
fig,axs=plt.subplots(2,1,figsize=(8.2,6.5),sharex=True)
axs[0].plot(d,(s+2*V*r)*ee+4*s*tp,color='#a92e43',label='Previous two-pole interpolation')
axs[0].plot(d,ee+4*s*tp,'--',color='#174b78',label='Hubbard first moment using high-T band')
axs[0].set_ylabel(r'$M_1(\mathbf{k})/D$');axs[0].legend(frameon=False,fontsize=9)
axs[1].plot(d,v,color='#a92e43',label='Previous two-pole central moment');axs[1].axhline(a['variance_mean'],color='#174b78',ls='--',label=r'Any onsite-$U$ Hubbard: constant $U^2/4$')
axs[1].set_ylabel(r'$[M_2-M_1^2]/D^2$');axs[1].set_xticks(d[[0,200,400,600]],['Γ','X','M','Γ']);axs[1].set_xlabel('Momentum path');axs[1].legend(frameon=False,fontsize=9);axs[1].set_ylim(min(v)-.5,max(v)+.5)
fig.suptitle('Exact Hubbard moment audit of the previous spectral interpolation',fontsize=13);fig.tight_layout();fig.savefig(R/'sts_moment_audit.png',dpi=190)
print(json.dumps(out,indent=2))
