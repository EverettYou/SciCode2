"""Physical one-orbital Hubbard spectra from exact-ground-state Lanczos.

No spectral ansatz or auxiliary orbital is introduced. Finite clusters are
diagnostics, not thermodynamic predictions. Parameters from charge gap alone
are not promoted to a joint fit.
"""
import os
for x in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[x]='1'
from pathlib import Path
import numpy as np,json,time
from scipy.optimize import brentq,least_squares
from scipy.linalg import eigh_tridiagonal
from electron_ed import Sector
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def bonds8():
    key=lambda x,y:((2*x+2*y)%8,(-2*x+2*y)%8)
    coords=[];lookup={}
    for x,y in sorted([(x,y) for x in range(-3,4) for y in range(-3,4)],key=lambda p:p[0]**2+p[1]**2):
        k=key(x,y)
        if k not in lookup:lookup[k]=len(coords);coords.append((x,y))
    assert len(coords)==8
    def bond(ds):return [tuple(sorted((i,lookup[key(x+dx,y+dy)]))) for i,(x,y) in enumerate(coords) for dx,dy in ds]
    return bond([(1,0),(0,1)]),bond([(1,1),(1,-1)])

def gap_sectors(N):
    kw={} if N==10 else dict(zip(['nn','nnn'],bonds8()))
    m=N//2
    return {(a,b):Sector(N,a,b,**kw) for a,b in [(m,m),(m+1,m-1),(m+1,m),(m-1,m)]}

def gaps(ss,p):
    m=next(iter(ss))[0]
    rr={k:s.ground(p) for k,s in ss.items()};E=lambda k:rr[k]['energy']
    e0=E((m,m));em=E((m-1,m));ep=E((m+1,m))
    return {'charge':ep+em-2*e0,'spin':E((m+1,m-1))-e0,'mu':(ep-em)/2,'energies':{str(k):v for k,v in rr.items()}}

def opvec(source,target,v,pos,create):
    occupied=(source.bits>>pos)&1;ids=np.flatnonzero(occupied==(0 if create else 1))
    b=source.bits[ids]^(1<<pos)
    dest=target.ui[b&((1<<source.N)-1)]*target.nD+target.di[b>>source.N]
    signs=1-2*(np.bitwise_count((source.bits[ids]&((1<<pos)-1)).astype(np.uint64))&1).astype(np.int8)
    out=np.zeros(target.dim);out[dest]=v[ids]*signs
    return out

def lanczos_poles(H,v,steps=200):
    weight=float(v@v)
    if weight<1e-14:return np.array([]),np.array([]),{}
    q=v/np.sqrt(weight);prev=np.zeros_like(q);bprev=0.;aa=[];bb=[]
    # Three-term Lanczos quadrature remains positive; convergence tested in eta.
    for n in range(steps):
        z=H@q-bprev*prev;a=float(q@z);z-=a*q
        # Remove round-off along the last two vectors.
        z-=q*(q@z);z-=prev*(prev@z)
        b=float(np.linalg.norm(z));aa.append(a)
        if b<1e-12 or n==steps-1:break
        bb.append(b);prev,q=q,z/b;bprev=b
    ev,vec=eigh_tridiagonal(np.array(aa),np.array(bb),lapack_driver='stev')
    ww=weight*vec[0]**2
    return ev,ww,{'norm':weight,'sum_rule_error':float(abs(ww.sum()-weight)),
                  'first_moment_error':float(abs(ww@ev-v@(H@v))),'iterations':len(aa)}

def spectrum(N,nu,nd,p,steps=200):
    ss=Sector(N,nu,nd);add=Sector(N,nu+1,nd);rem=Sector(N,nu-1,nd)
    e0=ss.ground(p)['energy'];v=ss.v0.copy()
    ep=add.ground(p)['energy'];em=rem.ground(p)['energy'];mu=(ep-em)/2
    energies=[];weights=[];audit=[]
    # Average all sites to avoid choosing a density modulation in a degenerate shell.
    for site in range(N):
        for create,target in [(False,rem),(True,add)]:
            vv=opvec(ss,target,v,site,create)
            ee,ww,a=lanczos_poles(target.matrix(p),vv,steps)
            E=ee-e0-mu if create else e0-ee-mu
            energies.extend(E.tolist());weights.extend((ww/N).tolist());audit.append(a)
    return np.array(energies),np.array(weights),{'E0':e0,'mu_canonical_mid':mu,'nu':nu/N,'checks':audit}

def DOS(x,E,w,eta):
    return np.sum(w[None,:]*eta/np.pi/((x[:,None]-E[None,:])**2+eta**2),axis=1)

def main():
    start=time.time();t=.9970683327571924;tp=.19534428112180086;target=8.00186428295935
    out={'model':'ordinary one-orbital t-tprime-U Hubbard, physical Fock space',
         'charge_target':target,'target_note':'Target gap and .0111D statistical error are from earlier STS spectral extraction, not an exact nonparametric measurement.',
         't':t,'tp':tp,'gap_fits':[]}
    for N in [8,10]:
        ss=gap_sectors(N)
        for sign in [1,-1]:
            cache={}
            def f(u):
                p={'t':t,'tp':tp,'U':sign*u};g=gaps(ss,p);cache[str(u)]=g
                print('gapfit',N,sign,u,g['charge'],g['spin'],flush=True)
                return g['charge']-target
            u=brentq(f,8,15,xtol=2e-5);center=gaps(ss,{'t':t,'tp':tp,'U':sign*u})
            dp=(gaps(ss,{'t':t,'tp':tp,'U':sign*(u+.025)})['charge']-gaps(ss,{'t':t,'tp':tp,'U':sign*(u-.025)})['charge'])/.05
            fit={'N':N,'sign':sign,'U':sign*u,'U_sigma_gap_only':.01109912284569511/abs(dp),'gaps':center,
                 'slope_dgap_dabsU':dp,'trace':cache}
            out['gap_fits'].append(fit);(ROOT/'data/hubbard_gap_fits.json').write_text(json.dumps(out,indent=2))
    # Exact 10-site physical Hubbard spectral diagnostics, both signs of U.
    data=json.load(open(ROOT/'data/measurements.json'))['measurements'][0]['spectra']
    fig,axs=plt.subplots(2,3,figsize=(13,8),sharex=True)
    out['spectral_trials']=[]
    for sign,row in [(1,0),(-1,1)]:
        uf=next(q['U'] for q in out['gap_fits'] if q['N']==10 and q['sign']==sign)
        for col,m in enumerate([5,3,2]):
            p={'t':t,'tp':tp,'U':uf};E,w,audit=spectrum(10,m,m,p)
            x=np.array(data[col]['bias']);y=np.array(data[col]['dI_dV'])
            def model(q):
                eta,A,b0,b2,shift=q
                return A*DOS(x-shift,E,w,eta)+b0+b2*x*x
            if col==0:
                fun=lambda q:model([*q,0])-y
                fit=least_squares(fun,[.3,4.,0.,.0013],bounds=([.05,.1,-.1,-.003],[1.5,15,.2,.005]),max_nfev=80)
                q=np.r_[fit.x,0]
            else:
                best=None
                for sh in [-4,0,4]:
                    fit=least_squares(lambda q:model(q)-y,[.3,4,0,.0013,sh],bounds=([.05,.1,-.1,-.003,-8],[1.5,15,.2,.005,8]),max_nfev=80)
                    if best is None or fit.fun@fit.fun<best.fun@best.fun:best=fit
                fit=best;q=fit.x
            rms=float(np.sqrt(np.mean(fit.fun**2)))
            result={'U':uf,'nu':m/10,'measurement_fit_parameters':q.tolist(),'rms':rms,'spectral_weight':float(w.sum()),
                    'occupied_weight_clean':float(w[E<0].sum()),'audit':audit}
            out['spectral_trials'].append(result)
            np.savez_compressed(ROOT/f'data/hubbard_spectrum_{sign}_{m}.npz',E=E,w=w,bias=x,data=y,fit=model(q),q=q)
            ax=axs[row,col];ax.plot(x,y,color='.65',lw=.7,label='data');ax.plot(x,model(q),color='#295c8f' if sign==1 else '#b55642',lw=1.1,label='physical Hubbard ED')
            ax.set_title(f'U/D={uf:.3f}, nu={m/10:g}; RMS={rms:.3f}',fontsize=10)
            ax.set_ylim(-.04,1.15);ax.set_xlim(-10,10)
            if col==0:ax.set_ylabel('Normalized dI/dV')
            if row==1:ax.set_xlabel('Bias from measured gap midpoint / D')
            ax.legend(frameon=False,fontsize=8)
            print('SPECTRUM',sign,m,rms,'q',q,flush=True)
            out['seconds']=time.time()-start;(ROOT/'data/hubbard_gap_fits.json').write_text(json.dumps(out,indent=2))
    fig.suptitle('Actual single-orbital Hubbard spectra: finite 10-site diagnostic, not a validated material fit',fontsize=13)
    fig.tight_layout();fig.savefig(ROOT/'figures/hubbard_ed_sts.png',dpi=210)
    print('done',time.time()-start,flush=True)

if __name__=='__main__':main()
