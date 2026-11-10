import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar
d = json.load(open('/app/measurements.json'))
nmr = {s['filling']:(np.array(s['temperature']),np.array(s['one_over_T1']),np.array(s['uncertainty'])) for s in d['measurements'][1]['samples']}
T, r, u = nmr['1/2']; data = r/T; i4 = np.argmin(np.abs(T-4)); data = data/data[i4]
nk=400; kx, ky = kgrid(nk); t,tp,U = 1.0,-0.2,12.0
eb = ebar(kx,ky,t,tp); ek = eb + 4*tp
def bands(kind):
    if kind=='lin':
        R = np.sqrt(ek**2/4+U**2/4); Ep = eb/2+U/2; Em = eb/2-U/2; Zp = 0.5+ek/(4*R); Zm = 0.5-ek/(4*R)
    else:  # exact HI relative to midgap
        R = np.sqrt(ek**2/4+U**2/4); Epa = (ek+U)/2+R; Ema = (ek+U)/2-R
        mid = (Ema.max()+Epa.min())/2; Ep = Epa-mid; Em = Ema-mid; Zp = 0.5+ek/(4*R); Zm = 0.5-ek/(4*R)
    return [(Ep,Zp),(Em,Zm)]
def dfdw(w, T):
    x = np.clip(w/(2*T), -300, 300); return 1/(4*T*np.cosh(x)**2)
def rate_Q(bds, T, sigma=0.1):
    tot = 0.0
    sh = nk//2
    for E,Z in bds:
        EQ = np.roll(np.roll(E, sh, 0), sh, 1); ZQ = np.roll(np.roll(Z, sh, 0), sh, 1)
        delta = np.exp(-(E-EQ)**2/(2*sigma**2))/(np.sqrt(2*np.pi)*sigma)
        tot += np.sum(Z*ZQ*delta*dfdw(E,T))
    return tot
for kind in ['lin','exact']:
    bds = bands(kind)
    m = np.array([rate_Q(bds,Ti) for Ti in T]); m = m/m[i4]
    lnm = np.log(m); lnd = np.log(data)
    print(kind, " data/model:", " ".join(f"{Ti:.2f}:{di/mi:.2f}" for Ti,di,mi in zip(T[::2],data[::2],m[::2])))
    # effective slopes
    for (a,b) in [(0.25,1.0),(1.0,2.0)]:
        ia = np.argmin(np.abs(1/T-a)); ib = np.argmin(np.abs(1/T-b))
        print(f"    slope 1/T {a}->{b}: model {(lnm[ia]-lnm[ib])/(1/T[ib]-1/T[ia]):.2f}  data {(lnd[ia]-lnd[ib])/(1/T[ib]-1/T[ia]):.2f}")
