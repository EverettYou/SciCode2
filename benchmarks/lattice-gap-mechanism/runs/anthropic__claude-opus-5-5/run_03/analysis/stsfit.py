import json, numpy as np
from scipy.optimize import least_squares
d = json.load(open('/app/measurements.json'))
S = {s['panel']: (np.array(s['bias']), np.array(s['dI_dV'])) for s in d['measurements'][0]['spectra']}
N = 300
k = (np.arange(N)+0.5)/N
KX, KY = np.meshgrid(k, k, indexing='ij')
CX, CY = np.cos(2*np.pi*KX).ravel(), np.cos(2*np.pi*KY).ravel()
def eps(t, tp, tpp=0.0):
    return -2*t*(CX+CY) - 4*tp*CX*CY - 2*tpp*(2*CX**2-1+2*CY**2-1)
def cic(E, W, V):
    """cloud-in-cell binning onto uniform grid V (density per unit energy per k-point)"""
    dV = V[1]-V[0]
    x = (E - V[0])/dV
    i0 = np.floor(x).astype(int); f = x - i0
    h = np.zeros(len(V)+2)
    m = (i0 >= -1) & (i0 < len(V))
    np.add.at(h, i0[m]+1, W[m]*(1-f[m]))
    np.add.at(h, i0[m]+2, W[m]*f[m])
    return h[1:-1]/dV/len(CX)
def gauss(h, dV, sig):
    if sig <= 0: return h
    n = int(6*sig/dV)+1
    x = np.arange(-n, n+1)*dV
    g = np.exp(-x**2/(2*sig**2)); g/=g.sum()
    return np.convolve(h, g, mode='same')
def lor(h, dV, gam):
    n = len(h)//2 - 1
    x = np.arange(-n, n+1)*dV
    g = gam/np.pi/(x**2+gam**2); g/=g.sum()
    return np.convolve(h, g, mode='same')
def dos(E, W, V, sig, kind='g'):
    h = cic(E, W, V)
    return gauss(h, V[1]-V[0], sig) if kind=='g' else lor(h, V[1]-V[0], sig)
def fitreport(s, names):
    J = s.jac; dof = len(s.fun)-len(s.x); s2 = (s.fun**2).sum()/dof
    try:
        cov = np.linalg.pinv(J.T@J)*s2; err = np.sqrt(np.abs(np.diag(cov)))
    except Exception:
        err = np.full(len(s.x), np.nan)
    return '  '.join('%s=%.4f+-%.4f'%(n,v,e) for n,v,e in zip(names,s.x,err)) + '  SSE=%.4f'%(2*s.cost)
