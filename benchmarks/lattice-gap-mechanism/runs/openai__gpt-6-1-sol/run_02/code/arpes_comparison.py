"""Compare conditional and rejected spectral candidates without overstating them."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/layered-oxide-mpl')
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import PowerNorm
from spectral_checks import poles, spectral, kpath, bare

ROOT=Path(__file__).resolve().parents[1]
j=json.load(open(ROOT/'data/sts_fit_results.json'))
kx,ky,d,ticks=kpath(220);omega=np.linspace(-10,10,1801)
E0,w0=poles(kx,ky);eta0=j['half_linear_weights']['params'][3]

p=j['general_dispersion']['1']['params']
tc,tpc,tf,tpf,c,b,V,eta1=p[:8]
cx=np.cos(2*np.pi*kx);cy=np.cos(2*np.pi*ky)
ec=-2*tc*(cx+cy)-4*tpc*cx*cy+c
ef=-2*tf*(cx+cy)-4*tpf*cx*cy+b
delta=np.sqrt(((ec-ef)/2)**2+V*V)
E1=np.stack([(ec+ef)/2-delta,(ec+ef)/2+delta],axis=-1)
wm=.5-(ec-ef)/(4*delta);w1=np.stack([wm,1-wm],axis=-1)

p2=j['low_models']['2']['BCS']['expanded_params']
scale,_,c2,_,Delta,eta2=p2[:6]
xi=scale*bare(kx,ky)+c2;en=np.sqrt(xi*xi+Delta*Delta)
E2=np.stack([-en,en],axis=-1);wm2=.5*(1-xi/en);w2=np.stack([wm2,1-wm2],axis=-1)

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'savefig.facecolor':'white'})
fig,axs=plt.subplots(1,3,figsize=(13.5,6.1),sharey=True)
models=[(E0,w0,eta0),(E1,w1,eta1),(E2,w2,eta2)]
titles=[r'$\nu=1/2$: fitted two-pole spectrum',r'$\nu\simeq0.3$: rejected two-pole candidate',r'$\nu\simeq0.2$: conditional BCS candidate']
subtitles=['Local fit and number sum rule pass','Line-shape RMS 0.049; noise about 0.015','Local fit passes; calculated filling 0.256']
colors=['#216a58','#ad502b','#a37422']
saved={}
for i,(ax,model,title,subtitle,col) in enumerate(zip(axs,models,titles,subtitles,colors)):
    E,w,eta=model;A=spectral(omega,E,w,eta)
    im=ax.pcolormesh(d,omega,A,shading='auto',cmap='magma',norm=PowerNorm(.6,vmin=0,vmax=3.1),rasterized=True)
    ax.axhline(0,color='white',ls=':',lw=.7)
    for q in ticks[1:-1]:ax.axvline(q,color='white',lw=.5,alpha=.6)
    ax.set_xticks(ticks,[r'$\Gamma$','X','M',r'$\Gamma$'])
    ax.set_xlabel('Momentum path');ax.set_title(title,fontsize=11,pad=10)
    ax.text(.5,-.18,subtitle,ha='center',va='top',transform=ax.transAxes,color=col,fontsize=9)
    ax.text(.03,.025,rf'$\eta/D={eta:.3f}$',transform=ax.transAxes,color='white',fontsize=9)
    saved[f'A{i}']=A;saved[f'E{i}']=E;saved[f'w{i}']=w
axs[0].set_ylabel(r'Energy from STS gap midpoint / $D$')
fig.suptitle('Fermi-function-divided ARPES candidates along Gamma - X - M - Gamma',fontsize=15,y=.98)
fig.text(.5,.92,'Constant photoemission matrix element assumed. These are not three validated predictions of one Hamiltonian.',ha='center',fontsize=10,color='#45576b')
fig.subplots_adjust(left=.065,right=.9,top=.82,bottom=.20,wspace=.11)
fig.colorbar(im,ax=axs,fraction=.022,pad=.025,label=r'$A_c(\mathbf{k},\omega)$ per spin ($D^{-1}$)')
fig.savefig(ROOT/'figures/arpes_candidates.png',dpi=230)
np.savez_compressed(ROOT/'data/arpes_candidates.npz',omega=omega,kx=kx,ky=ky,distance=d,**saved)
json.dump({'energy_origin':'gap midpoint; equals mu at half filling. Doped mu unknown except as assumed by BCS candidate.',
 'momentum_path':[[0,0],[.5,0],[.5,.5],[0,0]],'points':len(kx),'energy_range':[-10,10],
 'statuses':{'half':'accepted local spectral fit with correct filling; conditional momentum assignment',
             'nu_0.3':'rejected candidate shown solely to document what was computed; not a prediction',
             'nu_0.2':'accepted line-shape fit but density tension; conditional illustration'},
 'intensity':'physical-c spectral function per spin with constant matrix element; measurement backgrounds removed',
 'widths':[float(eta0),float(eta1),float(eta2)]},open(ROOT/'data/arpes_candidates_metadata.json','w'),indent=2)
