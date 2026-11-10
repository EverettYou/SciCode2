"""Strict one-physical-orbital response checks; no auxiliary degrees of freedom.

This computes exact atomic/two-site checks and a variational optical-stiffness
upper bound. It does not purport to solve the thermodynamic PKH phase diagram.
"""
from pathlib import Path
import json, os
os.environ.setdefault('MPLCONFIGDIR','/tmp/one-orbital-response-mpl')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
normal=json.load(open(ROOT/'data/sts_prior_spectral_fit_results.json'))['normal']
t,tp=normal['params'][:2]
cov=np.array(normal['covariance'])[:2,:2]
gap_fits=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
U=next(q['U'] for q in gap_fits['gap_fits'] if q['N']==10 and q['sign']==1)


def curvature_bound(nu, L=1024):
    k=2*np.pi*(np.arange(L)+.5)/L
    x=np.cos(k)[:,None];y=np.cos(k)[None,:]
    ct=(x+y)+np.zeros((L,L));cp=4*x*y
    curvature=t*ct+tp*cp
    order=np.argsort(curvature.ravel())[::-1]
    count=nu*L*L;whole=int(count);frac=count-whole
    selected=order[:whole]
    g=np.array([ct.ravel()[selected].sum(),cp.ravel()[selected].sum()])
    if whole<L*L:g+=frac*np.array([ct.ravel()[order[whole]],cp.ravel()[order[whole]]])
    g*=np.pi/(4*L*L)
    return {'nu':nu,'grid_L':L,'Tc_bound_D':float(g@np.array([t,tp])),
            'conditional_standard_error_D':float(np.sqrt(g@cov@g)),
            'gradient_wrt_t_tprime':g.tolist()}


def destroy(state,orb):
    if not ((state>>orb)&1):return None
    return state^(1<<orb),(-1)**((state&((1<<orb)-1)).bit_count())


def create(state,orb):
    if (state>>orb)&1:return None
    return state|(1<<orb),(-1)**((state&((1<<orb)-1)).bit_count())


def operator(ops):
    """ops listed in right-to-left action order; 4 physical spin orbitals."""
    mat=np.zeros((16,16))
    for state in range(16):
        s=state;sign=1
        for kind,o in ops:
            out=(create if kind=='+' else destroy)(s,o)
            if out is None:break
            s,sgn=out;sign*=sgn
        else:mat[s,state]+=sign
    return mat


def dimer_check(U,J,V):
    H=np.zeros((16,16))
    for a,b in [(0,2),(1,3)]:
        hop=operator([('-',b),('+',a)])
        H-=t*(hop+hop.T)
    for state in range(16):
        nu=[(state>>i)&1 for i in range(4)]
        n0=nu[0]+nu[1];n1=nu[2]+nu[3]
        H[state,state]+=U*(nu[0]*nu[1]+nu[2]*nu[3])+V*(n0-1)*(n1-1)
    pair=operator([('-',2),('-',3),('+',1),('+',0)])
    H-=J*(pair+pair.T)
    # N=2, Sz=0 sector contains the singlet and Sz=0 triplet.
    sector=[s for s in range(16) if s.bit_count()==2]
    ev=np.linalg.eigvalsh(H[np.ix_(sector,sector)])
    delta=U-V-J
    formula=(np.sqrt(delta*delta+16*t*t)-delta)/2
    return {'U_D':U,'J_pair_D':J,'V_D':V,'two_electron_levels_D':ev.tolist(),
            'lowest_singlet_to_zero_energy_triplet_D':float(-ev[0]),
            'formula_singlet_triplet_D':float(formula),
            'formula_difference':float(-ev[0]-formula),
            'note':'If another pair eigenstate becomes the ground state, this singlet-branch formula is not the physical spin gap; chosen validation points avoid that crossing.'}


def main():
    scans=[curvature_bound(.2,L) for L in [256,512,1024]]
    b=scans[-1]['Tc_bound_D'];nu=.2
    jlower=(1.075-b)/(np.pi*nu)
    result={'physical_degrees_of_freedom':'one spinful electron orbital per site, four local states',
        'conditional_hopping_input':{'t_D':t,'tprime_D':tp,
            'source':'data/sts_prior_spectral_fit_results.json',
            'warning':'Hoppings inferred from a noninteracting high-T DOS fit; not an interaction-independent experimental determination.'},
        'strict_2D_bound_assumptions':['BKT transition','one isolated band with this hopping dispersion',
            'interactions carry no uniform charge current (e.g. onsite U, density interactions, spin exchange)',
            'density n=2nu and canonical fermionic Pauli bound'],
        'curvature_bound_convergence':scans,
        'max_curvature_looser_bound_D':float(np.pi*(2*nu)*(2*t+4*abs(tp))/8),
        'pair_hopping_escape':{'Hamiltonian_term':'-J sum_<ij> (P_i^dagger P_j + h.c.), P_i=c_i,down c_i,up',
            'additional_Tc_bound_D':'pi*abs(J)*min(nu,1-nu)',
            'necessary_J_D_for_Tc_above_1p075_at_nu_0p2':float(jlower),
            'warning':'Necessary loose bound, not a sufficient prediction of superconductivity.'},
        'conditional_repulsive_hubbard':{'U_D':U,'J1_superexchange_D':float(4*t*t/U),
            'J2_superexchange_D':float(4*tp*tp/U),
            'J2_over_J1':float(tp*tp/(t*t)),
            'source':'data/hubbard_gap_fits.json; repulsive 10-site canonical charge-gap match',
            'warning':'Conditional on hopping and finite-cluster gap extraction; not a thermodynamic many-body fit.'},
        'dimer_checks':[dimer_check(U,0,0),dimer_check(U,1.3,0),dimer_check(U,1.3,.65),dimer_check(U,6,2)],
        'atomic_uniform_susceptibility':'chi_s(U,T)=1/[4*T*(1+exp(-U/(2*T)))] at mu=U/2, g*mu_B=1',
        'atomic_NMR_warning':'Atomic spins do not relax because local spin commutes with the atomic Hamiltonian. Static susceptibility cannot be substituted for 1/T1. Weak dynamics may inherit occupation activation but must be calculated.',
        'attractive_strong_coupling_projection':{'pair_density':'nu=n/2',
            'pair_hopping_tB':'J+2*t^2/abs(U)',
            'nearest_pair_repulsion_VB':'4*V+4*t^2/abs(U)',
            'half_filling_pseudospin_isotropy':'VB=2*tB, equivalently V=J/2 for positive J and NN terms',
            'scope':'Leading order in t/|U|; pair hopping and density interactions must not close the eliminated singly-occupied-state gap. tprime generates smaller NNN pair terms.'},
        'references':[
            {'title':'Bounds on the Superconducting Transition Temperature','url':'https://doi.org/10.1103/PhysRevX.9.031049'},
            {'title':'Superconductivity in the Hubbard model with pair hopping','url':'https://arxiv.org/abs/cond-mat/9806088'},
            {'title':'Nature of the quantum phase transitions in the two-dimensional hardcore boson model','url':'https://arxiv.org/abs/cond-mat/0105450'}]}
    (ROOT/'response_constraints.json').write_text(json.dumps(result,indent=2))
    # Bound curves: a bound is not a predicted transition line.
    L=512;k=2*np.pi*(np.arange(L)+.5)/L;x=np.cos(k)[:,None];y=np.cos(k)[None,:]
    c=(t*(x+y)+4*tp*x*y).ravel();c=np.sort(c)[::-1]
    cumul=np.r_[0,np.cumsum(c)]/(L*L)*np.pi/4
    ns=np.linspace(0,1,401);bare=np.interp(ns,np.arange(len(c)+1)/len(c),cumul)
    fig,ax=plt.subplots(figsize=(7.8,4.6),layout='constrained')
    ax.plot(ns,bare,color='#24538a',label='Density interactions only: rigorous bound')
    ax.plot(ns,bare+np.pi*1.3*np.minimum(ns,1-ns),ls='--',color='#8a6624',label=r'Adding $J=1.3D$ pair hopping: loose bound')
    ax.errorbar([.2,.3],[1.1125,.3625],yerr=[.0375,.0375],fmt='o',capsize=4,color='#b7314a',label='Zero-resistance transition brackets')
    ax.set(xlim=(0,1),ylim=(0,2.6),xlabel=r'Filling $\nu=n/2$',ylabel=r'$T/D$',title='One-orbital stiffness constraints, conditional on the fitted hopping')
    ax.text(.03,.96,'Bounds, not predicted phase boundaries',transform=ax.transAxes,va='top',fontsize=10)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.legend(frameon=False,loc='upper right',fontsize=8)
    fig.savefig(ROOT/'response_stiffness_bounds.png',dpi=220)
    print(json.dumps({'Tc_bound_D':b,'conditional_sigma_D':scans[-1]['conditional_standard_error_D'],
                      'pair_J_lower_D':jlower,'dimer_errors':[q['formula_difference'] for q in result['dimer_checks']]},indent=2))


if __name__=='__main__':main()
