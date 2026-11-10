import json, numpy as np
from scipy.ndimage import uniform_filter1d
d = json.load(open('/app/measurements.json'))
for s in d['measurements'][0]['spectra']:
    V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
    # estimate background from |V|>9
    bgL = g[V<-9].mean(); bgR = g[V>9].mean()
    gap = g[np.abs(V)<0.5].mean()
    print(f"panel {s['panel']} nu={s['filling']} T={s['temperature']}: bg(V<-9)={bgL:.3f} bg(V>9)={bgR:.3f}  in-gap={gap:.4f}")
    # define band windows by threshold of smoothed g above local background
    gs = uniform_filter1d(g, 9)
    for bg_mode in ['none','const_bg']:
        gg = g.copy()
        if bg_mode=='const_bg':
            # subtract background only where outside-band level is ~0.1: model bg as constant 0.1 outside the gap region
            bg = 0.5*(bgL+bgR)
            gg = gg - bg
        neg = gg[(V<0)&(V>-9.5)].clip(min=-1).sum()*dV
        pos = gg[(V>0)&(V<9.5)].clip(min=-1).sum()*dV
        print(f"    {bg_mode:9s}: W(V<0)={neg:.3f} W(V>0)={pos:.3f}  frac_occ={neg/(neg+pos):.3f}")
    # band-limited windows
    if s['panel']=='a': wl, wu = (-8.3,-3.7), (3.7,8.3)
    if s['panel']=='b': wl, wu = (-6.8,-2.3), (2.3,6.9)
    if s['panel']=='c': wl, wu = (-4.0,-1.4), (1.4,5.8)
    if s['panel']=='d': wl, wu = (-4.3,0.0), (0.0,4.5)
    bg = 0.5*(bgL+bgR)
    for lab,(a,b) in [('lower',wl),('upper',wu)]:
        m = (V>a)&(V<b)
        print(f"    window {lab} {a},{b}: raw={g[m].sum()*dV:.3f}  bg-sub(bg={bg:.3f})={(g[m]-bg).sum()*dV:.3f}")
    ml = (V>wl[0])&(V<wl[1]); mu=(V>wu[0])&(V<wu[1])
    L = (g[ml]-bg).sum(); U_=(g[mu]-bg).sum()
    print(f"    band-window bg-sub occupied fraction = {L/(L+U_):.3f};  raw = {g[ml].sum()/(g[ml].sum()+g[mu].sum()):.3f}")
