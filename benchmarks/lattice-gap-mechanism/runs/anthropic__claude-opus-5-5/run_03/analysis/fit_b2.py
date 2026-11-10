import sys; sys.path.insert(0,'/app/analysis')
from stsfit import *
Vf = np.linspace(-10, 10, 801)
t0, tp0 = 0.9993, 0.1945
E0 = eps(t0, tp0)
def twopole(xi, eta, Phi):
    # G^-1 = w - xi - Phi^2/(w + eta)
    A_ = (xi - eta)/2; R = np.sqrt(((xi+eta)/2)**2 + Phi**2)
    wp, wm = A_ + R, A_ - R
    Zp = (wp + eta)/(wp - wm); Zm = (wm + eta)/(wm - wp)
    return wp, wm, Zp, Zm
def model_gen(p, panel_bg=True, kind='g'):
    a, m1, b, m2, Phi, sig, amp, bb = p
    xi = a*(E0 - m1); eta = b*(E0 - m2)
    wp, wm, Zp, Zm = twopole(xi, eta, Phi)
    A = dos(np.concatenate([wp,wm]), np.concatenate([Zp,Zm]), Vf, sig, kind)
    lo, hi = wm.min(), wp.max(); glo, ghi = wm.max(), wp.min()
    bg = bb*np.abs(Vf)*((Vf<glo)|(Vf>ghi))
    return amp*A + bg
res = {}
for panel in ['a','b','c']:
    V, G = S[panel]
    best=None
    for a0 in [0.5, 1.0]:
      for b0 in [-0.5, 0.0, 0.5, 1.0]:
        for m in [-1.9, -0.9, -0.8, 0.0]:
          for Phi0 in [2.0, 4.0, 6.0]:
            try:
                s = least_squares(lambda p: model_gen(p)-G, [a0, m, b0, m, Phi0, 0.1, 3, 0.012],
                    bounds=([0.1,-5,-1.5,-5,0.3,0.01,0.1,0],[1.5,5,1.5,5,9,0.6,30,0.05]), diff_step=1e-3, max_nfev=400)
            except Exception as ex:
                continue
            if best is None or s.cost < best.cost: best = s
    res[panel] = best.x
    print('panel %s: '%panel + fitreport(best, ['a','mu1','b','mu2','Phi','sig','amp','bg']))
np.save('/app/analysis/gen_fits.npy', res)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(3,1,figsize=(10,11))
for ax, panel in zip(axs, ['a','b','c']):
    ax.plot(S[panel][0], S[panel][1], 'k-', lw=0.5); ax.plot(Vf, model_gen(res[panel]), 'r-'); ax.set_title(panel)
fig.savefig('/app/analysis/fit_gen.png', dpi=100)
