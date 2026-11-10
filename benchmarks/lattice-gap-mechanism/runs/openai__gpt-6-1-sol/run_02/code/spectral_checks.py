"""Causal half-filled spectral reconstruction and independent KK checks.

This is a conditional spectral model, not a fitted microscopic interaction model.
All momenta are in the units used in the supplied prompt.
"""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/layered-oxide-mpl')
from pathlib import Path
import json
import numpy as np
from scipy.integrate import simpson
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm, PowerNorm

ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.facecolor':'white'})
normal=np.load(ROOT/'data/sts_normal_fit.npz')
half=np.load(ROOT/'data/sts_half_linear_weights.npz')
t,tp=normal['params'][:2]
s,V,r,eta,amp,b0,b2=half['params']

def bare(kx,ky):
    cx,cy=np.cos(2*np.pi*kx),np.cos(2*np.pi*ky)
    return -2*t*(cx+cy)-4*tp*cx*cy

def poles(kx,ky,shift=False):
    e=bare(kx+(.5 if shift else 0),ky+(.5 if shift else 0))
    d=s*(e+4*tp)
    E=np.stack([d-V,d+V],axis=-1)
    w=np.stack([.5-r*e,.5+r*e],axis=-1)
    return E,w

def spectral(omega,E,w,broadening):
    return np.sum(w[None,...]*broadening/np.pi/
                  ((omega[:,None,None]-E[None,...])**2+broadening**2),axis=-1)

def kpath(n=180):
    p=np.linspace(0,1,n,endpoint=False)
    kx=np.r_[p*.5,np.full(n,.5),(1-p)*.5,0]
    ky=np.r_[p*0,p*.5,(1-p)*.5,0]
    dist=np.r_[0,np.cumsum(np.hypot(np.diff(kx),np.diff(ky)))]
    ticks=[0,.5,1,1+np.sqrt(.5)]
    return kx,ky,dist,ticks

def run():
    kx,ky,dist,ticks=kpath()
    E,w=poles(kx,ky)
    omega=np.linspace(-10,10,1601)
    A=spectral(omega,E,w,eta)
    E2,w2=poles(kx,ky,True); A2=spectral(omega,E2,w2,eta)
    fig,axs=plt.subplots(1,2,figsize=(12.1,5.6),sharey=True)
    for ax,aa,title in zip(axs,[A,A2],['A. Fitted momentum assignment','B. Shift by (1/2, 1/2): identical local STS']):
        im=ax.pcolormesh(dist,omega,aa,shading='auto',cmap='magma',norm=PowerNorm(.6,vmin=0,vmax=3.1),rasterized=True)
        ax.axhline(0,color='white',ls=':',lw=.6)
        for q in ticks[1:-1]:ax.axvline(q,color='white',lw=.5,alpha=.5)
        ax.set_xticks(ticks,[r'$\Gamma$','X','M',r'$\Gamma$'])
        ax.set_title(title,fontsize=11,pad=10)
        ax.set_xlabel('Momentum path')
    axs[0].set_ylabel(r'Energy relative to gap midpoint, $\omega/D$')
    fig.suptitle('Half-filled ARPES: a successful local fit does not fix its momentum assignment',fontsize=14,y=.99)
    fig.colorbar(im,ax=axs,fraction=.025,pad=.025,label=r'$A_c(\mathbf{k},\omega)$ per spin ($D^{-1}$)')
    fig.subplots_adjust(top=.87,bottom=.13,left=.07,right=.89,wspace=.10)
    fig.savefig(ROOT/'figures/half_arpes_nonuniqueness.png',dpi=220)
    np.savez_compressed(ROOT/'data/half_arpes.npz',omega=omega,kx=kx,ky=ky,distance=dist,
                        spectral=A,shifted_spectral=A2,energies=E,weights=w)

    # Numerical principal-value KK integral of the *broadened* spectrum.
    # Pair +/- omega, removing the singularity analytically at omega=0.
    j=np.arange(0,len(kx),9)
    Ek,wk=E[j],w[j]
    checks=[]
    for cutoff,nw in [(24,12001),(40,20001),(80,40001)]:
        om=np.linspace(0,cutoff,nw)
        ap=spectral(om,Ek,wk,eta);am=spectral(-om,Ek,wk,eta)
        integrand=np.empty_like(ap)
        integrand[1:]=(am[1:]-ap[1:])/om[1:,None]
        derivative=np.sum(wk*(2*eta*Ek)/(np.pi*(Ek**2+eta**2)**2),axis=-1)
        integrand[0]=-2*derivative
        gkk=simpson(integrand,x=om,axis=0)
        gd=np.sum(wk/(-Ek+1j*eta),axis=-1).real
        checks.append({'cutoff':cutoff,'omega_points_positive':nw,
                       'max_absolute_error':float(np.max(np.abs(gkk-gd))),
                       'rms_error':float(np.sqrt(np.mean((gkk-gd)**2)))})
    gzero=np.sum(w/(-E),axis=-1)
    gridchecks=[]
    for nk in [128,256,512,1024,2048]:
        kval=(np.arange(nk)+.5)/nk-.5
        xx,yy=np.meshgrid(kval,kval,indexing='ij')
        ee,ww=poles(xx,yy)
        gg=np.sum(-ww/ee,axis=-1)
        gamma_sign=float(np.sum(-poles(np.array(0.),np.array(0.))[1]/poles(np.array(0.),np.array(0.))[0]))
        frac=float(np.mean(gg*gamma_sign>0))
        gridchecks.append({'nk':nk,'Gamma_side_fraction':frac,
                           'occupation_per_spin':float(ww[...,0].mean()),
                           'max_sum_rule_error':float(np.max(np.abs(ww.sum(-1)-1))),
                           'minimum_weight':float(ww.min())})
    nk=600;kval=(np.arange(nk)+.5)/nk-.5
    xx,yy=np.meshgrid(kval,kval,indexing='xy')
    ee,ww=poles(xx,yy);gg=np.sum(-ww/ee,axis=-1)
    fig,axs=plt.subplots(1,2,figsize=(11.7,4.8))
    axs[0].plot(dist,gzero,color='#174b7e',lw=2,label=r'Pole sum, $\eta=0$')
    axs[0].plot(dist,np.sum(w/(-E+1j*eta),axis=-1).real,color='#c47b2b',lw=1.2,label=r'Direct resolvent, fitted $\eta$')
    axs[0].scatter(dist[j],gkk,facecolors='none',edgecolors='#152a3c',s=22,label='Numerical KK integral')
    axs[0].axhline(0,color='.4',lw=.7);axs[0].set_xticks(ticks,[r'$\Gamma$','X','M',r'$\Gamma$'])
    axs[0].set_ylabel(r'$\mathrm{Re}\,G_c(\mathbf{k},0)$ ($D^{-1}$)');axs[0].set_xlabel('Momentum path')
    axs[0].set_title('Independent Kramers-Kronig reconstruction');axs[0].legend(frameon=False,fontsize=9)
    vmax=np.max(np.abs(gg))
    im=axs[1].pcolormesh(kval,kval,gg,shading='auto',cmap='RdBu_r',norm=TwoSlopeNorm(vcenter=0,vmin=-vmax,vmax=vmax))
    axs[1].contour(xx,yy,gg,levels=[0],colors=['#18232e'],linewidths=1.6)
    axs[1].plot(0,0,'ko',ms=3);axs[1].text(.02,.01,r'$\Gamma$',fontsize=11)
    axs[1].set_aspect('equal');axs[1].set_xlabel(r'$k_x/(2\pi/a)$');axs[1].set_ylabel(r'$k_y/(2\pi/a)$')
    axs[1].set_title(f'Zero contour; Gamma-side area {gridchecks[-1]["Gamma_side_fraction"]:.4f}')
    fig.colorbar(im,ax=axs[1],fraction=.046,pad=.04,label=r'$\mathrm{Re}\,G_c(0)$')
    fig.suptitle('Conditional half-filled spectral model; chemical potential fixed at the gap midpoint',fontsize=13,y=1.01)
    fig.tight_layout();fig.savefig(ROOT/'figures/half_green_zeros.png',dpi=220,bbox_inches='tight')
    np.savez_compressed(ROOT/'data/half_zero_surface.npz',k=kval,Gzero=gg,energies=ee,weights=ww)
    # Broadening biases the contour; the physical zero uses eta -> 0.
    eta_checks=[]
    sign=np.sign(gg[nk//2,nk//2])
    for et in [0,.02,.04,.08,.16]:
        g=np.sum(ww/(-ee+1j*et),axis=-1).real
        eta_checks.append({'eta':et,'fraction':float(np.mean(g*sign>0))})
    result={'model':'half-filled linear-dispersion, linear-residue two-pole phenomenology',
            'parameters':{'t':float(t),'tprime':float(tp),'s':float(s),'V':float(V),'r':float(r),'eta':float(eta)},
            'KK_quadrature':checks,'momentum_grid_checks':gridchecks,'broadening_checks':eta_checks,
            'shifted_momentum_assignment_Gamma_side_fraction':1-gridchecks[-1]['Gamma_side_fraction'],
            'note':'The fitted linewidth is excluded from the Hamiltonian. The plotted spectral intensity uses it only as resolution/lifetime broadening. The auxiliary representation does not determine spin vertices, dc transport or a phase diagram.'}
    json.dump(result,open(ROOT/'data/spectral_checks.json','w'),indent=2)
    print(json.dumps(result,indent=2))

if __name__=='__main__':run()
