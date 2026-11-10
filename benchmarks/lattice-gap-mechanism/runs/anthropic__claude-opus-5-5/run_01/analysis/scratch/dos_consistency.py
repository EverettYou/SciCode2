import json, numpy as np
from scipy.ndimage import uniform_filter1d
d = json.load(open('/app/measurements.json'))
sts = d['measurements'][0]['spectra']; nmr = d['measurements'][1]['samples']; rho = d['measurements'][2]['samples']
s = sts[0]
V = np.array(s['bias']); g = uniform_filter1d(np.array(s['dI_dV']), 5)
for bg_sub in [False, True]:
    N = g.copy()
    if bg_sub:
        N = np.where((V>-8.1)&(V<8.1), N, 0.0)   # keep only the two bands
    dE = V[1]-V[0]
    def f(E,T): return 1/(np.exp(E/T)+1)
    Ts = np.array(nmr[0]['temperature'])
    rate = []; nqp = []
    for T in Ts:
        mf = f(V,T)*(1-f(V,T))/T   # -df/dE
        rate.append(np.sum(N**2*mf)*dE)
        nqp.append(np.sum(N*np.where(V>0, f(V,T), 1-f(V,T)))*dE)
    rate = np.array(rate); nqp=np.array(nqp)
    i4 = np.argmin(abs(Ts-4))
    rate/=rate[i4]; 
    print('bg_sub=',bg_sub)
    y = np.array(nmr[0]['one_over_T1'])/Ts
    for T, r, yy in zip(Ts, rate, y):
        print(f'   T={T:.3f}  model 1/T1T (N^2 Korringa)={r:.3e}   data={yy:.3e}  ratio={yy/r:.2f}')
    # effective activation
    m = (Ts>0.55)
    p = np.polyfit(1/Ts[m], np.log(rate[m]), 1); print('   model NMR activation', -p[0])
    Tr = np.array(rho[0]['temperature'])
    nq = np.array([np.sum(N*np.where(V>0, f(V,T), 1-f(V,T)))*dE for T in Tr])
    p = np.polyfit(1/Tr, np.log(nq), 1); print('   model n_qp activation', -p[0])
