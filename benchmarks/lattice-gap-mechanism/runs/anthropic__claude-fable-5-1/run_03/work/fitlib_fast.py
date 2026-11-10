import json, numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import least_squares
d=json.load(open('/app/measurements.json'))
STS=d['measurements'][0]['spectra']
NK=260
k=(np.arange(NK)+0.5)/NK*2*np.pi-np.pi
KX,KY=np.meshgrid(k,k,indexing='ij')
CX,CY=np.cos(KX),np.cos(KY)
def band(t,tp,tpp=0.0):
    return -2*t*(CX+CY)-4*tp*CX*CY-2*tpp*(np.cos(2*KX)+np.cos(2*KY))
GRID=np.linspace(-14,14,5601); DG=GRID[1]-GRID[0]
EDGES=np.append(GRID-DG/2,GRID[-1]+DG/2)
def dos(E,w,sigma):
    h,_=np.histogram(E.ravel(),bins=EDGES,weights=w.ravel())
    h=h/DG/E.size
    return gaussian_filter1d(h,max(sigma,1e-3)/DG)
def sample(rho,V):
    return np.interp(V,GRID,rho)
def mu_for_filling(eps,n):
    es=np.sort(eps.ravel()); i=int(round(n/2*es.size)); i=min(max(i,0),es.size-1); return es[i]
