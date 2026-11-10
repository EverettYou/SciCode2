"""Final model spectral functions for the three crystals (poles and weights on a k-grid)."""
import numpy as np
from fitlib import kgrid, ebar
T_HOP, TP_HOP, U_HUB = 1.0, -0.2, 12.0     # ebar convention: eps_k = -2t(cos kx+cos ky) + 4 tp cos kx cos ky, tp=-0.2
def spectrum_half(kx, ky, weights='free'):
    """nu=1/2 Mott insulator: linearized two-pole bands, weights variants"""
    eb = ebar(kx, ky, T_HOP, TP_HOP); U = U_HUB
    Ep = eb/2 + U/2; Em = eb/2 - U/2
    if weights == 'free':      # best fit to STS: Z+ = 1/2 + (eb - e0)/(2 Uw)
        e0, Uw = 0.5293, 15.3723
        dlt = (eb - e0)/(2*Uw)
    elif weights == 'HI':      # Hubbard-I weights referenced to bare level eps_k = eb - 0.8
        ek = eb + 4*TP_HOP; R = np.sqrt(ek**2/4 + U**2/4); dlt = ek/(4*R)
    elif weights == 'const':
        dlt = 0*eb
    return [(Em, 0.5 - dlt), (Ep, 0.5 + dlt)]
def spectrum_03(kx, ky):
    """nu~0.3 pseudogap (pair) state: two Hubbard-like branches, fit B9"""
    eb = ebar(kx, ky, T_HOP, TP_HOP); x = eb/4.0
    a,b,c,a2,b2,c2,p0,p1,p2,q0,q1,q2 = 4.1204,2.3402,0.1025,-3.8892,2.4212,-0.109,0.4279,0.5155,0.0003,0.3915,-1.0145,-0.0043
    EU = a + b*x + c*x**2; EL = a2 + b2*x + c2*x**2
    ZU = np.clip(p0+p1*x+p2*x**2, 0, None); ZL = np.clip(q0+q1*x+q2*x**2, 0, None)
    return [(EL, ZL), (EU, ZU)]
def spectrum_02(kx, ky, Delta=1.9594, mu=-1.1004):
    """nu~0.2 BCS state on the bare band"""
    eb = ebar(kx, ky, T_HOP, TP_HOP); xi = eb - mu
    E = np.sqrt(xi**2 + Delta**2); u2 = 0.5*(1+xi/E); v2 = 0.5*(1-xi/E)
    return [(-E, v2), (E, u2)], xi, Delta
SIGMA = {'half':0.084, '03':0.115, '02':0.111}
