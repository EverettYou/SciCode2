import json, numpy as np
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d
d = json.load(open('/app/measurements.json'))
s = d['measurements'][0]['spectra'][1]
V = np.array(s['bias']); g = np.array(s['dI_dV']); dV = V[1]-V[0]
Nk = 500
k = 2*np.pi*(np.arange(Nk)+0.5)/Nk
kx, ky = np.meshgrid(k, k, indexing='ij')
e = (-2*(np.cos(kx)+np.cos(ky)) - 0.8*np.cos(kx)*np.cos(ky)).ravel()
mu0 = np.sort(e)[int(0.3*len(e))]
edges = np.append(V - dV/2, V[-1] + dV/2)
def dos(D0, Dinf, wid, sig, mu=mu0):
    xi = e - mu
    D = Dinf - (Dinf - D0)*np.exp(-np.abs(xi)/max(wid,1e-3))
    E = np.sqrt(xi**2 + D**2)
    h1, _ = np.histogram(E, bins=edges, weights=0.5*(1+xi/E))
    h2, _ = np.histogram(-E, bins=edges, weights=0.5*(1-xi/E))
    return gaussian_filter1d((h1+h2)/len(e)/dV, max(sig/dV, 0.3))
