import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/sts-mpl-cache')
from pathlib import Path
import json,hashlib
import numpy as np
from scipy.integrate import quad
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Patch
from matplotlib.lines import Line2D
R=Path(__file__).resolve().parent;source=R/'data/measurements.json';dat=json.load(open(source))['measurements'];old=json.load(open(R/'data/sts_empirical_response_fits.json'))
sts,nmr,rho=dat[0]['spectra'],dat[1]['samples'],dat[2]['samples']
colors=['#b63547','#24816b','#285ba7'];nus=[.5,.3,.2];labels=[r'$\nu=1/2$',r'$\nu\simeq0.3$',r'$\nu\simeq0.2$']
plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'legend.fontsize':8.5,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white','pdf.fonttype':42,'ps.fonttype':42})
def save(fig,name):
 fig.savefig(R/(name+'.png'),dpi=220,bbox_inches='tight');fig.savefig(R/(name+'.pdf'),bbox_inches='tight');plt.close(fig)
def slimfit(f):
 return {k:f[k] for k in ['activation_D','activation_se_D','activation_bootstrap_95_D','temperature_range_D','n','chi_square','degrees_of_freedom','power_q'] if k in f}
validation=[];samples=[]
for i,nu in enumerate(nus):
 nf=old['nmr'][i]['fixed_prefactor_fit'];T=np.array(nmr[i]['temperature']);y=np.array(nmr[i]['one_over_T1']);sig=np.array(nmr[i]['uncertainty']);lo,hi=nf['temperature_range_D'];mask=(T>=lo-1e-9)&(T<=hi+1e-9);pred=nf['A']*T*np.exp(-nf['activation_D']/T);chi=float(np.sum(((pred[mask]-y[mask])/sig[mask])**2));validation.append({'experiment':'NMR','nu':nu,'recomputed_chi2':chi,'recorded_chi2':nf['chi_square'],'abs_difference':abs(chi-nf['chi_square'])})
 rt=np.array(rho[i]['temperature']);ry=np.array(rho[i]['resistivity']);rs=np.array(rho[i]['uncertainty']);zeros=rt[ry==0];bracket=None
 if len(zeros):bracket=[float(max(zeros)),float(min(rt[(ry>0)&(rt>max(zeros))]))]
 row={'nu_nominal':nu,'nmr_activation_empirical':slimfit(nf),'nmr_power_prefactor_sensitivity':slimfit(old['nmr'][i]['free_prefactor_fit']),'rho_measured_T_range_D':[float(rt.min()),float(rt.max())],'zero_resistance_measured_T_range_D':[float(zeros.min()),float(zeros.max())] if len(zeros) else None,'zero_resistance_onset_bracket_D':bracket}
 if i<2:
  rf=old['resistivity'][i]['fixed_prefactor_fit'];mask=ry>0;pred=rf['A']*np.exp(rf['activation_D']/rt);chi=float(np.sum(((pred[mask]-ry[mask])/rs[mask])**2));validation.append({'experiment':'rho','nu':nu,'recomputed_chi2':chi,'recorded_chi2':rf['chi_square'],'abs_difference':abs(chi-rf['chi_square'])});row['rho_activation_empirical']=slimfit(rf);row['rho_prefactor_sensitivity']=slimfit(old['resistivity'][i]['free_prefactor_fit'])
 else:
  rf=old['resistivity'][i]['linear_positive_branch_fit'];row['rho_linear_positive_branch']=rf;mask=ry>0;chi=float(np.sum(((rf['intercept']+rf['slope_per_D']*rt[mask]-ry[mask])/rs[mask])**2));validation.append({'experiment':'rho_linear','nu':nu,'recomputed_chi2':chi,'recorded_chi2':rf['chi_square'],'abs_difference':abs(chi-rf['chi_square'])})
 samples.append(row)
assert max(q['abs_difference'] for q in validation)<1e-9
# Phase-constraint map.
fig,ax=plt.subplots(figsize=(9.5,5.7));ax.set_xlim(0,1);ax.set_ylim(0,4.5);ax.set_facecolor('#f4f5f6')
for nu in [.2,.3,.5]:ax.axvline(nu,color='#a9adb3',lw=.8,ls=(0,(3,3)),zorder=1)
zero='#245fa5';activated='#bf4d42';metal='#397d70';interval='#efbd50';width=.016
segments=[(.2,.1,1.075,zero),(.2,1.15,4,metal),(.3,.1,.325,zero),(.3,.4,4,activated),(.5,.45,4,activated)]
for nu,t0,t1,col in segments:ax.add_patch(Rectangle((nu-width/2,t0),width,t1-t0,facecolor=col,edgecolor='none',zorder=3));ax.plot([nu-width/2,nu+width/2],[t0,t0],color=col,lw=1.2);ax.plot([nu-width/2,nu+width/2],[t1,t1],color=col,lw=1.2)
for nu,lo,hi in [(.2,1.075,1.15),(.3,.325,.4)]:ax.add_patch(Rectangle((nu-.022,lo),.044,hi-lo,facecolor=interval,edgecolor='#9c761e',lw=.6,zorder=4))
for nu,lab in [(.2,r'$\nu\simeq0.2$'),(.3,r'$\nu\simeq0.3$'),(.5,r'$\nu=1/2$')]:ax.text(nu,4.15,lab,ha='center',va='bottom',fontsize=10)
ax.annotate(r'$1.075<T_{\rho=0}/D\leq1.150$',xy=(.2,1.11),xytext=(.18,1.58),ha='right',arrowprops=dict(arrowstyle='-',lw=.8,color='#816528'),fontsize=9,color='#71521c')
ax.annotate(r'$0.325<T_{\rho=0}/D\leq0.400$',xy=(.3,.363),xytext=(.32,.18),arrowprops=dict(arrowstyle='-',lw=.8,color='#816528'),fontsize=9,color='#71521c')
ax.text(.68,2.65,'Unmeasured fillings\nPhase boundaries undetermined',ha='center',va='center',fontsize=12,color='#717882',bbox=dict(facecolor='white',edgecolor='#d7dade',boxstyle='round,pad=.65'))
ax.text(.515,.18,r'$T<0.45D$ unmeasured',fontsize=8.5,color='#747a82')
handles=[Patch(color=zero,label='Observed zero resistance'),Patch(color=activated,label='Activated positive resistance'),Patch(color=metal,label='Positive resistance, metallic T trend'),Patch(facecolor=interval,edgecolor='#9c761e',label='Onset bracket from sampling')]
ax.legend(handles=handles,loc='upper right',frameon=True,facecolor='white',edgecolor='#d8dce0',fontsize=8.5)
ax.set_xlabel(r'Filling fraction $\nu$ (two electrons per site at $\nu=1$)');ax.set_ylabel(r'Temperature $T/D$');ax.set_xticks(np.arange(0,1.01,.1));ax.set_title('Measured phase constraints',loc='left',fontweight='bold',pad=14)
fig.text(.11,.025,'Colored widths are visual guides, not measured doping intervals. No boundaries are interpolated.\nZero resistance is consistent with superconductivity; a Meissner or stiffness measurement was not supplied.',fontsize=8.6,color='#515862')
fig.subplots_adjust(bottom=.20,top=.91,left=.10,right=.98);save(fig,'sts_empirical_phase_map')
# Original STS and empirical NMR/rho fits in one figure.
fig,axs=plt.subplots(3,2,figsize=(10,10.5));fig.subplots_adjust(hspace=.48,wspace=.30,left=.10,right=.97,bottom=.11,top=.94)
for j,ax in enumerate(axs[:2].flat):
 s0=sts[j];xx=np.array(s0['bias']);yy=np.array(s0['dI_dV']);col=colors[j] if j<3 else colors[1];ax.plot(xx,yy,color=col,lw=.75)
 ax.set_xlim(-10,10);ax.set_ylim(-.02,1.12);ax.set_xticks([-8,-4,0,4,8]);ax.set_ylabel('Normalized dI/dV');ax.set_xlabel('Gap-centered bias / D' if j<3 else 'Bias relative to chemical potential / D')
 title=[r'(a) $\nu=1/2$, low T',r'(b) $\nu\simeq0.3$, low T',r'(c) $\nu\simeq0.2$, low T',r'(d) $\nu\simeq0.3$, high T'][j];ax.set_title(title,loc='left');ax.axvline(0,color='#c7cbd0',lw=.6,zorder=0)
ax=axs[2,0]
for i,(s0,col,lab) in enumerate(zip(nmr,colors,labels)):
 T=np.array(s0['temperature']);v=np.array(s0['one_over_T1'])/T;err=np.array(s0['uncertainty'])/T;ref=v[np.argmin(abs(T-4))];v/=ref;err/=ref
 ax.errorbar(1/T,v,yerr=err,fmt='o',ms=2.7,capsize=1.7,lw=.6,color=col,alpha=.75,label=lab)
 f=old['nmr'][i]['fixed_prefactor_fit'];lo,hi=f['temperature_range_D'];tt=np.geomspace(lo,hi,200);log=f['log_A']-f['activation_D']/tt-np.log(ref);C=np.array(f['covariance']);J=np.c_[np.ones_like(tt),-1/tt];se=np.sqrt(np.einsum('ij,jk,ik->i',J,C,J));ax.plot(1/tt,np.exp(log),color=col,lw=1.4);ax.fill_between(1/tt,np.exp(log-1.96*se),np.exp(log+1.96*se),color=col,alpha=.13)
ax.set_yscale('log');ax.set_ylim(5e-7,5);ax.set_xlim(0,5.1);ax.set_xlabel(r'Inverse temperature $D/T$');ax.set_ylabel(r'$[1/(T_1T)]/[1/(T_1T)]_{T=4D}$');ax.set_title('(e) NMR: empirical activation fits',loc='left');ax.legend(frameon=False,ncol=3,loc='upper right')
ax=axs[2,1]
for i,(s0,col,lab) in enumerate(zip(rho,colors,labels)):
 T=np.array(s0['temperature']);v=np.array(s0['resistivity']);err=np.array(s0['uncertainty']);ax.errorbar(T,v,yerr=err,fmt='o',ms=2.7,capsize=1.5,lw=.6,color=col,alpha=.75,label=lab)
 if i<2:
  f=old['resistivity'][i]['fixed_prefactor_fit'];lo,hi=f['temperature_range_D'];tt=np.linspace(lo,hi,300);log=f['log_A']+f['activation_D']/tt;C=np.array(f['covariance']);J=np.c_[np.ones_like(tt),1/tt];se=np.sqrt(np.einsum('ij,jk,ik->i',J,C,J));ax.plot(tt,np.exp(log),color=col,lw=1.4);ax.fill_between(tt,np.exp(log-1.96*se),np.exp(log+1.96*se),color=col,alpha=.13)
 else:
  f=old['resistivity'][i]['linear_positive_branch_fit'];tt=np.linspace(*f['temperature_range_D'],200);m=f['intercept']+f['slope_per_D']*tt;J=np.c_[np.ones_like(tt),tt];C=np.array(f['covariance']);se=np.sqrt(np.einsum('ij,jk,ik->i',J,C,J));ax.plot(tt,m,color=col,lw=1.4);ax.fill_between(tt,m-1.96*se,m+1.96*se,color=col,alpha=.13)
ax.set_yscale('symlog',linthresh=.15,linscale=.5);ax.set_ylim(-.025,2500);ax.set_xlim(0,4.08);ax.set_yticks([0,.1,1,10,100,1000],['0','0.1','1','10','100','1000']);ax.set_xlabel(r'Temperature $T/D$');ax.set_ylabel(r'$\rho(T)/\rho(4D)$');ax.set_title('(f) Resistivity: empirical fits',loc='left');ax.legend(frameon=False,ncol=3,loc='upper right')
fig.suptitle('Supplied observables and empirical response scales',fontsize=14,fontweight='bold',x=.10,ha='left')
fig.text(.10,.025,'STS: original supplied traces; each trace has its own normalization. Low/high STS temperatures are unspecified.\nNMR fits use raw 1/T1 and its quoted errors; curves show the derived 1/(T1T). Shading: pointwise 95% fit-mean intervals.\nNMR error bars extending below zero are outside the logarithmic plotting range. Resistivity uses a linear scale near zero.',fontsize=8.3,color='#515862')
save(fig,'sts_empirical_observables')
# Exact one-physical-orbital counterexample with HK momentum-local interaction, NOT a material fit.
t=1.;tp=.2;U=12.;mu=U/2-4*tp;N=768;kk=np.linspace(-.5,.5,N,endpoint=False);cx=np.cos(2*np.pi*kk)[:,None];cy=np.cos(2*np.pi*kk)[None,:];e1=-2*t*(cx+cy)-4*tp*cx*cy+4*tp;e2=2*t*(cx+cy)-4*tp*cx*cy+4*tp
w=np.linspace(-11,11,900);eta=.08;edges=np.linspace(-4.01,4.01,1601);cent=(edges[:-1]+edges[1:])/2
# Identical dispersion histograms under the exact grid permutation k->k+Q.
h1=np.histogram(e1,bins=edges)[0]/e1.size;h2=np.histogram(e2,bins=edges)[0]/e2.size
L=lambda z:eta/(np.pi*(z*z+eta*eta))
D1=np.sum(h1[None,:]*(.5*L(w[:,None]-cent[None,:]+U/2)+.5*L(w[:,None]-cent[None,:]-U/2)),axis=1);D2=np.sum(h2[None,:]*(.5*L(w[:,None]-cent[None,:]+U/2)+.5*L(w[:,None]-cent[None,:]-U/2)),axis=1)
area=quad(lambda q:np.arccos(np.clip(-(-4*tp+2*t*np.cos(q))/(2*t+4*tp*np.cos(q)),-1,1))/np.pi,0,np.pi,epsabs=1e-10,limit=200)[0]/np.pi
fig=plt.figure(figsize=(10.8,3.6));gs=fig.add_gridspec(1,3,width_ratios=[1.25,1,1]);a0=fig.add_subplot(gs[0]);a1=fig.add_subplot(gs[1]);a2=fig.add_subplot(gs[2]);a0.plot(w,D1,color='#176b86',lw=2,label=r'$t=+1$');a0.plot(w,D2,color='#b65b43',lw=1.4,ls='--',label=r'$t=-1$');a0.set_xlabel(r'Energy $\omega$');a0.set_ylabel('Local spectral density');a0.set_title('Identical local spectra');a0.legend(frameon=False);a0.set_xlim(-11,11)
for ax,e,sgn,ar in [(a1,e1,1,area),(a2,e2,-1,1-area)]:
 region=e<0 if sgn==1 else e>0;ax.contourf(kk,kk,region.T,levels=[-.5,.5,1.5],colors=['#f0f2f4','#a7cbd8']);ax.contour(kk,kk,e.T,levels=[0],colors=['#183e50'],linewidths=1.2);ax.plot(0,0,'o',ms=4,color='#9c3f30');ax.text(.025,.025,r'$\Gamma$',color='#9c3f30',fontsize=9);ax.set_aspect('equal');ax.set_xlim(-.5,.5);ax.set_ylim(-.5,.5);ax.set_xticks([-.5,0,.5]);ax.set_yticks([-.5,0,.5]);ax.set_xlabel(r'$k_x/(2\pi)$');ax.set_ylabel(r'$k_y/(2\pi)$');ax.set_title(f'Γ-side zero area: {ar:.4f}')
fig.suptitle('Exact one-orbital illustration of the local-to-momentum inverse problem',fontsize=12,fontweight='bold',y=1.03);fig.subplots_adjust(wspace=.40,bottom=.24,top=.82);fig.text(.03,.025,'Illustrative HK interaction, infinite range in real space; not fitted to the samples.\nBoth models have filling 1/2 and a causal normalized electron Green function. No fit to NMR or transport is asserted.',fontsize=8.5,color='#515862');save(fig,'sts_local_inverse_example')
example={'status':'Mathematical/physical inverse-problem illustration only; not fit to any measurement and not proposed material Hamiltonian.','one_physical_orbital_Hamiltonian':'H=Σ_kσ(ε_k−µ)n_kσ+U Σ_k n_k↑n_k↓. Interaction is local in momentum and infinite range in real space; all fermions are the physical one-orbital c.','parameters':{'t_plus':t,'t_minus':-t,'tprime':tp,'U':U,'mu_gap_midpoint':mu},'state':'T=0 spin-symmetric ensemble in singly occupied manifold: n_k↑=n_k↓=1/2, ν=1/2. Extensive spin degeneracy. NMR and transport have not been fitted; this is not proposed as a model of the samples.','G_retarded':'G(k,z)=.5/[z−ebar(k)+U/2]+.5/[z−ebar(k)−U/2], ebar=ε+4tprime, Im(z)>0.','zero_condition':'ebar(k)=0','momentum_relation':'ε_minus(k)=ε_plus(k+Q), Q=(π,π). The local spectra are identical by relabeling momenta.','Gamma_side_areas':[float(area),float(1-area)],'numerical_DOS_max_difference':float(np.max(np.abs(D1-D2))),'histogram_exact_max_weight_difference':float(np.max(np.abs(h1-h2))),'momentum_grid':[N,N],'line_broadening_for_plot':eta,'reference':'https://www.jstage.jst.go.jp/article/jpsj1946/61/6/61_6_2056/_article','what_it_proves':'A local spectral density and its frequency Kramers–Kronig transform do not identify the momentum assignment of G or the Γ-side zero area. This does not assert matching of NMR, transport, diffraction, or all other material constraints.'}
json.dump(example,open(R/'sts_local_inverse_example.json','w'),indent=2)
summary={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'definition':'Empirical constraints, not a computed Hamiltonian phase diagram.','samples':samples,'fit_validation':validation,'method':old['method'],'empirical_fit_limitations':old['limitations'],'sequences':{'0.5':'Below T=.45D unmeasured; activated positive resistivity from .45D to4D. No zero resistance observed.','0.3':'Measured zero resistance .1-.325D; onset bracket(.325,.4]D; activated positive resistivity .4-4D.','0.2':'Measured zero resistance .1-1.075D; onset bracket(1.075,1.15]D; positive resistivity with metallic T trend1.15-4D.'},'observable_statements':{'diffraction':'One-site in-plane crystallographic period, equivalent transition-metal sites, and fourfold in-plane axis; no observed structural transition. Does not independently measure time reversal or every electronic order.','STS':'Low-T spectra have a gap interval by the prompt, centered at plotted zero; only half-filled low-T chemical potential is explicitly fixed to that midpoint. Spatially uniform on the measured surface. Independent trace normalization and unknown matrix elements/background prevent an absolute spectral-weight sum-rule inversion. STS temperatures are only labeled low/high.','NMR':'One line persists in each sample. Low-T relaxation is strongly suppressed. Empirical activation parameters characterize the measured rate; they are not automatically exact many-body singlet-triplet gaps. ν≈.2 has a suggestive coherence-like enhancement near the resistive onset, not a determination of pairing symmetry.','resistivity':'Zero values define onset intervals, not exact transition temperatures or error-free finite weights in fits. Positive branches atν=.5,.3 show activated insulating trends;ν=.2 shows a metallic temperature trend. Zero resistance is consistent with superconductivity, but no Meissner or stiffness measurement was supplied.','inverse_problem':'Local STS integrates over momentum with tunneling weights. Even if calibrated STS were the complete local spectral function, frequency Kramers–Kronig would yield only the local Green function; G(k,ω) and its momentum zero contour require a microscopic model or momentum-resolved information.'},'inverse_example':example,'outputs':['sts_empirical_phase_map.png','sts_empirical_phase_map.pdf','sts_empirical_observables.png','sts_empirical_observables.pdf','sts_local_inverse_example.png','sts_local_inverse_example.pdf']}
json.dump(summary,open(R/'sts_empirical_summary.json','w'),indent=2)
lines=['EMPIRICAL CONSTRAINTS FOR THE SINGLE-ORBITAL REANALYSIS','', 'All activation uncertainties below are conditional on the stated empirical prefactor and the supplied independent errors. They are not microscopic Hamiltonian parameter confidence intervals.','']
for row in samples:
 f=row['nmr_activation_empirical'];lines.append(f"nu={row['nu_nominal']}: NMR E/D={f['activation_D']:.4f} +/- {f['activation_se_D']:.4f} (1 sigma), bootstrap95%={f['activation_bootstrap_95_D']}; raw-rate fit R=A*T*exp(-E/T), T range={f['temperature_range_D']}.")
 if 'rho_activation_empirical' in row:
  f=row['rho_activation_empirical'];lines.append(f"  Resistivity E/D={f['activation_D']:.4f} +/- {f['activation_se_D']:.4f}; bootstrap95%={f['activation_bootstrap_95_D']}; rho=A*exp(E/T).")
 if row['zero_resistance_onset_bracket_D']:lines.append(f"  Last-zero/first-positive bracket={row['zero_resistance_onset_bracket_D']}D; these endpoints are sampling limits, not a fitted uncertainty distribution.")
lines+=['',*summary['sequences'].values(),'',*summary['observable_statements'].values(),'',f"Illustrative exact one-orbital HK models have identical local spectra and Gamma-side zero areas {area:.8f} and {1-area:.8f}. They are not material fits; agreement with the supplied NMR and transport is not asserted."]
(R/'sts_empirical_summary.txt').write_text('\n'.join(lines)+'\n')
print(json.dumps({'fit_validation':validation,'samples':samples,'inverse_example_checks':{k:example[k] for k in ['Gamma_side_areas','numerical_DOS_max_difference','histogram_exact_max_weight_difference']}},indent=2))
