"""Independent targeted checks of the physical electron ED/spectral pipeline."""
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
os.environ.setdefault('MPLCONFIGDIR','/tmp/one-orbital-audit-mpl')
from pathlib import Path
import sys,json,time
from collections import Counter
import numpy as np
from scipy.sparse.linalg import eigsh
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from electron_ed import Sector
from hubbard_spectra import bonds8,spectrum,DOS,lanczos_poles,opvec
t=.9970683327571924;tp=.19534428112180086


def geometry_checks():
    result=[]
    for N in [8,10]:
        kw={} if N==10 else dict(zip(['nn','nnn'],bonds8()))
        sector=Sector(N,1,0,**kw);H=sector.matrix({'t':t,'tp':tp}).toarray()
        actual=np.linalg.eigvalsh(H)
        if N==10:
            q=2*np.pi*np.arange(10)/10;kx=q;ky=-3*q
        else:
            ks=[(i*np.pi/2,j*np.pi/2) for i in range(4) for j in range(4) if (i-j)%2==0]
            kx,ky=np.array(ks).T
        expected=np.sort(-2*t*(np.cos(kx)+np.cos(ky))-4*tp*np.cos(kx)*np.cos(ky))
        result.append({'N':N,'NN_entries':len(sector.nn),'NN_unique':len(set(sector.nn)),
            'NNN_entries':len(sector.nnn),'NNN_unique':len(set(sector.nnn)),
            'NNN_multiplicities':sorted(Counter(sector.nnn).values()),
            'one_particle_energies_D':actual.tolist(),
            'dispersion_eigenvalue_max_error':float(np.max(abs(actual-expected))),
            'noninteracting_half_charge_gap_D':float(actual[N//2]-actual[N//2-1]),
            'local_band_second_moment_D2':float(np.trace(H@H)/N),
            'note':'8-site repeated NNN image bonds must be retained for the periodic dispersion; they are not an accidental duplication.'})
    return result


def bond_sign_checks():
    p={'t':.71,'tp':0,'U':5.,'J1':1.3,'P':.8,'V1':.4}
    sector=Sector(2,1,1,[(0,1)],[]);actual=np.linalg.eigvalsh(sector.matrix(p).toarray())
    singletblock=np.array([[-p['J1'],-2*p['t']],[-2*p['t'],p['U']-p['P']-p['V1']]])
    expected=np.sort(np.r_[np.linalg.eigvalsh(singletblock),0.,p['U']+p['P']-p['V1']])
    return {'parameters':p,'actual_eigenvalues':actual.tolist(),'analytic_eigenvalues':expected.tolist(),
            'maximum_error':float(np.max(abs(actual-expected))),
            'terms_checked':'hopping fermion signs, onsite U, physical singlet exchange, pair hopping, centered NN density interaction'}


def stored_moment_checks():
    result=[];fits=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
    for f in fits.get('spectral_trials',[]):
        nu=f['nu'];sgn=1 if f['U']>0 else -1;m=round(10*nu)
        name=f'hubbard_spectrum_{sgn}_{m}.npz';z=np.load(ROOT/'data'/name)
        E,w=z['E'],z['w'];U=f['U'];mu=f['audit']['mu_canonical_mid']
        M0=float(w.sum());M1=float(w@E);M2=float(w@(E*E));variance=M2-M1*M1
        expectedM1=U*nu-mu;expectedVariance=4*t*t+4*tp*tp+U*U*nu*(1-nu)
        result.append({'file':name,'U_D':U,'nu':nu,'M0':M0,'M1_D':M1,
            'M1_exact_D':expectedM1,'M1_error_D':M1-expectedM1,
            'M2_D2':M2,'variance_D2':variance,'variance_exact_D2':expectedVariance,
            'variance_error_D2':variance-expectedVariance,
            'occupied_weight':float(w[E<0].sum()),'occupied_weight_exact':nu,
            'pole_weight_min':float(w.min()),
            'note':'Moments of clean Lanczos poles; a finite-window Lorentzian DOS has different/truncated moments.'})
    return result


def warm_start_checks():
    sector=Sector(10,5,5);results=[]
    for U in [12.,-12.,0.]:
        p={'t':t,'tp':tp,'U':U};warm=sector.ground(p);warm_vector=sector.v0.copy()
        H=sector.matrix(p);rng=np.random.default_rng(77801+int(U));v=rng.normal(size=sector.dim);v/=np.linalg.norm(v)
        values,vectors=eigsh(H,k=2,which='SA',v0=v,tol=1e-10,ncv=40,maxiter=5000)
        order=np.argsort(values);values=values[order];vectors=vectors[:,order]
        error=float(warm['energy']-values[0]);residual=float(np.linalg.norm(H@vectors[:,0]-values[0]*vectors[:,0]))
        out={'U_D':U,'warm_energy':warm['energy'],'independent_cold_k2_energies':values.tolist(),
             'ground_energy_difference':error,'warm_residual':warm['residual'],'cold_residual':residual}
        if U==0:
            one=np.array(geometry_checks()[1]['one_particle_energies_D']);exact=2*one[:5].sum()
            out['noninteracting_ground_energy_exact']=float(exact);out['exact_energy_error']=float(values[0]-exact)
        results.append(out);sector.v0=warm_vector
        print('warm/cold',U,error,flush=True)
    return results


def noninteracting_spectrum_check():
    E,w,a=spectrum(10,3,3,{'t':t,'tp':tp,'U':0},steps=80)
    one=np.array(geometry_checks()[1]['one_particle_energies_D']);mu=a['mu_canonical_mid']
    x=np.linspace(-8,8,641);eta=.08
    actual=DOS(x,E,w,eta);expected=DOS(x,one-mu,np.full(10,.1),eta)
    return {'N':10,'nu':.3,'U_D':0.,'mu_D':mu,'eta_D':eta,
            'DOS_max_abs_difference':float(np.max(abs(actual-expected))),
            'DOS_rms_difference':float(np.sqrt(np.mean((actual-expected)**2))),
            'M0':float(w.sum()),'occupied_weight':float(w[E<-1e-7].sum()),
            'note':'Canonical U=0 doped shell is degenerate: some poles lie at zero, so strict E<0 occupied-weight counting need not equal nu. Addition/removal sum still exactly reproduces the complete noninteracting DOS.'}


def lanczos_convergence_check():
    fitted=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
    trial=next(q for q in fitted['spectral_trials'] if q['U']>0 and abs(q['nu']-.3)<1e-8)
    p={'t':t,'tp':tp,'U':trial['U']};source=Sector(10,3,3);target=Sector(10,4,3)
    ground=source.ground(p);v=opvec(source,target,source.v0.copy(),0,True);H=target.matrix(p)
    x=np.linspace(-10,20,1001);mu=trial['audit']['mu_canonical_mid'];curves={};results=[]
    for steps in [80,160,240]:
        E,w,a=lanczos_poles(H,v,steps);freq=E-ground['energy']-mu
        curves[steps]={eta:DOS(x,freq,w,eta) for eta in [.05,.1,.3]}
        results.append({'steps':steps,'audit':a,'M2_error':float(abs(w@(E*E)-(H@v)@(H@v)))})
    differences={}
    for a,b in [(80,160),(160,240)]:
        differences[f'{a}_to_{b}']={str(eta):{'max_abs':float(np.max(abs(curves[a][eta]-curves[b][eta]))),
            'rms':float(np.sqrt(np.mean((curves[a][eta]-curves[b][eta])**2)))} for eta in [.05,.1,.3]}
    return {'N':10,'nu':.3,'U_D':p['U'],'channel':'site0 spin-up addition','steps':results,
            'differences':differences,'ground_energy_reproduction_error':float(ground['energy']-trial['audit']['E0'])}


def main():
    tic=time.time();out={'scope':'Code/finite-cluster audit, not a bulk Hubbard-model rejection',
         'geometry':geometry_checks(),'bond_signs':bond_sign_checks(),'stored_spectral_moments':stored_moment_checks()}
    out['warm_start_crossing_checks']=warm_start_checks()
    (ROOT/'audit_electron_spectra.json').write_text(json.dumps(out,indent=2))
    out['noninteracting_spectrum']=noninteracting_spectrum_check()
    print('noninteracting',out['noninteracting_spectrum'],flush=True)
    out['lanczos_convergence']=lanczos_convergence_check()
    out['seconds']=time.time()-tic
    (ROOT/'audit_electron_spectra.json').write_text(json.dumps(out,indent=2))
    print('complete seconds',time.time()-tic,flush=True)
    print(json.dumps(out['lanczos_convergence']['differences'],indent=2),flush=True)


if __name__=='__main__':main()
