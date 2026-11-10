import numpy as np
from load import *
def kgrid(N):
    ks=(np.arange(N)+0.5)/N*np.pi
    KX,KY=np.meshgrid(ks,ks,indexing='ij')
    m=KY<=KX+1e-12
    w=np.where(np.isclose(KX,KY),1.0,2.0)
    return KX[m],KY[m],w[m]/np.sum(w[m])
class DOS:
    def __init__(self,N=90):
        self.KX,self.KY,self.W=kgrid(N)
        self.CX,self.CY=np.cos(self.KX),np.cos(self.KY)
        self.C2=np.cos(2*self.KX)+np.cos(2*self.KY)
    def eps(self,t,tp):
        return -2*t*(self.CX+self.CY)-4*tp*self.CX*self.CY
    def g(self,V,E,Z,sig):
        A=np.exp(-(V[:,None]-E[None,:])**2/(2*sig**2))
        return A@(Z*self.W)/(np.sqrt(2*np.pi)*sig)
