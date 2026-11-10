import sys; sys.path.insert(0,'/app/analysis')
from stsfit import *
Vf = np.linspace(-10, 10, 801)
t0, tp0 = 0.9993, 0.1945
def bcs_dos(xi, Dk, sig, kind='g'):
    Ek = np.sqrt(xi**2 + Dk**2)
    u2 = 0.5*(1+xi/Ek); v2 = 0.5*(1-xi/Ek)
    return dos(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2]), Vf, sig, kind), Ek
# ---- (c): BCS, constant gap, free mu and bandwidth factor g
V, G = S['c']
def model_c(p, kind='g'):
    g, mu, D0, sig, amp, b0, b1 = p
    e = g*eps(t0, tp0)
    xi = e - mu
    A, Ek = bcs_dos(xi, D0*np.ones_like(xi), sig, kind)
    lo = -np.sqrt(xi.min()**2 + D0**2); hi = np.sqrt(xi.max()**2+D0**2)
    bg = np.where(Vf<lo, b0*np.abs(Vf), 0) + np.where(Vf>hi, b1*np.abs(Vf), 0)
    return amp*A + bg
for kind in ['g','l']:
    s = least_squares(lambda p: model_c(p,kind)-G, [1.0,-1.8,1.9,0.1,3,0.01,0.01], bounds=([0.5,-4,0.5,0.005,0.1,0,0],[1.5,1,4,0.6,30,0.05,0.05]), diff_step=1e-3)
    print('(c) BCS const gap (%s): '%kind + fitreport(s, ['g','mu','Delta','sig','amp','b0','b1']))
    e = s.x[0]*eps(t0,tp0); print('     normal-state filling nu = %.4f'%np.mean(e<s.x[1]))
sc = s.x
# ---- (b): BCS with general s-wave harmonics, mu fixed by (d) or free
V, G = S['b']
def model_b(p, kind='g'):
    g, mu, D0, D1, D2, sig, amp, b0, b1 = p
    e = g*eps(t0, tp0); xi = e - mu
    Dk = D0 + D1*(CX+CY)/2 + D2*CX*CY
    A, Ek = bcs_dos(xi, Dk, sig, kind)
    lo = -Ek.max(); hi = Ek.max()
    bg = np.where(Vf<lo, b0*np.abs(Vf), 0) + np.where(Vf>hi, b1*np.abs(Vf), 0)
    return amp*A + bg
best=None
for D0 in [0, 2.6, 4.0]:
  for D1 in [-4, 0, 4]:
    for D2 in [-2, 0, 2]:
        s = least_squares(lambda p: model_b(p)-G, [1.0,-0.91,D0,D1,D2,0.1,3,0.01,0.01], bounds=([0.5,-4,-8,-12,-8,0.005,0.1,0,0],[1.5,2,8,12,8,0.6,30,0.05,0.05]), diff_step=1e-3)
        if best is None or s.cost < best.cost: best = s
print('(b) BCS general s (g): ' + fitreport(best, ['g','mu','D0','D1','D2','sig','amp','b0','b1']))
e = best.x[0]*eps(t0,tp0); print('     normal-state filling nu = %.4f'%np.mean(e<best.x[1]))
sb = best.x
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, axs = plt.subplots(2,1,figsize=(10,8))
axs[0].plot(S['c'][0], S['c'][1], 'k-', lw=0.5); axs[0].plot(Vf, model_c(sc,'l'), 'r-'); axs[0].set_title('(c) BCS const gap')
axs[1].plot(S['b'][0], S['b'][1], 'k-', lw=0.5); axs[1].plot(Vf, model_b(sb), 'r-'); axs[1].set_title('(b) BCS general s-wave harmonics')
fig.savefig('/app/analysis/fit_bc.png', dpi=110)
