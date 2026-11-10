"""Exact physical-current Kubo benchmark: six-site open square-lattice patch.

All 924 states at Ne=6, all Sz sectors. No auxiliary orbitals. D=hbar=e=a=1.
The open cluster has zero charge stiffness. Broadening is a display/numerical
parameter, not an inferred physical scattering rate or a controlled dc limit.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/model-review-mpl')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import json,itertools
import numpy as np
from scipy.linalg import eigh
from scipy.sparse import csr_matrix
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'data/measurements.json'
NS=6;NX=3;NY=2;NE=6;t=.9970683327571924;tp=.19534428112180086;U=11.493525192155293

def hop(state,src,dst):
    if not (state>>src)&1 or (state>>dst)&1:return None
    a=state^(1<<src)
    sign=(-1)**((state&((1<<src)-1)).bit_count()+ (a&((1<<dst)-1)).bit_count())
    return a|(1<<dst),sign

def build():
    basis=np.array([sum(1<<i for i in b) for b in itertools.combinations(range(2*NS),NE)])
    lookup={int(s):i for i,s in enumerate(basis)};dim=len(basis)
    pos=np.array([(i%NX,i//NX) for i in range(NS)])
    bonds=[]
    for i in range(NS):
        for j in range(i+1,NS):
            dx,dy=pos[j]-pos[i]
            if abs(dx)+abs(dy)==1:bonds.append((i,j,t,int(dx),'NN'))
            elif abs(dx)==1 and abs(dy)==1:bonds.append((i,j,tp,int(dx),'NNN'))
    H=np.zeros((dim,dim));A=np.zeros_like(H);K=np.zeros_like(H)
    X=np.zeros(dim)
    for col,ss in enumerate(basis):
        s=int(ss)
        H[col,col]=U*sum(((s>>i)&1)*((s>>(i+NS))&1) for i in range(NS))
        X[col]=sum(pos[i,0]*(((s>>i)&1)+((s>>(i+NS))&1)) for i in range(NS))
        for i,j,tij,dx,kind in bonds:
            for spin in (0,1):
                a=i+spin*NS;b=j+spin*NS
                for src,dst,current_sign in [(b,a,-1),(a,b,1)]:
                    hit=hop(s,src,dst)
                    if hit is not None:
                        row=lookup[hit[0]];sgn=hit[1]
                        H[row,col]+=-tij*sgn
                        A[row,col]+=current_sign*tij*dx*sgn
                        K[row,col]+=tij*dx*dx*sgn
    # J=iA=i[H,X]; K=d2H(A)/dA2 from the Peierls phases.
    comm=H*(X[None,:]-X[:,None])
    assert np.max(np.abs(A-comm))<1e-12
    assert np.max(np.abs(H-H.T))<1e-12
    assert np.max(np.abs(A+A.T))<1e-12
    return H,csr_matrix(A),csr_matrix(K),bonds

def main():
    H,A,K,bonds=build();E,Q=eigh(H,driver='evd',overwrite_a=True)
    E-=E[0]
    Ae=Q.T@(A@Q);kdiag=np.sum(Q*(K@Q),axis=0)
    m,n=np.triu_indices(len(E),k=1);de=E[n]-E[m];j2=Ae[m,n]**2
    select=(de>1e-9)&(j2>1e-20);m=m[select];n=n[select];de=de[select];j2=j2[select]
    source=json.loads(SOURCE.read_text())
    rho=next(z for z in source['measurements'] if z['experiment']=='resistivity')['samples'][0]
    temps=np.array(rho['temperature']);observed=np.array(rho['resistivity']);unc=np.array(rho['uncertainty'])
    etas=np.array([.025,.05,.1,.2,.4,.8]);dc=np.zeros((len(etas),len(temps)))
    stiffness=[];diamag=[];sumrule=[]
    def weights(T):
        p=np.exp(-E/T);p/=p.sum()
        w=(p[m]-p[n])*j2/de
        return p,w
    for z,T in enumerate(temps):
        p,w=weights(T)
        kval=float(p@kdiag);chistat=float(2*w.sum())
        stiffness.append(float(np.pi/NS*(kval-chistat)))
        diamag.append(kval)
        sumrule.append(float(abs(kval-chistat)/max(abs(kval),1e-15)))
        for k,eta in enumerate(etas):
            # Both +/- transition peaks: positive-frequency integrated sum rule
            # remains exactly pi<K>/(2N) under this even Lorentzian broadening.
            dc[k,z]=2/NS*np.sum(w*eta/(de*de+eta*eta))
    nr=(1/dc)/(1/dc[:,-1,None])
    freqs=np.linspace(0,20,1201);specT=np.array([.45,1.,2.,4.]);eta_display=.15
    spectra=[]
    for T in specT:
        _,w=weights(T);spec=np.zeros_like(freqs)
        for start in range(0,len(de),2000):
            d=de[start:start+2000,None];ww=w[start:start+2000,None]
            kernel=eta_display/((freqs[None,:]-d)**2+eta_display**2)+eta_display/((freqs[None,:]+d)**2+eta_display**2)
            spec+=np.sum(ww*kernel,axis=0)/NS
        spectra.append(spec)
    spectra=np.array(spectra)
    # Diagnostic eta->0 scaling at the actual lowest measured temperature.
    tiny=np.array([.0005,.001,.002,.005,.01,.02,.05,.1,.2,.4,.8]);sc=[]
    for T in [.45,4.]:
        _,w=weights(T)
        sc.append([float(2/NS*np.sum(w*eta/(de*de+eta*eta))) for eta in tiny])
    out={'status':'exact open-cluster physical-current benchmark; not a bulk transport fit',
         'geometry':{'Nx':NX,'Ny':NY,'boundary':'open in x and y','sites':NS,'electrons':NE,
                     'all_Sz_sectors':True,'Hilbert_dimension':len(E),'bonds':[list(b) for b in bonds]},
         'Hamiltonian':'-sum_ij,sigma t_ij(c_i^dag c_j+h.c.)+U sum_i n_iup n_idown',
         'parameters_D':{'t':t,'tprime':tp,'U':U},
         'current':'Jx=i sum_ij,sigma t_ij(x_j-x_i)(c_j^dag c_i-c_i^dag c_j)',
         'diamagnetic':'Kx=sum_ij,sigma t_ij(x_j-x_i)^2(c_i^dag c_j+c_j^dag c_i)',
         'conductivity_convention':'sigma_reg(w>0)=pi/N sum_m<n (p_m-p_n)|J_mn|^2/(En-Em) delta(w-(En-Em))',
         'exact_static_open_cluster_Drude_coefficient_max_abs':float(np.max(np.abs(stiffness))),
         'f_sum_rule_max_relative_error':float(max(sumrule)),
         'display_broadening_eta_D':eta_display,'eta_values_D':etas.tolist(),
         'temperature_D':temps.tolist(),'normalized_rho_from_inverse_broadened_sigma0':nr.tolist(),
         'experimental_normalized_rho':observed.tolist(),'experimental_uncertainty':unc.tolist(),
         'small_eta_test':{'etas':tiny.tolist(),'temperatures':[.45,4.],'sigma0':sc},
         'limitations':['U=11.493525192155293 is the 10-site charge-gap-matched baseline; parameters were not jointly fitted.',
                        'Open finite cluster has exactly zero stiffness because a uniform vector potential is pure gauge.',
                        'All optical peaks are discrete. Lorentzian tails produce artificial subgap dc response.',
                        'eta is not a measured scattering rate. Its zero limit on this cluster is not the bulk dc limit.',
                        'No activation energy is substituted for a current-current response.']}
    (ROOT/'transport_kubo_results.json').write_text(json.dumps(out,indent=2))
    np.savez_compressed(ROOT/'transport_kubo_data.npz',eigenvalues=E,temperature=temps,eta=etas,sigma0=dc,
                        rho_normalized=nr,omega=freqs,spectra=spectra,spectra_temperature=specT,
                        current_transition_energies=de,current_matrix_element_squared=j2)
    plot(out,freqs,spectra,specT,temps,nr,observed,unc,tiny,np.array(sc))
    print(json.dumps({'dimension':len(E),'Dmax':max(abs(np.array(stiffness))),'sumrule_error':max(sumrule),
                      'rho_Tlowest_by_eta':dict(zip(map(str,etas),nr[:,0].tolist())),
                      'measured_rho_Tlowest':observed[0]},indent=2))

def plot(out,w,spectra,specT,temps,nr,observed,unc,tiny,sc):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,'axes.labelsize':10,'savefig.dpi':300})
    fig,axes=plt.subplots(1,3,figsize=(13,4.7),gridspec_kw={'width_ratios':[1.08,1.1,1]})
    fig.subplots_adjust(left=.065,right=.985,bottom=.24,top=.76,wspace=.34)
    fig.suptitle('Physical-current transport on a six-site Hubbard cluster',x=.065,ha='left',y=.97,fontsize=16,fontweight='bold',color='#173C55')
    fig.text(.065,.87,f'3 × 2 open Hubbard patch, 924 states, U={U:.3f}D; exact finite-cluster response, not a bulk transport fit',fontsize=10.5,color='#A95029')
    colors=['#1C4C68','#358B9A','#D1A54B','#BC6439']
    ax=axes[0]
    for i,T in enumerate(specT):ax.plot(w,spectra[i],color=colors[i],lw=1.5,label=rf'$T={T:g}D$')
    ax.set(xlim=(0,20),ylim=(0,None),xlabel=r'Frequency $\omega/D$',ylabel=r'$\mathrm{Re}\,\sigma_{xx}^{\rm reg}(\omega)$')
    ax.set_title('(a) Optical conductivity',loc='left');ax.legend(frameon=False,fontsize=8)
    ax.text(.97,.94,r'$\eta=0.15D$',transform=ax.transAxes,ha='right',fontsize=9)
    ax=axes[1]
    ax.errorbar(temps,observed,yerr=unc,fmt='.',color='black',ms=3,lw=.6,label='Half-filled measurements',zorder=5)
    for i,eta in enumerate(out['eta_values_D']):
        if eta in [.025,.1,.4,.8]:ax.plot(temps,nr[i],lw=1.4,label=rf'Cluster, $\eta={eta:g}D$')
    ax.set(yscale='log',ylim=(.4,3000),xlabel=r'Temperature $T/D$',ylabel=r'$\rho(T)/\rho(4D)$')
    ax.set_title(r'(b) Inverse broadened $\sigma(0)$',loc='left');ax.legend(frameon=False,fontsize=7.8,loc='upper right')
    ax=axes[2]
    for i,T in enumerate([.45,4.]):ax.loglog(tiny,sc[i],'-o',color=colors[i],ms=3,lw=1.5,label=rf'$T={T:g}D$')
    ax.set(xlabel=r'Artificial broadening $\eta/D$',ylabel=r'$\sigma_{xx}(0;\eta)$')
    ax.set_title('(c) Artificial dc response vanishes',loc='left');ax.legend(frameon=False,fontsize=9)
    ax.text(.05,.93,r'$\sigma(0;\eta)\to0$ as $\eta\to0$',transform=ax.transAxes,fontsize=10,va='top')
    for ax in axes:ax.spines[['top','right']].set_visible(False)
    fig.text(.065,.115,'The current operator is derived from the same physical-electron Hamiltonian. No charge gap is substituted for conductivity.',fontsize=10,color='#173C55')
    fig.text(.065,.055,'Open boundaries give zero Drude weight. Lorentzian tails create artificial subgap response; a scattering rate and the bulk limit are not determined here.',fontsize=9.5,color='#53636D')
    fig.savefig(ROOT/'transport_kubo.png');plt.close(fig)

if __name__=='__main__':main()
