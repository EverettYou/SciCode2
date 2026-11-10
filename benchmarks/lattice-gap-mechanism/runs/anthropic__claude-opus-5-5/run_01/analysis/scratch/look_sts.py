import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
d = json.load(open('/app/measurements.json'))
sts = d['measurements'][0]['spectra']
fig, axs = plt.subplots(4,1, figsize=(14,16))
for ax, s in zip(axs, sts):
    V = np.array(s['bias']); g = np.array(s['dI_dV'])
    ax.plot(V, g, lw=0.6, color='0.6')
    ax.plot(V, uniform_filter1d(g, 7), lw=1.2, color='k')
    ax.set_xticks(np.arange(-10, 10.1, 0.5), minor=True)
    ax.set_xticks(np.arange(-10, 10.1, 1))
    ax.grid(which='both', alpha=0.3)
    ax.set_title(f"panel {s['panel']} nu={s['filling']} T={s['temperature']}")
    ax.set_ylim(-0.05, 1.1)
plt.tight_layout(); plt.savefig('sts_zoom.png', dpi=80)
