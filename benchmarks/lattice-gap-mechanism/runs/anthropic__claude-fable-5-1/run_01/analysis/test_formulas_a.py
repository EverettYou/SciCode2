import json, numpy as np
with open('/app/measurements.json') as f:
    d = json.load(f)
nmr = {s['filling']: s for s in d['measurements'][1]['samples']}
res = {s['filling']: s for s in d['measurements'][2]['samples']}
N = 800
kx = (np.arange(N)+0.5)/N*2*np.pi - np.pi
KX, KY = np.meshgrid(kx, kx, indexing='ij')
cx, cy = np.cos(KX), np.cos(KY)
EPS = (-2*(cx+cy) - 4*0.196*cx*cy).ravel()
egrid = np.arange(-14, 14, 0.01); de = egrid[1]-egrid[0]
bins = np.concatenate([egrid-de/2, [egrid[-1]+de/2]])
def hist(E, w):
    h,_ = np.histogram(E, bins=bins, weights=w); return h/de/E.size
def broaden(A, eta, kind='lorentz'):
    x = np.arange(-int(8*eta/de+5), int(8*eta/de+5)+1)*de
    ker = (eta/np.pi)/(x**2+eta**2) if kind=='lorentz' else np.exp(-x**2/2/eta**2)
    ker/=ker.sum(); return np.convolve(A, ker, mode='same')
# panel a model: E± = ±6 + xi/2, w± = (1 ± xi/16)/2, xi = eps + 0.11
xi = EPS + 0.11
Ep = 6 + xi/2; Em = -6 + xi/2
wp = 0.5*(1+xi/16.2); wm = 1-wp
mid = 0.5*(Ep.min()+Em.max())
A0 = hist(np.concatenate([Ep-mid, Em-mid]), np.concatenate([wp, wm]))
print("total weight", A0.sum()*de, " occupied weight", A0[egrid<0].sum()*de)

def dfdw(w, T):
    x = w/(2*T); return 1/(4*T*np.cosh(np.clip(x,-300,300))**2)

for label, A in [('sharp', A0), ('lorentz0.084', broaden(A0,0.084)), ('gauss0.084', broaden(A0,0.084,'gauss'))]:
    s = nmr['1/2']; T = np.array(s['temperature']); r = np.array(s['one_over_T1']); u = np.array(s['uncertainty'])
    K = np.array([np.sum(A**2*dfdw(egrid,Ti))*de for Ti in T])
    K1 = np.array([np.sum(A*dfdw(egrid,Ti))*de for Ti in T])   # carrier density-like
    Kn = K/K[T==4][0]; K1n = K1/K1[T==4][0]
    print(f"\n=== DOS model {label}: NMR nu=1/2 : T, data 1/T1T (norm), bubble N^2, (N^1)^2, N^1")
    for Ti, ri, ui, k, k1 in zip(T, r/T, u/T, Kn, K1n):
        print(f"  T={Ti:6.3f}  data={ri:9.3e}+-{ui:8.1e}   N^2={k:9.3e}   (N1)^2={k1**2:9.3e}  N1={k1:9.3e}")
    s = res['1/2']; T = np.array(s['temperature']); rr = np.array(s['resistivity']); u = np.array(s['uncertainty'])
    S = np.array([np.sum(A*dfdw(egrid,Ti))*de for Ti in T]); rho = (1/S)/(1/S[T==4][0])
    print(f"  resistivity: T, data, 1/int N(-df): ")
    for Ti, ri, ui, rh in list(zip(T, rr, u, rho))[::4]:
        print(f"  T={Ti:6.3f}  data={ri:9.3f}+-{ui:7.3f}   model={rh:9.3f}")
