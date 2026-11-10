import sys; sys.path.insert(0,'/app/code')
from model import *
import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = json.load(open('/app/measurements.json')); STS = d['measurements'][0]['spectra']
def sample(rho, V): return np.interp(V, GRID, rho)
# backgrounds / scales from the earlier fits
fig, axs = plt.subplots(2, 2, figsize=(13, 8))
# (a)
s = STS[0]; V = np.array(s['bias']); g = np.array(s['dI_dV'])
rho = mott_dos(0.15); m = (np.abs(V) < 9)
sc = np.max(g[m]) / rho.max(); axs[0,0].plot(V, g, 'k', lw=0.6, label='data'); axs[0,0].plot(GRID, 0.95*sc*rho+0.045, 'r', lw=1.2, label=r'Mott insulator, $U=12.0$, bands $\pm U/2+\epsilon_k/2$')
axs[0,0].set_title(r'(a) $\nu=1/2$, low $T$'); axs[0,0].set_xlim(-10,10)
# (b)
s = STS[1]; V = np.array(s['bias']); g = np.array(s['dI_dV'])
rho = pg_dos(0.19); sc = 1.0/rho.max()
axs[0,1].plot(V, g, 'k', lw=0.6, label='data'); axs[0,1].plot(GRID, 0.96*sc*rho+0.06, 'r', lw=1.2, label='pseudogap/SC state (fitted, see text)')
axs[0,1].set_title(r'(b) $\nu\approx0.3$, low $T$'); axs[0,1].set_xlim(-10,10)
# (c)
s = STS[2]; V = np.array(s['bias']); g = np.array(s['dI_dV'])
mu2 = mu_for_filling(0.198); D2 = 1.967
rho = bcs_dos(mu2, D2, 0.10); sc = 1.0/rho.max()
axs[1,0].plot(V, g, 'k', lw=0.6, label='data'); axs[1,0].plot(GRID, 0.98*sc*rho+0.064, 'r', lw=1.2, label=r'BCS on bare band, $\Delta=1.97$')
axs[1,0].set_title(r'(c) $\nu\approx0.2$, low $T$'); axs[1,0].set_xlim(-10,10)
# (d)
s = STS[3]; V = np.array(s['bias']); g = np.array(s['dI_dV'])
mu3 = mu_for_filling(0.295); rho = free_dos(mu3, 0.125); sc = 1.0/rho.max()
axs[1,1].plot(V, g, 'k', lw=0.6, label='data'); axs[1,1].plot(GRID, 0.93*sc*rho+0.07, 'r', lw=1.2, label=r"bare band $t=0.99$, $t'=0.195$, $\nu=0.295$")
axs[1,1].set_title(r'(d) $\nu\approx0.3$, high $T$'); axs[1,1].set_xlim(-10,10)
for ax in axs.ravel(): ax.legend(fontsize=8, loc='upper center'); ax.set_xlabel('bias V / D'); ax.set_ylabel('dI/dV (norm.)'); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('/app/figures/fig_sts_fits.png', dpi=110)
print('ok')
