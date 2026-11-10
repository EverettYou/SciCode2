import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar, dos
from n0lib import N0_grid, hist_poles, bgfun
from models import spectrum_half, spectrum_03, spectrum_02, T_HOP, TP_HOP
from vizstyle import *
import matplotlib.pyplot as plt
setup()
d = json.load(open('/app/measurements.json'))
S = {s['panel']:(np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V = S['a'][0]
kx,ky = kgrid(700)
def bg(V,b0,p,Vin,w=0.1):
    return b0*(np.abs(V)/5.0)**p*0.5*(1+np.tanh((np.abs(V)-Vin)/w))
# (a)
pa = np.load('/app/work/fit_a_free.npy'); t,tp,U,sig,b0,p,e0,Uw = pa
bands = spectrum_half(kx,ky,'free'); h = dos([bands[0][0],bands[1][0]],[bands[0][1],bands[1][1]],V,sig); ma = h/h.max() + bg(V,b0,p,(U-4*t)/2)
# (b)
pb = np.load('/app/work/fit_b_B9.npy'); sigb,b0b,pb_ = pb[12],pb[13],pb[14]
bands = spectrum_03(kx,ky); h = dos([bands[0][0],bands[1][0]],[bands[0][1],bands[1][1]],V,sigb); hm=h/h.max()
i0=np.argmin(np.abs(V)); up=np.where(hm[i0:]>0.02)[0][0]; dn=np.where(hm[:i0][::-1]>0.02)[0][0]; Vin=0.5*(V[i0+up]-V[i0-1-dn])
mb = hm + bg(V,b0b,pb_,Vin)
# (c)
pc = np.load('/app/work/fit_c.npy'); t_c,tp_c,mu_c,D_c,sig_c,b0c,pc_ = pc
b02,xi,D = spectrum_02(kx,ky); h = dos([b02[0][0],b02[1][0]],[b02[0][1],b02[1][1]],V,sig_c); mc = h/h.max() + bg(V,b0c,pc_,D)
# (d)
pd = np.load('/app/work/fit_d.npy'); t_d,tp_d,mu_d,sig_d,b0d,pd_ = pd
eb = ebar(kx,ky,t_d,tp_d)-mu_d; h = dos([eb],[np.ones(1)],V,sig_d); hm=h/h.max()
s = 0.5*(1+np.tanh((V-(4*t_d-mu_d))/0.1))+0.5*(1-np.tanh((V-(-4*t_d-mu_d))/0.1)); md = hm + b0d*(np.abs(V)/5.0)**pd_*s
np.savez('/app/work/sts_models.npz', V=V, ma=ma, mb=mb, mc=mc, md=md)
fig, axes = plt.subplots(2,2, figsize=(13,8), sharex=True)
items = [('a', ma, r'(a) $\nu=1/2$, low $T$: Mott insulator (Hubbard-I bands, $t$=1.00, $t^\prime$=0.20, $U$=12.0)', C['half']),
         ('b', mb, r'(b) $\nu\approx0.3$, low $T$: paired pseudogap state (two Hubbard-like branches)', C['03']),
         ('c', mc, r'(c) $\nu\approx0.2$, low $T$: BCS state on bare band ($\Delta$=1.96, $\mu$ at $\nu$=0.20)', C['02']),
         ('d', md, r'(d) $\nu\approx0.3$, high $T$: bare $t$–$t^\prime$ band, $\mu$ at band midpoint ($\nu$=0.31)', C['03'])]
for ax,(pnl,m,ttl,col) in zip(axes.ravel(), items):
    Vd,gd = S[pnl]; ax.plot(Vd,gd,color=C['muted'],lw=0.8,label='STS data'); ax.plot(V,m,color=col,lw=2,label='effective theory')
    ax.set_title(ttl, fontsize=9.5, loc='left'); ax.set_ylim(0,1.15); ax.legend(loc='upper left', fontsize=8)
    r = (m-gd); ax.text(0.98,0.9, f"rms residual {np.sqrt(np.mean(r**2)):.3f}", transform=ax.transAxes, ha='right', fontsize=8, color=C['ink2'])
for ax in axes[1]: ax.set_xlabel('bias $V/D$')
for ax in axes[:,0]: ax.set_ylabel('$dI/dV$ (normalised)')
plt.savefig('/app/figures/fig_sts_fits.png', dpi=150, bbox_inches='tight'); print("sts figure done")
