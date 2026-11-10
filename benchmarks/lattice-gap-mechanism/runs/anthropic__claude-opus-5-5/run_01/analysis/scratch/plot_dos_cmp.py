import json, numpy as np, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
d = json.load(open('/app/measurements.json'))
panel = sys.argv[1]; files = sys.argv[2].split(','); out = sys.argv[3]
idx = {'a':0,'b':1,'c':2,'d':3}[panel]
s = d['measurements'][0]['spectra'][idx]
V = np.array(s['bias']); g = uniform_filter1d(np.array(s['dI_dV']),5)
fig, ax = plt.subplots(figsize=(11,4.5))
ax.plot(V, g, 'k', lw=1.2, label=f'STS ({panel})')
for f in files:
    w, dos = np.load(f)
    # midgap shift: find largest zero region around center
    thr = 0.02*dos.max()
    inside = dos < thr
    # locate the gap containing the global position nearest to the middle of the spectral weight
    cen = np.sum(w*dos)/np.sum(dos)
    i0 = np.argmin(abs(w - cen))
    # expand left/right while inside gap; if not inside, search nearest inside index
    if not inside[i0]:
        cand = np.where(inside & (abs(w-cen) < 4))[0]
        i0 = cand[np.argmin(abs(cand - i0))] if len(cand) else i0
    l = i0; r = i0
    while l > 0 and inside[l-1]: l -= 1
    while r < len(w)-1 and inside[r+1]: r += 1
    mid = 0.5*(w[l]+w[r])
    sc = g[(V>-9)&(V<9)].max()/dos.max()
    ax.plot(w-mid, dos*sc, lw=1.2, label=f'{f}: gap [{w[l]-mid:.2f},{w[r]-mid:.2f}]')
ax.set_xlim(-10,10); ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.savefig(out, dpi=80)
