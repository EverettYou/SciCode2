import sys; sys.path.insert(0,'/app/analysis')
import numpy as np, json
from scipy.optimize import least_squares
from multiprocessing import Pool
d = json.load(open('/app/measurements.json'))
S = {s['panel']: (np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
N = 160
k = (np.arange(N)+0.5)/N
KX, KY = np.meshgrid(k, k, indexing='ij')
CX, CY = np.cos(2*np.pi*KX).ravel(), np.cos(2*np.pi*KY).ravel()
t0, tp0 = 0.9993, 0.1945
E0 = -2*t0*(CX+CY) - 4*tp0*CX*CY
Vf = np.linspace(-10, 10, 801); dV = Vf[1]-Vf[0]
def cic(E, W):
    x = (E - Vf[0])/dV; i0 = np.floor(x).astype(int); f = x - i0
    h = np.zeros(len(Vf)+2); m = (i0 >= -1) & (i0 < len(Vf))
    np.add.at(h, i0[m]+1, W[m]*(1-f[m])); np.add.at(h, i0[m]+2, W[m]*f[m])
    return h[1:-1]/dV/len(CX)
def gauss(h, sig):
    n = int(6*sig/dV)+1; x = np.arange(-n, n+1)*dV
    g = np.exp(-x**2/(2*sig**2)); g/=g.sum(); return np.convolve(h, g, mode='same')
def model_gen(p):
    a, m1, b, m2, Phi, sig, amp, bb = p
    xi = a*(E0 - m1); eta = b*(E0 - m2)
    A_ = (xi - eta)/2; R = np.sqrt(((xi+eta)/2)**2 + Phi**2)
    wp, wm = A_ + R, A_ - R
    Zp = (wp + eta)/(wp - wm); Zm = (wm + eta)/(wm - wp)
    A = gauss(cic(np.concatenate([wp,wm]), np.concatenate([Zp,Zm])), sig)
    glo, ghi = wm.max(), wp.min()
    return amp*A + bb*np.abs(Vf)*((Vf<glo)|(Vf>ghi))
def run(args):
    panel, p0 = args
    V, G = S[panel]
    try:
        s = least_squares(lambda p: model_gen(p)-G, p0, bounds=([0.05,-6,-1.5,-6,0.3,0.02,0.1,0],[1.5,6,1.5,6,9,0.6,30,0.05]), diff_step=1e-3, max_nfev=300)
        return (2*s.cost, list(s.x), panel)
    except Exception as e:
        return (1e9, None, panel)
if __name__ == '__main__':
    jobs = []
    for panel in ['b']:
        for a0 in [0.5, 1.0]:
            for b0 in [-0.5, 0.5, 1.0]:
                for m in [-0.9, 0.0]:
                    for Phi0 in [2.5, 4.5]:
                        jobs.append((panel, [a0, m, b0, m, Phi0, 0.15, 3, 0.012]))
    with Pool(8) as pool:
        out = pool.map(run, jobs)
    out.sort(key=lambda x: x[0])
    for o in out[:6]:
        print('SSE=%.4f'%o[0], np.round(o[1],4))
    np.save('/app/analysis/fit_b3_best.npy', np.array(out[0][1]))
