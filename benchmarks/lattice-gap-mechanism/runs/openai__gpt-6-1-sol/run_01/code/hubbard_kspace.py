"""Physical finite-cluster electron Green functions; NOT a material fit.

Allowed momenta are exact. Continuous maps use explicitly disclosed positive
plane-wave projection and two choices of the finite-cluster embedding.
"""
import os
for name in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[name]='1'
import json,time
from pathlib import Path
import numpy as np
from scipy.ndimage import label
from electron_ed import Sector
from hubbard_spectra import opvec,lanczos_poles
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def coords10():
    out={}
    for x,y in sorted([(x,y) for x in range(-5,6) for y in range(-5,6)],key=lambda p:(p[0]**2+p[1]**2,p)):
        i=(x-3*y)%10
        if i not in out:out[i]=(x,y)
    return np.array([out[i] for i in range(10)])

def kweights(k,K,coords):
    # Average equivalent embeddings. Input spectra are separately C4 averaged.
    ans=np.zeros((len(k),len(K)))
    r=coords.copy()
    for _ in range(4):
        amp=np.exp(2j*np.pi*np.einsum('aki,ni->akn',k[:,None,:]-K[None,:,:],r)).mean(axis=-1)
        ans+=abs(amp)**2/4
        r=np.column_stack((-r[:,1],r[:,0]))
    assert np.max(abs(ans.sum(axis=1)-1))<1e-12
    return ans

def gamma_fraction(field):
    n=field.shape[0];m=n//2;mask=field*field[m,m]>0
    lab,_=label(np.tile(mask,(3,3)))
    center=lab[n+m,n+m]
    return float(np.mean(lab[n:2*n,n:2*n]==center))

def main():
    start=time.time();cfg=json.load(open(ROOT/'data/hubbard_gap_fits.json'))
    U=next(q['U'] for q in cfg['gap_fits'] if q['N']==10 and q['sign']==1)
    p={'t':cfg['t'],'tp':cfg['tp'],'U':U};coords=coords10()
    K=np.array([(j/10,(-3*j/10)%1) for j in range(10)])
    kpath=np.vstack([np.column_stack((np.linspace(0,.5,61),np.zeros(61))),
                     np.column_stack((np.full(60,.5),np.linspace(0,.5,61)[1:])),
                     np.column_stack((np.linspace(.5,0,61)[1:],np.linspace(.5,0,61)[1:]))])
    W=kweights(kpath,K,coords);omega=np.linspace(-11,11,601);eta=.3
    fig,axes=plt.subplots(1,3,figsize=(12.5,5.2),sharey=True)
    allout={'parameters':p,'N':10,'eta':eta,'momenta':K.tolist(),'embedding':coords.tolist(),
      'warning':'Finite-cluster Hubbard benchmark, not validated against measurements. Continuous k uses a positive finite-window projection, not the thermodynamic Green function.','spectra':[]}
    for col,m in enumerate([5,3,2]):
        source=Sector(10,m,m);add=Sector(10,m+1,m);rem=Sector(10,m-1,m)
        e0=source.ground(p)['energy'];gs=source.v0.copy();ep=add.ground(p)['energy'];em=rem.ground(p)['energy'];mu=(ep-em)/2
        mats={True:add.matrix(p),False:rem.matrix(p)}
        vv={create:np.array([opvec(source,sec,gs,i,create) for i in range(10)]) for create,sec in [(True,add),(False,rem)]}
        poles=[];A=[];G=[];checks=[]
        for kval in K:
            coeff=np.exp(2j*np.pi*(coords@kval))/np.sqrt(10)
            ee=[];ww=[]
            for create in [True,False]:
                v=coeff@vv[create]
                for vreal in [v.real,v.imag]:
                    E,w,a=lanczos_poles(mats[create],vreal,240)
                    if len(E):
                        ee.extend((E-e0-mu if create else e0-E-mu).tolist());ww.extend(w.tolist());checks.append(a)
            E=np.array(ee);w=np.array(ww);poles.append((E,w))
            A.append(np.sum(w[None,:]*eta/np.pi/((omega[:,None]-E)**2+eta**2),axis=1))
            G.append(float(np.sum(-w/E)))
        A=np.array(A);G=np.array(G)
        # A degenerate finite-cluster ground vector can select one orientation.
        # Average the density matrix over C4: j -> 3j mod 10 for these momenta.
        orbit=np.array([np.arange(10)*(3**n)%10 for n in range(4)])
        rawA=A.copy();rawG=G.copy();A=A[orbit].mean(axis=0);G=G[orbit].mean(axis=0)
        projected=W@A
        ax=axes[col];im=ax.imshow(projected.T,origin='lower',aspect='auto',extent=(0,3,-11,11),cmap='magma',vmin=0,vmax=.65)
        ax.axhline(0,color='w',lw=.6,alpha=.7);ax.set_xticks([0,1,2,3],['Γ','X','M','Γ']);ax.set_title(f'ν = {m/10:g}');ax.set_xlabel('Requested path (equal segment lengths)')
        for tick in [1,2]:ax.axvline(tick,color='w',ls=':',lw=.5,alpha=.5)
        if col==0:ax.set_ylabel('ω / D from canonical midgap μ')
        spec={'nu':m/10,'mu':mu,'G0_allowed_momenta':G.tolist(),'sum_rule_maxerr':float(max(abs(w.sum()-1) for E,w in poles))}
        np.savez_compressed(ROOT/f'data/hubbard_kspace_{m}.npz',K=K,coords=coords,omega=omega,A_allowed=A,kpath=kpath,A_path=projected,G0_allowed=G,A_raw_ground_vector=rawA,G0_raw_ground_vector=rawG)
        if m==5:
            n=241;grid=np.linspace(-.5,.5,n,endpoint=False);xx,yy=np.meshgrid(grid,grid,indexing='ij');pts=np.column_stack((xx.ravel(),yy.ravel()))
            emb2=coords.copy();emb2[2]+=[3,1]
            fields=[(kweights(pts,K,c)@G).reshape(n,n) for c in [coords,emb2]]
            fz,az=plt.subplots(1,2,figsize=(10,4.9));fractions=[]
            for axz,F,name in zip(az,fields,['Shortest representatives','One representative shifted by a period']):
                fraction=gamma_fraction(F);fractions.append(fraction)
                vmax=max(abs(F.min()),abs(F.max()));z=axz.imshow(F.T,origin='lower',extent=(-.5,.5,-.5,.5),cmap='coolwarm',vmin=-vmax,vmax=vmax)
                axz.contour(grid,grid,F.T,levels=[0],colors='k',linewidths=1)
                displayK=(K+.5)%1-.5;axz.scatter(displayK[:,0],displayK[:,1],s=25,c=G,cmap='coolwarm',vmin=-vmax,vmax=vmax,edgecolors='k',lw=.5)
                axz.plot(0,0,'k+',ms=9);axz.set_xlabel('kx / (2π/a)');axz.set_ylabel('ky / (2π/a)');axz.set_title(f'{name}\nΓ-connected fraction = {fraction:.3f}',fontsize=10)
                fz.colorbar(z,ax=axz,label='Re G(k,0) / D⁻¹',shrink=.8)
            fz.suptitle('Same exact 10 momentum values; different continuous zero contours',fontsize=12)
            fz.tight_layout(rect=[0,0,1,.94]);fz.savefig(ROOT/'figures/hubbard_zero_embedding.png',dpi=210)
            spec['Gamma_fraction_two_embeddings']=fractions
            spec['zero_note']='No statistical material error bar: embedding sensitivity is a systematic diagnostic. Neither number is a validated material prediction.'
            np.savez_compressed(ROOT/'data/hubbard_zero_embedding.npz',grid=grid,fields=np.array(fields),G0_allowed=G,K=K)
        allout['spectra'].append(spec);print(spec,flush=True)
    fig.suptitle('Single-orbital Hubbard: physical-electron spectral benchmark\nContinuous path is a finite-window projection; NOT a joint fit to the material',fontsize=12)
    fig.subplots_adjust(top=.79,right=.91,wspace=.12,bottom=.13);cax=fig.add_axes([.93,.16,.015,.60]);fig.colorbar(im,cax=cax,label='A(k,ω), per spin / D⁻¹')
    fig.savefig(ROOT/'figures/hubbard_arpes_benchmark.png',dpi=210)
    allout['seconds']=time.time()-start;(ROOT/'data/hubbard_kspace_results.json').write_text(json.dumps(allout,indent=2))
    print('complete',time.time()-start,flush=True)

if __name__=='__main__':main()
