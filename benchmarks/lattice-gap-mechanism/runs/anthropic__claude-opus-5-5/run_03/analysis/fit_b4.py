import numpy as np, json
from scipy.optimize import least_squares
from multiprocessing import Pool
d = json.load(open('/app/measurements.json'))
S = {s['panel']: (np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
V, G = S['b']
N = 160
k = (np.arange(N)+0.5)/N
KX, KY = np.meshgrid(k, k, indexing='ij')
CX, CY = np.cos(2*np.pi*KX).ravel(), np.cos(2*np.pi*KY).ravel()
C2 = (2*CX**2-1 + 2*CY**2-1)/2
t0, tp0 = 0.9993, 0.1945
E0 = -2*t0*(CX+CY) - 4*tp0*CX*CY
mu0 = -0.907
Vf = np.linspace(-10, 10, 801); dV = Vf[1]-Vf[0]
def cic(E, W):
    x = (E - Vf[0])/dV; i0 = np.floor(x).astype(int); f = x - i0
    h = np.zeros(len(Vf)+2); m = (i0 >= -1) & (i0 < len(Vf))
    np.add.at(h, i0[m]+1, W[m]*(1-f[m])); np.add.at(h, i0[m]+2, W[m]*f[m])
    return h[1:-1]/dV/len(CX)
def gauss(h, sig):
    n = int(6*sig/dV)+1; x = np.arange(-n, n+1)*dV
    g = np.exp(-x**2/(2*sig**2)); g/=g.sum(); return np.convolve(h, g, mode='same')
def bcs(xi, Dk, sig):
    Ek = np.sqrt(xi**2 + Dk**2); u2 = 0.5*(1+xi/Ek); v2 = 0.5*(1-xi/Ek)
    return gauss(cic(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2])), sig), Ek
def bgf(Ek, b):
    return b*np.abs(Vf)*(np.abs(Vf) > Ek.min())
def F6(p):  # harmonics, mu fixed
    D0, D1, D2, D3, sig, amp, b = p
    xi = E0 - mu0; Dk = D0 + D1*(CX+CY)/2 + D2*CX*CY + D3*C2
    A, Ek = bcs(xi, Dk, sig); return amp*A + bgf(Ek, b)
def F7(p):  # xi-dependent gap
    D0, D1, D2, sig, amp, b = p
    xi = E0 - mu0; Dk = D0 + D1*np.abs(xi) + D2*xi**2
    A, Ek = bcs(xi, Dk, sig); return amp*A + bgf(Ek, b)
def F9(p):  # two bands split by +-tau with different gaps
    tau, Da, Db, sig, amp, b = p
    xa = E0 - mu0 - tau; xb = E0 - mu0 + tau
    A1, E1 = bcs(xa, Da*np.ones_like(xa), sig); A2, E2 = bcs(xb, Db*np.ones_like(xb), sig)
    return amp*(A1+A2)/2 + b*np.abs(Vf)*(np.abs(Vf) > min(E1.min(),E2.min()))
models = {'F6':(F6, [([2.6,0,0,0,0.15,3,0.01]),([4,2,0,0,0.15,3,0.01]),([4,0,1.5,0,0.15,3,0.01]),([3,0,0,1.5,0.15,3,0.01]),([5,-2,-1,0,0.15,3,0.01])],
              ([-8,-12,-8,-8,0.02,0.1,0],[8,12,8,8,0.6,30,0.05])),
          'F7':(F7, [([2.6,0.5,0,0.15,3,0.01]),([2.6,0,0.2,0.15,3,0.01]),([4,0,0,0.15,3,0.01])],
              ([0,-3,-1,0.02,0.1,0],[8,3,1,0.6,30,0.05])),
          'F9':(F9, [([1.0,2.6,5.0,0.15,3,0.01]),([2.0,5.0,2.6,0.15,3,0.01]),([3.0,3,3,0.15,3,0.01]),([0.5,4,2,0.15,3,0.01])],
              ([0,0,0,0.02,0.1,0],[6,8,8,0.6,30,0.05]))}
def run(args):
    name, i = args
    f, p0s, bnd = models[name]
    try:
        s = least_squares(lambda p: f(p)-G, p0s[i], bounds=bnd, diff_step=1e-3, max_nfev=400)
        return (name, 2*s.cost, list(np.round(s.x,4)))
    except Exception as e:
        return (name, 1e9, str(e))
if __name__ == '__main__':
    jobs = [(n,i) for n in models for i in range(len(models[n][1]))]
    with Pool(8) as pool: out = pool.map(run, jobs)
    for n in models:
        best = sorted([o for o in out if o[0]==n], key=lambda o:o[1])[0]
        print(n, 'SSE=%.4f'%best[1], best[2])
