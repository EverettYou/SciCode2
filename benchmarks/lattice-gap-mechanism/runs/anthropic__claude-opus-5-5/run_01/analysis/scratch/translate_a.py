import json, numpy as np
from scipy.ndimage import uniform_filter1d, gaussian_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][0]
V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
bg = 0.0665 + 0.00059*V**2
gb = g - bg
gb[np.abs(V)<3.6] = 0
gs = gaussian_filter1d(gb, 2)
lower = np.where(V<0, gs, 0); upper = np.where(V>0, gs, 0)
# cross-correlate lower and upper (normalized shapes)
best=None
for shift in np.arange(11.0, 13.0, 0.025):
    up_sh = np.interp(V+shift, V, upper)   # upper(V+shift)
    m = (V>-8.6)&(V<-3.4)
    a = lower[m]/np.linalg.norm(lower[m]); b = up_sh[m]/np.linalg.norm(up_sh[m])
    c = np.dot(a,b)
    if best is None or c>best[1]: best=(shift,c)
print('best translation U =', best)
# mirror test
mir = np.interp(-V, V, upper)
m = (V>-8.6)&(V<-3.4)
a = lower[m]/np.linalg.norm(lower[m]); b = mir[m]/np.linalg.norm(mir[m])
print('mirror overlap =', np.dot(a,b))
U = best[0]
# ratio lower(w)/upper(w+U) vs position in band
for w in np.arange(-7.8, -4.1, 0.3):
    lo = np.interp(w, V, gs); up = np.interp(w+U, V, gs)
    eps = 2*(w - (-6.0)) - 0.8   # map band position to bare eps assuming band center -6 <-> eps=-0.8
    print(f'w={w:6.2f} eps~{eps:6.2f}  lower={lo:.3f} upper={up:.3f} ratio={lo/up:.3f}  HubI(1-e/U)/(1+e/U)={(1-eps/12)/(1+eps/12):.3f}')
