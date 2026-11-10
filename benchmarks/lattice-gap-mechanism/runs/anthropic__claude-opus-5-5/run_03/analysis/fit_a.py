import sys; sys.path.insert(0,'/app/analysis')
from stsfit import *
V, G = S['a']
Vf = np.linspace(-10, 10, 801)
def bg(V, b, edge):
    return b*np.abs(V)*(np.abs(V) > edge)
def model_lin(p):
    t, tp, Phi, sig, amp, b, alpha = p
    e = eps(t, tp); ec = 0.5*(e.min()+e.max()); x = (e-ec)/2
    Ep = Phi + x; Em = -Phi + x
    Zp = 0.5*(1+alpha*(e-ec)); Zm = 0.5*(1-alpha*(e-ec))
    A = dos(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm]), Vf, sig)
    edge = Phi - (e.max()-e.min())/4
    return amp*A + bg(Vf, b, edge)
def model_hyb(p):
    # hybridization / Hubbard-I like: E = (e+lam)/2 +- sqrt(((e-lam)/2)^2+V^2), shift so midgap=0
    t, tp, Vh, lam, sig, amp, b = p
    e = eps(t, tp)
    R = np.sqrt(((e-lam)/2)**2 + Vh**2)
    Ep = (e+lam)/2 + R; Em = (e+lam)/2 - R
    mid = 0.5*(Ep.min()+Em.max())
    Ep -= mid; Em -= mid
    Zp = 0.5*(1+(e-lam)/(2*R)); Zm = 0.5*(1-(e-lam)/(2*R))
    A = dos(np.concatenate([Ep,Em]), np.concatenate([Zp,Zm]), Vf, sig)
    edge = Ep.min()
    return amp*A + bg(Vf, b, edge)
def model_bcs(p):
    t, tp, mu, Dl, sig, amp, b = p
    e = eps(t, tp) - mu
    Ek = np.sqrt(e**2 + Dl**2)
    u2 = 0.5*(1+e/Ek); v2 = 0.5*(1-e/Ek)
    A = dos(np.concatenate([Ek,-Ek]), np.concatenate([u2,v2]), Vf, sig)
    return amp*A + bg(Vf, b, Dl)
def fit(model, p0, lo, hi):
    r = lambda p: (model(p) - G)
    s = least_squares(r, p0, bounds=(lo, hi))
    return s
s1 = fit(model_lin, [1.0, 0.19, 6.0, 0.1, 3.0, 0.012, 0.0], [0.8,0.0,4,0.01,0.1,0,-0.2],[1.2,0.4,8,0.5,20,0.05,0.2])
print('linear copies: ', np.round(s1.x,4), ' SSE=%.4f'%(2*s1.cost))
s2 = fit(model_hyb, [1.0, 0.19, 6.0, -0.8, 0.1, 3.0, 0.012], [0.8,0.0,3,-6,0.01,0.1,0],[1.2,0.4,9,6,0.5,20,0.05])
print('hybridization: ', np.round(s2.x,4), ' SSE=%.4f'%(2*s2.cost))
best3=None
for mu0 in [-1.5,-0.5,0.0,0.5]:
    s3 = fit(model_bcs, [1.0, 0.19, mu0, 4.0, 0.1, 3.0, 0.012], [0.8,0.0,-4,1,0.01,0.1,0],[1.2,0.4,4,8,0.5,20,0.05])
    if best3 is None or s3.cost<best3.cost: best3=s3
print('BCS mirror:    ', np.round(best3.x,4), ' SSE=%.4f'%(2*best3.cost))
# noise estimate from gap region
m = np.abs(V)<3.5
print('noise var in gap ~', np.var(G[m]), ' -> expected SSE ~', np.var(G[m])*len(G))
np.save('/app/analysis/fit_a_lin.npy', s1.x); np.save('/app/analysis/fit_a_hyb.npy', s2.x)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10,5))
ax.plot(V, G, 'k-', lw=0.5, label='data (a)')
ax.plot(Vf, model_lin(s1.x), 'r-', label='linear copies')
ax.plot(Vf, model_hyb(s2.x), 'b--', label='hybridization/Hubbard-I')
ax.plot(Vf, model_bcs(best3.x), 'g:', label='BCS mirror')
ax.legend(); fig.savefig('/app/analysis/fit_a.png', dpi=120)
