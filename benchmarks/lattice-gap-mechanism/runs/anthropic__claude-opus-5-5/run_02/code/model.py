"""Shared tools: data loading, tight-binding band, smooth DOS evaluation, spectral-function models.
Energies and temperatures in units of D (k_B = 1). Momenta: k in radians per lattice spacing
(the problem's units are k/(2*pi))."""
import json, numpy as np
DATA=json.load(open('/app/measurements.json'))['measurements']

def sts(panel):
    for s in DATA[0]['spectra']:
        if s['panel']==panel: return np.array(s['bias']),np.array(s['dI_dV'])
def nmr(f):
    for s in DATA[1]['samples']:
        if s['filling']==f: return np.array(s['temperature']),np.array(s['one_over_T1']),np.array(s['uncertainty'])
def res(f):
    for s in DATA[2]['samples']:
        if s['filling']==f: return np.array(s['temperature']),np.array(s['resistivity']),np.array(s['uncertainty'])

def eps(kx,ky,t,tp):
    """bare band: H = -t sum_NN c^dag c - t' sum_NNN c^dag c  ->  eps_k = -2t(cos kx+cos ky) - 4t' cos kx cos ky"""
    return -2*t*(np.cos(kx)+np.cos(ky))-4*tp*np.cos(kx)*np.cos(ky)

class Wedge:
    """irreducible 1/8 of the BZ with weights (for C4v-symmetric DOS sums)"""
    def __init__(self,N=90):
        ks=(np.arange(N)+0.5)/N*np.pi
        KX,KY=np.meshgrid(ks,ks,indexing='ij'); m=KY<=KX+1e-12
        w=np.where(np.isclose(KX,KY),1.0,2.0)
        self.kx,self.ky=KX[m],KY[m]; self.w=w[m]/w[m].sum()
    def eps(self,t,tp): return eps(self.kx,self.ky,t,tp)
    def gauss(self,V,E,Z,sig):
        sig=np.broadcast_to(np.asarray(sig,float),E.shape)
        A=np.exp(-(V[:,None]-E[None,:])**2/(2*sig[None,:]**2))/(np.sqrt(2*np.pi)*sig[None,:])
        return A@(Z*self.w)

# ---------------- spectral-function models (pole positions and weights for each k) -------------
def replica_poles(e,tp,c,Dl,Uw):
    """paired-liquid (nu=1/2) model: two replica bands of half bandwidth, centred at +-Dl about mid-gap.
       e = bare eps_k ; x = e - (band centre) ; weights follow the momentum distribution
       n_k = 1/2 - e/(2 sqrt(e^2+Uw^2)) (Hubbard-I form, Uw from data)."""
    x=e+4*tp
    Ep=0.5*x+c+Dl; Em=0.5*x+c-Dl
    Zp=0.5*(1+e/np.sqrt(e**2+Uw**2)); Zm=1-Zp
    return [(Ep,Zp),(Em,Zm)]

def bcs_poles(e,mu,Dk):
    xi=e-mu; E=np.sqrt(xi**2+Dk**2)
    u2=0.5*(1+xi/E); v2=1-u2
    return [(E,u2),(-E,v2)]

def nu03_parts(e,p):
    """nu~0.3 phenomenological strong-coupling SC: k-dependent gap rising from Delta_FS on the
       underlying Fermi surface to Delta_inf away from it, with extra broadening of Fermi-surface
       quasiparticles (pair-fluctuation smearing)."""
    mu,DF,Dinf,w,s0,s1,ws=p
    xi=e-mu
    Dk=DF+(Dinf-DF)*(1-np.exp(-xi**2/w**2))
    E=np.sqrt(xi**2+Dk**2); u2=0.5*(1+xi/E); v2=1-u2
    sig=s0+s1*np.exp(-xi**2/ws**2)
    return xi,Dk,E,u2,v2,sig

# ---------------- final parameter sets (filled by fit_all.py; defaults are the fitted values) -----
PARAMS_FILE='/app/code/params.json'
def load_params():
    return json.load(open(PARAMS_FILE))
