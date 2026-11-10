# Smooth DOS models (sum of Gaussians over irreducible k-points) for fitting STS spectra
import numpy as np
from load import *
def kgrid(N=160):
    # irreducible wedge 0<=ky<=kx<=pi with weights
    ks=(np.arange(N)+0.5)/N*np.pi
    KX,KY=np.meshgrid(ks,ks,indexing='ij')
    m=KY<=KX
    w=np.where(np.isclose(KX,KY),1.0,2.0)
    return KX[m],KY[m],w[m]/np.sum(w[m])
KX,KY,WK=kgrid(140)
CX,CY=np.cos(KX),np.cos(KY)
def eps(t,tp,tpp=0.0):
    return -2*t*(CX+CY)-4*tp*CX*CY-2*tpp*(np.cos(2*KX)+np.cos(2*KY))
def gdos(V,E,Z,sig):
    # E,Z arrays over k ; returns sum_k w Z gaussian(V-E)
    out=np.zeros_like(V)
    for i in range(0,len(E),4000):
        e=E[i:i+4000]; z=Z[i:i+4000]*WK[i:i+4000]
        out+=np.exp(-(V[:,None]-e[None,:])**2/(2*sig**2))@z
    return out/(np.sqrt(2*np.pi)*sig)
