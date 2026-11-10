import sys; sys.path.insert(0,'/app/analysis')
import numpy as np
from ed_rungs import spectrum
def bond_params(t, U, J, nnq=False):
    bonds=[(0,2,t),(1,3,t)]; Jb=[(0,1,J),(2,3,J)]
    w0 = spectrum(4,bonds,U,Jb,4,0,8,nnq); w1 = np.sort(spectrum(4,bonds,U,Jb,4,2,6,nnq))
    r0 = spectrum(2,[],U,[(0,1,J)],2,0,4,nnq)
    Es = w0[0]; dss = Es - 2*r0[0]
    g1, g2 = w1[0]-Es, w1[1]-Es
    J0 = r0[0]  # singlet energy
    trip = spectrum(2,[],U,[(0,1,J)],2,2,2,nnq)[0] - r0[0]   # bare triplet gap
    mid = 0.5*(g1+g2); tt = 0.5*(g2-g1)
    dts_minus_dss = mid - trip
    return trip, dts_minus_dss, tt
t, tp = 1.0, 0.1945
print(' J     U    bare_gap  2D triplon gap (NN+NNN, 2nd order)')
for J in [5.0, 6.0, 7.0, 7.5, 8.0]:
    U = 2*(6.0 - 0.75*J)
    g0, d1, t1 = bond_params(t, U, J)
    _, d2, t2 = bond_params(tp, U, J)
    # dispersion: g0 + 4*d1 + 4*d2 + 2 t1 (cx+cy) + 4 t2 cx cy ; scan BZ for min
    k = np.linspace(-np.pi, np.pi, 201); KX, KY = np.meshgrid(k,k)
    for s1 in (+1,-1):
        pass
    disp_p = g0 + 4*d1 + 4*d2 + 2*t1*(np.cos(KX)+np.cos(KY)) + 4*t2*np.cos(KX)*np.cos(KY)
    disp_m = g0 + 4*d1 + 4*d2 - 2*t1*(np.cos(KX)+np.cos(KY)) - 4*t2*np.cos(KX)*np.cos(KY)
    print('%.2f  %.2f   %.3f     min=%.3f (alt sign %.3f)  width=%.3f  [d_NN=%.4f t_NN=%.4f d_NNN=%.4f t_NNN=%.4f]' % (J, U, g0, disp_p.min(), disp_m.min(), disp_p.max()-disp_p.min(), d1, t1, d2, t2))
