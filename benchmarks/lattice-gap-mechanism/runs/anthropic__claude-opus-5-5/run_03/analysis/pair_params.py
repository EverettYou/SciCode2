import sys; sys.path.insert(0,'/app/analysis')
import numpy as np
from ed_rungs import spectrum
t, tp = 1.0, 0.1945
for (U,J) in [(0.0,8.0),(3.0,6.0)]:
    for tt,lab in [(t,'NN'),(tp,'NNN')]:
        bonds=[(0,2,tt),(1,3,tt)]; Jb=[(0,1,J),(2,3,J)]
        w2 = spectrum(4,bonds,U,Jb,2,0,6)     # one pair on two rungs
        w4 = spectrum(4,bonds,U,Jb,4,0,4)     # two pairs
        w1 = spectrum(4,bonds,U,Jb,1,1,4)     # one electron on two rungs
        w3 = spectrum(4,bonds,U,Jb,3,1,4)     # three electrons
        rs = spectrum(2,[],U,[(0,1,J)],2,0,1)[0]   # isolated singlet
        # pair: two lowest levels -> -3J/4+delta +- t_b
        Eb1, Eb2 = w2[0], w2[1]
        tb = 0.5*(Eb2-Eb1); delta_b = 0.5*(Eb1+Eb2) - rs
        Vb = w4[0] - (2*rs) - 2*delta_b   # NN pair-pair interaction relative to independent shifts (approx)
        print('U=%.1f J=%.1f %s: pair levels %.4f %.4f -> t_b=%.4f, shift=%.4f ; two-pair E=%.4f -> V_b~%.4f ; 1e levels %s'%(U,J,lab,Eb1,Eb2,tb,delta_b,w4[0],Vb,np.round(w1[:2],3)))
