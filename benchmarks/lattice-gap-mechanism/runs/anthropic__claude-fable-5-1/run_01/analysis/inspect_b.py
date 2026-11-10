import json, numpy as np, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
with open('/app/measurements.json') as f: d = json.load(f)
sts = {s['panel']: s for s in d['measurements'][0]['spectra']}
V = np.array(sts['b']['bias']); y = np.array(sts['b']['dI_dV'])
# noise estimate from gap region
print("noise std in gap (|V|<2):", y[np.abs(V)<2].std(), " mean", y[np.abs(V)<2].mean())
for p in 'acd':
    Vp = np.array(sts[p]['bias']); yp = np.array(sts[p]['dI_dV'])
    m = (np.abs(Vp)<1.5) if p!='d' else (Vp<-6)
    print(f"noise std panel {p}: {yp[m].std():.4f}")
N = 600
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
EPS = (-2*(cx+cy) - 4*0.196*cx*cy).ravel()
egrid = np.arange(-14, 14, 0.01); de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(E, w):
    h,_ = np.histogram(E, bins=bins, weights=w); return h/de/E.size
def broaden(A, eta):
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    ker = (eta/np.pi)/(x**2+eta**2); ker/=ker.sum(); return np.convolve(A, ker, mode='same')
# best 'linear' model for b
mu, D, Dc, eta, scale, b, c0 = -0.7370, 4.3742, 2.7490, 0.3146, 6.1880, 0.0010, 0.0177
xi = EPS-mu; Ep = D + xi/2; Em = -D + xi/2; wp = 0.5*(1+xi/Dc); wm = 1-wp
wp = np.clip(wp,0,1); wm = 1-wp
mid = 0.5*(Ep.min()+Em.max())
A = hist(np.concatenate([Ep-mid,Em-mid]), np.concatenate([wp,wm]))
model = scale*np.interp(V, egrid, broaden(A, eta)) + b*V**2 + c0
fig, ax = plt.subplots(2,1, figsize=(12,8), sharex=True)
ax[0].plot(V, y, lw=0.8, label='data b'); ax[0].plot(V, model, lw=1, label='linear fit')
# also unbroadened scaled
ax[0].plot(V, scale*np.interp(V, egrid, broaden(A,0.08)) + b*V**2 + c0, lw=0.6, alpha=0.6, label='same, eta=0.08')
ax[0].legend(); ax[0].set_xticks(np.arange(-10,11,1)); ax[0].grid(alpha=0.3)
ax[1].plot(V, y-model); ax[1].set_ylabel('resid'); ax[1].grid(alpha=0.3)
plt.savefig('/app/analysis/inspect_b.png', dpi=110)
# Print the occupied weight fraction for the data (bg-subtracted) more carefully
bg = 0.0013*V**2 + 0.003
yy = y - bg
lo = (V>-7.2)&(V<-2.0); hi=(V>2.0)&(V<7.2)
Wl = np.trapz(yy[lo], V[lo]); Wh = np.trapz(yy[hi], V[hi])
print("panel b occupied fraction:", Wl/(Wl+Wh), Wl, Wh)
for p in 'ac':
    Vp = np.array(sts[p]['bias']); yp = np.array(sts[p]['dI_dV']) - (0.0013*Vp**2+0.003)
    lo = (Vp<-1.0)&(Vp>-9.0); hi=(Vp>1.0)&(Vp<9.0)
    Wl = np.trapz(yp[lo], Vp[lo]); Wh = np.trapz(yp[hi], Vp[hi]); print(f"panel {p} occupied fraction: {Wl/(Wl+Wh):.4f}")
