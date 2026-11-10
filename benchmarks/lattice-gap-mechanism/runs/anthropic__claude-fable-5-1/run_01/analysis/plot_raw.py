import json, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
with open('/app/measurements.json') as f:
    d = json.load(f)
sts = d['measurements'][0]['spectra']
fig, axs = plt.subplots(2,2, figsize=(14,9))
for ax, s in zip(axs.flat, sts):
    V = np.array(s['bias']); y = np.array(s['dI_dV'])
    ax.plot(V, y, lw=0.7)
    ax.set_title(f"panel {s['panel']} nu={s['filling']} T={s['temperature']}")
    ax.set_xticks(np.arange(-10,11,1)); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig('/app/analysis/raw_sts.png', dpi=110)

nmr = d['measurements'][1]['samples']; res = d['measurements'][2]['samples']
fig, axs = plt.subplots(1,3, figsize=(18,5))
for s in nmr:
    T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    axs[0].errorbar(1/T, r/T, yerr=u/T, fmt='o', ms=3, label=s['filling'])
axs[0].set_yscale('log'); axs[0].set_xlabel('1/T'); axs[0].set_ylabel('1/T1T'); axs[0].legend(); axs[0].grid(alpha=0.3)
axs[0].set_ylim(1e-5, 3)
for s in res:
    T = np.array(s['temperature']); r = np.array(s['resistivity']); u = np.array(s['uncertainty'])
    axs[1].errorbar(T, r, yerr=u, fmt='o-', ms=3, label=s['filling'])
    m = r>0
    axs[2].errorbar(1/T[m], r[m], yerr=u[m], fmt='o', ms=3, label=s['filling'])
axs[1].set_yscale('log'); axs[1].set_xlabel('T'); axs[1].legend(); axs[1].grid(alpha=0.3)
axs[2].set_yscale('log'); axs[2].set_xlabel('1/T'); axs[2].legend(); axs[2].grid(alpha=0.3)
plt.tight_layout(); plt.savefig('/app/analysis/raw_nmr_res.png', dpi=110)
