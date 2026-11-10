import sys; sys.path.insert(0,'/app/work')
import json, numpy as np
from fitlib import kgrid, ebar, dos
d = json.load(open('/app/measurements.json'))
nmr = {s['filling']:(np.array(s['temperature']),np.array(s['one_over_T1']),np.array(s['uncertainty'])) for s in d['measurements'][1]['samples']}
res = {s['filling']:(np.array(s['temperature']),np.array(s['resistivity']),np.array(s['uncertainty'])) for s in d['measurements'][2]['samples']}
kx,ky = kgrid(800); t,tp,U = 1.0,-0.2,12.0
eb = ebar(kx,ky,t,tp); ek = eb - 0.8
grid = np.arange(-12,12.001,0.01)
Ep = eb/2+U/2; Em = eb/2-U/2; Zp = 0.5+ek/(2*U); Zm = 0.5-ek/(2*U)
N = dos([Ep,Em],[Zp,Zm],grid,0.08)
def dfdw(w,T): 
    x = np.clip(w/(2*T),-300,300); return 1/(4*T*np.cosh(x)**2)
T_nmr, r_nmr, u_nmr = nmr['1/2']
print("Mott NMR: compare 1/(T1T) model variants (normalized at T=4)")
def model_T1T(T, power):
    return np.array([np.trapz(dfdw(grid,Ti)*N**power, grid) for Ti in T])
for power in [1,2]:
    m = model_T1T(T_nmr, power); m = m/m[np.argmin(np.abs(T_nmr-4))]
    data = r_nmr/T_nmr; data = data/data[np.argmin(np.abs(T_nmr-4))]
    print(" power",power)
    for Ti, di, mi in zip(T_nmr, data, m):
        print(f"   T={Ti:6.3f} data={di:.3e} model={mi:.3e} ratio={di/mi:.2f}")
# resistivity
T_r, rho, u_r = res['1/2']
print("Mott resistivity: model rho = 1/sigma, sigma ∝ ∫(-df/dw) N^p")
for power in [1,2]:
    sig = np.array([np.trapz(dfdw(grid,Ti)*N**power, grid) for Ti in T_r])
    m = (1/sig); m = m/m[np.argmin(np.abs(T_r-4))]
    print(" power",power)
    for Ti, di, mi in list(zip(T_r, rho, m))[::4]:
        print(f"   T={Ti:6.3f} data={di:.3e} model={mi:.3e} ratio={di/mi:.2f}")
