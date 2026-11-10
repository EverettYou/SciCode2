import json, numpy as np
d = json.load(open('/app/measurements.json'))
regions = {'a':[(-10,-8.4),(8.4,10)], 'b':[(-10,-6.8),(6.9,10)], 'c':[(-10,-4.2),(5.9,10)], 'd':[(-10,-4.4),(4.6,10)]}
bands = {'a':[(-8.4,-3.6),(3.6,8.4)], 'b':[(-6.8,-2.0),(2.0,6.9)], 'c':[(-4.2,-1.2),(1.2,5.9)], 'd':[(-4.4,0),(0,4.6)]}
for s in d['measurements'][0]['spectra']:
    p = s['panel']; V = np.array(s['bias']); g = np.array(s['dI_dV']); dV=V[1]-V[0]
    m = np.zeros_like(V, bool)
    for a,b in regions[p]: m |= (V>=a)&(V<=b)
    for model in ['b0+b2V2','b0+b1V+b2V2']:
        if model=='b0+b2V2': A = np.vstack([np.ones(m.sum()), V[m]**2]).T
        else: A = np.vstack([np.ones(m.sum()), V[m], V[m]**2]).T
        c, *_ = np.linalg.lstsq(A, g[m], rcond=None)
        if model=='b0+b2V2': bg = c[0]+c[1]*V**2
        else: bg = c[0]+c[1]*V+c[2]*V**2
        (l0,l1),(u0,u1) = bands[p]
        ml=(V>l0)&(V<l1); mu=(V>u0)&(V<u1)
        L=(g[ml]-bg[ml]).sum()*dV; U=(g[mu]-bg[mu]).sum()*dV
        print(f"panel {p} nu={s['filling']:4s} T={s['temperature']:4s} bg[{model}] coef={np.round(c,5)}  occ frac={L/(L+U):.3f}  (L={L:.3f},U={U:.3f})")
