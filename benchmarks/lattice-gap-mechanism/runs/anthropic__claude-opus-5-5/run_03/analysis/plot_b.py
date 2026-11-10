import sys; sys.path.insert(0,'/app/analysis')
from fit_b4 import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2,1,figsize=(11,9))
ax=axs[0]
ax.plot(*S['b'], 'k-', lw=0.6, label='(b) data')
xi = E0-mu0
for D,c in [(5.0,'r'),(2.6,'b'),(4.0,'g')]:
    A,Ek = bcs(xi, D*np.ones_like(xi), 0.12)
    ax.plot(Vf, 3.2*A*0.6+0.0, c+'-', lw=1, label='BCS Delta=%.1f (scaled)'%D)
ax.plot(Vf, F7([3.2455,1.2092,-0.1901,0.2218,3.1045,0.0109]), 'm--', label='F7 fit')
ax.legend(fontsize=8); ax.set_xlim(-10,10)
ax=axs[1]
ax.plot(*S['a'], 'r-', lw=0.6, label='(a) nu=1/2')
ax.plot(*S['b'], 'g-', lw=0.6, label='(b) nu=0.3')
ax.plot(*S['c'], 'b-', lw=0.6, label='(c) nu=0.2')
ax.plot(S['d'][0], S['d'][1]*0.5-0.0, 'k-', lw=0.4, alpha=0.5, label='(d) high T x0.5')
ax.legend(fontsize=8); ax.set_xlim(-10,10); ax.grid(alpha=0.3)
fig.savefig('/app/analysis/plot_b.png', dpi=100)
