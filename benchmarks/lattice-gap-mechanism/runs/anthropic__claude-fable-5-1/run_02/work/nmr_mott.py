import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar
from nmr_lib import *
d = json.load(open('/app/measurements.json'))
nmr = {s['filling']:(np.array(s['temperature']),np.array(s['one_over_T1']),np.array(s['uncertainty'])) for s in d['measurements'][1]['samples']}
T, r, u = nmr['1/2']; data = r/T; i4 = np.argmin(np.abs(T-4)); data = data/data[i4]
kx, ky = kgrid(400); t,tp,U = 1.0,-0.2,12.0
eb = ebar(kx,ky,t,tp); ek = eb + 4*tp
R = np.sqrt(ek**2/4+U**2/4)
Ep = eb/2+U/2; Em = eb/2-U/2; Zp = 0.5+ek/(4*R); Zm = 0.5-ek/(4*R)
grid = np.arange(-10,10.001,0.02)
for AoverB in [0.0, -2.0, -3.0, -4.0, -5.0, -8.0, 1e6]:
    terms = hyperfine_terms(kx,ky,AoverB) if AoverB<1e5 else [(1.0, np.ones_like(kx))]
    Phi = phi_E([Ep,Em], [(1.0,[Zp,Zm])], terms, grid, 0.08)
    m = np.array([T1T_from_phi(Phi,grid,Ti) for Ti in T]); m = m/m[i4]
    # effective slope between 1/T=1 and 2
    lnm = np.log(m); 
    chi = np.sum((np.log(data[:-1]) - lnm[:-1])**2)  # crude
    print(f"A/B={AoverB:8.1f}: ", " ".join(f"{Ti:.2f}:{di/mi:.2f}" for Ti,di,mi in zip(T[::2],data[::2],m[::2])), f" | sum (ln ratio)^2 = {chi:.2f}")
