"""Physical U-J1-J2 search against explicitly provisional finite-cluster proxies.

NMR activation scales are NOT identified with ED triplet gaps by this script.
This is a candidate-generating diagnostic, not a joint experimental fit.
"""
from pathlib import Path
import os,sys,time,json
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/model-review-mpl')
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'code'))
from electron_ed import Sector

t=.9970683327571924;tp=.19534428112180086
TARGET=np.array([8.,5.54,2.63,1.75])
NAMES=['half_charge','half_spin','nu0p3_spin','nu0p2_spin']
PARAMS=['U','J1','J2']


def main():
    start=time.time()
    keys=[(5,5),(6,4),(5,4),(6,5),(3,3),(4,2),(2,2),(3,1)]
    sectors={key:Sector(10,*key) for key in keys}
    cache={};trace=[]
    def calc(x):
        token=tuple(float(z) for z in x)
        if token in cache:return cache[token]
        p={'t':t,'tp':tp,**dict(zip(PARAMS,token))}
        rr={key:sec.ground(p) for key,sec in sectors.items()}
        E=lambda k:rr[k]['energy']
        obs=lambda k:np.array([rr[k]['observables'][name] for name in ['D','J1','J2']])
        gaps=np.array([E((6,5))+E((5,4))-2*E((5,5)),E((6,4))-E((5,5)),
                       E((4,2))-E((3,3)),E((3,1))-E((2,2))])
        jac=np.array([obs((6,5))+obs((5,4))-2*obs((5,5)),obs((6,4))-obs((5,5)),
                      obs((4,2))-obs((3,3)),obs((3,1))-obs((2,2))])
        row={'parameters':p,'proxy_values':dict(zip(NAMES,map(float,gaps))),
             'residuals_D':(gaps-TARGET).tolist(),'sum_squared_proxy_residuals':float(np.sum((gaps-TARGET)**2)),
             'max_eigensolver_residual':max(v['residual'] for v in rr.values()),
             'seconds':time.time()-start}
        trace.append(row);cache[token]=(gaps,jac,rr)
        if len(trace)%5==0:print('eval',len(trace),row,flush=True)
        return cache[token]
    runs=[]
    for initial in ([4.,4.,2.],[8.,5.,2.]):
        fit=least_squares(lambda x:calc(x)[0]-TARGET,initial,jac=lambda x:calc(x)[1],
                          bounds=([-8,0,0],[16,12,12]),max_nfev=80,
                          ftol=1e-7,xtol=1e-7,gtol=1e-7,x_scale=[8,4,4])
        values,jac,rr=calc(fit.x)
        runs.append({'initial':initial,'parameters':{'t':t,'tp':tp,**dict(zip(PARAMS,map(float,fit.x)))},
                     'values':dict(zip(NAMES,map(float,values))),'residuals_D':(values-TARGET).tolist(),
                     'rms_proxy_mismatch_D':float(np.sqrt(np.mean((values-TARGET)**2))),
                     'nfev':fit.nfev,'njev':fit.njev,'status':fit.status,'message':fit.message,
                     'active_mask':fit.active_mask.tolist(),'jacobian':jac.tolist(),
                     'jacobian_singular_values':np.linalg.svd(jac,compute_uv=False).tolist()})
        print('RUN_COMPLETE',runs[-1],flush=True)
    best=min(runs,key=lambda r:r['rms_proxy_mismatch_D']);p=best['parameters']
    energies={};obs={}
    for N in [0,2,4,6,8,10]:
        if N==0:energies[str(N)]=0.;continue
        key=(N//2,N//2)
        sec=sectors.get(key) or Sector(10,*key)
        r=sec.ground(p)
        energies[str(N)]=r['energy'];obs[str(N)]=r['observables']
    pts=[(int(n),e) for n,e in energies.items()];hull=[]
    for point in pts:
        while len(hull)>1:
            a,b=hull[-2:]
            if (b[1]-a[1])/(b[0]-a[0]) >= (point[1]-b[1])/(point[0]-b[0]):hull.pop()
            else:break
        hull.append(point)
    curv={str(N):energies[str(N+2)]+energies[str(N-2)]-2*energies[str(N)] for N in [2,4,6,8]}
    above={}
    for n,e in pts:
        for a,b in zip(hull[:-1],hull[1:]):
            if a[0]<=n<=b[0]:
                line=a[1]+(b[1]-a[1])*(n-a[0])/(b[0]-a[0]);above[str(n)]=e-line;break
    out={'status':'finite-cluster proxy optimization; NOT a physical joint fit',
         'physical_model':'single-orbital t-tprime-U-J1-J2, J bonds multiply S.S-nn/4',
         'cluster':'10-site tilted square torus, (3,1),(-1,3)',
         'targets':dict(zip(NAMES,TARGET.tolist())),
         'critical_caveat':'ED triplet gaps are not measured NMR activation energies; charge-gap target is conditional spectral extraction.',
         'objective':'Unweighted sum of squared proxy residuals in D; no likelihood or confidence intervals inferred.',
         'runs':runs,'best':best,'ground_energies_even_N':energies,'ground_observables_even_N':obs,
         'pair_step_energy_curvature':curv,'lower_convex_hull_even_N':hull,'energy_above_convex_hull':above,
         'convexity_caveat':'Finite-cluster convexity is a screening diagnostic; negative curvature can include pairing/shell effects and is not alone thermodynamic phase separation.',
         'trace':trace,'seconds':time.time()-start}
    (ROOT/'extended_proxy_results.json').write_text(json.dumps(out,indent=2))
    if best['rms_proxy_mismatch_D']<1.:
        spectral_check(out)
    print('FINAL',json.dumps({'best':best,'curvature':curv,'hull':hull,'seconds':time.time()-start}),flush=True)


def spectral_check(out):
    from hubbard_spectra import spectrum,DOS
    import matplotlib.pyplot as plt
    samples=json.loads((ROOT/'data/measurements.json').read_text())['measurements'][0]['spectra']
    p=out['best']['parameters'];checks=[]
    fig,axes=plt.subplots(1,3,figsize=(13,4.5))
    for col,m in enumerate([5,3,2]):
        poles,weight,audit=spectrum(10,m,m,p,steps=220)
        x=np.array(samples[col]['bias']);y=np.array(samples[col]['dI_dV'])
        def model(q):
            eta,amp,b0,b2,shift=q
            return amp*DOS(x-shift,poles,weight,eta)+b0+b2*x*x
        if m==5:
            fit=least_squares(lambda q:model([*q,0])-y,[.2,4,0,.0013],
                              bounds=([.04,.1,-.1,-.003],[1.5,15,.2,.005]),max_nfev=80)
            q=np.r_[fit.x,0]
        else:
            fits=[least_squares(lambda q:model(q)-y,[.2,4,0,.0013,shift],
                                bounds=([.04,.1,-.1,-.003,-8],[1.5,15,.2,.005,8]),max_nfev=80) for shift in [-4,0,4]]
            fit=min(fits,key=lambda z:z.fun@z.fun);q=fit.x
        rms=float(np.sqrt(np.mean(fit.fun**2)))
        checks.append({'nu':m/10,'observational_parameters_eta_amp_b0_b2_shift':q.tolist(),
                       'rms':rms,'spectral_weight':float(weight.sum()),
                       'occupied_weight':float(weight[poles<0].sum()),'audit':audit})
        np.savez_compressed(ROOT/f'extended_spectrum_nu{m}.npz',poles=poles,weight=weight,bias=x,data=y,fit=model(q))
        ax=axes[col];ax.plot(x,y,color='.65',lw=.8,label='Measurements');ax.plot(x,model(q),color='#1C5472',label='Physical-electron ED')
        ax.set(title=rf'$\nu={m/10:g}$; RMS={rms:.3f}',xlabel='Bias / D',xlim=(-10,10),ylim=(-.04,1.12));ax.legend(frameon=False,fontsize=8)
        if col==0:ax.set_ylabel('Normalized dI/dV')
        print('SPECTRAL_CHECK',checks[-1],flush=True)
    fig.suptitle('Extended physical-electron Hamiltonian selected by gap proxies: an independent STS test',fontsize=13)
    fig.tight_layout();fig.savefig(ROOT/'extended_sts_check.png',dpi=250);plt.close(fig)
    out['physical_STS_checks']=checks
    (ROOT/'extended_proxy_results.json').write_text(json.dumps(out,indent=2))


if __name__=='__main__':main()
