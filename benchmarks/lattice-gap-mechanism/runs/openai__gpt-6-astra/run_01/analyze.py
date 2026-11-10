"""Reproduce the data analysis, conditional spectra and identifiability figures.

Run fit_spectra.py first.  All inputs and outputs stay alongside this script.
No microscopic many-body Hamiltonian is claimed to have been solved here.
"""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, brentq
from scipy.integrate import trapezoid
from scipy.ndimage import gaussian_filter1d
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm, TwoSlopeNorm
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'measurements.json').read_text())
FIT=json.loads((ROOT/'spectral_fit_results.json').read_text())
OUT={}
COLORS=['#c62a3a','#178249','#275abe']
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.bbox':'tight','axes.titlepad':10})

def save(fig,name):
    fig.savefig(ROOT/(name+'.png'),dpi=190)
    fig.savefig(ROOT/(name+'.pdf'))
    plt.close(fig)

def covariance(result):
    return np.linalg.pinv(result.jac.T@result.jac)

def analyze_response():
    fig,axs=plt.subplots(1,3,figsize=(15,4.6),layout='constrained')
    out={'nmr':[],'resistivity':[]}
    for i,s in enumerate(DATA['measurements'][1]['samples']):
        T=np.array(s['temperature']);rate=np.array(s['one_over_T1']);err=np.array(s['uncertainty'])
        cap=.8125 if i==2 else 4.
        use=T<=cap
        # Fit the raw quantity with its supplied uncertainties, not logs of
        # noise-floor points.  T is explicitly included in 1/T1 = T R(T).
        def residual(p):
            return (T[use]*np.exp(p[0]-p[1]/T[use])-rate[use])/err[use]
        fit=least_squares(residual,[1.,3.])
        cov=covariance(fit)
        def residual_power(p):
            return (T[use]*np.exp(p[0]+p[2]*np.log(T[use])-p[1]/T[use])-rate[use])/err[use]
        pfit=least_squares(residual_power,[*fit.x,0.])
        pcov=covariance(pfit)
        out['nmr'].append({'filling':s['filling'],'temperature_max':cap,
                          'activation':fit.x[1],'activation_se':np.sqrt(cov[1,1]),
                          'log_prefactor':fit.x[0],
                          'chi2_per_dof':float(fit.fun@fit.fun/(use.sum()-2)),
                          'free_power_activation':pfit.x[1],
                          'free_power_activation_se':np.sqrt(pcov[1,1]),
                          'free_power_exponent':pfit.x[2]})
        axs[0].errorbar(1/T,rate/T,yerr=err/T,fmt='o',ms=3,color=COLORS[i],alpha=.75,
                       label=s['filling'],capsize=2)
        tg=np.geomspace(max(T[0],.2),cap,250)
        axs[0].plot(1/tg,np.exp(fit.x[0]-fit.x[1]/tg),color=COLORS[i])
    axs[0].set(xlabel=r'$D/T$',ylabel=r'normalized $1/(T_1T)$',yscale='log',
               ylim=(3e-6,3),title='NMR: fit raw rates as $T C e^{-E_s/T}$')
    axs[0].legend(title=r'$\nu$',fontsize=8)
    for i,s in enumerate(DATA['measurements'][2]['samples']):
        T=np.array(s['temperature']);rho=np.array(s['resistivity']);err=np.array(s['uncertainty'])
        use=rho>0
        result={'filling':s['filling']}
        if i<2:
            y=np.log(rho[use]);sigma=err[use]/rho[use]
            design=np.column_stack([np.ones(use.sum()),1/T[use]])
            fit=least_squares(lambda p:(design@p-y)/sigma,[0,3.7 if i==0 else .9])
            cov=covariance(fit)
            result.update({'activation':fit.x[1],'activation_se':np.sqrt(cov[1,1]),
                           'log_prefactor':fit.x[0],
                           'chi2_per_dof':float(fit.fun@fit.fun/(use.sum()-2))})
            axs[1].errorbar(1/T[use],rho[use],yerr=err[use],fmt='o',ms=3,
                            color=COLORS[i],alpha=.75,capsize=2,label=s['filling'])
            tg=np.linspace(T[use][0],4,250)
            axs[1].plot(1/tg,np.exp(fit.x[0]+fit.x[1]/tg),color=COLORS[i])
        else:
            design=np.column_stack([np.ones(use.sum()),T[use]])
            fit=least_squares(lambda p:(design@p-rho[use])/err[use],[.1,.2])
            cov=covariance(fit)
            result.update({'normal_linear_intercept':fit.x[0],
                           'normal_linear_slope':fit.x[1],
                           'linear_errors':np.sqrt(np.diag(cov)).tolist(),
                           'chi2_per_dof':float(fit.fun@fit.fun/(use.sum()-2))})
        if np.any(~use):
            result['transition_bracket']=[float(T[~use][-1]),float(T[use][0])]
            result['transition_midpoint']=float((T[~use][-1]+T[use][0])/2)
            result['transition_half_interval']=float((T[use][0]-T[~use][-1])/2)
            axs[2].errorbar(T,rho,yerr=err,fmt='o',ms=3,color=COLORS[i],capsize=2,
                           alpha=.8,label=s['filling'])
            axs[2].axvspan(T[~use][-1],T[use][0],color=COLORS[i],alpha=.12)
        out['resistivity'].append(result)
    axs[1].set(xlabel=r'$D/T$',ylabel=r'$\rho(T)/\rho(4D)$',yscale='log',
               title='Activated-like normal resistivity')
    axs[1].legend(title=r'$\nu$',fontsize=8)
    axs[2].set(xlabel=r'$T/D$',ylabel=r'$\rho(T)/\rho(4D)$',ylim=(-.08,2.6),
               title='Measured transition intervals')
    axs[2].legend(title=r'$\nu$',fontsize=8)
    save(fig,'response_fits')
    OUT['response_fits']=out

def phase_constraints():
    fig,ax=plt.subplots(figsize=(12.5,6),layout='constrained')
    ax.set(xlim=(0,1),ylim=(0,4.6),xlabel=r'filling $\nu$ (two electrons/site at $\nu=1$)',
           ylabel=r'$T/D$',title='Phase information supported by the measurements')
    ax.set_facecolor('#f4f4f4')
    ax.text(.75,2.4,'No measurements here\nNo particle–hole symmetry\nwas established',
            ha='center',va='center',color='#666666',fontsize=12)
    for nu,tc,col in [(.2,(1.075,1.15),COLORS[2]),(.3,(.325,.4),COLORS[1])]:
        ax.axvline(nu,color=col,lw=1.2,ls='--',alpha=.8)
        ax.plot([nu,nu],[0,tc[0]],color=col,lw=9,solid_capstyle='butt')
        ax.errorbar(nu,np.mean(tc),yerr=(tc[1]-tc[0])/2,fmt='o',mfc='white',mec=col,
                    ecolor=col,capsize=8,ms=6,zorder=10)
    ax.axvline(.5,color=COLORS[0],ls='--',lw=1.3)
    ax.plot([.5,.5],[.4472,4.4318],color=COLORS[0],lw=8,alpha=.65)
    ax.plot([.5,.5],[0,.4472],color=COLORS[0],lw=3,ls=':')
    ax.annotate('Fully gapped SC',(.2,.5),xytext=(.075,.63),ha='center',color=COLORS[2],
                 arrowprops={'arrowstyle':'-','color':COLORS[2]})
    ax.annotate('SC',(.3,.15),xytext=(.36,.15),va='center',color=COLORS[1],
                 arrowprops={'arrowstyle':'-','color':COLORS[1]})
    ax.annotate('Normal metal;\nNMR nearly Korringa',(.2,2.5),xytext=(.035,2.9),
                 ha='left',color=COLORS[2],arrowprops={'arrowstyle':'-','color':COLORS[2]})
    ax.annotate('Resistive normal state;\nspin response suppressed;\nactivated-like resistivity',(.3,1.4),
                 xytext=(.33,1.5),ha='left',fontsize=9,color=COLORS[1],
                 arrowprops={'arrowstyle':'-','color':COLORS[1]})
    ax.annotate('Insulating response;\nno transition located',(.5,3.3),xytext=(.55,3.6),
                 ha='left',color=COLORS[0],arrowprops={'arrowstyle':'-','color':COLORS[0]})
    ax.text(.31,4.32,'High-T STS is gapless;\nits temperature is not specified',
            ha='center',va='top',fontsize=9,color=COLORS[1])
    ax.text(.75,.55,'Unmeasured fillings remain unassigned.\nLine widths do not represent phase widths.',
            ha='center',fontsize=10,color='#666666')
    ax.set_xticks([0,.2,.3,.5,.75,1])
    save(fig,'phase_constraints')

def dispersion(kx,ky,t,tp):
    cx=np.cos(2*np.pi*kx);cy=np.cos(2*np.pi*ky)
    return -2*t*(cx+cy)-4*tp*cx*cy

def path_grid():
    vertices=np.array([[0.,0.],[.5,0.],[.5,.5],[0.,0.]])
    points=[];distance=[];ticks=[0.];offset=0.
    for p,q,n in zip(vertices[:-1],vertices[1:],[220,220,311]):
        frac=np.arange(n)/n
        points.append(p[None,:]+frac[:,None]*(q-p)[None,:])
        length=np.linalg.norm(q-p)
        distance.extend(offset+frac*length)
        offset+=length;ticks.append(offset)
    points.append(vertices[-1][None,:]);distance.append(offset)
    return np.concatenate(points),np.array(distance),ticks

def poles_for_panel(panel,kx,ky):
    if panel=='a':
        t,tp,M,C,b,eta,*_=FIT['half_two_pole']['parameters']
        q=dispersion(kx,ky,t,tp)
        return C+q-M,C+q+M,.5-b*q,.5+b*q,eta
    t,tp=FIT['normal']['parameters'][:2]
    mu,gap,eta,*_=FIT['bcs_c']['parameters']
    xi=dispersion(kx,ky,t,tp)-mu
    E=np.sqrt(xi*xi+gap*gap)
    w=.5*(1+xi/E)
    return -E,E,1-w,w,eta

def flat_completion_b(omega):
    """A counterexample, not a prediction: a local spectral continuum.

    Retain a smoothed, background-subtracted version of the measured bands.
    The arbitrary absolute scale is fixed so the occupied weight is 0.3.
    Add the missing positive weight as an unobserved delta peak at +20D.
    """
    s=DATA['measurements'][0]['spectra'][1]
    x=np.asarray(s['bias']);y=np.asarray(s['dI_dV'])
    outside=abs(x)>7.2
    design=np.column_stack([np.ones_like(x),x*x])
    bg=np.linalg.lstsq(design[outside],y[outside],rcond=None)[0]
    cleaned=np.maximum(gaussian_filter1d(y-design@bg,1.5),0)
    cleaned[(abs(x)<2.6)|(abs(x)>6.65)]=0
    negative=trapezoid(np.where(x<0,cleaned,0),x)
    positive=trapezoid(np.where(x>0,cleaned,0),x)
    scale=negative/.3
    rho=cleaned/scale
    missing=1-(negative+positive)/scale
    assert missing>=0
    return np.interp(omega,x,rho),{
        'description':'Momentum-independent counterexample, not predicted flat bands.',
        'occupied_weight_per_spin':.3,'unseen_positive_weight_at_20D':missing,
        'background_constant':bg[0],'background_quadratic':bg[1],
        'support_assumed':[-6.65,-2.6,2.6,6.65],
        'sum_rule_with_unseen_peak':float(trapezoid(rho,x)+missing)}

def spectral_maps():
    pts,x,ticks=path_grid()
    omega=np.linspace(-9,9,1801)
    fig,axs=plt.subplots(1,3,figsize=(15,6),sharey=True,layout='constrained')
    grids=np.arange(900)/900-.5
    kx=grids[:,None];ky=grids[None,:]
    metadata={}
    for ax,panel,label in zip(axs,['a','b','c'],[r'$\nu=1/2$',r'$\nu\approx0.3$',r'$\nu\approx0.2$']):
        if panel=='b':
            flat,metadata[panel]=flat_completion_b(omega)
            A=np.broadcast_to(flat[:,None],(len(omega),len(x))).copy()
        else:
            en,ep,wn,wp,eta=poles_for_panel(panel,pts[:,0],pts[:,1])
            en2,ep2,wn2,wp2,_=poles_for_panel(panel,kx,ky)
            raw_density=float(np.mean(wn2))
            Z=.2/raw_density if panel=='c' else 1.
            # At c, one explicit way to repair the number sum rule is to put
            # missing weight at +20D.  This is arbitrary, illustrating that
            # normalized low-energy STS does not determine absolute weights.
            A=Z*(wn[None,:]*eta/((omega[:,None]-en[None,:])**2+eta**2)
              +wp[None,:]*eta/((omega[:,None]-ep[None,:])**2+eta**2))/np.pi
            metadata[panel]={'unscaled_occupied_weight_per_spin':raw_density,
                         'occupied_weight_per_spin_after_completion':Z*raw_density,
                         'coherent_scale_chosen':Z,'unseen_positive_weight_at_20D':1-Z,
                         'min_coherent_residue':float(Z*min(wn2.min(),wp2.min())),
                         'max_sum_rule_error_including_unseen_peak':float(np.max(abs(Z*(wn2+wp2)+1-Z-1))),
                         'negative_edge':float(en2.max()),'positive_edge':float(ep2.min()),
                         'linewidth_used':eta}
        im=ax.pcolormesh(x,omega,A,cmap='magma',norm=PowerNorm(.5,vmin=0,vmax=3.7),
                         shading='auto',rasterized=True)
        for tick in ticks[1:-1]:ax.axvline(tick,color='white',lw=.5,alpha=.45)
        ax.axhline(0,color='cyan',lw=.7,alpha=.8)
        ax.set_xticks(ticks,[r'$\Gamma$',r'$X$',r'$M$',r'$\Gamma$'])
        subtitles={'a':'two-pole fit','b':'local continuum counterexample','c':'BCS-like fit + unseen weight'}
        ax.set(title=label+'\n'+subtitles[panel],xlabel='momentum path',ylim=(-9,9))
        np.savez_compressed(ROOT/('spectrum_'+panel+'.npz'),momentum=pts,
                            path_distance=x,omega=omega,spectral_function=A)
    axs[0].set_ylabel(r'energy from assumed $\mu$, $\omega/D$')
    fig.colorbar(im,ax=axs,label=r'$A(\mathbf{k},\omega)$, $D^{-1}$',shrink=.82,pad=.02)
    fig.suptitle('Illustrative spectral completions — not predictions of a fitted Hamiltonian',fontsize=14)
    save(fig,'conditional_arpes')
    OUT['spectral_consistency_checks']=metadata

def fraction_below(t,tp,threshold,n=16384):
    cx=np.cos(2*np.pi*(np.arange(n)+.5)/n)
    y=(-threshold-2*t*cx)/(2*t+4*tp*cx)
    return float(np.mean(np.arccos(np.clip(y,-1,1))/np.pi))

def zeros_and_kk():
    record=FIT['half_two_pole'];p=np.array(record['parameters'])
    t,tp,M,C,b,eta,*_=p
    alpha=1-2*b*M
    qstar=-C/alpha
    fraction=fraction_below(t,tp,qstar)
    cov=np.array(record['covariance'])
    rng=np.random.default_rng(57031)
    draws=rng.multivariate_normal(p,cov,size=1500,check_valid='ignore')
    vals=[]
    for d in draws:
        ta,tpa,ma,ca,ba=d[:5];aa=1-2*ma*ba
        if aa>0 and ta>2*abs(tpa):
            vals.append(fraction_below(ta,tpa,-ca/aa,n=4096))
    q=np.linspace(-.5,.5,501)
    xx,yy=np.meshgrid(q,q,indexing='xy')
    en=dispersion(xx,yy,t,tp)
    enz=dispersion(xx+.5,yy+.5,t,tp)
    g=(C+alpha*en)/(M*M-(C+en)**2)
    gshift=(C+alpha*enz)/(M*M-(C+enz)**2)
    fig,axs=plt.subplots(1,2,figsize=(10.7,4.8),layout='constrained')
    for ax,gg,vol,label in zip(axs,[g,gshift],[fraction,1-fraction],['Fitted completion','Momentum-shifted completion']):
        im=ax.pcolormesh(xx,yy,gg,cmap='RdBu_r',norm=TwoSlopeNorm(vcenter=0,vmin=-.015,vmax=.04),
                        shading='auto',rasterized=True)
        ax.contour(xx,yy,gg,levels=[0],colors='black',linewidths=1.6)
        ax.plot(0,0,'ko',ms=4);ax.text(.025,.02,r'$\Gamma$')
        ax.set(xlabel=r'$k_x/(2\pi/a)$',ylabel=r'$k_y/(2\pi/a)$',aspect='equal',
               title=f'{label}\nΓ-side area = {vol:.4f} of BZ')
    fig.colorbar(im,ax=axs,label=r'$\mathrm{Re}\,G(\mathbf{k},0)$, $D^{-1}$',shrink=.85)
    fig.suptitle('Same momentum-integrated spectrum; different Γ-side zero areas',fontsize=13)
    save(fig,'conditional_zeros')
    # Independent 2D area check (quadrature, not an interacting finite lattice).
    estimates={}
    for n in [512,1024,2048]:
        grid=np.arange(n)/n-.5
        ep=dispersion(grid[:,None],grid[None,:],t,tp)
        estimates[str(n)]=float(np.mean(C+alpha*ep<0))
    # Kramers–Kronig integral of narrow Gaussian approximations to delta poles.
    # This check uses the full frequency support, not the limited ARPES window.
    points,_,_=path_grid();points=points[::25]
    qk=dispersion(points[:,0],points[:,1],t,tp)
    em=C+qk-M;ep=C+qk+M;wm=.5-b*qk;wp=.5+b*qk
    omega=np.arange(-12.0005,12.001,.001)
    width=.01
    A=(wm[:,None]*np.exp(-.5*((omega[None,:]-em[:,None])/width)**2)
      +wp[:,None]*np.exp(-.5*((omega[None,:]-ep[:,None])/width)**2))/(np.sqrt(2*np.pi)*width)
    gkk=-trapezoid(A/omega[None,:],omega,axis=1)
    exact=-wm/em-wp/ep
    OUT['half_filling_zero_calculation']={
        'approximation':'Fitted causal two-pole spectral ansatz; exact KK of its delta peaks',
        'alpha':alpha,'zero_q_threshold':qstar,'fraction_Gamma_side':fraction,
        'fraction_shifted_Gamma_side':1-fraction,'filling':.5,
        'conditional_fraction_sd':float(np.std(vals)),
        'conditional_fraction_95_percentile':np.percentile(vals,[2.5,97.5]).tolist(),
        'area_2d_grid_checks':estimates,'one_dimensional_quadrature_points':16384,
        'kk_check_gaussian_width':width,'kk_check_energy_step':.001,
        'kk_check_energy_window':[-12,12],
        'kk_check_max_abs_error':float(np.max(abs(gkk-exact))),
        'warning':'The fraction is model conditional, not identified by the supplied measurements.'}
    variants=[]
    qmin=-4*t-4*tp;qmax=4*t-4*tp
    for weight,lminus,lplus in [(0.,12.,30.),(.03,12.,30.),(.03,30.,12.)]:
        shift=weight/lminus-weight/lplus
        def modified_g(q):
            return (1-2*weight)*(C+alpha*q)/(M*M-(C+q)**2)+shift
        root=brentq(modified_g,qmin,qmax)
        variants.append({'weight_of_each_unseen_peak':weight,
                         'negative_unseen_peak_energy':-lminus,
                         'positive_unseen_peak_energy':lplus,
                         'fraction_Gamma_side':fraction_below(t,tp,root)})
    OUT['same_STS_same_density_different_high_energy_completions']=variants
    fig,axs=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    axs[0].plot(exact,gkk,'o',ms=4)
    lim=[float(exact.min()),float(exact.max())]
    axs[0].plot(lim,lim,'k--',lw=1)
    axs[0].set(xlabel='Analytic pole sum $G(0)$',ylabel='Numerical KK integral',title='Independent KK check')
    axs[1].hist(vals,bins=35,color='#456d96',alpha=.8)
    axs[1].axvline(fraction,color='black',ls='--')
    axs[1].set(xlabel='Γ-side fraction of BZ',ylabel='parameter draws',title='Conditional fit uncertainty only')
    save(fig,'kk_validation')

def main():
    analyze_response()
    phase_constraints()
    spectral_maps()
    zeros_and_kk()
    OUT['calculation_size']={'many_body_cluster':None,
        'description':'No finite-size many-body phase diagram was solved.',
        'local_DOS_integral_kx_points':768,'ARPES_path_points':752,
        'ARPES_energy_points':1801,'spectral_density_check_grid':[900,900],
        'largest_2d_zero_area_grid':[2048,2048]}
    (ROOT/'analysis_results.json').write_text(json.dumps(OUT,indent=2,ensure_ascii=False))
    print(json.dumps(OUT,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
