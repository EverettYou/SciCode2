"""Exact finite-T local spin Lehmann response on the 10-site tilted torus.

H_spin=J1 sum_NN S_i.S_j + J2 sum_NNN S_i.S_j is the leading strong-U
spin-sector approximation to the physical repulsive one-orbital Hubbard model.
All 2**10 spin states are retained. This is not a full finite-T Hubbard solve.
"""
import os
for variable in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:
    os.environ.setdefault(variable,'1')
os.environ.setdefault('MPLCONFIGDIR','/tmp/one-orbital-response-mpl')
from pathlib import Path
from itertools import combinations
import json,time
import numpy as np
from scipy.linalg import eigh
from scipy.optimize import minimize_scalar,brentq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
N=10
NN=sorted(set(tuple(sorted((i,(i+d)%N))) for i in range(N) for d in [1,-3]))
NNN=sorted(set(tuple(sorted((i,(i+d)%N))) for i in range(N) for d in [-2,4]))
NORMAL=json.load(open(ROOT/'data/sts_prior_spectral_fit_results.json'))['normal']
t,tp=NORMAL['params'][:2]
GAP_FITS=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
U=next(q['U'] for q in GAP_FITS['gap_fits'] if q['N']==10 and q['sign']==1)
J_PHYSICAL=4*t*t/U;RATIO=(tp/t)**2
SOURCE=json.load(open(ROOT/'data/measurements.json'))['measurements'][1]['samples'][0]
TEMPERATURE=np.array(SOURCE['temperature']);OBSERVED=np.array(SOURCE['one_over_T1']);ERROR=np.array(SOURCE['uncertainty'])


def build_spectrum():
    sectors=[]
    for m in range(N+1):
        states=np.array([sum(1<<i for i in c) for c in combinations(range(N),m)])
        index={int(s):i for i,s in enumerate(states)}
        H=np.zeros((len(states),len(states)))
        for bonds,J in [(NN,1.),(NNN,RATIO)]:
            for i,j in bonds:
                for a,s in enumerate(states):
                    ui=(int(s)>>i)&1;uj=(int(s)>>j)&1
                    H[a,a]+=J*(ui-.5)*(uj-.5)
                    if ui!=uj:H[index[int(s)^((1<<i)|(1<<j))],a]+=J/2
        e,v=eigh(H,check_finite=False,driver='evr')
        residual=float(np.max(np.linalg.norm(H@v-v*e[None,:],axis=0)))
        sectors.append({'m':m,'states':states,'index':index,'e':e,'v':v,'residual':residual})
    offsets=np.cumsum([0]+[len(s['e']) for s in sectors])
    energy=np.concatenate([s['e'] for s in sectors]);energy-=energy.min()
    ediffs=[];weights=[];initial=[];sumrule=np.zeros(2**N);site_comparison=[]
    for m in range(N):
        source,target=sectors[m],sectors[m+1]
        W=np.zeros((len(target['e']),len(source['e'])))
        Wsites=[]
        for site in range(N):
            op=np.zeros_like(W)
            for a,s in enumerate(source['states']):
                if not((int(s)>>site)&1):op[target['index'][int(s)|(1<<site)],a]=1
            matrix=target['v'].T@op@source['v']
            local=np.abs(matrix)**2;W+=local/N
            Wsites.append(local)
        ediff=target['e'][:,None]-source['e'][None,:]
        ediffs.append(ediff.ravel());weights.append(W.ravel())
        initial.append(np.broadcast_to(np.arange(offsets[m],offsets[m+1])[None,:],W.shape).ravel())
        sumrule[offsets[m]:offsets[m+1]]=W.sum(axis=0)
    gap=float(sectors[6]['e'][0]-sectors[5]['e'][0])
    return energy,np.concatenate(ediffs),np.concatenate(weights),np.concatenate(initial),sumrule,{
        'site_count':N,'dimension':2**N,'sector_dimensions':[len(s['e']) for s in sectors],
        'nearest_bonds':NN,'next_nearest_bonds':NNN,
        'maximum_eigenvector_residual_in_J1_units':max(s['residual'] for s in sectors),
        'finite_cluster_triplet_gap_over_J1':gap}


class LocalResponse:
    def __init__(self):
        self.E,self.dE,self.W,self.initial,self.weight_sum,self.info=build_spectrum()
        self.quasielastic=np.bincount(self.initial,weights=self.W*(np.abs(self.dE)<1e-9),minlength=2**N)

    def kernel(self,J,eta,omega=0.):
        if eta is None:return self.quasielastic
        lorentz=eta/(np.pi*((omega-J*self.dE)**2+eta**2))
        return np.bincount(self.initial,weights=self.W*lorentz,minlength=2**N)

    def response(self,T,J,eta,omega=0.):
        T=np.atleast_1d(T);boltz=np.exp(-J*self.E[None,:]/T[:,None]);Z=boltz.sum(axis=1)
        return (boltz@self.kernel(J,eta,omega))/Z

    def sum_rule(self,T,J):
        boltz=np.exp(-J*self.E[None,:]/np.atleast_1d(T)[:,None])
        return (boltz@self.weight_sum)/boltz.sum(axis=1)


def fit_scale(response,eta,mask,free_J=True):
    T,Y,SIG=TEMPERATURE[mask],OBSERVED[mask],ERROR[mask]
    def evaluate(logJ,details=False):
        J=float(np.exp(logJ));S=response.response(T,J,eta)
        amplitude=float(np.sum(S*Y/SIG**2)/np.sum(S*S/SIG**2))
        chi=float(np.sum(((amplitude*S-Y)/SIG)**2))
        return (chi,amplitude,S) if details else chi
    if free_J:
        grid=np.linspace(np.log(.02),np.log(50),160);chis=np.array([evaluate(q) for q in grid]);i=int(np.argmin(chis))
        lo=grid[max(i-1,0)];hi=grid[min(i+1,len(grid)-1)]
        fit=minimize_scalar(evaluate,bounds=(lo,hi),method='bounded',options={'xatol':1e-9});logJ=fit.x
    else:logJ=np.log(J_PHYSICAL)
    chi,A,S=evaluate(logJ,True);J=float(np.exp(logJ));dof=len(T)-(2 if free_J else 1)
    result={'J1_D':J,'J2_D':J*RATIO,'amplitude':A,'eta_D':eta,
        'chi_square':chi,'degrees_of_freedom':dof,'reduced_chi_square':chi/dof,
        'temperature_range_D':[float(T.min()),float(T.max())],
        'n_points':len(T),'J1_free':free_J,
        'triplet_gap_D':J*response.info['finite_cluster_triplet_gap_over_J1'],
        'predicted_raw_rate_at_measurement_temperatures':(A*response.response(TEMPERATURE,J,eta)).tolist(),
        'normalization_note':'Unknown hyperfine/relaxation scale A profiled in raw 1/T1 likelihood; quoted independent errors, no logarithmic fit.'}
    if free_J:
        for delta,label in [(1.,'68'),(3.841458820694124,'95')]:
            interval=[]
            for edge in [np.log(.02),np.log(50)]:
                scan=np.linspace(logJ,edge,100);prev=scan[0];root=None
                for trial in scan[1:]:
                    if evaluate(trial)-chi>=delta:
                        root=float(np.exp(brentq(lambda q:evaluate(q)-chi-delta,min(prev,trial),max(prev,trial))))
                        break
                    prev=trial
                interval.append(root)
            result['J1_profile_'+label+'_D']=interval
        result['profile_interval_note']='Contiguous profile-likelihood interval around the best minimum; conditional on the finite-cluster response and chosen broadening, not a microscopic uncertainty.'
    return result


def main():
    tic=time.time();r=LocalResponse();etas=[.02,.05,.1]
    all_mask=np.ones(len(TEMPERATURE),dtype=bool);low_mask=TEMPERATURE<=2
    fixed=[];free=[];free_low=[]
    for eta in etas:
        fixed.append(fit_scale(r,eta,all_mask,False));free.append(fit_scale(r,eta,all_mask,True));free_low.append(fit_scale(r,eta,low_mask,True))
    qe=fit_scale(r,None,all_mask,True);qe_low=fit_scale(r,None,low_mask,True)
    normalized=[];physical=[]
    for eta in etas:
        s=r.response(TEMPERATURE,J_PHYSICAL,eta);reference=float(r.response([4.],J_PHYSICAL,eta)[0])/4
        normalized.append(s/TEMPERATURE/reference);physical.append(s)
    out={'model':'exact finite-temperature H_spin=J1 sum_NN S.S+J2 sum_NNN S.S; Hubbard leading strong-coupling spin projection',
        'physical_hubbard_parameters':{'t_D':t,'tprime_D':tp,'U_D':U,'J1_D':J_PHYSICAL,'J2_D':J_PHYSICAL*RATIO,
            'U_source':'data/hubbard_gap_fits.json; repulsive 10-site canonical charge-gap match'},
        'cluster':r.info,'observable':'S_loc^+-(omega)=Z^-1/N sum_i,m,n exp(-E_n/T)|<m|S_i+|n>|^2 L_eta(omega-E_m+E_n); 1/T1 proportional to S_loc(omega_N~0)',
        'frequency_D':0.,'widths_D':etas,
        'source':'data/measurements.json, half-filled NMR raw 1/T1 and uncertainty',
        'fixed_J_raw_rate_fits':fixed,'free_J_raw_rate_fits_all_T':free,'free_J_raw_rate_fits_T_le_2':free_low,
        'exact_quasielastic_weight_free_J_all_T':qe,'exact_quasielastic_weight_free_J_T_le_2':qe_low,
        'spectral_sum_rule_expected':.5,'spectral_sum_rule_max_error':float(np.max(abs(r.sum_rule(TEMPERATURE,J_PHYSICAL)-.5))),
        'physical_J_normalized_R_over_T_at_lowest_T':{str(eta):float(v[0]) for eta,v in zip(etas,normalized)},
        'observed_normalized_R_over_T_at_lowest_T':float(OBSERVED[0]/TEMPERATURE[0]),
        'limitations':['Finite cluster has an artificial triplet gap; this is not a thermodynamic superconducting or magnetic phase calculation.',
          'Spin projection neglects charge states and higher-order exchange. Most reliable for T well below U and t/U small; the highest T~4D can have charge corrections.',
          'Lorentzian broadening creates artificial zero-frequency tails from gapped inelastic transitions, even at T=0.',
          'The eta->0 exact-degenerate transition weight is only a diagnostic of the finite-cluster quasielastic delta peak, not a finite physical relaxation rate.',
          'Changing J1 freely is a shape diagnostic and is not a fitted Hubbard U or validated microscopic Hamiltonian.',
          'Local, momentum-independent hyperfine coupling is assumed.'],
        'seconds':time.time()-tic}
    (ROOT/'response_spin_dynamics.json').write_text(json.dumps(out,indent=2))
    np.savez(ROOT/'response_spin_dynamics.npz',temperature=TEMPERATURE,observed_raw=OBSERVED,error_raw=ERROR,
        physical_J_raw_response=np.array(physical),physical_J_normalized_R_over_T=np.array(normalized),
        widths=np.array(etas),dimensionless_energy=r.E,dimensionless_transition_energy=r.dE,
        transition_weight=r.W,initial_state_index=r.initial,quasielastic_state_weight=r.quasielastic)
    plot(r,out,normalized)
    print(json.dumps({'triplet_gap_physical_D':J_PHYSICAL*r.info['finite_cluster_triplet_gap_over_J1'],
        'physical_lowest_T_ratios':out['physical_J_normalized_R_over_T_at_lowest_T'],
        'observed_lowest_T':out['observed_normalized_R_over_T_at_lowest_T'],
        'free_J_all':[(f['eta_D'],f['J1_D'],f['reduced_chi_square']) for f in free],
        'quasielastic_J':qe['J1_D'],'quasielastic_chi_dof':qe['reduced_chi_square'],
        'sumrule_error':out['spectral_sum_rule_max_error'],'elapsed':time.time()-tic},indent=2))


def plot(response,out,normalized):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(13,4.2),layout='constrained')
    colors=['#22649f','#318d83','#9b7027'];xi=1/TEMPERATURE
    for ax in axes[:2]:
        ax.errorbar(xi,OBSERVED/TEMPERATURE,yerr=ERROR/TEMPERATURE,fmt='o',ms=3,color='#b42f49',elinewidth=.7,capsize=2,label='Measured half-filled NMR')
        ax.set(yscale='log',xlabel=r'$D/T$',ylabel=r'Normalized $1/(T_1 T)$',ylim=(1e-5,30),xlim=(.15,2.4))
        ax.grid(axis='y',alpha=.15)
    for eta,col,v in zip(out['widths_D'],colors,normalized):axes[0].plot(xi,v,color=col,label=rf'$\eta={eta:.2f}D$')
    axes[0].set_title(rf'Physical Hubbard exchange: $J_1={J_PHYSICAL:.4f}D$')
    axes[0].legend(frameon=False,fontsize=8,loc='upper right')
    tf=np.geomspace(TEMPERATURE.min(),TEMPERATURE.max(),200)
    for fit,col in zip(out['free_J_raw_rate_fits_all_T'],colors):
        eta=fit['eta_D'];J=fit['J1_D'];curve=fit['amplitude']*response.response(tf,J,eta)/tf
        axes[1].plot(1/tf,curve,color=col,label=rf'$\eta={eta:.2f},\ J_1={J:.1f}$')
    q=out['exact_quasielastic_weight_free_J_all_T'];curve=q['amplitude']*response.response(tf,q['J1_D'],None)/tf
    axes[1].plot(1/tf,curve,color='.25',ls='--',label=rf'Exact-degenerate weight, $J_1={q["J1_D"]:.1f}$')
    axes[1].set_title('Free exchange is only a shape diagnostic');axes[1].legend(frameon=False,fontsize=8,loc='upper right')
    w=np.linspace(-1.5,1.5,301)
    for T,col in zip([.4472,1.,4.],colors):
        s=np.array([response.response([T],J_PHYSICAL,.05,ww)[0] for ww in w]);axes[2].plot(w,s,color=col,label=rf'$T={T:.3g}D$')
    axes[2].set(xlabel=r'$\omega/D$',ylabel=r'$S_{\rm loc}^{+-}(\omega)$',title=r'Actual Lehmann spectrum, $\eta=0.05D$')
    axes[2].legend(frameon=False,fontsize=8);axes[2].grid(axis='y',alpha=.15)
    fig.savefig(ROOT/'response_spin_dynamics.png',dpi=220)


if __name__=='__main__':main()
