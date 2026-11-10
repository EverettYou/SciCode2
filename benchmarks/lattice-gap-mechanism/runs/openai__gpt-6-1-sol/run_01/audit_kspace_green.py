"""Independent allowed-momentum moments and G(0) convergence audit."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/one-orbital-audit-mpl')
from pathlib import Path
import sys,json,time
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import cg
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from electron_ed import Sector
from hubbard_spectra import opvec,lanczos_poles


def main():
    tic=time.time();cfg=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
    U=next(q['U'] for q in cfg['gap_fits'] if q['N']==10 and q['sign']==1)
    p={'t':cfg['t'],'tp':cfg['tp'],'U':U}
    source=Sector(10,5,5);add=Sector(10,6,5);rem=Sector(10,4,5)
    e0=source.ground(p)['energy'];gs=source.v0.copy();ep=add.ground(p)['energy'];em=rem.ground(p)['energy'];mu=(ep-em)/2
    matrices={True:add.matrix(p),False:rem.matrix(p)}
    sitevectors={create:np.array([opvec(source,target,gs,i,create) for i in range(10)])
        for create,target in [(True,add),(False,rem)]}
    out={'N':10,'parameters':p,'E0':e0,'mu_canonical_mid':mu,
         'momenta_exact':True,'definition':'c_k and c_k^dagger are physical electron Fourier operators; complex vectors split into cosine/sine channels for real-symmetric resolvents.',
         'checks':[]}
    for j,k in [(0,[0.,0.]),(1,[.1,-.3]),(2,[.2,.4]),(5,[.5,.5])]:
        # Site label i is x-3y modulo10, so this independently reproduces
        # exp(2 pi i k.r_i) for all four allowed momenta.
        coeff=np.exp(2j*np.pi*j*np.arange(10)/10)/np.sqrt(10)
        epsilon=-2*p['t']*(np.cos(2*np.pi*k[0])+np.cos(2*np.pi*k[1]))-4*p['tp']*np.cos(2*np.pi*k[0])*np.cos(2*np.pi*k[1])
        M0=M1=M2=0.;Gs={200:0.,400:0.};Gcg=0.;cgchecks=[];polechecks=[]
        for create in [True,False]:
            # Creation and annihilation use conjugate Fourier conventions.
            v=(coeff if create else coeff.conj())@sitevectors[create]
            H=matrices[create]
            Hv=H@v
            shifted=Hv-(e0+mu)*v if create else (e0-mu)*v-Hv
            M0+=float(np.vdot(v,v).real);M1+=float(np.vdot(v,shifted).real);M2+=float(np.vdot(shifted,shifted).real)
            # Direct SPD resolvent solve is independent of Lanczos quadrature.
            shift=e0+mu if create else e0-mu
            A=H-shift*sp.eye(H.shape[0],format='csr')
            solution,info=cg(A,v,rtol=1e-12,atol=0,maxiter=3000)
            residual=float(np.linalg.norm(A@solution-v)/np.linalg.norm(v))
            Gcg+=(-1 if create else 1)*float(np.vdot(v,solution).real)
            cgchecks.append({'addition':create,'info':int(info),'relative_residual':residual})
            for real_vector in [v.real,v.imag]:
                if np.linalg.norm(real_vector)<1e-12:continue
                for steps in [200,400]:
                    E,w,a=lanczos_poles(H,real_vector,steps)
                    freq=E-e0-mu if create else e0-E-mu
                    Gs[steps]+=float(np.sum(-w/freq))
                    polechecks.append({'addition':create,'steps':steps,
                        'minimum_absolute_pole_D':float(np.min(abs(freq))),
                        'norm':float(w.sum()),'first_raw_H_moment_error':a['first_moment_error']})
        expected=epsilon+U/2-mu;variance=M2-M1*M1
        record={'k':k,'epsilon_k_D':epsilon,'M0':M0,'M1_D':M1,'M1_exact_D':expected,
            'M1_error_D':M1-expected,'variance_D2':variance,'variance_exact_D2':U*U/4,
            'variance_error_D2':variance-U*U/4,
            'G0_200':Gs[200],'G0_400':Gs[400],'G0_CG':Gcg,
            'G0_difference_200_400':Gs[200]-Gs[400],
            'G0_difference_400_CG':Gs[400]-Gcg,'CG_checks':cgchecks,'pole_checks':polechecks}
        out['checks'].append(record)
        (ROOT/'audit_kspace_green.json').write_text(json.dumps(out,indent=2))
        print('k',k,'G',Gs,Gcg,'M1err',M1-expected,'varerr',variance-U*U/4,flush=True)
    out['maximum_G0_200_400_difference']=max(abs(x['G0_difference_200_400']) for x in out['checks'])
    out['maximum_G0_400_direct_CG_difference']=max(abs(x['G0_difference_400_CG']) for x in out['checks'])
    out['seconds']=time.time()-tic
    (ROOT/'audit_kspace_green.json').write_text(json.dumps(out,indent=2))
    print('done',time.time()-tic,out['maximum_G0_200_400_difference'],out['maximum_G0_400_direct_CG_difference'],flush=True)


if __name__=='__main__':main()
