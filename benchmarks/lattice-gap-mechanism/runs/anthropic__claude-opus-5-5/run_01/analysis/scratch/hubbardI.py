import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.ndimage import uniform_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][0]
V = np.array(s['bias']); g = uniform_filter1d(np.array(s['dI_dV']),5)
N=400
k = 2*np.pi*(np.arange(N)+0.5)/N
kx, ky = np.meshgrid(k,k,indexing='ij')
def eps(t,tp): return (-2*t*(np.cos(kx)+np.cos(ky)) - 4*tp*np.cos(kx)*np.cos(ky)).ravel()
def hubI_dos(t,tp,U,eta=0.06, w=V):
    e = eps(t,tp)
    # half filling, G = 1/(w - U^2/(4w) - e) in frame mu=U/2 (atomic center)
    R = np.sqrt(e**2/4 + U**2/4)
    wp = e/2 + R; wm = e/2 - R
    Zp = wp/(wp-wm); Zm = -wm/(wp-wm)
    # midgap shift
    mid = 0.5*(wm.max()+wp.min())
    wp -= mid; wm -= mid
    dos = np.zeros_like(w)
    for pole, Z in [(wp,Zp),(wm,Zm)]:
        h, edges = np.histogram(pole, bins=np.append(w-0.0125, w[-1]+0.0125), weights=Z)
        dos += h
    dos = dos/len(e)/0.025
    # gaussian smooth
    from scipy.ndimage import gaussian_filter1d
    dos = gaussian_filter1d(dos, eta/0.025)
    return dos, mid, wm.max(), wp.min()
fig, ax = plt.subplots(figsize=(12,5))
ax.plot(V, g, 'k', lw=1, label='data (a)')
for (t,tp,U,c) in [(1.0,0.2,12,'r'),(1.0,0.2,12.3,'b'),(1.0,0.0,12,'g')]:
    dos, mid, top, bot = hubI_dos(t,tp,U)
    sc = g[(V>-8.5)&(V<8.5)].max()/dos.max()
    ax.plot(V, dos*sc+0.0, c, lw=1, label=f"Hubbard-I t={t} t'={tp} U={U}: edges {top:.2f},{bot:.2f}")
    print(t,tp,U,'gap edges', top, bot, 'midgap shift', mid)
ax.legend(fontsize=8); ax.set_xlim(-10,10); ax.grid(alpha=.3)
plt.savefig('hubI_vs_a.png', dpi=80)
