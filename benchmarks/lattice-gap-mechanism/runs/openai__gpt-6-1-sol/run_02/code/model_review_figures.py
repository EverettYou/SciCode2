"""Publication-style figures for the model identifiability checks."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures'
FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,
                     'axes.labelsize':10,'axes.titlesize':11,
                     'axes.linewidth':.75,'xtick.labelsize':9,'ytick.labelsize':9,
                     'savefig.dpi':300,'mathtext.fontset':'dejavusans'})
NAVY='#183D5D'; BLUE='#BFDCE9'; INK='#192E3A'; ORANGE='#B6582B'; GRAY='#F1F3F4'


def nonuniqueness():
    fig=plt.figure(figsize=(12.8,4.65),facecolor='white')
    gs=fig.add_gridspec(1,4,left=.061,right=.985,bottom=.25,top=.755,wspace=.32,
                        width_ratios=[1.1,1,1,1])
    axes=[fig.add_subplot(gs[0,j]) for j in range(4)]
    fig.text(.061,.94,'The same local spectrum does not determine the Green-function zero curve',
             fontsize=16,fontweight='bold',color=INK)
    fig.text(.061,.875,'Logical counterexample, not a fit to measurements',fontsize=11,color=ORANGE)
    w=np.linspace(-9,11,5000); poles=np.array([-6,-4,4,8]); weights=np.array([.4,.1,.1,.4]); sigma=.13
    dos=sum(p*np.exp(-.5*((w-e)/sigma)**2)/(sigma*np.sqrt(2*np.pi)) for e,p in zip(poles,weights))
    ax=axes[0]
    ax.plot(w,dos,color=NAVY,lw=1.7)
    ax.axvspan(-4,4,color='#E6F2F1',zorder=-2)
    ax.axvline(0,color='#9EACB5',lw=.7,ls=':')
    ax.text(0,.8,'gap',ha='center',color='#55736D',fontsize=10)
    ax.set(xlim=(-8,10),ylim=(0,1.4),xlabel=r'Energy $\omega/D$',ylabel=r'Local spectrum $N(\omega)$')
    ax.set_xticks([-6,-4,0,4,8]); ax.set_yticks([0,.5,1])
    ax.set_title(r'(a) Identical for every $\lambda$',loc='left',pad=13)
    ax.text(.03,.95,r'$\nu=1/2,\quad\mu=0$',transform=ax.transAxes,va='top',fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    k=np.linspace(-.5,.5,701); X,Y=np.meshgrid(k,k)
    f=(np.cos(2*np.pi*X)+np.cos(2*np.pi*Y))/2
    narea=2000; ka=-.5+(np.arange(narea)+.5)/narea
    fa=(np.cos(2*np.pi*ka)[:,None]+np.cos(2*np.pi*ka)[None,:])/2
    fractions=[]
    for j,lam in enumerate([.1,.2,.3]):
        ax=axes[j+1]; g=1/60+7*lam*f/24
        threshold=-2/(35*lam); frac=float(np.mean(fa>threshold)); fractions.append(frac)
        ax.contourf(X,Y,g,levels=[-1,0,1],colors=[GRAY,BLUE])
        ax.contour(X,Y,g,levels=[0],colors=[NAVY],linewidths=1.6)
        ax.plot(0,0,'o',ms=3.5,color=NAVY); ax.text(.025,.023,r'$\Gamma$',fontsize=11,color=NAVY)
        ax.set(xlim=(-.5,.5),ylim=(-.5,.5),aspect='equal',xlabel=r'$k_x/(2\pi)$')
        ax.set_xticks([-.5,0,.5]); ax.set_yticks([-.5,0,.5])
        if j==0: ax.set_ylabel(r'$k_y/(2\pi)$')
        ax.set_title(f'({chr(98+j)}) '+rf'$\lambda={lam:.1f}$',loc='left',pad=13)
        ax.text(.5,1.025,rf'$f_\Gamma={frac:.4f}$',transform=ax.transAxes,ha='center',fontsize=10)
    fig.legend(handles=[Patch(facecolor=BLUE,label=r'Side containing $\Gamma$'),
                        Line2D([0],[0],color=NAVY,lw=1.6,label=r'Exact $G(\mathbf{k},0)=0$')],
               loc='lower center',bbox_to_anchor=(.665,.095),ncol=2,frameon=False,fontsize=10)
    fig.text(.061,.115,r'$G(\mathbf{k},0)=1/60+(7\lambda/24)f(\mathbf{k})$, '
             r'$f=(\cos k_x+\cos k_y)/2$',fontsize=10,color=INK)
    fig.text(.061,.045,'All spectra have unit weight at every momentum and occupied weight 1/2 on average. '
             'Gaussian broadening appears only in panel (a).',fontsize=9,color='#53636D')
    p=FIG/'model_review_nonuniqueness.png';fig.savefig(p);plt.close(fig)
    return {'grid_for_fractions':[narea,narea], 'lambda':[.1,.2,.3], 'gamma_side_fractions':fractions,
            'display_gaussian_sigma_D':sigma,'green_sign_check':'G(0)=sum_j w_j/(0-E_j)=1/60+(7lambda/24)f'}


def stiffness():
    normal=json.loads((ROOT/'data'/'sts_fit_results.json').read_text())['normal']
    t,tp=normal['params'][:2];cov=np.array(normal['covariance'])[:2,:2];nu=.2
    grad=(np.pi*nu/2)*np.array([1,2*np.sign(tp)])
    bound=np.pi*nu/2*(abs(t)+2*abs(tp));se=np.sqrt(grad@cov@grad)
    ci=[float(bound-1.96*se),float(bound+1.96*se)]
    fig=plt.figure(figsize=(9.0,5.6),facecolor='white')
    fig.text(.08,.93,'A strict two-dimensional Hubbard model fails a stiffness check',
             fontsize=15.3,fontweight='bold',color=INK)
    fig.text(.08,.865,r'Conditional test at $\nu=0.2$: '
             r'$T_c\leq \pi\nu(|t|+2|t^{\prime}|)/2$',fontsize=13,color=INK)
    ax=fig.add_axes([.24,.39,.69,.36])
    ax.barh(1,bound,height=.25,color=BLUE,edgecolor=NAVY,lw=.8)
    ax.errorbar(bound,1,xerr=1.96*se,fmt='o',ms=5,color=NAVY,capsize=6,lw=1.5)
    ax.plot([1.075,1.15],[0,0],color=ORANGE,lw=6,solid_capstyle='butt')
    ax.plot(1.075,0,'o',ms=7,mfc='white',mec=ORANGE,mew=1.5)
    ax.plot(1.15,0,'o',ms=7,mfc=ORANGE,mec=ORANGE)
    ax.set_yticks([0,1],['Observed transition','Model upper bound'])
    ax.set(xlim=(0,1.29),ylim=(-.5,1.55),xlabel=r'Temperature $T/D$')
    ax.set_xticks(np.arange(0,1.3,.2));ax.tick_params(axis='y',length=0,pad=15)
    ax.spines[['top','right','left']].set_visible(False)
    ax.xaxis.grid(True,color='#E8ECEF',lw=.7);ax.set_axisbelow(True)
    ax.text(bound+.045,1.16,rf'${bound:.4f}\pm{se:.4f}$  (1$\sigma$)',fontsize=11,color=NAVY)
    ax.text(.84,-.26,r'$(1.075,\,1.150]D$',fontsize=11,color=ORANGE)
    fig.text(.08,.285,rf'High-temperature DOS fit: $t={t:.4f}D$, '
             rf'$t^\prime={tp:.4f}D$. Error bar: 95% interval from the joint fit covariance.',fontsize=10,color=INK)
    fig.text(.08,.205,'Assumptions: one band, strictly 2D; fitted hoppings are bare and independent of temperature;',
             fontsize=9.5,color='#53636D')
    fig.text(.08,.16,'interactions do not carry electrical current; the observed transition is superconducting.',
             fontsize=9.5,color='#53636D')
    fig.text(.08,.10,'Model uncertainty is not included. Extra bands/layers, 3D coupling, or pair hopping can change this bound.',
             fontsize=9.5,color='#53636D')
    fig.text(.08,.045,'Stiffness inequality: Hazra, Verma & Randeria, Phys. Rev. X 9, 031049 (2019).',
             fontsize=9,color='#53636D')
    p=FIG/'model_review_stiffness.png';fig.savefig(p);plt.close(fig)
    return {'t_D':t,'tprime_D':tp,'covariance_t_tprime':cov.tolist(),'nu_fixed':nu,
            'bound_D':float(bound),'standard_error_D':float(se),'conditional_95_percent_interval_D':ci,
            'observed_transition_bracket_D':[1.075,1.15],
            'uncertainty_scope':'Covariance from high-temperature DOS fit only; no model uncertainty or filling uncertainty.'}


if __name__=='__main__':
    results={'nonuniqueness':nonuniqueness(),'stiffness':stiffness()}
    (ROOT/'data'/'model_review_figure_results.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
